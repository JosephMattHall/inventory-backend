from pydantic import BaseModel
from datetime import datetime

class ItemBase(BaseModel):
    name: str
    category: str = "Misc"
    image_url: str | None = None
    description: str | None = None
    stock: int = 0
    min_stock: int = 5
    location: str | None = None

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: str | None = None
    category: str | None = None
    image_url: str | None = None
    description: str | None = None
    stock: int | None = None
    min_stock: int | None = None
    location: str | None = None

class ItemResponse(ItemBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
