"""
F1 Telemetry API - Main Application (Refactored)
High-performance Formula 1 telemetry and timing data API with clean architecture
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import F1APIException, handle_f1_exception

# Import refactored endpoints
from app.api.v1_endpoints_refactored import router as v1_router

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
cors_origins = settings.cors_origins_list
allow_credentials = True

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

# Include API routers
app.include_router(v1_router, prefix=settings.API_V1_PREFIX, tags=["v1"])


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "F1 Telemetry API",
        "version": settings.VERSION,
        "docs": "/docs",
        "health": f"{settings.API_V1_PREFIX}/health",
        "architecture": "clean_architecture_with_service_layer"
    }


@app.get("/health", tags=["System"])
async def health():
    """Global health check"""
    return {
        "status": "healthy",
        "api_version": settings.VERSION,
        "architecture": "refactored"
    }


# Global exception handlers
@app.exception_handler(F1APIException)
async def f1_exception_handler(request, exc: F1APIException):
    """Handle F1 API specific exceptions"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "detail": exc.message,
            "error_type": exc.__class__.__name__
        }
    )


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
