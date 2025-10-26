"""
F1 Telemetry API - Main Application
High-performance Formula 1 telemetry and timing data API
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import fastf1

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Enable FastF1 caching
if settings.FASTF1_CACHE_ENABLED:
    fastf1.Cache.enable_cache(settings.FASTF1_CACHE_DIR)

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
