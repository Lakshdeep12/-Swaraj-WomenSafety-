from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from routes.auth import get_current_user
from models.user import User
from schemas.reaction import ReactionCreate, ReactionResponse, ReactionSummary
from services.reaction import add_or_update_reaction, remove_reaction, get_reaction_summary

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/reactions", tags=["reactions"])

@router.post("/awareness/{post_id}", response_model=ReactionResponse)
async def react_to_post(
    post_id: int,
    reaction_data: ReactionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Add or update reaction to awareness post"""
    return add_or_update_reaction(db, current_user.id, post_id, reaction_data.emoji)

@router.delete("/awareness/{post_id}")
async def remove_reaction_from_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove user's reaction from awareness post"""
    success = remove_reaction(db, current_user.id, post_id)
    if not success:
        raise HTTPException(status_code=404, detail="Reaction not found")
    return {"message": "Reaction removed"}

@router.get("/awareness/{post_id}/summary", response_model=List[ReactionSummary])
async def get_post_reactions_summary(
    post_id: int,
    db: Session = Depends(get_db)
):
    """Get reaction summary for awareness post"""
    return get_reaction_summary(db, post_id)