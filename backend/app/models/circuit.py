from pydantic import BaseModel
from typing import List

class Point(BaseModel):
    x: float
    y: float
    z: float

class CircuitInfo(BaseModel):
    track: List[Point]
