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
    FIVE_MIN = "5min"
    TEN_MIN = "10min"
    FIFTEEN_MIN = "15min"
    THIRTY_MIN = "30min"
    SIXTY_MIN = "60min"
    SEVENTY_FIVE_MIN = "75min"
    ONE_DAY = "1d"
    ONE_WEEK = "1w"


# Mapping of Interval -> intervalInMinutes expected by Groww's API
INTERVAL_TO_MINUTES: dict = {
    Interval.ONE_MIN: 1,
    Interval.FIVE_MIN: 5,
    Interval.TEN_MIN: 10,
    Interval.FIFTEEN_MIN: 15,
    Interval.THIRTY_MIN: 30,
    Interval.SIXTY_MIN: 60,
    Interval.SEVENTY_FIVE_MIN: 75,
    Interval.ONE_DAY: 1440,
    Interval.ONE_WEEK: 10080,
}

# Intervals considered "intraday" for chunking purposes (all sub-daily intervals)
INTRADAY_INTERVALS = {
    Interval.ONE_MIN,
    Interval.FIVE_MIN,
    Interval.TEN_MIN,
    Interval.FIFTEEN_MIN,
    Interval.THIRTY_MIN,
    Interval.SIXTY_MIN,
    Interval.SEVENTY_FIVE_MIN,
}
