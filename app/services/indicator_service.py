"""
Technical indicator computation on OHLCV candle data.

Converts raw Groww candle rows into a pandas DataFrame, converts timestamps
to IST, computes RSI(14), EMA(20/50/100/200) on close, and EMA(50) on volume,
then serializes back into JSON-safe candle dicts (NaN -> None, 2dp rounding).
"""
from datetime import datetime
from typing import List, Optional

import pandas as pd
from ta.momentum import RSIIndicator
from ta.trend import EMAIndicator

from app.core.config import settings

IST = settings.IST


def _safe_round(value) -> Optional[float]:
    """Round to 2dp, converting NaN/None to None for valid JSON output."""
    if value is None or pd.isna(value):
        return None
    return round(float(value), 2)


def _candles_to_dataframe(raw_candles: List[list]) -> pd.DataFrame:
    """
    Convert raw [timestamp, open, high, low, close, volume] rows into a
    pandas DataFrame with IST-localized date/time columns.

    Timestamps from Groww are epoch seconds; this handles both seconds and
    milliseconds inputs defensively.
    """
    columns = ["timestamp", "open", "high", "low", "close", "volume"]
    df = pd.DataFrame(raw_candles, columns=columns)

    if df.empty:
        return df

    # Defend against seconds vs. milliseconds epoch values.
    sample_ts = df["timestamp"].iloc[0]
    unit = "ms" if sample_ts > 1_000_000_000_000 else "s"

    df["dt_utc"] = pd.to_datetime(df["timestamp"], unit=unit, utc=True)
    df["dt_ist"] = df["dt_utc"].dt.tz_convert(IST)

    df["date"] = df["dt_ist"].dt.strftime("%Y-%m-%d")
    df["time"] = df["dt_ist"].dt.strftime("%H:%M")

    for col in ("open", "high", "low", "close", "volume"):
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df = df.sort_values("timestamp").reset_index(drop=True)
    return df


def compute_indicators(
    raw_candles: List[list], include_indicators: bool = True
) -> List[dict]:
    """
    Build the final list of candle dicts (JSON-serializable) with optional
    technical indicators computed on the full series.
    """
    df = _candles_to_dataframe(raw_candles)

    if df.empty:
        return []

    if include_indicators:
        try:
            rsi = RSIIndicator(close=df["close"], window=settings.RSI_WINDOW)
            df["rsi_14"] = rsi.rsi()
        except Exception:
            df["rsi_14"] = pd.NA

        for period in settings.EMA_PRICE_WINDOWS:
            col_name = f"ema_{period}"
            try:
                ema = EMAIndicator(close=df["close"], window=period)
                df[col_name] = ema.ema_indicator()
            except Exception:
                df[col_name] = pd.NA

        try:
            volume_ema = EMAIndicator(
                close=df["volume"], window=settings.EMA_VOLUME_WINDOW
            )
            df["volume_ema_50"] = volume_ema.ema_indicator()
        except Exception:
            df["volume_ema_50"] = pd.NA
    else:
        df["rsi_14"] = pd.NA
        for period in settings.EMA_PRICE_WINDOWS:
            df[f"ema_{period}"] = pd.NA
        df["volume_ema_50"] = pd.NA

    records = []
    for _, row in df.iterrows():
        records.append(
            {
                "date": row["date"],
                "time": row["time"],
                "open": _safe_round(row["open"]),
                "high": _safe_round(row["high"]),
                "low": _safe_round(row["low"]),
                "close": _safe_round(row["close"]),
                "volume": _safe_round(row["volume"]),
                "rsi_14": _safe_round(row.get("rsi_14")),
                "ema_20": _safe_round(row.get("ema_20")),
                "ema_50": _safe_round(row.get("ema_50")),
                "ema_100": _safe_round(row.get("ema_100")),
                "ema_200": _safe_round(row.get("ema_200")),
                "volume_ema_50": _safe_round(row.get("volume_ema_50")),
            }
        )

    return records
