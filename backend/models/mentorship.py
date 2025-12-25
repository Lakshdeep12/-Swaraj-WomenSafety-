from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum as PyEnum


class MentorshipTopic(PyEnum):
    LEGAL_ADVICE = "legal_advice"
    EMOTIONAL_SUPPORT = "emotional_support"
    SAFETY_PLANNING = "safety_planning"
    REPORTING_GUIDANCE = "reporting_guidance"


class MentorshipStatus(PyEnum):
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"


class MentorshipSession(Base):
    __tablename__ = "mentorship_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mentor_id = Column(Integer, ForeignKey("mentors.id"), nullable=False, index=True)
    topic = Column(Enum(MentorshipTopic), nullable=False)
    status = Column(Enum(MentorshipStatus), default=MentorshipStatus.PENDING, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    closed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="mentorship_sessions")
    mentor = relationship("Mentor", back_populates="sessions")
    messages = relationship("MentorshipMessage", back_populates="session", cascade="all, delete-orphan")
