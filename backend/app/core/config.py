"""
Configuration settings for F1 Telemetry API
"""

from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings"""

    # Environment
    ENVIRONMENT: str = "development"

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "F1 Telemetry API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "High-performance Formula 1 telemetry and timing data API"

    # CORS Settings - Parse comma-separated string from env
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:8080",
    ]

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS from environment variable if it's a string"""
        if isinstance(self.CORS_ORIGINS, str):
            return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]
        return self.CORS_ORIGINS

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
