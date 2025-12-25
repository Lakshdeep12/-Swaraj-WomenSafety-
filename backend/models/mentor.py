from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum as PyEnum


class MentorRole(PyEnum):
    NGO = "NGO"
    LAWYER = "Lawyer"
    PSYCHOLOGIST = "Psychologist"


class Mentor(Base):
    __tablename__ = "mentors"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    role = Column(Enum(MentorRole), nullable=False, index=True)
    verified = Column(Boolean, default=False, nullable=False)
    active_status = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sessions = relationship("MentorshipSession", back_populates="mentor")
