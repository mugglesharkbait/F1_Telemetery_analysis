from pydantic import BaseModel
from typing import List

class TelemetryData(BaseModel):
    distance: float
    speed: float
    gear: float
    throttle: float

class LapData(BaseModel):
    driver_id: str
    lap_number: int
    telemetry: List[TelemetryData]

class ComparisonData(BaseModel):
    lap1: LapData
    lap2: LapData
    delta_time: List[float]
