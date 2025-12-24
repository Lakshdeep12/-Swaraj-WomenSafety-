from sqlalchemy import Column, Float, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from models.user import User
from datetime import datetime, timedelta

class SOSEvent(Base):
    __tablename__ = "sos_events"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    status = Column(String, default = "triggered") # e.g., triggered, resolved
    triggered_at = Column(DateTime, default=datetime.utcnow() + timedelta(hours=5, minutes=30))
    timestamp = Column(DateTime, default=datetime.utcnow() + timedelta(hours=5, minutes=30))

    user = relationship("User", back_populates="sos_requests")