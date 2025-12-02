from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.item import InventoryItem
from app.models.user import User
from app.models.activity import ActivityLog
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.models.project import Project, ProjectStatus

router = APIRouter()

class ActivityLogResponse(BaseModel):
    id: int
    action: str
    details: str
    timestamp: datetime
    item_name: Optional[str] = None
    user_name: str

    class Config:
        orm_mode = True

class DashboardStats(BaseModel):
    total_items: int
    low_stock_items: List[dict]
    most_used_items: List[dict]
    recent_items: List[dict]
    recent_activity: List[ActivityLogResponse]
    maintenance_items: List[dict]
    active_projects: List[dict]

@router.get("/dashboard/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    # 1. Total Items
    total_items = db.query(InventoryItem).filter(InventoryItem.owner_id == user.id).count()

    # 2. Low Stock (Top 5)
    low_stock = db.query(InventoryItem).filter(
        InventoryItem.owner_id == user.id,
        InventoryItem.stock <= InventoryItem.min_stock
    ).limit(5).all()
    
    low_stock_data = [
        {"id": item.id, "name": item.name, "stock": item.stock, "min_stock": item.min_stock}
        for item in low_stock
    ]

    # 3. Most Used (Top 5 by transaction count)
    # We count logs where action is ADD_STOCK or REMOVE_STOCK for user's items
    most_used_query = db.query(
        InventoryItem.id,
        InventoryItem.name,
        func.count(ActivityLog.id).label("count")
    ).join(ActivityLog, ActivityLog.item_id == InventoryItem.id)\
    .filter(
        InventoryItem.owner_id == user.id,
        ActivityLog.action.in_(["ADD_STOCK", "REMOVE_STOCK"])
    ).group_by(InventoryItem.id)\
    .order_by(desc("count"))\
    .limit(5).all()

    most_used_data = [
        {"id": r.id, "name": r.name, "count": r.count}
        for r in most_used_query
    ]

    # 4. Recent Items (Last 5)
    recent_items = db.query(InventoryItem).filter(
        InventoryItem.owner_id == user.id
    ).order_by(desc(InventoryItem.created_at)).limit(5).all()

    recent_items_data = [
        {"id": item.id, "name": item.name, "image_url": item.image_url, "created_at": item.created_at}
        for item in recent_items
    ]

    # 5. Recent Activity (Last 10)
    recent_activity = db.query(ActivityLog).filter(
        ActivityLog.user_id == user.id
    ).order_by(desc(ActivityLog.timestamp)).limit(10).all()

    activity_data = []
    for log in recent_activity:
        # Fetch item name manually or via relationship if we had one. 
        # Since item_id is nullable and we didn't set up relationship in model yet, query it.
        item_name = "Unknown Item"
        if log.item_id:
            item = db.query(InventoryItem).filter(InventoryItem.id == log.item_id).first()
            if item:
                item_name = item.name
            else:
                item_name = "Deleted Item"
        
        activity_data.append({
            "id": log.id,
            "action": log.action,
            "details": log.details,
            "timestamp": log.timestamp,
            "item_name": item_name,
            "user_name": user.username
        })

    # 6. Maintenance (Missing Information)
    # Check for missing image, description, or location
    maintenance_items = db.query(InventoryItem).filter(
        InventoryItem.owner_id == user.id,
        (
            (InventoryItem.image_url == None) | (InventoryItem.image_url == "") |
            (InventoryItem.description == None) | (InventoryItem.description == "") |
            (InventoryItem.location == None) | (InventoryItem.location == "")
        )
    ).limit(10).all()

    maintenance_data = []
    for item in maintenance_items:
        missing = []
        if not item.image_url:
            missing.append("Image")
        if not item.description:
            missing.append("Description")
        if not item.location:
            missing.append("Location")
            
        maintenance_data.append({
            "id": item.id, 
            "name": item.name,
            "missing_fields": missing
        })

    # 7. Active Projects
    active_projects = db.query(Project).filter(
        Project.owner_id == user.id,
        Project.status == ProjectStatus.ACTIVE
    ).limit(5).all()

    active_projects_data = [
        {"id": p.id, "title": p.title, "status": p.status, "items_count": len(p.items)}
        for p in active_projects
    ]

    return {
        "total_items": total_items,
        "low_stock_items": low_stock_data,
        "most_used_items": most_used_data,
        "recent_items": recent_items_data,
        "recent_activity": activity_data,
        "maintenance_items": maintenance_data,
        "active_projects": active_projects_data
    }
