from pathlib import Path
import os
import re
import secrets
import time

import yaml
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.config.config_exception import ConfigException

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core import signing
from django.db import transaction
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from myapp.models import TrainingContainer, budget, pr


KUBE_NAMESPACE = os.environ.get("KUBE_NAMESPACE", "ai-training")

TEMPLATE_DIR = Path(__file__).resolve().parent / "ai_containers"
POD_TEMPLATE_FILES = {
    "ollama_a100": TEMPLATE_DIR / "ollama_a100.yaml",
    "ollama_h800": TEMPLATE_DIR / "ollama_h800.yaml",
    "ollama_rtx5090": TEMPLATE_DIR / "ollama_rtx5090.yaml",
}

ACTION_LABELS = {
    "start": "Start Ollama",
    "stop": "Stop Ollama",
    "remove": "Remove Ollama",
}


def _load_k8s_api():
    try:
        config.load_incluster_config()
    except ConfigException:
        config.load_kube_config()
    return client.CoreV1Api()


def _safe_pod_suffix(username):
    safe = re.sub(r"[^a-z0-9.-]", "-", username.lower()).strip("-.")
    return safe or "anon"


def _build_pod_name(profile_key, username):
    suffix = secrets.token_hex(4)
    base = f"ollama-{profile_key}-{_safe_pod_suffix(username)}-{suffix}"
    return base[:63].rstrip("-")


def _load_pod_template(profile_key, username):
    template_path = POD_TEMPLATE_FILES.get(profile_key)
    if not template_path:
        raise ValueError("Please select a valid profile.")

    if not template_path.exists():
        raise FileNotFoundError(f"Pod template not found: {template_path}")

    manifest = yaml.safe_load(template_path.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Invalid YAML pod template.")

    pod_name = _build_pod_name(profile_key, username)

    metadata = manifest.setdefault("metadata", {})
    metadata["name"] = pod_name
    metadata["namespace"] = KUBE_NAMESPACE
    labels = metadata.setdefault("labels", {})
    labels["app"] = "training"
    labels["profile"] = profile_key
    labels["owner"] = username.lower()

    spec = manifest.setdefault("spec", {})
    containers = spec.get("containers") or []
    if not containers:
        raise ValueError("Pod template must define at least one container.")

    main_container = containers[0]
    main_container["name"] = main_container.get("name", "ollama")

    return manifest, pod_name


def _wait_for_pod_running(api, pod_name, namespace, timeout_seconds=120):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            pod = api.read_namespaced_pod(name=pod_name, namespace=namespace)
            if pod.status and pod.status.phase == "Running":
                return True
            if pod.status and pod.status.phase in {"Failed", "Succeeded"}:
                return False
        except ApiException:
            pass
        time.sleep(2)
    return False


def _delete_pod(api, pod_name, namespace):
    try:
        api.delete_namespaced_pod(
            name=pod_name,
            namespace=namespace,
            body=client.V1DeleteOptions(grace_period_seconds=30),
        )
    except ApiException as exc:
        if exc.status != 404:
            raise


def index(request):
    return HttpResponse("Hello, world. You're at the myapp index.")


def add(request):
    lists = pr.objects.all()
    for pr_obj in lists:
        print(pr_obj)
    return HttpResponse("Add......")


@login_required
@user_passes_test(lambda u: u.is_staff)
def training_page(request):
    my_active_container = TrainingContainer.objects.filter(
        owner=request.user,
        status__in=[TrainingContainer.Status.STARTING, TrainingContainer.Status.RUNNING, TrainingContainer.Status.STOPPED],
    ).first()

    return render(
        request,
        "myapp/training.html",
        {
            "script_options": [
                ("ollama_a100", "ollama_a100.yaml"),
                ("ollama_h800", "ollama_h800.yaml"),
                ("ollama_rtx5090", "ollama_rtx5090.yaml"),
            ],
            "my_active_container": my_active_container,
        },
    )


@login_required
@user_passes_test(lambda u: u.is_staff)
def training_run_ollama(request):
    if request.method != "POST":
        return HttpResponseNotAllowed(["POST"])

    action = request.POST.get("action", "").strip()
    script_key = request.POST.get("script_choice", "").strip()

    if action not in {"start", "stop", "remove"}:
        messages.error(request, "Invalid action selected.")
        return redirect("training_page")

    try:
        if action == "start":
            if script_key not in POD_TEMPLATE_FILES:
                messages.error(request, "Please select a valid profile.")
                return redirect("training_page")

            owned_active = TrainingContainer.objects.filter(
                owner=request.user,
                status__in=[TrainingContainer.Status.STARTING, TrainingContainer.Status.RUNNING],
            ).first()
            if owned_active:
                messages.error(
                    request,
                    f"You already have an active pod: {owned_active.pod_name}",
                )
                return redirect("training_page")

            with transaction.atomic():
                slot = (
                    TrainingContainer.objects.select_for_update()
                    .filter(
                        profile=script_key,
                        status=TrainingContainer.Status.FREE,
                        owner__isnull=True,
                    )
                    .first()
                )

                if not slot:
                    messages.error(request, "No free pod slot for selected hardware profile.")
                    return redirect("training_page")

                slot.owner = request.user
                slot.status = TrainingContainer.Status.STARTING
                slot.allocated_at = timezone.now()
                slot.started_at = None
                slot.stopped_at = None
                slot.host_port = None
                slot.token_nonce = secrets.token_hex(16)
                slot.save(
                    update_fields=[
                        "owner",
                        "status",
                        "allocated_at",
                        "started_at",
                        "stopped_at",
                        "host_port",
                        "token_nonce",
                        "updated_at",
                    ]
                )

            try:
                api = _load_k8s_api()
                manifest, pod_name = _load_pod_template(script_key, request.user.username)

                api.create_namespaced_pod(
                    namespace=KUBE_NAMESPACE,
                    body=manifest,
                )

                if not _wait_for_pod_running(api, pod_name, KUBE_NAMESPACE, timeout_seconds=120):
                    slot.status = TrainingContainer.Status.ERROR
                    slot.save(update_fields=["status", "updated_at"])
                    messages.error(request, "Pod failed to reach Running state.")
                    return redirect("training_page")

                slot.pod_name = pod_name
                slot.host_port = None
                slot.status = TrainingContainer.Status.RUNNING
                slot.started_at = timezone.now()
                slot.save(
                    update_fields=[
                        "pod_name",
                        "host_port",
                        "status",
                        "started_at",
                        "updated_at",
                    ]
                )

                label = ACTION_LABELS.get(action, action)
                messages.success(
                    request,
                    f"{label} completed. Pod: {slot.pod_name}",
                )

            except ApiException as e:
                slot.status = TrainingContainer.Status.ERROR
                slot.save(update_fields=["status", "updated_at"])
                messages.error(request, f"Kubernetes API error: {e.reason}")

            except Exception as e:
                slot.status = TrainingContainer.Status.ERROR
                slot.save(update_fields=["status", "updated_at"])
                messages.error(request, f"Unexpected error: {str(e)}")

        elif action == "stop":
            mine = TrainingContainer.objects.filter(
                owner=request.user,
                status__in=[TrainingContainer.Status.STARTING, TrainingContainer.Status.RUNNING],
            ).first()
            if not mine:
                messages.error(request, "You do not have a running pod to stop.")
                return redirect("training_page")

            try:
                api = _load_k8s_api()
                _delete_pod(api, mine.pod_name, KUBE_NAMESPACE)

                mine.status = TrainingContainer.Status.STOPPED
                mine.stopped_at = timezone.now()
                mine.save(update_fields=["status", "stopped_at", "updated_at"])

                messages.success(request, f"{ACTION_LABELS['stop']} completed.")

            except ApiException as e:
                messages.error(request, f"Kubernetes API error: {e.reason}")

            except Exception as e:
                messages.error(request, f"Unexpected error: {str(e)}")

        else:
            mine = TrainingContainer.objects.filter(owner=request.user).first()
            if not mine:
                messages.error(request, "You do not own any pod to remove.")
                return redirect("training_page")

            try:
                api = _load_k8s_api()
                _delete_pod(api, mine.pod_name, KUBE_NAMESPACE)

                mine.status = TrainingContainer.Status.FREE
                mine.owner = None
                mine.host_port = None
                mine.token_nonce = ""
                mine.allocated_at = None
                mine.started_at = None
                mine.stopped_at = timezone.now()
                mine.save(
                    update_fields=[
                        "status",
                        "owner",
                        "host_port",
                        "token_nonce",
                        "allocated_at",
                        "started_at",
                        "stopped_at",
                        "updated_at",
                    ]
                )

                messages.success(request, f"{ACTION_LABELS['remove']} completed.")

            except ApiException as e:
                messages.error(request, f"Kubernetes API error: {e.reason}")

            except Exception as e:
                messages.error(request, f"Unexpected error: {str(e)}")

    except ApiException as e:
        messages.error(request, f"Kubernetes API error: {e.reason}")

        if action == "start":
            failed_slot = TrainingContainer.objects.filter(
                owner=request.user,
                status=TrainingContainer.Status.STARTING,
            ).first()
            if failed_slot:
                failed_slot.status = TrainingContainer.Status.ERROR
                failed_slot.save(update_fields=["status", "updated_at"])

    except Exception as e:
        messages.error(request, f"Unexpected error: {str(e)}")

        if action == "start":
            failed_slot = TrainingContainer.objects.filter(
                owner=request.user,
                status=TrainingContainer.Status.STARTING,
            ).first()
            if failed_slot:
                failed_slot.status = TrainingContainer.Status.ERROR
                failed_slot.save(update_fields=["status", "updated_at"])

    return redirect("training_page")


@require_POST
@login_required
@user_passes_test(lambda u: u.is_staff)
def training_connect_terminal(request):
    mine = TrainingContainer.objects.filter(
        owner=request.user,
        status=TrainingContainer.Status.RUNNING,
    ).first()

    if not mine:
        return JsonResponse({"error": "No running pod owned by current user."}, status=400)

    token = signing.dumps(
        {
            "container_id": mine.id,
            "user_id": request.user.id,
            "pod_name": mine.pod_name,
            "pod_namespace": KUBE_NAMESPACE,
            "pod_container_name": "ollama",
            "nonce": mine.token_nonce,
        },
        salt="xterm-connect",
    )

    return JsonResponse(
        {
            "ws_url": "/ws/training/terminal/",
            "token": token,
            "pod_name": mine.pod_name,
            "pod_namespace": KUBE_NAMESPACE,
            "pod_container_name": "ollama",
        }
    )

