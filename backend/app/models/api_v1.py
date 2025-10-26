from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# Reusing Point from circuit.py for track coordinates
class Point(BaseModel):
    x: float
    y: float
    z: float

# 1. Event Discovery Endpoints

class SessionInfo(BaseModel):
    session_type: str
    session_name: str
    session_date: datetime

class DriverInfo(BaseModel):
    driver_id: str
    full_name: str
    team_name: Optional[str] = None
    team_color: Optional[str] = None

# 2. Lap Timing and Analysis Endpoints

class LapTimeData(BaseModel):
    driver: str
    lap_number: int
    lap_time_s: float
    tyre_compound: str
    is_in_lap: bool
    is_out_lap: bool

class FastestLap(BaseModel):
    driver: str
    time: float
    speed: float
    team: str
    lap_number: int
    gap_to_leader: Optional[float] = None

# 3. Core Telemetry Comparison Endpoint

class ComparisonTelemetry(BaseModel):
    distance: List[float]
    speed_d1: List[float]
    speed_d2: List[float]
    gear_d1: List[float]
    gear_d2: List[float]
    throttle_d1: List[float]
    throttle_d2: List[float]
    brake_d1: List[int]
    brake_d2: List[int]
    delta_time: List[float]

# 4. Circuit and Visualisation Data Endpoints

class CornerAnnotation(BaseModel):
    number: int
    angle: float
    x: float
    y: float

class CircuitMapData(BaseModel):
    track_coordinates: List[Point]
    corner_annotations: List[CornerAnnotation]

class WeatherData(BaseModel):
    time: datetime
    air_temp: float
    track_temp: float
    humidity: float
    wind_speed: float
    wind_direction: float
    rain_indicator: int
