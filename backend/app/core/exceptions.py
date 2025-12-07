"""
Custom exception classes for F1 Telemetry API
Provides specific error types for better error handling
"""

from fastapi import HTTPException
from typing import Optional


class F1APIException(Exception):
    """Base exception for F1 API errors"""

    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DataNotFoundError(F1APIException):
    """Raised when requested F1 data is not available"""

    def __init__(self, message: str, resource: Optional[str] = None):
        self.resource = resource
        super().__init__(message, status_code=404)


class TelemetryNotAvailableError(DataNotFoundError):
    """Raised when telemetry data is not available for a session"""

    def __init__(self, year: int, event: str, session: str, reason: Optional[str] = None):
        message = (
            f"Telemetry data is not available for {event} {year} {session}."
        )
        if year < 2011:
            message += f" Telemetry data is only available from 2011 onwards. "
            message += "For best results, use years 2018-2025."
        elif year < 2018:
            message += " Some sessions from 2011-2017 may not have complete telemetry. "
            message += "For guaranteed telemetry data, use years 2018-2025."
        
        if reason:
            message += f" Reason: {reason}"
        
        super().__init__(message, resource="telemetry")


class DriverNotFoundError(DataNotFoundError):
    """Raised when a driver is not found in a session"""

    def __init__(self, driver_identifier: str, session_info: Optional[str] = None):
        message = f"Driver '{driver_identifier}' not found"
        if session_info:
            message += f" in {session_info}"
        super().__init__(message, resource="driver")


class SessionNotFoundError(DataNotFoundError):
    """Raised when a session is not found"""

    def __init__(self, year: int, event: str, session_type: str):
        message = f"Session '{session_type}' not found for {event} in {year}"
        super().__init__(message, resource="session")


class InvalidSessionTypeError(F1APIException):
    """Raised when an invalid session type is provided"""

    def __init__(self, session_type: str):
        message = (
            f"Invalid session type: '{session_type}'. "
            "Valid types: FP1, FP2, FP3, Q, S, SS, SQ, R"
        )
        super().__init__(message, status_code=400)


class SessionLoadError(F1APIException):
    """Raised when a session fails to load"""

    def __init__(self, year: int, event: str, session_type: str, original_error: Optional[str] = None):
        message = f"Failed to load session {event} {year} {session_type}"
        if original_error:
            message += f": {original_error}"
        super().__init__(message, status_code=500)


def handle_f1_exception(exc: F1APIException) -> HTTPException:
    """Convert F1APIException to FastAPI HTTPException"""
    return HTTPException(
        status_code=exc.status_code,
        detail=exc.message
    )
