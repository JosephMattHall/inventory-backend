from pydantic import BaseModel, field_validator
from typing import Optional, List
from datetime import datetime
import json

class ItemBase(BaseModel):
    name: str
    category: str = "Misc"
    description: Optional[str] = None
    stock: int = 0
    min_stock: int = 5
    location: Optional[str] = None
    image_url: Optional[str] = None
    manufacturer_part_number: Optional[str] = None
    attachments: List[str] = []

class ItemCreate(ItemBase):
    pass

class ItemUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    stock: Optional[int] = None
    min_stock: Optional[int] = None
    location: Optional[str] = None
    image_url: Optional[str] = None
    manufacturer_part_number: Optional[str] = None
    attachments: Optional[List[str]] = None

class ItemResponse(ItemBase):
    id: int
    attachments: List[str] = []
    qr_code_url: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    @field_validator('attachments', mode='before')
    @classmethod
    def parse_attachments(cls, v):
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return []
        return v or []

    class Config:
        from_attributes = True
