import httpx
from datetime import datetime
from app.db.models import CurrencyRate
from app.nats.client.py import NATSClient
from app.config import settings

CURRENCIES = ["USD", "EUR", "JPY"]
API_URL = "https://api.exchangerate.host/latest?base=RUB"

async def fetch_and_save(session, nats: NATSClient):
    async with httpx.AsyncClient() as client:
        resp = await client.get(API_URL)
        data = resp.json()
        rates = data.get("rates", {})

        for cur in CURRENCIES:
            rate = rates.get(cur)
            if rate:
                obj = CurrencyRate(currency=cur, rate=rate, timestamp=datetime.utcnow())
                session.add(obj)
        await session.commit()

        # Публикуем в NATS
        for cur in CURRENCIES:
            await nats.publish("rates.updates", {"currency": cur, "rate": rates.get(cur)})
