"""
Pydantic schemas for stock history requests and responses.
"""
from typing import List, Optional

from pydantic import BaseModel, Field


class Candle(BaseModel):
    """A single OHLCV candle enriched with optional technical indicators."""

    date: str = Field(..., description="Candle date in yyyy-MM-dd (IST)")
    time: str = Field(..., description="Candle time in HH:mm (IST)")
    open: float
    high: float
    low: float
    close: float
    volume: float

    rsi_14: Optional[float] = None
    ema_20: Optional[float] = None
    ema_50: Optional[float] = None
    ema_100: Optional[float] = None
    ema_200: Optional[float] = None
    volume_ema_50: Optional[float] = None

    class Config:
        json_schema_extra = {
            "example": {
                "date": "2024-01-15",
                "time": "09:15",
                "open": 1640.0,
                "high": 1655.5,
                "low": 1635.0,
                "close": 1650.2,
                "volume": 1254300.0,
                "rsi_14": 56.42,
                "ema_20": 1630.15,
                "ema_50": 1610.80,
                "ema_100": 1580.45,
                "ema_200": 1520.10,
                "volume_ema_50": 1105400.0,
            }
        }


class StockHistoryResponse(BaseModel):
    """Response envelope for the /stocks/history endpoint."""

    symbol: str
    interval: str
    total_candles: int
    data: List[Candle]


class HealthResponse(BaseModel):
    status: str = "ok"
    service: str
    version: str
