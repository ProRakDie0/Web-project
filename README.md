## Запуск
1) docker compose up -d
2) python -m venv .venv && source .venv/bin/activate
3) pip install -r requirements.txt
4) uvicorn app.main:app --reload

## Swagger
http://127.0.0.1:8000/docs

## WebSocket
ws://127.0.0.1:8000/ws/manager

## Ручной запуск фоновой задачи
POST http://127.0.0.1:8000/tasks/run
