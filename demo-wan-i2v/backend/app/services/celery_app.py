# backend/app/services/celery_app.py
import os
from celery import Celery

# Берём BROKER_URL из переменных окружения или используем Redis по умолчанию
BROKER_URL = os.getenv("BROKER_URL", "redis://redis:6379/0")
RESULT_BACKEND = os.getenv("RESULT_BACKEND", BROKER_URL)  # можно задать отдельный, но Redis справится

celery_app = Celery(
    "wan_i2v_worker",
    broker=BROKER_URL,
    backend=RESULT_BACKEND,
)

# Если нужно, можно установить настройки Celery здесь:
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    result_expires=3600,  # через час удаляем результаты из Redis
    task_track_started=True,
)
