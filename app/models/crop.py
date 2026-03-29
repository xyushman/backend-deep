from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class CropInput(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float
    soil_moisture_avg: Optional[float] = None
    timestamp: Optional[datetime] = None
