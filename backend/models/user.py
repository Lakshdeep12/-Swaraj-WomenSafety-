from app.database import Base, engine
from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum

class UserRole(PyEnum):
    user = "user"
    admin = "admin"
    ngo = "ngo"

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.user, nullable=False)
    contacts = relationship("Contact", back_populates="user")  # Relationship to Contact model
    sos_requests = relationship("SOSEvent", back_populates="user")  # Relationship to SOSEvent model
    reactions = relationship("Reaction", back_populates="user")  # Relationship to Reaction model
    locations = relationship("LiveLocation", back_populates="user")  # Relationship to LiveLocation model
    mentorship_sessions = relationship("MentorshipSession", back_populates="user")  # Relationship to MentorshipSession model