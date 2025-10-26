from pydantic import BaseModel

class DriverInfo(BaseModel):
    driver_id: str
    full_name: str
