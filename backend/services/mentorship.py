from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from fastapi import HTTPException, status
from datetime import datetime, timedelta

from models.mentor import Mentor, MentorRole
from models.mentorship import MentorshipSession, MentorshipTopic, MentorshipStatus
from models.mentorship_message import MentorshipMessage, MessageRole
from schemas.mentorship import (
    MentorshipSessionBase,
    MentorshipMessageCreate,
    MentorshipSessionResponse
)
from utils.content_filter import is_content_safe  # Reuse existing filter


def request_mentorship(
    db: Session,
    user_id: int,
    topic: MentorshipTopic
) -> MentorshipSessionResponse:
    """Create new mentorship session (1 active per user)"""
    
    # Check if user has active session
    active_session = db.query(MentorshipSession).filter(
        MentorshipSession.user_id == user_id,
        MentorshipSession.status.in_([MentorshipStatus.PENDING, MentorshipStatus.ACTIVE])
    ).first()
    
    if active_session:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already has an active mentorship session"
        )
    
    # Auto-assign available mentor by role/topic
    mentor_role = _get_mentor_role_for_topic(topic)
    available_mentor = db.query(Mentor).filter(
        Mentor.role == mentor_role,
        Mentor.active_status == True,
        Mentor.verified == True
    ).order_by(func.random()).first()  # Simple round-robin
    
    if not available_mentor:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="No available mentors right now. Try again later."
        )
    
    # Create session
    session = MentorshipSession(
        user_id=user_id,
        mentor_id=available_mentor.id,
        topic=topic,
        status=MentorshipStatus.PENDING
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return MentorshipSessionResponse(
        id=session.id,
        user_id=session.user_id,
        mentor_id=session.mentor_id,
        mentor_name=available_mentor.name,
        topic=session.topic,
        status=session.status,
        created_at=session.created_at
    )


def mentor_reply(
    db: Session,
    session_id: int,
    mentor_id: int,
    message: str
) -> MentorshipMessage:
    """Mentor sends reply (content filtered)"""
    
    session = _get_user_session(db, session_id, mentor_id, allow_mentor=True)
    
    if session.status == MentorshipStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is closed"
        )
    
    # Content safety check
    is_safe, reason = is_content_safe(message)
    if not is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Message rejected: {reason}"
        )
    
    msg = MentorshipMessage(
        session_id=session_id,
        sender_id=mentor_id,
        role=MessageRole.MENTOR,
        message=message.strip(),
        is_filtered=False
    )
    
    db.add(msg)
    db.commit()
    db.refresh(msg)
    
    # Auto-activate session on first mentor reply
    if session.status == MentorshipStatus.PENDING:
        session.status = MentorshipStatus.ACTIVE
        db.commit()
    
    return msg


def user_reply(
    db: Session,
    session_id: int,
    user_id: int,
    message: str
) -> MentorshipMessage:
    """User sends reply (strict filtering)"""
    
    session = _get_user_session(db, session_id, user_id, allow_mentor=False)
    
    if session.status == MentorshipStatus.CLOSED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Session is closed"
        )
    
    # Strict content check (no links, shorter max length)
    if any(word in message.lower() for word in ['http', 'www', '.com', '.in']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Links not allowed"
        )
    
    is_safe, reason = is_content_safe(message)
    if not is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Message rejected: {reason}"
        )
    
    msg = MentorshipMessage(
        session_id=session_id,
        sender_id=user_id,
        role=MessageRole.USER,
        message=message.strip()[:500],  # Strict length limit
        is_filtered=False
    )
    
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


def close_session(
    db: Session,
    session_id: int,
    closer_id: int,
    closer_role: MessageRole
) -> bool:
    """Close session (user/mentor/admin)"""
    
    session = db.query(MentorshipSession).filter(
        MentorshipSession.id == session_id
    ).first()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Auto-close after 7 days inactivity
    if session.status == MentorshipStatus.ACTIVE:
        last_message = db.query(MentorshipMessage).filter(
            MentorshipMessage.session_id == session_id
        ).order_by(MentorshipMessage.created_at.desc()).first()
        
        if last_message and (datetime.utcnow() - last_message.created_at) > timedelta(days=7):
            session.status = MentorshipStatus.CLOSED
            session.closed_at = datetime.utcnow()
            db.commit()
            return True
    
    session.status = MentorshipStatus.CLOSED
    session.closed_at = datetime.utcnow()
    db.commit()
    return True


def get_user_sessions(
    db: Session,
    user_id: int
) -> List[MentorshipSessionResponse]:
    """Get all sessions for user"""
    
    sessions = db.query(MentorshipSession).filter(
        MentorshipSession.user_id == user_id
    ).order_by(MentorshipSession.created_at.desc()).all()
    
    result = []
    for session in sessions:
        mentor = db.query(Mentor).filter(Mentor.id == session.mentor_id).first()
        messages = db.query(MentorshipMessage).filter(
            MentorshipMessage.session_id == session.id
        ).order_by(MentorshipMessage.created_at).all()
        
        result.append(MentorshipSessionResponse(
            id=session.id,
            user_id=session.user_id,
            mentor_id=session.mentor_id,
            mentor_name=mentor.name if mentor else "Unknown",
            topic=session.topic,
            status=session.status,
            created_at=session.created_at,
            messages=[MentorshipMessage(
                id=msg.id,
                sender_id=msg.sender_id,
                role=msg.role,
                message=msg.message,
                created_at=msg.created_at
            ) for msg in messages]
        ))
    
    return result


# Helper functions
def _get_mentor_role_for_topic(topic: MentorshipTopic) -> MentorRole:
    # Convert schema enum to model enum by value
    topic_value = topic.value
    mapping = {
        "legal_advice": MentorRole.LAWYER,
        "reporting_guidance": MentorRole.LAWYER,
        "safety_planning": MentorRole.NGO,
        "emotional_support": MentorRole.PSYCHOLOGIST
    }
    return mapping.get(topic_value, MentorRole.NGO)


def _get_user_session(db: Session, session_id: int, user_id: int, allow_mentor: bool = False):
    session = db.query(MentorshipSession).filter(MentorshipSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.user_id != user_id and (allow_mentor and session.mentor_id != user_id):
        raise HTTPException(status_code=403, detail="Unauthorized")
    
    return session
