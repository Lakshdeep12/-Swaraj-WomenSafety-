from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.database import SessionLocal
from routes.auth import get_current_user
from schemas.mentorship import (
    MentorshipSessionBase,
    MentorshipMessageCreate,
    UserSessionsResponse,
    MentorshipSessionResponse
)
from services.mentorship import (
    request_mentorship,
    mentor_reply,
    user_reply,
    close_session,
    get_user_sessions
)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/mentorship", tags=["mentorship"])


@router.post("/request", response_model=MentorshipSessionResponse)
async def request_session(
    topic_data: MentorshipSessionBase,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """User requests mentorship session"""
    return request_mentorship(db, current_user.id, topic_data.topic)


@router.get("/sessions", response_model=UserSessionsResponse)
async def list_sessions(
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's mentorship sessions"""
    sessions = get_user_sessions(db, current_user.id)
    return UserSessionsResponse(
        sessions=sessions,
        total=len(sessions),
        active_count=len([s for s in sessions if s.status == "active"])
    )


@router.post("/{session_id}/user-reply")
async def send_user_reply(
    session_id: int,
    message_data: MentorshipMessageCreate,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """User replies in session"""
    return user_reply(db, session_id, current_user.id, message_data.message)


@router.post("/{session_id}/mentor-reply")
async def send_mentor_reply(
    session_id: int,
    message_data: MentorshipMessageCreate,
    current_user=Depends(get_current_user),  # Mentor user
    db: Session = Depends(get_db)
):
    """Mentor replies in session"""
    return mentor_reply(db, session_id, current_user.id, message_data.message)


@router.post("/{session_id}/close")
async def close_mentorship_session(
    session_id: int,
    current_user=Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Close session (user or mentor)"""
    success = close_session(db, session_id, current_user.id, "user")
    if success:
        return {"message": "Session closed successfully"}
    raise HTTPException(status_code=400, detail="Failed to close session")
