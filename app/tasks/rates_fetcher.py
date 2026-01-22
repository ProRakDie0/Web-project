import asyncio
import httpx
from app.config import settings
from app.db.session import SessionLocal
from app.schemas.rate import RateCreate
from app.services.rates_service import upsert_rate_unique


class RatesFetcher:
    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._running_task: asyncio.Task | None = None
        self._stop = asyncio.Event()

    async def start_loop(self, on_event):
        """
        on_event: async callback(payload: dict)
        """
        self._stop.clear()
        while not self._stop.is_set():
            try:
                await self.run_once(on_event=on_event, reason="scheduled")
            except Exception as e:
                await on_event({"type": "task.error", "error": str(e)})
            await asyncio.sleep(settings.fetch_interval_seconds)

    async def stop(self):
        self._stop.set()

    async def run_once(self, on_event, reason: str = "manual"):
        # анти-шторм: не запускать параллельно два fetch
        async with self._lock:
            await on_event({"type": "task.started", "reason": reason})

            async with httpx.AsyncClient(timeout=15) as client:
                r = await client.get(settings.ecb_url)
                r.raise_for_status()
                payload = r.json()

            as_of = payload.get("date") or payload.get("time_last_update_utc") or "unknown"
            base = (payload.get("base") or "EUR").upper()
            rates = payload.get("rates") or {}

            # возьмем несколько валют для примера
            wanted = ["USD", "EUR", "GBP", "JPY", "CHF"]
            items = []
            for q in wanted:
                if q == base:
                    continue
                if q in rates:
                    items.append((q, float(rates[q])))

            saved = 0
            async with SessionLocal() as db:
                for quote, value in items:
                    obj = await upsert_rate_unique(
                        db,
                        RateCreate(base=base, quote=quote, value=value, as_of=str(as_of)),
                    )
                    saved += 1

                    await on_event({
                        "type": "rates.fetched",
                        "base": obj.base,
                        "quote": obj.quote,
                        "value": obj.value,
                        "as_of": obj.as_of,
                    })

            await on_event({"type": "task.finished", "saved": saved, "reason": reason})


rates_fetcher = RatesFetcher()