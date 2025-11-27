from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import require_admin
from app.models.item import InventoryItem
from app.models.user import User
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse

router = APIRouter()

# Anyone can read items
@router.get("/items", response_model=list[ItemResponse])
def list_items(db: Session = Depends(get_db)):
    return db.query(InventoryItem).all()

@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: int, db: Session = Depends(get_db)):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")
    return item

# Admin only: create item
@router.post("/items", response_model=ItemResponse)
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    item = InventoryItem(**data.dict())
    db.add(item)
    db.commit()
    db.refresh(item)
    return item

# Admin only: update item
@router.put("/items/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    data: ItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")

    for field, value in data.dict(exclude_unset=True).items():
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item

# Admin only: delete item
@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")

    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}

# Admin only: add stock
@router.post("/items/{item_id}/add/{amount}", response_model=ItemResponse)
def add_stock(
    item_id: int,
    amount: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")

    item.stock += amount
    db.commit()
    db.refresh(item)
    return item

# Admin only: remove stock
@router.post("/items/{item_id}/remove/{amount}", response_model=ItemResponse)
def remove_stock(
    item_id: int,
    amount: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_admin)
):
    item = db.query(InventoryItem).filter(InventoryItem.id == item_id).first()
    if not item:
        raise HTTPException(404, "Item not found")

    if item.stock - amount < 0:
        raise HTTPException(400, "Not enough stock")

    item.stock -= amount
    db.commit()
    db.refresh(item)
    return item
