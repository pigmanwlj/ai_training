#from django.shortcuts import render
from pathlib import Path
import subprocess

from django.http import HttpResponse
from myapp.models import budget
from myapp.models import pr
from django.shortcuts import render, redirect
from django.http import HttpResponseNotAllowed
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.core import signing
from django.views.decorators.http import require_POST


SCRIPT_DIR = Path(__file__).resolve().parent / "ai_containers"

SCRIPT_CHOICES = {
    "nginx001": SCRIPT_DIR / "nginx001.sh",
    "nginx002": SCRIPT_DIR / "nginx002.sh",
    "nginx003": SCRIPT_DIR / "nginx003.sh",
}

ACTION_LABELS = {
    "start": "Start Nginx",
    "stop": "Stop Nginx",
    "remove": "Remove Nginx",
}


# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the myapp index.")

def add(request):
    lists = budget.objects.all()
    for budget in lists:
        print(budget)

    print(budget.objects.get(id=3))
    return HttpResponse("Add......")

def add(request):
    lists = pr.objects.all()
    for pr_obj in lists:
        print(pr_obj)

    print(pr.objects.get(id=3))
    return HttpResponse("Add......")

#def uploads(request):
#    return HttpResponse('hello world')

@login_required
@user_passes_test(lambda u: u.is_staff)
def training_page(request):
    return render(
        request,
        "myapp/training.html",
        {
            "script_options": [
                ("nginx001", "nginx001.sh"),
                ("nginx002", "nginx002.sh"),
                ("nginx003", "nginx003.sh"),
            ]
        },
    )

@login_required
@user_passes_test(lambda u: u.is_staff)
def training_run_nginx(request):
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

            # SECURITY_NOTE: script path is selected from a fixed server-side allow-list.
            cmd = ["/bin/sh", str(script_path)]
        elif action == "stop":
            cmd = ["docker", "stop", "nginx"]
        else:  # remove
            cmd = ["docker", "rm", "-f", "nginx"]

        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            timeout=45,
        )

        label = ACTION_LABELS.get(action, action)
        out = (result.stdout or "").strip()
        if out:
            messages.success(request, f"{label} completed. Output: {out}")
        else:
            messages.success(request, f"{label} completed.")
    except subprocess.TimeoutExpired:
        messages.error(request, "Command timed out.")
    except subprocess.CalledProcessError as e:
        err = (e.stderr or str(e)).strip()
        messages.error(request, f"Failed to run action: {err}")
    except FileNotFoundError:
        messages.error(request, "Docker or shell executable was not found on server.")

    return redirect("training_page")

@require_POST
@login_required
@user_passes_test(lambda u: u.is_staff)
def training_connect_terminal(request):
    token = signing.dumps(
        {"container": "nginx", "user": request.user.username},
        salt="xterm-connect"
    )
    return JsonResponse({
        "ws_url": "/ws/training/terminal/",
        "token": token,
    })

