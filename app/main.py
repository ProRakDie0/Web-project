import asyncio
from fastapi import FastAPI, WebSocket
from app.db.models import Base
from app.db.session import engine
from app.api import items
from app.ws.websocket import websocket_endpoint, broadcast, clients
from app.nats.client import NATSClient
from app.tasks.fetch_rates import fetch_and_save
from app.config import settings

app = FastAPI()
app.include_router(items.router)

nats_client = NATSClient(settings.NATS_URL)

@app.on_event("startup")
async def startup():
    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Подключаем NATS
    await nats_client.connect()

    # Подписка на канал
    async def nats_cb(msg):
        await broadcast(msg)

    await nats_client.subscribe("rates.updates", nats_cb)

    # Фоновая задача
    asyncio.create_task(periodic_task())

@app.websocket("/ws/items")
async def websocket(ws: WebSocket):
    await websocket_endpoint(ws)

async def periodic_task():
    from app.db.session import async_session
    while True:
        async with async_session() as session:
            await fetch_and_save(session, nats_client)
        await asyncio.sleep(settings.FETCH_INTERVAL)

@app.post("/tasks/run")
async def run_task():
    from app.db.session import async_session
    async with async_session() as session:
        await fetch_and_save(session, nats_client)
    return {"status": "task run successfully"}
