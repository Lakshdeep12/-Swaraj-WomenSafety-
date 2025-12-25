from typing import Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum


# Fixed emoji whitelist
class AllowedEmoji(str, Enum):
    JUSTICE = "⚖️"
    CANDLE = "🕯️"
    HANDSHAKE = "🤝"
    ANGRY = "😡"
    HEART = "🤍"
    BOOK = "📘"


EMOJI_MAP = {
    "justice": AllowedEmoji.JUSTICE,
    "candle": AllowedEmoji.CANDLE,
    "handshake": AllowedEmoji.HANDSHAKE,
    "angry": AllowedEmoji.ANGRY,
    "heart": AllowedEmoji.HEART,
    "book": AllowedEmoji.BOOK
}


class ReactionCreate(BaseModel):
    emoji: AllowedEmoji
    
    @validator('emoji')
    def validate_emoji(cls, v):
        if v not in AllowedEmoji:
            raise ValueError(f"Emoji must be one of: {list(AllowedEmoji)}")
        return v


class ReactionResponse(BaseModel):
    id: int
    user_id: int
    awareness_id: int
    emoji: AllowedEmoji
    created_at: str


class ReactionSummary(BaseModel):
    total_reactions: int
    emoji_counts: Dict[str, int]
    user_has_reacted: bool = False
    users_reacted: int


ReactionResponse.model_config = {"from_attributes": True}
ReactionSummary.model_config = {"from_attributes": True}
ReactionCreate.model_config = {"use_enum_values": True}