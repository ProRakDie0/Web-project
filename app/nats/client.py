import asyncio
from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout, ErrNoServers

class NATSClient:
    def __init__(self, url):
        self.nc = NATS()
        self.url = url

    async def connect(self):
        await self.nc.connect(self.url)

    async def publish(self, subject: str, msg: dict):
        import json
        await self.nc.publish(subject, json.dumps(msg).encode())

    async def subscribe(self, subject: str, cb):
        import json
        async def wrapper(msg):
            data = json.loads(msg.data.decode())
            await cb(data)
        await self.nc.subscribe(subject, cb=wrapper)
