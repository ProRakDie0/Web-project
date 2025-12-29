# Web-project
project for или по основы Web API 2025

# Currency Rates API

**Проект** Парсер курсов валют (USD, EUR, JPY) с поддержкой REST API, WebSocket уведомлений, фоновой задачи и интеграцией с NATS.

---

## 📂 Структура проекта

project/
│
├─ app/
│ ├─ api/ # REST API роутеры
│ ├─ db/ # Модели и сессии базы данных
│ ├─ nats/ # Клиент для работы с NATS
│ ├─ tasks/ # Фоновые задачи
│ ├─ ws/ # WebSocket обработчики
│ ├─ config.py # Конфигурация проекта
│ └─ main.py # Точка входа FastAPI
│
├─ requirements.txt
└─ docker-compose.yml


---

## ⚙️ Технологический стек

- **FastAPI** – асинхронный веб-фреймворк
- **httpx** – асинхронные HTTP-запросы
- **NATS.io (`asyncio-nats-client`)** – брокер сообщений
- **SQLite + SQLAlchemy (asyncio)** – база данных
- **WebSockets (fastapi.WebSocket)** – real-time уведомления
- **uvicorn** – ASGI сервер

---

## 🚀 Установка и запуск

### 1. Клонируем репозиторий

```bash
git clone <REPO_URL>
cd project
```

2. Запуск через Docker Compose
```
docker-compose up --build
```

NATS: порт 4222

FastAPI: порт 8000
