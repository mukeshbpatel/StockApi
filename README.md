# Stock Analytics Service

Production-grade, modular FastAPI microservice providing OHLCV candle history
and technical indicators (RSI-14, EMA 20/50/100/200 on price, EMA-50 on
volume) for Indian (NSE) equities, sourced from Groww's public charting
service.

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Then open:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## Run with Docker

```bash
docker build -t stock-analytics-service .
docker run -p 8000:8000 stock-analytics-service
```

## Example request

```
GET /api/v1/stocks/history?symbol=HDFCBANK&interval=1d&start_date=20240101&end_date=20240401&technical_indicators=true
```

## Deploy to Render

This repo includes a `render.yaml` (Python 3.11, Singapore region, free
tier, binds to `$PORT`, health check at `/health`). Push to a Git repo and
create a new Blueprint on Render pointing at it, or import via the Render
dashboard.

## Project layout

```
app/
├── main.py                    # FastAPI app, CORS, docs, /health
├── api/v1/router.py           # /api/v1/stocks/history endpoint
├── core/config.py             # Settings, Interval enum, constants
├── schemas/stock.py           # Pydantic request/response models
└── services/
    ├── groww_client.py        # Async Groww fetch + chunking + merge
    └── indicator_service.py   # pandas/ta indicator computation
```

## Notes

- `technical_indicators=false` returns `null` for all indicator fields
  while still returning OHLCV data.
- Long date ranges are automatically chunked based on interval (e.g. 4 days for 1m,
  15 days for 5m, 60 days / 2 months for 30m/60m/75m, 365 days for 1d) and fetched
  concurrently, preventing upstream response truncation, then merged, de-duplicated
  by timestamp, and sorted chronologically.
- All timestamps are converted to `Asia/Kolkata` (IST) before being
  formatted into `date` (`yyyy-MM-dd`) and `time` (`HH:mm`) fields.
- Note: Groww's public charting service maintains a rolling ~90-day retention window
  for intraday candle data (`1m` through `75min`), while daily (`1d`) and weekly (`1w`)
  intervals provide multi-year historical data.

