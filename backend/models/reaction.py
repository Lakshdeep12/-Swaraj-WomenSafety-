from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import UniqueConstraint
from app.database import Base


class Reaction(Base):
    __tablename__ = "reactions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    awareness_id = Column(Integer, ForeignKey("awareness_posts.id"), nullable=False, index=True)
    emoji = Column(String(10), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="reactions")
    awareness_post = relationship("Awareness", back_populates="reactions")
    
    __table_args__ = (
        UniqueConstraint('user_id', 'awareness_id', name='unique_user_awareness_reaction'),
    )
