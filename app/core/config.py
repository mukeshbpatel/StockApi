"""
Application configuration and constants.
"""
from enum import Enum
from zoneinfo import ZoneInfo


class Settings:
    """Central application settings."""

    APP_NAME: str = "Indian Stock Market Analytics Service"
    APP_VERSION: str = "1.0.0"
    API_V1_PREFIX: str = "/api/v1"

    # Groww charting service
    GROWW_BASE_URL: str = (
        "https://groww.in/v1/api/charting_service/v4/chart/exchange/NSE/segment/CASH"
    )
    GROWW_TIMEOUT_SECONDS: float = 15.0

    # Chunking limits (in days)
    INTRADAY_CHUNK_DAYS: int = 30
    DAILY_CHUNK_DAYS: int = 365

    # Concurrency
    MAX_CONCURRENT_REQUESTS: int = 8

    # Indicator windows
    RSI_WINDOW: int = 14
    EMA_PRICE_WINDOWS: tuple = (20, 50, 100, 200)
    EMA_VOLUME_WINDOW: int = 50

    # Timezone
    IST = ZoneInfo("Asia/Kolkata")

    # CORS
    CORS_ALLOW_ORIGINS: list = ["*"]


settings = Settings()


class Interval(str, Enum):
    """Supported chart intervals mapped to Groww's intervalInMinutes parameter."""

    ONE_MIN = "1m"
    ONE_MIN_LONG = "1min"
    FIVE_MIN = "5min"
    FIVE_MIN_SHORT = "5m"
    TEN_MIN = "10min"
    TEN_MIN_SHORT = "10m"
    FIFTEEN_MIN = "15min"
    FIFTEEN_MIN_SHORT = "15m"
    THIRTY_MIN = "30min"
    THIRTY_MIN_SHORT = "30m"
    SIXTY_MIN = "60min"
    SIXTY_MIN_SHORT = "60m"
    SEVENTY_FIVE_MIN = "75min"
    SEVENTY_FIVE_MIN_SHORT = "75m"
    ONE_DAY = "1d"
    ONE_DAY_LONG = "1day"
    ONE_WEEK = "1w"
    ONE_WEEK_LONG = "1week"


# Mapping of Interval -> intervalInMinutes expected by Groww's API
INTERVAL_TO_MINUTES: dict = {
    Interval.ONE_MIN: 1,
    Interval.ONE_MIN_LONG: 1,
    Interval.FIVE_MIN: 5,
    Interval.FIVE_MIN_SHORT: 5,
    Interval.TEN_MIN: 10,
    Interval.TEN_MIN_SHORT: 10,
    Interval.FIFTEEN_MIN: 15,
    Interval.FIFTEEN_MIN_SHORT: 15,
    Interval.THIRTY_MIN: 30,
    Interval.THIRTY_MIN_SHORT: 30,
    Interval.SIXTY_MIN: 60,
    Interval.SIXTY_MIN_SHORT: 60,
    Interval.SEVENTY_FIVE_MIN: 75,
    Interval.SEVENTY_FIVE_MIN_SHORT: 75,
    Interval.ONE_DAY: 1440,
    Interval.ONE_DAY_LONG: 1440,
    Interval.ONE_WEEK: 10080,
    Interval.ONE_WEEK_LONG: 10080,
}

# Mapping of Interval -> max chunk size (in days) per Groww API request.
# Fine-grained chunking prevents Groww's ~3,000 candle response truncation limit.
INTERVAL_CHUNK_DAYS: dict = {
    Interval.ONE_MIN: 4,          # 4 days (~1,500 candles, keeps response well below ~3,000 limit)
    Interval.ONE_MIN_LONG: 4,
    Interval.FIVE_MIN: 15,        # 15 days (~1,125 candles)
    Interval.FIVE_MIN_SHORT: 15,
    Interval.TEN_MIN: 30,         # 30 days (~1,125 candles)
    Interval.TEN_MIN_SHORT: 30,
    Interval.FIFTEEN_MIN: 45,     # 45 days (~1,125 candles)
    Interval.FIFTEEN_MIN_SHORT: 45,
    Interval.THIRTY_MIN: 60,      # 60 days (~750 candles / 2 months)
    Interval.THIRTY_MIN_SHORT: 60,
    Interval.SIXTY_MIN: 60,       # 60 days (~375 candles / 2 months)
    Interval.SIXTY_MIN_SHORT: 60,
    Interval.SEVENTY_FIVE_MIN: 60,# 60 days (~300 candles / 2 months)
    Interval.SEVENTY_FIVE_MIN_SHORT: 60,
    Interval.ONE_DAY: 365,        # 365 days (~250 candles / 1 year)
    Interval.ONE_DAY_LONG: 365,
    Interval.ONE_WEEK: 730,       # 730 days (~104 candles / 2 years)
    Interval.ONE_WEEK_LONG: 730,
}

# Intervals considered "intraday" for chunking purposes (all sub-daily intervals)
INTRADAY_INTERVALS = {
    Interval.ONE_MIN,
    Interval.ONE_MIN_LONG,
    Interval.FIVE_MIN,
    Interval.FIVE_MIN_SHORT,
    Interval.TEN_MIN,
    Interval.TEN_MIN_SHORT,
    Interval.FIFTEEN_MIN,
    Interval.FIFTEEN_MIN_SHORT,
    Interval.THIRTY_MIN,
    Interval.THIRTY_MIN_SHORT,
    Interval.SIXTY_MIN,
    Interval.SIXTY_MIN_SHORT,
    Interval.SEVENTY_FIVE_MIN,
    Interval.SEVENTY_FIVE_MIN_SHORT,
}


