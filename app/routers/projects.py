from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.project import Project, ProjectItem, ProjectStatus
from app.models.item import InventoryItem
from app.schemas.project import ProjectCreate, ProjectResponse, ProjectUpdate, ProjectItemCreate
from app.models.activity import ActivityLog

router = APIRouter()

@router.get("/projects", response_model=List[ProjectResponse])
def get_projects(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(Project).filter(Project.owner_id == user.id).all()

@router.post("/projects", response_model=ProjectResponse)
def create_project(
    project: ProjectCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    db_project = Project(**project.dict(), owner_id=user.id)
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    
    # Log activity
    log = ActivityLog(
        user_id=user.id,
        action="CREATE_PROJECT",
        details=f"Created project '{db_project.title}'"
    )
    db.add(log)
    db.commit()
    
    return db_project

@router.get("/projects/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/projects/{project_id}/items", response_model=ProjectResponse)
def add_project_item(
    project_id: int,
    item_data: ProjectItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    if project.status != ProjectStatus.PLANNING:
        raise HTTPException(status_code=400, detail="Cannot add items to active or completed projects")

    # Check if item exists
    item = db.query(InventoryItem).filter(InventoryItem.id == item_data.item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    # Check if item already in project
    existing_item = db.query(ProjectItem).filter(
        ProjectItem.project_id == project_id,
        ProjectItem.item_id == item_data.item_id
    ).first()

    if existing_item:
        existing_item.quantity += item_data.quantity
    else:
        new_item = ProjectItem(
            project_id=project_id,
            item_id=item_data.item_id,
            quantity=item_data.quantity
        )
        db.add(new_item)
    
    db.commit()
    db.refresh(project)
    return project

@router.put("/projects/{project_id}/status", response_model=ProjectResponse)
def update_project_status(
    project_id: int,
    status_update: ProjectUpdate, # We use this just for status field
    return_items: bool = False, # Query param for completion logic
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    project = db.query(Project).filter(Project.id == project_id, Project.owner_id == user.id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    new_status = status_update.status
    if not new_status:
        raise HTTPException(status_code=400, detail="Status is required")

    # Logic for status transitions
    if new_status == ProjectStatus.ACTIVE and project.status == ProjectStatus.PLANNING:
        # Activate: Deduct stock
        for p_item in project.items:
            inventory_item = db.query(InventoryItem).filter(InventoryItem.id == p_item.item_id).first()
            if not inventory_item:
                continue # Should not happen ideally
            
            if inventory_item.stock < p_item.quantity:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Not enough stock for {inventory_item.name}. Required: {p_item.quantity}, Available: {inventory_item.stock}"
                )
            
            inventory_item.stock -= p_item.quantity
            
            # Log stock deduction
            log = ActivityLog(
                user_id=user.id,
                action="PROJECT_USE",
                item_id=inventory_item.id,
                details=f"Used {p_item.quantity} for project '{project.title}'"
            )
            db.add(log)

    elif new_status == ProjectStatus.COMPLETED and project.status == ProjectStatus.ACTIVE:
        # Complete: Handle items
        if return_items:
            # Return items to stock
            for p_item in project.items:
                inventory_item = db.query(InventoryItem).filter(InventoryItem.id == p_item.item_id).first()
                if inventory_item:
                    inventory_item.stock += p_item.quantity
                    
                    # Log return
                    log = ActivityLog(
                        user_id=user.id,
                        action="PROJECT_RETURN",
                        item_id=inventory_item.id,
                        details=f"Returned {p_item.quantity} from project '{project.title}'"
                    )
                    db.add(log)
        else:
            # Consume items (do nothing, they are already deducted)
             log = ActivityLog(
                user_id=user.id,
                action="PROJECT_CONSUME",
                details=f"Consumed items for project '{project.title}'"
            )
             db.add(log)

    project.status = new_status
    db.commit()
    db.refresh(project)
    return project
