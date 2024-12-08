from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import FileResponse
from models import IllData, SoilData, TemData, CommandData
import os
import uvicorn
from starlette.middleware.cors import CORSMiddleware
from pathlib import Path
from uuid import uuid4
from db_config import get_db_connection


app = FastAPI()

# 사진 저장할 폴더 설정
UPLOAD_DIRECTORY = "/image"


origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")


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
        # 고유한 파일 이름 생성
        unique_filename = f"{uuid4().hex}_{file.filename}"
        file_path = os.path.join(UPLOAD_DIRECTORY, unique_filename)

        # 파일 저장
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # 파일 경로를 데이터베이스에 저장
        conn = get_db_connection()
        cursor = conn.cursor()
        query = "INSERT INTO image_path (file_path) VALUES (%s)"
        cursor.execute(query, (file_path,))
        conn.commit()
        cursor.close()
        conn.close()

        return {"message": "File uploaded successfully", "file_path": file_path}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading file: {str(e)}")


# 센서 명령어 로그 추가
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
        cursor = conn.cursor(dictionary=True)

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


# 센서 작동 로그 불러오기
@app.get("/data/log")
async def get_log_data():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 조도 및 수위 데이터 조회
        cursor.execute("SELECT * FROM control_log")
        logs = cursor.fetchall()
        conn.close()

        # 조회 결과 반환
        return {"logs": logs}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching data: {str(e)}")


# 식물 이미지 불러오기
@app.get("/data/images")
async def list_uploaded_files():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 파일 경로 조회
        cursor.execute(
            "SELECT id, file_path, uploaded_at FROM image_path ORDER BY uploaded_at DESC"
        )
        files = cursor.fetchall()

        cursor.close()
        conn.close()

        return {"files": files}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching files: {str(e)}")


@app.get("/data/images/{image_id}")
async def download_image(image_id: int):
    try:
        # 파일 경로 조회
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT file_path FROM image_path WHERE id = %s", (image_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        if not result:
            raise HTTPException(status_code=404, detail="Image not found")

        file_path = result["file_path"]
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="File not found on server")

        # 파일 반환
        return FileResponse(file_path)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching image: {str(e)}")
