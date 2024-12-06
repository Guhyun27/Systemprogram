from fastapi import FastAPI, File, UploadFile, HTTPException
from models import IllData, SoilData, TemData, CommandData
from db_config import get_db_connection
import os
from pathlib import Path

app = FastAPI()

# 사진 저장할 폴더 설정
UPLOAD_DIRECTORY = "plant_iamges"

# 디렉터리가 없으면 생성
Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)


# 조도,수위 데이터 추가
@app.post("/data/illumination")
async def add_illumination_data(data: IllData):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO illu_data (illumination, water_level, time)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (data.illumination, data.water_level, data.time))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Illumination and water level data added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 공기온습도 데이터 추가
@app.post("/data/temperature_air")
async def add_temperature_air_data(data: TemData):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO tem_air_data (temperature, air_humid, time)
        VALUES (%s, %s, %s)
        """
        cursor.execute(query, (data.temperature, data.air_humid, data.time))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Temperature and air humidity data added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 토양습도 데이터 추가
@app.post("/data/soil")
async def add_soil_data(data: SoilData):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO soil_data (soil_humid, time)
        VALUES (%s, %s)
        """
        cursor.execute(query, (data.soil_humid, data.time))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Soil humidity data added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 식물 이미지 저장
@app.post("/data/image")
async def upload_image(file: UploadFile = File(...)):
    try:
        # 파일 저장 경로 설정
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)

        # 파일 저장
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        return {"message": f"File {file.filename} uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


# 센서 명령어 기록 추가
@app.post("/data/control")
async def add_control_log(data: CommandData):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        query = """
        INSERT INTO control_log (opcode, time)
        VALUES (%s, %s)
        """
        cursor.execute(query, (data.opcode, data.time))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Control log added successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# 식물 데이터 불러오기
@app.get("/data/all")
async def get_all_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 조도 및 수위 데이터 조회
        cursor.execute("SELECT * FROM illu_data")
        illumination_data = [dict(row) for row in cursor.fetchall()]

        # 온도 및 공기 습도 데이터 조회
        cursor.execute("SELECT * FROM tem_air_data")
        temperature_air_data = [dict(row) for row in cursor.fetchall()]

        # 토양 습도 데이터 조회
        cursor.execute("SELECT * FROM soil_data")
        soil_data = [dict(row) for row in cursor.fetchall()]

        conn.close()

        # 하나의 JSON으로 결합
        return {
            "illumination_data": illumination_data,
            "temperature_air_data": temperature_air_data,
            "soil_data": soil_data,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")
