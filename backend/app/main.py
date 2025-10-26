"""
F1 Telemetry API - Main Application
High-performance Formula 1 telemetry and timing data API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import fastf1
from pathlib import Path

from app.core.config import settings
from app.api.v1_endpoints import router as v1_router

# Initialize FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
# Support wildcard for development, specific origins for production
cors_origins = settings.cors_origins_list
allow_credentials = True

# If wildcard is specified, use it but disable credentials
if "*" in cors_origins:
    cors_origins = ["*"]
    allow_credentials = False

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "X-API-Key"],
)

# Enable FastF1 caching - create directory if it doesn't exist
if settings.FASTF1_CACHE_ENABLED:
    cache_dir = Path(settings.FASTF1_CACHE_DIR)
    cache_dir.mkdir(parents=True, exist_ok=True)
    fastf1.Cache.enable_cache(str(cache_dir))

# Include API routers
app.include_router(v1_router, prefix=settings.API_V1_PREFIX, tags=["v1"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "F1 Telemetry API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health"
    }


@app.get("/health", tags=["System"])
async def health():
    """Global health check"""
    return {
        "status": "healthy",
        "api_version": settings.VERSION
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Handle uncaught exceptions"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "error": str(exc)
        }
    )
