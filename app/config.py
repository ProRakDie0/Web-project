import os
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    NATS_URL: str = "nats://localhost:4222"
    FETCH_INTERVAL: int = 60  # секунды

settings = Settings()
