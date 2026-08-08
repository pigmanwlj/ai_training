import asyncio
import os
import pty
import signal
import subprocess
from urllib.parse import parse_qs

from channels.generic.websocket import AsyncWebsocketConsumer
from django.core import signing


class DockerTerminalConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope.get("user")
        if not user or not user.is_authenticated or not user.is_staff:
            await self.close(code=4403)
            return

        try:
            raw_qs = self.scope.get("query_string", b"").decode()
            token = parse_qs(raw_qs).get("token", [""])[0]
            data = signing.loads(token, salt="xterm-connect", max_age=300)
            if data.get("container") != "ollama":
                await self.close(code=4400)
                return
        except Exception:
            await self.close(code=4400)
            return

        self.master_fd, self.slave_fd = pty.openpty()

        self.proc = subprocess.Popen(
            ["docker", "exec", "-it", "ollama", "/bin/sh"],
            stdin=self.slave_fd,
            stdout=self.slave_fd,
            stderr=self.slave_fd,
            close_fds=True,
        )

        await self.accept()
        self.reader_task = asyncio.create_task(self._read_output())

    async def _read_output(self):
        try:
            while True:
                chunk = await asyncio.to_thread(os.read, self.master_fd, 1024)
                if not chunk:
                    break
                await self.send(text_data=chunk.decode(errors="replace"))
        except Exception:
            pass
        finally:
            if getattr(self, "close_code", None) is None:
                await self.close()

    async def receive(self, text_data=None, bytes_data=None):
        if not hasattr(self, "master_fd"):
            return

        data = bytes_data if bytes_data is not None else (text_data or "").encode()
        if data:
            os.write(self.master_fd, data)

    async def disconnect(self, close_code):
        if hasattr(self, "reader_task"):
            self.reader_task.cancel()

        if hasattr(self, "proc") and self.proc.poll() is None:
            try:
                self.proc.terminate()
                await asyncio.to_thread(self.proc.wait, 2)
            except Exception:
                try:
                    self.proc.kill()
                except Exception:
                    pass

        for fd_name in ("master_fd", "slave_fd"):
            if hasattr(self, fd_name):
                try:
                    os.close(getattr(self, fd_name))
                except Exception:
                    pass

