from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.db.models import CurrencyRate
from app.db.session import get_session

router = APIRouter(prefix="/items")

@router.get("/")
async def get_rates(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(CurrencyRate))
    rates = result.scalars().all()
    return rates
