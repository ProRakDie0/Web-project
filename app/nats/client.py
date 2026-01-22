import json
from typing import Awaitable, Callable, Optional

from nats.aio.client import Client as NATS
from app.config import settings


class NatsClient:
    def __init__(self) -> None:
        self.nc = NATS()
        self._sub_sid: Optional[int] = None

    async def connect(self) -> None:
        await self.nc.connect(servers=[settings.nats_url])

    async def close(self) -> None:
        if self.nc.is_connected:
            await self.nc.drain()

    async def publish(self, subject: str, payload: dict) -> None:
        data = json.dumps(payload).encode("utf-8")
        await self.nc.publish(subject, data)

    async def subscribe(self, subject: str, handler: Callable[[dict], Awaitable[None]]) -> None:
        async def _cb(msg):
            try:
                payload = json.loads(msg.data.decode("utf-8"))
            except Exception:
                payload = {"raw": msg.data.decode("utf-8", errors="ignore")}
            await handler(payload)

        self._sub_sid = await self.nc.subscribe(subject, cb=_cb)


nats_client = NatsClient()