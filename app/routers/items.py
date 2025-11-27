from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.item import InventoryItem
from app.models.user import User
from app.schemas.item import ItemCreate, ItemUpdate, ItemResponse
import json
import qrcode
import os
from uuid import uuid4

router = APIRouter()

def generate_qr_code(data: str, media_dir: str = "media") -> str:
    filename = f"qr_{uuid4()}.png"
    filepath = os.path.join(media_dir, filename)
    
    # Ensure directory exists
    os.makedirs(media_dir, exist_ok=True)

    img = qrcode.make(data)
    img.save(filepath)

    return filename

# List items (scoped to user)
@router.get("/items", response_model=list[ItemResponse])
def list_items(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(InventoryItem).filter(InventoryItem.owner_id == user.id).all()

# Get item (scoped to user)
@router.get("/items/{item_id}", response_model=ItemResponse)
def get_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id,
        InventoryItem.owner_id == user.id
    ).first()
    if not item:
        raise HTTPException(404, "Item not found")
    return item

# Create item (assign to user)
@router.post("/items", response_model=ItemResponse)
def create_item(
    data: ItemCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    item_data = data.dict()
    if "attachments" in item_data:
        item_data["attachments"] = json.dumps(item_data["attachments"])
    
    # Generate QR Code
    # We don't have the ID yet, so we'll commit first then update, OR we can just encode a placeholder and update, 
    # BUT better to just encode the intended URL structure. 
    # Actually, we need the ID for the URL. 
    # Strategy: Create item -> flush to get ID -> generate QR -> update item -> commit.
    
    item = InventoryItem(**item_data, owner_id=user.id)
    db.add(item)
    db.flush() # Get ID
    
    qr_data = f"http://localhost:3000/inventory/{item.id}" # pointing to frontend detail page
    qr_filename = generate_qr_code(qr_data)
    item.qr_code_url = f"/media/{qr_filename}"
    
    db.commit()
    db.refresh(item)
    return item

# Update item (scoped to user)
@router.put("/items/{item_id}", response_model=ItemResponse)
def update_item(
    item_id: int,
    data: ItemUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id,
        InventoryItem.owner_id == user.id
    ).first()
    if not item:
        raise HTTPException(404, "Item not found")

    for field, value in data.dict(exclude_unset=True).items():
        if field == "attachments" and isinstance(value, list):
            value = json.dumps(value)
        setattr(item, field, value)

    db.commit()
    db.refresh(item)
    return item

# Delete item (scoped to user)
@router.delete("/items/{item_id}")
def delete_item(
    item_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id,
        InventoryItem.owner_id == user.id
    ).first()
    if not item:
        raise HTTPException(404, "Item not found")

    db.delete(item)
    db.commit()
    return {"message": "Item deleted"}

# Add stock (scoped to user)
@router.post("/items/{item_id}/add/{amount}", response_model=ItemResponse)
def add_stock(
    item_id: int,
    amount: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id,
        InventoryItem.owner_id == user.id
    ).first()
    if not item:
        raise HTTPException(404, "Item not found")

    item.stock += amount
    db.commit()
    db.refresh(item)
    return item

# Remove stock (scoped to user)
@router.post("/items/{item_id}/remove/{amount}", response_model=ItemResponse)
def remove_stock(
    item_id: int,
    amount: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    item = db.query(InventoryItem).filter(
        InventoryItem.id == item_id,
        InventoryItem.owner_id == user.id
    ).first()
    if not item:
        raise HTTPException(404, "Item not found")

    if item.stock - amount < 0:
        raise HTTPException(400, "Not enough stock")

    item.stock -= amount
    db.commit()
    db.refresh(item)
    return item
