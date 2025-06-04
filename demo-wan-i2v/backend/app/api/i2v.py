# backend/app/api/i2v.py
import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.worker import generate_video_task_async
from celery.result import AsyncResult

router = APIRouter()

UPLOAD_DIR = "/app/uploads"
VIDEO_DIR = "/app/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

@router.post("/api/i2v/")
async def submit_i2v(
    file: UploadFile = File(...),
    prompt: str = Form(...),
):
    """
    Принимаем изображение (file) и prompt.
    Сохраняем файл в /app/uploads/{job_id}_{имя_файла}.
    Запускаем Celery-таску generate_video_task_async(job_id, filename, prompt).
    """
    job_id = str(uuid.uuid4())
    filename = f"{job_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Запускаем Celery-таску с заданным job_id
    generate_video_task_async.apply_async(
        args=[job_id, filename, prompt],
        task_id=job_id
    )

    return {"job_id": job_id, "status": "submitted"}

@router.get("/api/i2v/{job_id}")
async def get_i2v_status(job_id: str):
    """
    Проверяем через AsyncResult статус задачи по job_id.
    Если завершено успешно, возвращаем JSON с video_url = /videos/{job_id}.mp4
    """
    result = AsyncResult(job_id, app=generate_video_task_async.app)
    if result.state in ("PENDING", "STARTED"):
        return {"status": "running"}
    if result.state == "SUCCESS":
        data = result.result
        if data.get("status") == "success":
            video_filename = os.path.basename(data.get("output_path"))
            return {"status": "completed", "video_url": f"/videos/{video_filename}"}
        else:
            return {"status": "failed", "message": data.get("message", "")}
    if result.state in ("FAILURE", "REVOKED"):
        return {"status": "failed", "message": str(result.info)}
    return {"status": "running"}
