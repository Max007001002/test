# backend/app/api/i2v.py
import os
import uuid
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
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
    neg_prompt: str = Form(""),
    duration_sec: int = Form(5),
    fps: int = Form(16),
    num_inference_steps: int = Form(25),
):
    job_id = str(uuid.uuid4())
    content = await file.read()
    filename = f"{job_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(content)

    # Запускаем Celery-таску с task_id = job_id
    generate_video_task_async.apply_async(
        args=[job_id, content, prompt, neg_prompt, duration_sec, fps, num_inference_steps],
        task_id=job_id
    )
    return {"job_id": job_id, "status": "submitted"}

@router.get("/api/i2v/{job_id}")
async def get_i2v_status(job_id: str):
    result = AsyncResult(job_id, app=generate_video_task_async.app)
    # result.state может быть: PENDING, STARTED, SUCCESS, FAILURE
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
