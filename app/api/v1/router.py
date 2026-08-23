"""
API v1 routes: stock history endpoint and service health check.
"""
import re
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query

from app.core.config import Interval
from app.schemas.stock import StockHistoryResponse
from app.services.groww_client import GrowwClientError, fetch_candles
from app.services.indicator_service import compute_indicators

router = APIRouter()

_DATE_PATTERN = re.compile(r"^\d{8}$")


def _validate_date_string(value: str, field_name: str) -> None:
    if not _DATE_PATTERN.match(value):
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} '{value}': expected format yyyyMMdd",
        )
    try:
        datetime.strptime(value, "%Y%m%d")
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid {field_name} '{value}': not a real calendar date",
        ) from exc


@router.get("/stocks/history", response_model=StockHistoryResponse)
async def get_stock_history(
    symbol: str = Query(..., description="NSE trading symbol, e.g. HDFCBANK"),
    interval: Interval = Query(..., description="Candle interval"),
    start_date: str = Query(..., description="Start date, format yyyyMMdd"),
    end_date: str = Query(..., description="End date, format yyyyMMdd"),
    technical_indicators: bool = Query(
        True, description="Compute technical indicators when true"
    ),
):
    """
    Fetch OHLCV candle history for an NSE symbol from Groww's charting
    service, enriched with technical indicators (RSI-14, EMA 20/50/100/200
    on price, EMA-50 on volume).
    """
    symbol = symbol.strip().upper()
    if not symbol:
        raise HTTPException(status_code=400, detail="symbol must not be empty")

    _validate_date_string(start_date, "start_date")
    _validate_date_string(end_date, "end_date")

    if start_date > end_date:
        raise HTTPException(
            status_code=400, detail="start_date must be less than or equal to end_date"
        )

    try:
        raw_candles = await fetch_candles(symbol, interval, start_date, end_date)
    except GrowwClientError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    if not raw_candles:
        raise HTTPException(
            status_code=404,
            detail=f"No candles found for {symbol} between {start_date} and {end_date}",
        )

    data = compute_indicators(raw_candles, include_indicators=technical_indicators)

    return StockHistoryResponse(
        symbol=symbol,
        interval=interval.value,
        total_candles=len(data),
        data=data,
    )
