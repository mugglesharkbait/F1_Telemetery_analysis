"""
Pydantic models for F1 Telemetry API
"""

# Import all schemas from the new comprehensive schemas module
from .schemas import *

# Keep backward compatibility with old imports
from .circuit import CircuitInfo, Point
from .comparison import ComparisonData, LapData as OldLapData, TelemetryData
from .driver import DriverInfo as OldDriverInfo
from .race import RaceEvent

__all__ = [
    # New comprehensive schemas
    "Point",
    "SessionInfo",
    "RaceEventInfo",
    "EventDetail",
    "SeasonsResponse",
    "EventsResponse",
    "SessionsResponse",
    "DriverInfo",
    "DriverDetail",
    "DriversResponse",
    "DriverResult",
    "SessionResultsResponse",
    "LapData",
    "LapsResponse",
    "FastestLapData",
    "FastestLapsResponse",
    "LapInfo",
    "TelemetryChannels",
    "TelemetryData",
    "ComparisonTelemetry",
    "CornerAnnotation",
    "TrackMapData",
    "CircuitInfo",
    "WeatherDataPoint",
    "WeatherSummary",
    "WeatherResponse",
    "TeamColor",
    "TeamColorsResponse",
    "CompoundColor",
    "CompoundColorsResponse",
    "ErrorResponse",
    # Legacy exports
    "RaceEvent",
    "ComparisonData",
]
