from sqlalchemy import String, DateTime, Float, func, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class Rate(Base):
    __tablename__ = "rates"
    __table_args__ = (
        UniqueConstraint("base", "quote", "as_of", name="uq_rate_base_quote_asof"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    base: Mapped[str] = mapped_column(String(10), default="EUR")
    quote: Mapped[str] = mapped_column(String(10))
    value: Mapped[float] = mapped_column(Float)

    as_of: Mapped[str] = mapped_column(String(32))  # date string from provider (e.g. "2026-01-22")
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())