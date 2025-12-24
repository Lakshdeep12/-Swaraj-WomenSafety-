from sqlalchemy import Column, Float, ForeignKey, Integer, DateTime
from sqlalchemy.orm import relationship
from app.database import Base
from models.user import User
from datetime import datetime, timedelta

class LiveLocation(Base):
    __tablename__ = "live_locations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    update_at = Column(DateTime, default=datetime.utcnow() + timedelta(hours=5, minutes=30), onupdate=datetime.utcnow() + timedelta(hours=5, minutes=30))

    user = relationship("User", back_populates="locations")