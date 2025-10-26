"""
Comprehensive Pydantic Models for F1 Telemetry API
Based on FastF1 data structures and API Blueprint
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from datetime import datetime


# ============================================================================
# COMMON MODELS
# ============================================================================

class Point(BaseModel):
    """3D point for track coordinates"""
    x: float
    y: float
    z: float = 0.0


# ============================================================================
# 1. EVENT & SCHEDULE DISCOVERY
# ============================================================================

class SessionInfo(BaseModel):
    """Session information for an event"""
    session_name: str = Field(..., description="Name of the session (e.g., 'Practice 1', 'Qualifying')")
    session_type: str = Field(..., description="Session type abbreviation (FP1, FP2, FP3, Q, S, SQ, R)")
    session_number: Optional[int] = Field(None, description="Session number (1-5)")
    date_utc: datetime = Field(..., description="Session date/time in UTC")
    date_local: Optional[datetime] = Field(None, description="Session date/time in local timezone")


class RaceEventInfo(BaseModel):
    """Race event information from event schedule"""
    round_number: int = Field(..., description="Round number in the championship")
    event_name: str = Field(..., description="Event name (e.g., 'Monaco Grand Prix')")
    official_event_name: Optional[str] = Field(None, description="Official full event name")
    location: str = Field(..., description="Circuit location/city")
    country: str = Field(..., description="Country name")
    country_code: Optional[str] = Field(None, description="3-letter country code")
    event_date: datetime = Field(..., description="Main event date")
    event_format: Optional[Literal["conventional", "sprint", "sprint_shootout", "sprint_qualifying", "testing"]] = Field(
        None, description="Weekend format type"
    )
    is_testing: bool = Field(default=False, description="Whether this is a testing event")


class EventDetail(BaseModel):
    """Detailed event information with all sessions"""
    round_number: int
    event_name: str
    official_event_name: Optional[str] = None
    location: str
    country: str
    event_format: Optional[str] = None
    sessions: List[SessionInfo]


class SeasonsResponse(BaseModel):
    """Response for available seasons"""
    seasons: List[int]


class EventsResponse(BaseModel):
    """Response for events in a season"""
    events: List[RaceEventInfo]


class SessionsResponse(BaseModel):
    """Response for sessions in an event"""
    sessions: List[SessionInfo]


# ============================================================================
# 2. DRIVER & TEAM INFORMATION
# ============================================================================

class DriverInfo(BaseModel):
    """Driver information"""
    driver_number: str = Field(..., description="Driver's racing number")
    abbreviation: str = Field(..., description="3-letter driver abbreviation (e.g., VER)")
    full_name: str = Field(..., description="Driver's full name")
    first_name: Optional[str] = Field(None, description="First name")
    last_name: Optional[str] = Field(None, description="Last name")
    team_name: str = Field(..., description="Team name")
    team_color: str = Field(..., description="Team color (hex)")
    country_code: Optional[str] = Field(None, description="Driver's country code")
    headshot_url: Optional[str] = Field(None, description="URL to driver headshot")


class DriverDetail(BaseModel):
    """Detailed driver information including session performance"""
    driver_number: str
    abbreviation: str
    full_name: str
    team_name: str
    team_color: str
    grid_position: Optional[float] = None
    finish_position: Optional[float] = None
    points: float = 0.0
    status: Optional[str] = None
    dnf: bool = False
    total_laps: Optional[float] = None
    fastest_lap: Optional[str] = None
    fastest_lap_number: Optional[float] = None


class DriversResponse(BaseModel):
    """Response for drivers in a session"""
    drivers: List[DriverInfo]


# ============================================================================
# 3. SESSION RESULTS
# ============================================================================

class DriverResult(BaseModel):
    """Individual driver session result"""
    position: Optional[float] = None
    driver_number: str
    broadcast_name: str
    full_name: str
    abbreviation: str
    driver_id: str
    team_name: str
    team_color: str
    team_id: str
    first_name: str
    last_name: str
    headshot_url: Optional[str] = None
    country_code: Optional[str] = None
    grid_position: Optional[float] = None
    classified_position: Optional[str] = None
    q1: Optional[str] = None  # Formatted as string for display
    q2: Optional[str] = None
    q3: Optional[str] = None
    time: Optional[str] = None  # Race time as string
    status: Optional[str] = None
    points: float = 0.0
    laps: Optional[float] = None


class SessionResultsResponse(BaseModel):
    """Complete session results"""
    session_info: dict
    results: List[DriverResult]


# ============================================================================
# 4. LAP TIMING & ANALYSIS
# ============================================================================

class LapData(BaseModel):
    """Individual lap data"""
    time: str = Field(..., description="Session time when lap ended (formatted)")
    driver: str
    driver_number: str
    lap_time: Optional[str] = None  # Formatted lap time
    lap_time_seconds: Optional[float] = None  # Raw seconds for calculations
    lap_number: float
    lap_start_time: Optional[str] = None
    lap_start_date: Optional[datetime] = None
    stint: Optional[float] = None
    sector_1_time: Optional[str] = None
    sector_2_time: Optional[str] = None
    sector_3_time: Optional[str] = None
    sector_1_session_time: Optional[str] = None
    sector_2_session_time: Optional[str] = None
    sector_3_session_time: Optional[str] = None
    speed_i1: Optional[float] = None
    speed_i2: Optional[float] = None
    speed_fl: Optional[float] = None
    speed_st: Optional[float] = None
    is_personal_best: bool = False
    is_accurate: bool = True
    compound: Optional[str] = None
    tyre_life: Optional[float] = None
    fresh_tyre: Optional[bool] = None
    pit_out_time: Optional[str] = None
    pit_in_time: Optional[str] = None
    team: Optional[str] = None
    track_status: Optional[str] = None
    position: Optional[float] = None
    deleted: Optional[bool] = None
    deleted_reason: Optional[str] = None


class LapsResponse(BaseModel):
    """Response for lap data"""
    laps: List[LapData]
    total_laps: int


class FastestLapData(BaseModel):
    """Fastest lap information"""
    driver: str
    driver_number: str
    team: str
    team_color: str
    lap_time: str
    lap_time_seconds: float
    lap_number: float
    speed_st: Optional[float] = None
    compound: Optional[str] = None
    tyre_life: Optional[float] = None
    gap_to_fastest: str
    gap_to_fastest_seconds: float
    sector_1_time: Optional[str] = None
    sector_2_time: Optional[str] = None
    sector_3_time: Optional[str] = None


class FastestLapsResponse(BaseModel):
    """Response for fastest laps"""
    fastest_laps: List[FastestLapData]


# ============================================================================
# 5. TELEMETRY & COMPARISON
# ============================================================================

class LapInfo(BaseModel):
    """Lap metadata for telemetry"""
    driver: str
    driver_number: str
    team: str
    team_color: str
    lap_number: float
    lap_time: str
    lap_time_seconds: float


class TelemetryChannels(BaseModel):
    """Telemetry data channels"""
    time: List[float] = Field(default_factory=list, description="Time in seconds from lap start")
    session_time: List[float] = Field(default_factory=list, description="Session time in seconds")
    distance: List[float] = Field(default_factory=list, description="Distance in meters")
    speed: List[float] = Field(default_factory=list, description="Speed in km/h")
    rpm: List[float] = Field(default_factory=list, description="Engine RPM")
    n_gear: List[int] = Field(default_factory=list, description="Gear number")
    throttle: List[float] = Field(default_factory=list, description="Throttle position (0-100%)")
    brake: List[bool] = Field(default_factory=list, description="Brake status")
    drs: List[int] = Field(default_factory=list, description="DRS status")
    x: List[float] = Field(default_factory=list, description="X coordinate")
    y: List[float] = Field(default_factory=list, description="Y coordinate")
    z: List[float] = Field(default_factory=list, description="Z coordinate")


class TelemetryData(BaseModel):
    """Single lap telemetry response"""
    lap_info: LapInfo
    telemetry: TelemetryChannels
    data_points: int


class ComparisonTelemetry(BaseModel):
    """Telemetry comparison between two laps"""
    driver1: LapInfo
    driver2: LapInfo
    comparison_data: dict  # Contains arrays for distance, speed, throttle, etc.
    lap_time_delta: float
    max_speed_delta: float
    data_points: int


# ============================================================================
# 6. CIRCUIT & TRACK INFORMATION
# ============================================================================

class CornerAnnotation(BaseModel):
    """Corner information for circuit map"""
    number: int
    letter: Optional[str] = None
    name: Optional[str] = None
    angle: float
    distance: Optional[float] = None
    x: float
    y: float


class TrackMapData(BaseModel):
    """Track map coordinates"""
    x_coordinates: List[float]
    y_coordinates: List[float]


class CircuitInfo(BaseModel):
    """Circuit information including track map and corners"""
    circuit_name: Optional[str] = None
    location: str
    country: str
    rotation: float = 0.0
    track_map: TrackMapData
    corners: List[CornerAnnotation] = Field(default_factory=list)
    marshal_lights: List[dict] = Field(default_factory=list)
    marshal_sectors: List[dict] = Field(default_factory=list)


# ============================================================================
# 7. WEATHER DATA
# ============================================================================

class WeatherDataPoint(BaseModel):
    """Single weather data point"""
    time: str = Field(..., description="Session time when recorded")
    air_temp: float = Field(..., description="Air temperature in Celsius")
    humidity: float = Field(..., description="Humidity percentage")
    pressure: float = Field(..., description="Air pressure in hPa")
    rainfall: bool = Field(..., description="Rain detected")
    track_temp: float = Field(..., description="Track temperature in Celsius")
    wind_direction: int = Field(..., description="Wind direction in degrees")
    wind_speed: float = Field(..., description="Wind speed in m/s")


class WeatherSummary(BaseModel):
    """Weather summary statistics"""
    avg_air_temp: float
    avg_track_temp: float
    max_wind_speed: float
    rain_detected: bool


class WeatherResponse(BaseModel):
    """Weather data response"""
    session_info: dict
    weather_data: List[WeatherDataPoint]
    summary: WeatherSummary


# ============================================================================
# 8. VISUALIZATION HELPERS
# ============================================================================

class TeamColor(BaseModel):
    """Team color information"""
    team_name: str
    team_id: str
    official_color: str
    fastf1_color: str


class TeamColorsResponse(BaseModel):
    """Team colors response"""
    year: int
    teams: List[TeamColor]


class CompoundColor(BaseModel):
    """Tire compound color"""
    name: str
    color: str


class CompoundColorsResponse(BaseModel):
    """Compound colors response"""
    compounds: List[CompoundColor]


# ============================================================================
# 9. ERROR RESPONSES
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response model"""
    detail: str
    error_type: Optional[str] = None
    status_code: int
