from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.database import engine, Base
from app.routers import auth, items

# Create tables (if not using Alembic)
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Inventory System with Authentication + Roles")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

app.include_router(auth.router)
app.include_router(items.router)
