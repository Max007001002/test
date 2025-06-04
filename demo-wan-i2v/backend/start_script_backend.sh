#!/bin/bash
# Запуск FastAPI приложения с помощью Uvicorn
echo "Starting FastAPI server..."
uvicorn app.main:app --host 0.0.0.0 --port 8000
