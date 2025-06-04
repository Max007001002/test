#!/usr/bin/env bash
set -e

echo "🔧 Установка базовых пакетов..."
apt update && apt install -y git redis-server ffmpeg python3-venv npm

echo "🚀 Запуск Redis..."
service redis-server start

echo "📁 Переход в backend..."
cd backend

echo "🐍 Подготовка виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

echo "📦 Установка Python-зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

echo "🔁 Запуск Celery..."
mkdir -p /workspace/logs
nohup celery -A app.worker.celery_app worker --loglevel=info \
  > /workspace/logs/celery.log 2>&1 &

echo "🌐 Запуск FastAPI (uvicorn)..."
nohup uvicorn app.main:app --host 0.0.0.0 --port 8000 \
  > /workspace/logs/uvicorn.log 2>&1 &

echo "✅ Всё готово. Сервер запущен. FastAPI: :8000, Celery: в фоне"
tail -f /dev/null
