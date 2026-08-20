from django.urls import path

from . import views


urlpatterns = [
    path("", views.index, name="index"),
    path("add", views.add, name="madd"),
    path("training/", views.training_page, name="training_page"),
    path("training/usage-report/", views.training_usage_report, name="training_usage_report"),
    path("training/run-ollama/", views.training_run_ollama, name="training_run_ollama"),
    path("training/connect-terminal/", views.training_connect_terminal, name="training_connect_terminal"),
]

