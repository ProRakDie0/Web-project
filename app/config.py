from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    database_url: str = "sqlite+aiosqlite:///./app.db"

    nats_url: str = "nats://127.0.0.1:4222"
    nats_subject: str = "rates.updates"

    fetch_interval_seconds: int = 30

    # ECB base rates endpoint (daily)
    ecb_url: str = "https://api.exchangerate.host/latest?base=EUR"


settings = Settings()