from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.rate import Rate
from app.schemas.rate import RateCreate, RatePatch


async def list_rates(db: AsyncSession, quote: str | None = None, limit: int = 100) -> list[Rate]:
    stmt = select(Rate).order_by(Rate.id.desc()).limit(limit)
    if quote:
        stmt = stmt.where(Rate.quote == quote.upper())
    res = await db.execute(stmt)
    return list(res.scalars().all())


async def get_rate(db: AsyncSession, rate_id: int) -> Rate | None:
    res = await db.execute(select(Rate).where(Rate.id == rate_id))
    return res.scalar_one_or_none()


async def create_rate(db: AsyncSession, data: RateCreate) -> Rate:
    obj = Rate(base=data.base.upper(), quote=data.quote.upper(), value=data.value, as_of=data.as_of)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def patch_rate(db: AsyncSession, obj: Rate, data: RatePatch) -> Rate:
    if data.value is not None:
        obj.value = data.value
    if data.as_of is not None:
        obj.as_of = data.as_of
    await db.commit()
    await db.refresh(obj)
    return obj


async def delete_rate(db: AsyncSession, rate_id: int) -> bool:
    res = await db.execute(delete(Rate).where(Rate.id == rate_id))
    await db.commit()
    return (res.rowcount or 0) > 0


async def upsert_rate_unique(db: AsyncSession, data: RateCreate) -> Rate:
    """
    upsert по (base, quote, as_of). Если запись уже есть — обновим value.
    """
    base = data.base.upper()
    quote = data.quote.upper()

    res = await db.execute(select(Rate).where(Rate.base == base, Rate.quote == quote, Rate.as_of == data.as_of))
    existing = res.scalar_one_or_none()
    if existing:
        existing.value = data.value
        await db.commit()
        await db.refresh(existing)
        return existing

    obj = Rate(base=base, quote=quote, value=data.value, as_of=data.as_of)
    db.add(obj)
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # если гонка — повторно прочитаем и обновим
        res2 = await db.execute(select(Rate).where(Rate.base == base, Rate.quote == quote, Rate.as_of == data.as_of))
        obj2 = res2.scalar_one()
        obj2.value = data.value
        await db.commit()
        await db.refresh(obj2)
        return obj2

    await db.refresh(obj)
    return obj