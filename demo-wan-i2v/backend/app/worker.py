# backend/app/worker.py
import os
import io
import torch
from PIL import Image
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
from app.services.celery_app import celery_app  # при том, что в root`е есть папка app/
import sageattention
import teacache

MODEL_DIR = os.getenv("WAN_MODEL_PATH", "/models/wan14B-720p")
# Если вы хотите, чтобы модель автоматически скачивалась из HuggingFace на первом запуске,
# MODEL_DIR можно не задавать, и внутри WanI2V.from_pretrained указывать название из репы.

pipe = None

def load_pipe():
    """
    Загружает WanI2V pipeline (fp16) с SageAttention и teacache.
    Вызывается один раз (pipe=global).
    """
    global pipe
    if pipe is None:
        try:
            from wan.image2video import WanI2V
        except ImportError as e:
            raise ImportError(f"WanI2V не найден: {e}")

        # Загружаем в fp16 на CUDA
        pipe = WanI2V.from_pretrained(
            MODEL_DIR,
            torch_dtype=torch.float16
        ).to("cuda")

        # Применяем ускорители
        teacache.patch(pipe.unet)
        sageattention.apply_sage_attention(pipe.unet, int8_kv=True)
        try:
            pipe.enable_attention_slicing()
        except Exception:
            pass

        print("Пайплайн WanI2V загружен с SageAttention + teacache.")
    return pipe

@celery_app.task(name="generate_video_task_async", bind=True)
def generate_video_task_async(self, job_id: str, img_bytes: bytes,
                              prompt: str, neg_prompt: str,
                              duration_sec: int, fps: int, num_inference_steps: int):
    """
    1. Декодируем img_bytes в PIL Image
    2. Запускаем pipeline(img2video) → список numpy кадров [H,W,3]
    3. Сохраняем mp4 через MoviePy в /app/videos/{job_id}.mp4
    4. Возвращаем {"status":"success","output_path":"/app/videos/job_id.mp4"} или ошибку
    """
    try:
        image = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        pipeline = load_pipe()
        total_frames = duration_sec * fps

        # Генерируем кадры (WanI2V API: img2video)
        result = pipeline(
            prompt=prompt,
            negative_prompt=neg_prompt,
            image=image,
            num_inference_steps=num_inference_steps,
            fps=fps,
            frames=total_frames,
            height=720,
            width=1280,
        )
        try:
            video_frames = result.videos  # если API вернул объект с .videos
        except Exception:
            video_frames = result  # если вернулся список напрямую

        out_dir = "/app/videos"
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, f"{job_id}.mp4")

        clip = ImageSequenceClip(video_frames, fps=fps)
        clip.write_videofile(
            out_path,
            codec="libx264",
            preset="veryfast",
            audio=False
        )
        return {"status": "success", "output_path": out_path}
    except Exception as e:
        msg = f"Ошибка при генерации видео: {e}"
        print(msg)
        return {"status": "error", "message": msg}
