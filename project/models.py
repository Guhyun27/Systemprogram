from pydantic import BaseModel
from datetime import datetime


# sensordata 정의
class SensorData(BaseModel):
    illumination: float
    soil_humid: float
    temperature: float
    air_humid: float
    water_level: float
    time: datetime


# sensor command 데이터 정의
class CommandData(BaseModel):
    opcode: str
    time: datetime
