from pydantic import BaseModel


class RateOut(BaseModel):
    id: int
    base: str
    quote: str
    value: float
    as_of: str

    class Config:
        from_attributes = True


class RateCreate(BaseModel):
    base: str = "EUR"
    quote: str
    value: float
    as_of: str


class RatePatch(BaseModel):
    value: float | None = None
    as_of: str | None = None