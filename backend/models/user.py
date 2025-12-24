from app.database import Base, engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    contacts = relationship("Contact", back_populates="user")  # Relationship to Contact model
    sos_requests = relationship("SOSEvent", back_populates="user")  # Relationship to SOSEvent model