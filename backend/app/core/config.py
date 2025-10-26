"""
Configuration settings for F1 Telemetry API
"""

from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "F1 Telemetry API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "High-performance Formula 1 telemetry and timing data API"

    # CORS Settings
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    # FastF1 Settings
    FASTF1_CACHE_DIR: str = "fastf1_cache"
    FASTF1_CACHE_ENABLED: bool = True

    # Data Processing Settings
    TELEMETRY_INTERPOLATION_POINTS: int = 1000
    MAX_LAPS_PER_REQUEST: int = 500

    # Performance Settings
    ENABLE_THREADPOOL: bool = True
    MAX_WORKERS: int = 4

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
