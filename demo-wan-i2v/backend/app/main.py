# backend/app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api.i2v import router as i2v_router

app = FastAPI(title="WAN2.1 I2V API")

origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(i2v_router)

VIDEO_DIR = "/app/videos"
if not os.path.isdir(VIDEO_DIR):
    os.makedirs(VIDEO_DIR, exist_ok=True)

app.mount("/videos", StaticFiles(directory=VIDEO_DIR), name="videos")
