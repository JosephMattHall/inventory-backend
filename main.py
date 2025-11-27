from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.database import engine, Base
from app.routers import auth, items, upload
import os

# Create tables (if not using Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory System with Authentication + Roles")

# Ensure media directory exists
MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

app.mount("/media", StaticFiles(directory=MEDIA_DIR), name="media")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

app.include_router(auth.router)
app.include_router(items.router)
app.include_router(upload.router)
