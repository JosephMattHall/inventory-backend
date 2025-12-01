from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from datetime import datetime
from app.core.database import Base

class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=True)
    action = Column(String, index=True) # CREATE, UPDATE, ADD_STOCK, REMOVE_STOCK
    details = Column(String, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
