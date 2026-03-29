from pydantic import BaseModel
from datetime import datetime

class CropInput(BaseModel):
    N: float
    P: float
    K: float
    temperature: float
    humidity: float
    ph: float
    rainfall: float
    soil_moisture_avg: float
    timestamp: datetime = datetime.utcnow()   # auto assign current UTC time
