from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.schemas.item import ItemResponse

class ProjectItemBase(BaseModel):
    item_id: int
    quantity: int = 1

class ProjectItemCreate(ProjectItemBase):
    pass

class ProjectItemResponse(ProjectItemBase):
    id: int
    project_id: int
    item: Optional[ItemResponse] = None

    class Config:
        from_attributes = True

class ProjectBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "PLANNING"

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None

class ProjectResponse(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: datetime
    items: List[ProjectItemResponse] = []

    class Config:
        from_attributes = True
