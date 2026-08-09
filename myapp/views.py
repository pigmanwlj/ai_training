from pathlib import Path
import secrets
import subprocess

from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core import signing
from django.db import transaction
from django.http import HttpResponse, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from myapp.models import TrainingContainer, budget, pr


SCRIPT_DIR = Path(__file__).resolve().parent / "ai_containers"

SCRIPT_CHOICES = {
    "ollama_a100": SCRIPT_DIR / "ollama_a100.sh",
    "ollama_h800": SCRIPT_DIR / "ollama_h800.sh",
    "ollama_rtx5090": SCRIPT_DIR / "ollama_rtx5090.sh",
}

ACTION_LABELS = {
    "start": "Start Ollama",
    "stop": "Stop Ollama",
    "remove": "Remove Ollama",
}


def _parse_kv_output(text):
    data = {}
    for raw_line in (text or "").splitlines():
        line = raw_line.strip()
        if not line or "=" not in line:
            continue
        k, v = line.split("=", 1)
        data[k.strip()] = v.strip()
    return data


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
                ("ollama_a100", "ollama_a100.sh"),
                ("ollama_h800", "ollama_h800.sh"),
                ("ollama_rtx5090", "ollama_rtx5090.sh"),
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
            script_path = SCRIPT_CHOICES.get(script_key)
            if not script_path:
                messages.error(request, "Please select a valid script for Start.")
                return redirect("training_page")

            owned_active = TrainingContainer.objects.filter(
                owner=request.user,
                status__in=[TrainingContainer.Status.STARTING, TrainingContainer.Status.RUNNING],
            ).first()
            if owned_active:
                messages.error(
                    request,
                    f"You already have an active container: {owned_active.docker_name}",
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
                    messages.error(request, "No free container slot for selected hardware profile.")
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

            # SECURITY_NOTE: script path is selected from a fixed server-side allow-list.
            # SECURITY_NOTE: username is passed as a positional argument list, no shell interpolation.
            cmd = ["/bin/sh", str(script_path), request.user.username]

            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=120,
            )

            meta = _parse_kv_output(result.stdout)
            container_name = meta.get("CONTAINER_NAME", "").strip()
            host_port_raw = meta.get("HOST_PORT", "").strip()

            if not container_name:
                raise ValueError("Script did not return CONTAINER_NAME.")

            try:
                host_port = int(host_port_raw)
            except Exception:
                raise ValueError("Script did not return valid HOST_PORT.")

            slot.docker_name = container_name
            slot.host_port = host_port
            slot.status = TrainingContainer.Status.RUNNING
            slot.started_at = timezone.now()
            slot.save(update_fields=["docker_name", "host_port", "status", "started_at", "updated_at"])

            label = ACTION_LABELS.get(action, action)
            messages.success(
                request,
                f"{label} completed. Container: {slot.docker_name}, Port: {slot.host_port}",
            )

        elif action == "stop":
            mine = TrainingContainer.objects.filter(
                owner=request.user,
                status__in=[TrainingContainer.Status.STARTING, TrainingContainer.Status.RUNNING],
            ).first()
            if not mine:
                messages.error(request, "You do not have a running container to stop.")
                return redirect("training_page")

            cmd = ["docker", "stop", mine.docker_name]
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=45,
            )

            mine.status = TrainingContainer.Status.STOPPED
            mine.stopped_at = timezone.now()
            mine.save(update_fields=["status", "stopped_at", "updated_at"])

            out = (result.stdout or "").strip()
            if out:
                messages.success(request, f"{ACTION_LABELS['stop']} completed. Output: {out}")
            else:
                messages.success(request, f"{ACTION_LABELS['stop']} completed.")

        else:
            mine = TrainingContainer.objects.filter(owner=request.user).first()
            if not mine:
                messages.error(request, "You do not own any container to remove.")
                return redirect("training_page")

            cmd = ["docker", "rm", "-f", mine.docker_name]
            result = subprocess.run(
                cmd,
                check=True,
                capture_output=True,
                text=True,
                timeout=45,
            )

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

            out = (result.stdout or "").strip()
            if out:
                messages.success(request, f"{ACTION_LABELS['remove']} completed. Output: {out}")
            else:
                messages.success(request, f"{ACTION_LABELS['remove']} completed.")

    except subprocess.TimeoutExpired:
        messages.error(request, "Command timed out.")
    except subprocess.CalledProcessError as e:
        err = (e.stderr or str(e)).strip()
        messages.error(request, f"Failed to run action: {err}")

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
    except FileNotFoundError:
        messages.error(request, "Docker or shell executable was not found on server.")

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
        return JsonResponse({"error": "No running container owned by current user."}, status=400)

    token = signing.dumps(
        {
            "container_id": mine.id,
            "user_id": request.user.id,
            "docker_name": mine.docker_name,
            "host_port": mine.host_port,
            "nonce": mine.token_nonce,
        },
        salt="xterm-connect",
    )

    return JsonResponse(
        {
            "ws_url": "/ws/training/terminal/",
            "token": token,
            "container_name": mine.docker_name,
            "host_port": mine.host_port,
        }
    )

