from django.urls import re_path

from .consumers import PodTerminalConsumer


websocket_urlpatterns = [
    re_path(r"^ws/training/terminal/$", PodTerminalConsumer.as_asgi()),
]

