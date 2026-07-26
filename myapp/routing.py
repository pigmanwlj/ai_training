from django.urls import re_path
from .consumers import DockerTerminalConsumer

websocket_urlpatterns = [
    re_path(r'^ws/training/terminal/$', DockerTerminalConsumer.as_asgi()),
]

