from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base
from enum import Enum as PyEnum


class MessageRole(PyEnum):
    USER = "user"
    MENTOR = "mentor"


class MentorshipMessage(Base):
    __tablename__ = "mentorship_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("mentorship_sessions.id"), nullable=False, index=True)
    sender_id = Column(Integer, nullable=False)  # user_id or mentor_id
    role = Column(Enum(MessageRole), nullable=False)
    message = Column(String(1000), nullable=False)
    is_filtered = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    session = relationship("MentorshipSession", back_populates="messages")
