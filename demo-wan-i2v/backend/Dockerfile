# ┌────────────────────────────────────────────────────────────────────┐
# │                      backend/Dockerfile                           │
# │    базовый образ – CUDA 12.9 на Ubuntu 22.04 (devel), чтобы       │
# │    flash_attn и другие GPU-библиотеки смогли собраться правильно. │
# └────────────────────────────────────────────────────────────────────┘
FROM nvidia/cuda:12.9.0-devel-ubuntu22.04

ENV DEBIAN_FRONTEND=noninteractive

# 1) Устанавливаем системные пакеты, включая git, Python, ffmpeg, OpenCV-зависимости
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    wget \
    build-essential \
    ca-certificates \
    libgl1-mesa-glx \
    libglib2.0-0 \
    ffmpeg \
    python3 \
    python3-venv \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# 2) Клонируем репозиторий Wan 2.1 и переходим внутрь
RUN git clone https://github.com/Wan-Video/Wan2.1.git /app/Wan2.1

# 3) Обновляем pip и устанавливаем зависимости, перечисленные в Wan 2.1 (в точности как вы прислали),
#    включая flash_attn, accelerate, diffusers и т.д.
#    Здесь мы просто «жёстко» перечисляем все пакеты, указанные в requirements Wan 2.1.
RUN python3 -m pip install --upgrade pip && \
    pip install --no-cache-dir \
      "torch>=2.4.0" \
      "torchvision>=0.19.0" \
      "opencv-python>=4.9.0.80" \
      "diffusers>=0.31.0" \
      "transformers>=4.49.0" \
      "tokenizers>=0.20.3" \
      "accelerate>=1.1.1" \
      tqdm \
      imageio \
      easydict \
      ftfy \
      dashscope \
      imageio-ffmpeg \
      flash_attn \
      "gradio>=5.0.0" \
      "numpy>=1.23.5,<2"

# 4) (Опционально) Если в Wan 2.1 есть файл requirements.txt, и вы хотите его использовать целиком,
#    но без установки flash_attn из оригинального файла (чтобы избежать дублирования),
#    вы можете сделать что-то вроде:
#    RUN cd /app/Wan2.1 && sed '/flash_attn/d' requirements.txt > req_no_flash.txt && \
#        pip install --no-cache-dir -r /app/Wan2.1/req_no_flash.txt
#    Однако мы уже прописали все нужные зависимости явно, так что этот шаг не нужен.

# 5) Копируем ваш собственный код бэкенда (FastAPI, Celery, worker.py и т.д.)
COPY . .

# 6) Создаём папки для загруженных изображений и результирующих видео
RUN mkdir -p /app/uploads /app/videos

# 7) Для удобства (чтобы Python не буферизовал вывод)
ENV PYTHONUNBUFFERED=1

# 8) По умолчанию запускаем FastAPI (uvicorn). Celery-воркер будет стартовать отдельно через docker-compose.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
