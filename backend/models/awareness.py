from sqlalchemy import Column, Integer, String, Boolean, DateTime, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from app.database import Base  # Adjust import based on your DB setup
from enum import Enum as PyEnum

# Add to top of awareness.py
from sqlalchemy.orm import relationship

# Add to Awareness class (after reactions line)
user_reactions = relationship("Reaction", back_populates="awareness_post")


class AwarenessCategory(PyEnum):
    crime = "crime"
    law = "law"
    guideline = "guideline"


class AwarenessSource(PyEnum):
    ngo = "NGO"
    govt = "Govt"
    admin = "Admin"


class Awareness(Base):
    __tablename__ = "awareness_posts"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(String, nullable=False)
    category = Column(Enum(AwarenessCategory), nullable=False, index=True)
    source = Column(Enum(AwarenessSource), nullable=False)
    is_verified = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships (for future reactions)
    reactions = relationship("Reaction", back_populates="awareness_post")
