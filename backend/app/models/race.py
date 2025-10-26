from pydantic import BaseModel
from datetime import datetime

class RaceEvent(BaseModel):
    round_number: int
    country: str
    location: str
    event_name: str
    event_date: datetime
