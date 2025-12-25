from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status
from typing import List, Dict, Optional
from models.reaction import Reaction
from models.awareness import Awareness
from schemas.reaction import (
    ReactionCreate,
    ReactionResponse,
    ReactionSummary,
    AllowedEmoji
)
from utils.validator import validate_awareness_exists, validate_allowed_emoji


def add_or_update_reaction(
    db: Session,
    user_id: int,
    awareness_id: int,
    emoji: str
) -> ReactionResponse:
    """Add new reaction or update existing one"""

    # Validate post exists
    awareness = validate_awareness_exists(db, awareness_id)
    validate_allowed_emoji(emoji)

    # Check existing reaction
    existing = db.query(Reaction).filter(
        Reaction.user_id == user_id,
        Reaction.awareness_id == awareness_id
    ).first()

    if existing:
        # Update emoji
        existing.emoji = emoji
        db.commit()
        db.refresh(existing)
        return ReactionResponse.model_validate(existing)

    # Create new reaction
    new_reaction = Reaction(
        user_id=user_id,
        awareness_id=awareness_id,
        emoji=emoji
    )

    db.add(new_reaction)
    db.commit()
    db.refresh(new_reaction)

    return ReactionResponse.model_validate(new_reaction)


def remove_reaction(
    db: Session,
    user_id: int,
    awareness_id: int
) -> bool:
    """Remove user's reaction"""

    reaction = db.query(Reaction).filter(
        Reaction.user_id == user_id,
        Reaction.awareness_id == awareness_id
    ).first()

    if not reaction:
        return False

    db.delete(reaction)
    db.commit()
    return True


def get_reaction_summary(
    db: Session,
    awareness_id: int,
    current_user_id: Optional[int] = None
) -> ReactionSummary:
    """Get emoji counts + user reaction status"""

    validate_awareness_exists(db, awareness_id)

    # Get all reactions for this post
    reactions = db.query(Reaction).filter(
        Reaction.awareness_id == awareness_id
    ).all()

    # Count emojis
    emoji_counts = {}
    for reaction in reactions:
        emoji = reaction.emoji
        emoji_counts[emoji] = emoji_counts.get(emoji, 0) + 1

    # Check if current user reacted
    user_has_reacted = False
    if current_user_id:
        user_reaction = db.query(Reaction).filter(
            Reaction.user_id == current_user_id,
            Reaction.awareness_id == awareness_id
        ).first()
        user_has_reacted = bool(user_reaction)

    return ReactionSummary(
        total_reactions=len(reactions),
        emoji_counts=emoji_counts,
        user_has_reacted=user_has_reacted,
        users_reacted=len(reactions)
    )
