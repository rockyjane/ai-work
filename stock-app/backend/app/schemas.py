"""API 的請求/回應資料格式（Pydantic）。"""
from typing import Optional
from pydantic import BaseModel


class StockOut(BaseModel):
    stock_id: str
    name: Optional[str] = None
    industry: Optional[str] = None
    market: Optional[str] = None

    class Config:
        from_attributes = True


class ValuationOut(BaseModel):
    date: str
    per: Optional[float] = None
    pbr: Optional[float] = None
    dividend_yield: Optional[float] = None

    class Config:
        from_attributes = True


class WatchlistCreate(BaseModel):
    stock_id: str
    note: Optional[str] = ""


class WatchlistOut(BaseModel):
    id: int
    stock_id: str
    name: Optional[str] = None
    note: Optional[str] = None

    class Config:
        from_attributes = True
