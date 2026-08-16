import asyncio
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.core import signing
from kubernetes import client, config
from kubernetes.config.config_exception import ConfigException
from kubernetes.stream import stream

from myapp.models import TrainingContainer


def _load_k8s_api_client():
    try:
        config.load_incluster_config()
    except ConfigException:
        config.load_kube_config()
    return client.CoreV1Api()


class PodTerminalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated or not user.is_staff:
            await self.close(code=4403)
            return

        try:
            raw_qs = self.scope.get("query_string", b"").decode()
            token = parse_qs(raw_qs).get("token", [""])[0]
            data = signing.loads(token, salt="xterm-connect", max_age=300)
        except Exception:
            await self.close(code=4400)
            return

        container = await self._get_valid_user_container(user.id, data)
        if not container:
            await self.close(code=4403)
            return

        self.pod_name = container["pod_name"]
        self.pod_namespace = container["pod_namespace"]
        self.pod_container_name = container["pod_container_name"]

        try:
            self.api = _load_k8s_api_client()
            self.exec_ws = await asyncio.to_thread(self._open_exec_session)
        except Exception:
            await self.close(code=4500)
            return

        await self.accept()
        self.reader_task = asyncio.create_task(self._read_output())

    def _open_exec_session(self):
        return stream(
            self.api.connect_get_namespaced_pod_exec,
            self.pod_name,
            self.pod_namespace,
            container=self.pod_container_name,
            command=["/bin/sh"],
            stdin=True,
            stdout=True,
            stderr=True,
            tty=True,
            _preload_content=False,
        )

    @database_sync_to_async
    def _get_valid_user_container(self, user_id, token_data):
        container_id = token_data.get("container_id")
        token_user_id = token_data.get("user_id")
        pod_name = token_data.get("pod_name")
        pod_namespace = token_data.get("pod_namespace")
        pod_container_name = token_data.get("pod_container_name")
        nonce = token_data.get("nonce")

        if token_user_id != user_id:
            return None

        try:
            obj = TrainingContainer.objects.get(
                id=container_id,
                owner_id=user_id,
                status=TrainingContainer.Status.RUNNING,
            )
        except TrainingContainer.DoesNotExist:
            return None

        if obj.pod_name != pod_name:
            return None

        if not nonce or obj.token_nonce != nonce:
            return None

        if not pod_namespace:
            return None

        if not pod_container_name:
            return None

        return {
            "pod_name": pod_name,
            "pod_namespace": pod_namespace,
            "pod_container_name": pod_container_name,
        }

    async def _read_output(self):
        try:
            while True:
                if not getattr(self, "exec_ws", None):
                    break

                try:
                    if self.exec_ws.peek_stdout():
                        data = self.exec_ws.read_stdout()
                        if data:
                            await self.send(text_data=data)

                    if self.exec_ws.peek_stderr():
                        err = self.exec_ws.read_stderr()
                        if err:
                            await self.send(text_data=err)

                    if not self.exec_ws.is_open():
                        break

                    await asyncio.sleep(0.05)
                except Exception:
                    break
        finally:
            try:
                if getattr(self, "exec_ws", None):
                    self.exec_ws.close()
            except Exception:
                pass

            try:
                await self.close()
            except Exception:
                pass

    async def receive(self, text_data=None, bytes_data=None):
        if not getattr(self, "exec_ws", None):
            return

        data = bytes_data if bytes_data is not None else (text_data or "").encode()
        if not data:
            return

        try:
            await asyncio.to_thread(self.exec_ws.write_stdin, data.decode(errors="replace"))
        except Exception:
            try:
                await self.close()
            except Exception:
                pass

    async def disconnect(self, close_code):
        if hasattr(self, "reader_task"):
            self.reader_task.cancel()

        try:
            if getattr(self, "exec_ws", None):
                await asyncio.to_thread(self.exec_ws.close)
        except Exception:
            pass

