# backend/app/worker.py
import os
import subprocess
from celery import Celery
from app.services.celery_app import celery_app  # убедитесь, что путь корректный

@celery_app.task(name="generate_video_task_async", bind=True)
def generate_video_task_async(self, job_id: str, filename: str, prompt: str):
    """
    Таска для генерации видео с помощью Wan 2.1 через скрипт generate.py.

    Аргументы:
      - job_id: уникальный идентификатор (UUID)
      - filename: имя загруженного файла (например, "1234_myimage.png"), лежащего в /app/uploads
      - prompt: текстовый prompt

    Логика:
      1) Формируем путь до входного изображения: /app/uploads/{filename}
      2) Запускаем torchrun с 2 GPU внутри каталога /app/Wan2.1
      3) Ждём завершения и проверяем returncode
      4) Если всё успешно, ожидаем файл /app/videos/{job_id}.mp4
      5) Возвращаем {"status":"success","output_path":"/app/videos/job_id.mp4"} или ошибку
    """
    try:
        # 1) Пути и директории
        uploads_dir = "/app/uploads"
        videos_dir = "/app/videos"
        ckpt_dir = "/app/Wan2.1-I2V-14B-720P"  # <-- здесь должны лежать чекпоинты (скачайте заранее!)
        os.makedirs(videos_dir, exist_ok=True)

        img_path = os.path.join(uploads_dir, filename)
        out_name = f"{job_id}.mp4"

        # 2) Формируем команду torchrun
        cmd = [
            "torchrun",
            "--nproc_per_node=2",       # запускаем на 2 GPU (Pro 6000 и Pro 6000)
            "generate.py",
            "--task", "i2v-14B",
            "--size", "1280*720",
            "--ckpt_dir", ckpt_dir,
            "--image", img_path,
            "--dit_fsdp",
            "--t5_fsdp",
            "--ulysses_size", "8",
            "--prompt", prompt,
            "--output_dir", videos_dir,
            "--output_name", out_name
        ]

        # 3) Запускаем процесс внутри каталога /app/Wan2.1
        result = subprocess.run(cmd, cwd="/app/Wan2.1", capture_output=True, text=True)
        if result.returncode != 0:
            # Если ошибка, возвращаем stderr
            return {"status": "error", "message": result.stderr}

        # 4) Вернём относительный путь до видео
        return {"status": "success", "output_path": f"/app/videos/{out_name}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}
