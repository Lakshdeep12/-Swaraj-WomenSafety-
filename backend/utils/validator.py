from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from models.awareness import Awareness
from schemas.reaction import AllowedEmoji


def validate_awareness_exists(db: Session, awareness_id: int):
    """Ensure awareness post exists and is verified"""
    post = db.query(Awareness).filter(
        Awareness.id == awareness_id, 
        Awareness.is_verified.is_(True)
    ).first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Awareness post not found or not verified"
        )
    return post


def validate_allowed_emoji(emoji: str) -> str:
    """Validate emoji is from whitelist"""
    allowed = [e.value for e in AllowedEmoji]
    if emoji not in allowed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid emoji. Allowed: {allowed}"
        )
    return emoji
