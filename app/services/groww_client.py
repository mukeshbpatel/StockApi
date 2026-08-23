"""
Async client for Groww's public charting endpoint.

Handles:
- Building request URLs/params for a given symbol/interval/time range
- Splitting long date ranges into bounded chunks (30d intraday / 365d daily)
- Fetching chunks concurrently with httpx.AsyncClient
- Merging, de-duplicating (by timestamp) and chronologically sorting candles
"""
import asyncio
import time
from datetime import datetime, timedelta
from typing import List, Tuple
from zoneinfo import ZoneInfo

import httpx

from app.core.config import (
    INTERVAL_TO_MINUTES,
    INTRADAY_INTERVALS,
    Interval,
    settings,
)

IST = ZoneInfo("Asia/Kolkata")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Origin": "https://groww.in",
    "Referer": "https://groww.in/",
    "Accept": "application/json, text/plain, */*",
}


class GrowwClientError(Exception):
    """Raised when the upstream Groww API cannot be reached or returns an error."""


def _parse_yyyymmdd_to_ist_midnight(date_str: str) -> datetime:
    """Parse a yyyyMMdd string into an IST-aware midnight datetime."""
    naive = datetime.strptime(date_str, "%Y%m%d")
    return naive.replace(tzinfo=IST)


def _to_epoch_millis(dt: datetime) -> int:
    return int(dt.timestamp() * 1000)


def build_time_chunks(
    start_date: str, end_date: str, interval: Interval
) -> List[Tuple[int, int]]:
    """
    Split the [start_date, end_date] range into (start_ms, end_ms) chunk tuples,
    bounded by the configured max chunk size for the interval class.
    """
    start_dt = _parse_yyyymmdd_to_ist_midnight(start_date)
    # end_date is inclusive; push to end-of-day so the last day's candles are captured
    end_dt = _parse_yyyymmdd_to_ist_midnight(end_date) + timedelta(
        hours=23, minutes=59, seconds=59
    )

    max_days = (
        settings.INTRADAY_CHUNK_DAYS
        if interval in INTRADAY_INTERVALS
        else settings.DAILY_CHUNK_DAYS
    )

    chunks: List[Tuple[int, int]] = []
    cursor = start_dt
    while cursor <= end_dt:
        chunk_end = min(cursor + timedelta(days=max_days), end_dt)
        chunks.append((_to_epoch_millis(cursor), _to_epoch_millis(chunk_end)))
        cursor = chunk_end + timedelta(seconds=1)

    return chunks


def _extract_candles(payload: dict) -> List[list]:
    """
    Normalize Groww's response into a flat list of raw candle rows.

    Groww's charting service typically returns candle arrays under a
    "candles" key, where each candle is
    [epoch_seconds, open, high, low, close, volume]. We defensively handle
    a couple of shapes since the exact envelope can vary by endpoint version.
    """
    if not payload:
        return []

    candles = payload.get("candles")
    if candles is None and isinstance(payload.get("payload"), dict):
        candles = payload["payload"].get("candles")

    return candles or []


async def _fetch_chunk(
    client: httpx.AsyncClient,
    symbol: str,
    interval: Interval,
    start_ms: int,
    end_ms: int,
    semaphore: asyncio.Semaphore,
) -> List[list]:
    url = f"{settings.GROWW_BASE_URL}/{symbol.upper()}"
    params = {
        "intervalInMinutes": INTERVAL_TO_MINUTES[interval],
        "startTimeInMillis": start_ms,
        "endTimeInMillis": end_ms,
    }

    async with semaphore:
        try:
            response = await client.get(url, params=params, headers=HEADERS)
        except httpx.RequestError as exc:
            raise GrowwClientError(
                f"Network error while contacting Groww for {symbol}: {exc}"
            ) from exc

    if response.status_code == 404:
        return []
    if response.status_code >= 400:
        raise GrowwClientError(
            f"Groww API returned HTTP {response.status_code} for {symbol}: "
            f"{response.text[:200]}"
        )

    try:
        payload = response.json()
    except ValueError as exc:
        raise GrowwClientError(
            f"Groww API returned non-JSON response for {symbol}"
        ) from exc

    return _extract_candles(payload)


async def fetch_candles(
    symbol: str, interval: Interval, start_date: str, end_date: str
) -> List[list]:
    """
    Fetch all candles for the requested symbol/interval/date-range, chunking
    and parallelizing requests as needed, then merge + dedupe + sort.

    Returns a list of raw candle rows: [timestamp, open, high, low, close, volume]
    sorted ascending by timestamp, with duplicate timestamps removed.
    """
    chunks = build_time_chunks(start_date, end_date, interval)
    semaphore = asyncio.Semaphore(settings.MAX_CONCURRENT_REQUESTS)

    async with httpx.AsyncClient(timeout=settings.GROWW_TIMEOUT_SECONDS) as client:
        tasks = [
            _fetch_chunk(client, symbol, interval, start_ms, end_ms, semaphore)
            for start_ms, end_ms in chunks
        ]
        results = await asyncio.gather(*tasks)

    merged: dict = {}
    for chunk_candles in results:
        for row in chunk_candles:
            if not row:
                continue
            timestamp = row[0]
            merged[timestamp] = row

    sorted_rows = [merged[ts] for ts in sorted(merged.keys())]
    return sorted_rows
