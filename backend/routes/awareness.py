from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from routes.auth import require_admin_or_ngo, get_current_user
from schemas.awareness import (
    AwarenessCreate,
    AwarenessResponse,
    AwarenessFeedResponse,
    AwarenessCategory
)
from schemas.reaction import ReactionCreate, ReactionResponse, ReactionSummary
from services.awareness import (
    create_awareness_post,
    get_awareness_feed,
    get_awareness_by_id
)
from services.reaction import (
    add_or_update_reaction,
    remove_reaction,
    get_reaction_summary
)
from app.database import SessionLocal


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


router = APIRouter(prefix="/awareness", tags=["awareness"])


@router.get("/feed", response_model=AwarenessFeedResponse)
async def read_feed(
    category: Optional[AwarenessCategory] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(get_db)
):
    """Public: Get paginated awareness feed"""
    return get_awareness_feed(db, category, page, page_size)


@router.get("/{post_id}", response_model=AwarenessResponse)
async def read_post(post_id: int, db: Session = Depends(get_db)):
    """Public: Get single awareness post"""
    return get_awareness_by_id(db, post_id)


@router.post("/create", response_model=AwarenessResponse, status_code=201)
async def create_post(
    awareness_data: AwarenessCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin_or_ngo)
):
    """Protected: Admin/NGO create post"""
    return create_awareness_post(db, awareness_data)


@router.post("/{post_id}/react", response_model=ReactionResponse)
async def react_to_post(
    post_id: int,
    reaction_data: ReactionCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Users react with emoji (1 per user per post)"""
    return add_or_update_reaction(
        db, current_user.id, post_id, reaction_data.emoji
    )


@router.delete("/{post_id}/react")
async def unreact_post(
    post_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove user's reaction"""
    removed = remove_reaction(db, current_user.id, post_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No reaction found"
        )
    return {"message": "Reaction removed successfully"}


@router.get("/{post_id}/reactions", response_model=ReactionSummary)
async def get_reactions(
    post_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get reaction summary for post"""
    return get_reaction_summary(db, post_id, current_user.id)
