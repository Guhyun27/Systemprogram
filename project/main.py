from fastapi import FastAPI, HTTPException
from models import SensorData, CommandData
from db_config import get_db_connection

app = FastAPI()


# 센서 데이터 추가
@app.post("/data")
async def add_sensor_data(data: SensorData):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO data (illumination, soil_humid, temperature, air_humid, water_level, time)
        VALUES (%s, %s, %s, %s, %s, %s)
        """
        values = (
            data.illumination,
            data.soil_humid,
            data.temperature,
            data.air_humid,
            data.water_level,
            data.time,
        )
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Sensor data added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 센서 명령어 기록 추가
@app.post("/command")
async def add_command_data(command: CommandData):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """ 
        INSERT INTO command (opcode, time)
        VALUES (%s, %s)
        """
        values = (command.opcode, command.time)
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Command data added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
