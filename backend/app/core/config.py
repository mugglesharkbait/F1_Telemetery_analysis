"""
Configuration settings for F1 Telemetry API
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings"""

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True,
    )

    # Environment
    ENVIRONMENT: str = "development"

    # API Settings
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "F1 Telemetry API"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "High-performance Formula 1 telemetry and timing data API"

    # CORS Settings - Store as string, parse to list via property
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:8080"

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS_ORIGINS to list"""
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # FastF1 Settings
    FASTF1_CACHE_DIR: str = "fastf1_cache"
    FASTF1_CACHE_ENABLED: bool = True

    # Data Processing Settings
    TELEMETRY_INTERPOLATION_POINTS: int = 1000
    MAX_LAPS_PER_REQUEST: int = 500

    # Performance Settings
    ENABLE_THREADPOOL: bool = True
    MAX_WORKERS: int = 4


settings = Settings()
