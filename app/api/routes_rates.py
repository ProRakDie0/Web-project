from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import SessionLocal
from app.schemas.rate import RateOut, RateCreate, RatePatch
from app.services import rates_service

router = APIRouter(prefix="/rates", tags=["rates"])


async def get_db():
    async with SessionLocal() as session:
        yield session


@router.get("", response_model=list[RateOut])
async def rates_list(quote: str | None = None, limit: int = 100, db: AsyncSession = Depends(get_db)):
    return await rates_service.list_rates(db, quote=quote, limit=limit)


@router.get("/{rate_id}", response_model=RateOut)
async def rates_get(rate_id: int, db: AsyncSession = Depends(get_db)):
    obj = await rates_service.get_rate(db, rate_id)
    if not obj:
        raise HTTPException(404, "Not found")
    return obj


@router.post("", response_model=RateOut)
async def rates_create(body: RateCreate, db: AsyncSession = Depends(get_db)):
    return await rates_service.create_rate(db, body)


@router.patch("/{rate_id}", response_model=RateOut)
async def rates_patch(rate_id: int, body: RatePatch, db: AsyncSession = Depends(get_db)):
    obj = await rates_service.get_rate(db, rate_id)
    if not obj:
        raise HTTPException(404, "Not found")
    return await rates_service.patch_rate(db, obj, body)


@router.delete("/{rate_id}")
async def rates_delete(rate_id: int, db: AsyncSession = Depends(get_db)):
    ok = await rates_service.delete_rate(db, rate_id)
    if not ok:
        raise HTTPException(404, "Not found")
    return {"status": "deleted", "id": rate_id}