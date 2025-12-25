from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from fastapi import HTTPException, status

from models.awareness import Awareness, AwarenessCategory
from schemas.awareness import (
    AwarenessCreate, 
    AwarenessResponse, 
    AwarenessFeedResponse,
    AwarenessFeedFilter
)
from utils.content_filter import is_content_safe
from services.reaction import get_reaction_summary


def create_awareness_post(
    db: Session, 
    awareness_data: AwarenessCreate
) -> AwarenessResponse:
    """Create verified awareness post (Admin/NGO only)"""
    
    # Safety check
    is_safe, reason = is_content_safe(awareness_data.content)
    if not is_safe:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Content rejected: {reason}"
        )
    
    # Create post
    post = Awareness(
        title=awareness_data.title.strip(),
        content=awareness_data.content.strip(),
        category=awareness_data.category,
        source=awareness_data.source,
        is_verified=True
    )
    
    db.add(post)
    db.commit()
    db.refresh(post)
    
    return AwarenessResponse.model_validate(post)


def get_awareness_feed(
    db: Session,
    category: Optional[AwarenessCategory] = None,
    page: int = 1,
    page_size: int = 10
) -> AwarenessFeedResponse:
    """Public paginated feed"""
    
    query = db.query(Awareness).filter(Awareness.is_verified.is_(True))
    
    if category:
        query = query.filter(Awareness.category == category)
    
    # Count total
    total = query.count()
    
    # Paginated results
    posts = query.order_by(desc(Awareness.created_at)) \
                .offset((page - 1) * page_size) \
                .limit(page_size).all()
    
    response_posts = []
    for post in posts:
        reactions = get_reaction_summary(db, post.id, None)
        post_response = AwarenessResponse.model_validate(post)
        post_response.reactions = reactions
        response_posts.append(post_response)
    
    return AwarenessFeedResponse(
        posts=response_posts,
        total=total,
        page=page,
        page_size=page_size,
        has_next=(len(posts) == page_size)
    )


def get_awareness_by_id(
    db: Session, 
    post_id: int
) -> AwarenessResponse:
    """Get single verified post"""
    
    post = db.query(Awareness) \
            .filter(Awareness.id == post_id, 
                   Awareness.is_verified.is_(True)) \
            .first()
    
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    reactions = get_reaction_summary(db, post.id, None)
    response = AwarenessResponse.model_validate(post)
    response.reactions = reactions
    return response
