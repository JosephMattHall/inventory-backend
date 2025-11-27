from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from datetime import datetime
from app.core.database import Base

class InventoryItem(Base):
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    category = Column(String, default="Misc")
    image_url = Column(String, nullable=True)
    description = Column(Text, nullable=True)
    stock = Column(Integer, default=0)
    min_stock = Column(Integer, default=5)
    location = Column(String, nullable=True)
    attachments = Column(String, default="[]") # JSON string of URLs
    qr_code_url = Column(String, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
