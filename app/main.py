import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from sqlalchemy import text

from app.api.routes_rates import router as rates_router
from app.config import settings
from app.db.session import engine
from app.db.base import Base
from app.nats.client import nats_client
from app.tasks.rates_fetcher import rates_fetcher
from app.ws.manager import ws_manager


app = FastAPI(title="Async Backend: Rates + WS + Tasks + NATS")
app.include_router(rates_router)
print([route.path for route in app.routes])



async def emit_event(payload: dict):
    # 1) publish to NATS
    if nats_client.nc.is_connected:
        await nats_client.publish(settings.nats_subject, payload)
    # 2) broadcast to WS
    await ws_manager.broadcast(payload)


@app.websocket("/ws/manager")
async def ws_manager_endpoint(ws: WebSocket):
    await ws_manager.connect(ws)
    try:
        print("Client connected to WS manager")
        await ws.send_json({"type": "ws.connected"})
        while True:
            # можно принимать команды от клиента
            msg = await ws.receive_json()
            if msg.get("action") == "ping":
                await ws.send_json({"type": "pong"})
    except WebSocketDisconnect:
        await ws_manager.disconnect(ws)


@app.post("/tasks/run")
async def run_task_now():
    # ручной запуск фоновой задачи
    asyncio.create_task(rates_fetcher.run_once(on_event=emit_event, reason="manual"))
    return {"status": "started"}


@app.on_event("startup")
async def on_startup():
    # create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
        # проверка соединения SQLite
        await conn.execute(text("SELECT 1"))

    # connect NATS + subscribe
    await nats_client.connect()

    async def on_nats_message(payload: dict):
        # сообщения, пришедшие извне (или от нас же) — транслируем в WS и логируем
        # если нужно "не зацикливать" — добавляйте метку origin/service_id
        await ws_manager.broadcast({**payload, "via": "nats"})

    await nats_client.subscribe(settings.nats_subject, on_nats_message)

    # start scheduler loop
    app.state.scheduler_task = asyncio.create_task(rates_fetcher.start_loop(on_event=emit_event))


@app.on_event("shutdown")
async def on_shutdown():
    await rates_fetcher.stop()
    task = getattr(app.state, "scheduler_task", None)
    if task:
        task.cancel()
    await nats_client.close()
    await engine.dispose()