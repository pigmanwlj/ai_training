from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path


def healthz(request):
    return JsonResponse({"status": "ok"})


def readyz(request):
    return JsonResponse({"status": "ready"})


urlpatterns = [
    path("healthz/", healthz, name="healthz"),
    path("readyz/", readyz, name="readyz"),
    path("admin/", admin.site.urls),
    path("myapp/", include("myapp.urls")),
]

