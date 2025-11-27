from pydantic import BaseModel
from datetime import datetime

class ItemBase(BaseModel):
    name: str
    image_url: str | None = None
    description: str | None = None
    stock: int = 0

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: str | None = None
    image_url: str | None = None
    description: str | None = None
    stock: int | None = None

class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
