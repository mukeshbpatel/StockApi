"""
FastAPI application entrypoint.

Wires up CORS, the versioned API router, Swagger/ReDoc docs, and a
top-level /health endpoint for platform liveness checks (e.g. Render).
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import router as v1_router
from app.core.config import settings
from app.schemas.stock import HealthResponse

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=(
        "Production-grade FastAPI microservice providing OHLCV candle history "
        "and technical indicators (RSI, EMA) for Indian (NSE) equities, "
        "sourced from Groww's public charting service."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(v1_router, prefix=settings.API_V1_PREFIX, tags=["stocks"])


@app.get("/health", response_model=HealthResponse, tags=["health"])
async def health():
    """Top-level health check used by deployment platforms (e.g. Render)."""
    return HealthResponse(service=settings.APP_NAME, version=settings.APP_VERSION)


@app.get("/", tags=["health"])
async def root():
    """Basic root endpoint pointing to interactive docs."""
    return {
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
    }
