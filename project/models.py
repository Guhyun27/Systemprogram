from pydantic import BaseModel
from datetime import datetime


# sensordata 정의
class IllData(BaseModel):
    illumination: float
    water_level: float
    time: datetime


class SoilData(BaseModel):
    soil_humid: float
    time: datetime


class TemData(BaseModel):
    temperature: float
    air_humid: float
    time: datetime


# sensor command 데이터 정의
class CommandData(BaseModel):
    opcode: str
    time: datetime
