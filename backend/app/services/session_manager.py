"""
Session Manager for FastF1 Session Caching
Centralizes all session loading and caching logic
"""

import fastf1
from typing import Optional
from pathlib import Path

from app.core.config import settings
from app.core.exceptions import SessionLoadError, SessionNotFoundError
from app.core.utils import validate_session_type


class SessionManager:
    """
    Manages FastF1 session loading and caching
    
    Features:
    - LRU-style caching with configurable size
    - Selective data loading (telemetry, laps, weather, etc.)
    - Automatic cache cleanup
    """

    def __init__(self, max_cache_size: int = 20):
        self._session_cache: dict = {}
        self._max_cache_size = max_cache_size
        self._initialize_cache()

    def _initialize_cache(self):
        """Initialize FastF1 cache directory"""
        if settings.FASTF1_CACHE_ENABLED:
            cache_dir = Path(settings.FASTF1_CACHE_DIR)
            cache_dir.mkdir(parents=True, exist_ok=True)
            fastf1.Cache.enable_cache(str(cache_dir))

    def _generate_cache_key(
        self, 
        year: int, 
        event: str, 
        session_type: str, 
        **load_params
    ) -> str:
        """Generate unique cache key for a session"""
        load_sig = "_".join(f"{k}={v}" for k, v in sorted(load_params.items()))
        return f"{year}_{event}_{session_type}_{load_sig}"

    def _evict_oldest(self):
        """Remove oldest session from cache"""
        if self._session_cache:
            oldest_key = next(iter(self._session_cache))
            del self._session_cache[oldest_key]

    def get_session(
        self,
        year: int,
        event: str,
        session_type: str,
        *,
        laps: bool = True,
        telemetry: bool = False,
        weather: bool = False,
        messages: bool = False,
    ):
        """
        Get a cached session or load it fresh
        
        Args:
            year: Season year
            event: Event identifier
            session_type: Session type (will be validated)
            laps: Load lap data
            telemetry: Load telemetry data
            weather: Load weather data
            messages: Load race control messages
            
        Returns:
            Loaded FastF1 session object
            
        Raises:
            SessionNotFoundError: If session doesn't exist
            SessionLoadError: If session fails to load
        """
        # Validate session type
        try:
            normalized_session = validate_session_type(session_type)
        except ValueError as e:
            raise SessionNotFoundError(year, event, session_type) from e

        # Generate cache key
        load_params = {
            "laps": laps,
            "telemetry": telemetry,
            "weather": weather,
            "messages": messages,
        }
        cache_key = self._generate_cache_key(year, event, normalized_session, **load_params)

        # Return from cache if available
        if cache_key in self._session_cache:
            return self._session_cache[cache_key]

        # Load fresh session
        try:
            session = fastf1.get_session(year, event, normalized_session)
            session.load(**load_params)
        except Exception as e:
            error_msg = str(e)
            # Check for specific errors
            if "not been loaded" in error_msg or "DataNotLoadedError" in error_msg:
                raise SessionLoadError(
                    year, event, normalized_session,
                    "Data could not be loaded. Session may not have required data available."
                ) from e
            raise SessionLoadError(year, event, normalized_session, error_msg) from e

        # Maintain cache size limit (FIFO eviction)
        if len(self._session_cache) >= self._max_cache_size:
            self._evict_oldest()

        # Cache the session
        self._session_cache[cache_key] = session
        return session

    def clear_cache(self):
        """Clear all cached sessions"""
        self._session_cache.clear()

    def get_cache_stats(self) -> dict:
        """Get cache statistics"""
        return {
            "cached_sessions": len(self._session_cache),
            "max_size": self._max_cache_size,
            "cache_keys": list(self._session_cache.keys()),
        }


# Global session manager instance
_session_manager: Optional[SessionManager] = None


def get_session_manager() -> SessionManager:
    """Get or create global session manager instance"""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
