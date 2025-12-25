from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum
from schemas.reaction import ReactionSummary


class AwarenessCategory(str, Enum):
    crime = "crime"
    law = "law"
    guideline = "guideline"


class AwarenessSource(str, Enum):
    ngo = "NGO"
    govt = "Govt"
    admin = "Admin"


class AwarenessBase(BaseModel):
    title: str = Field(..., max_length=255)
    content: str = Field(..., max_length=5000)
    category: AwarenessCategory
    source: AwarenessSource


class AwarenessCreate(AwarenessBase):
    pass


class AwarenessResponse(AwarenessBase):
    id: int
    created_at: datetime
    reactions: ReactionSummary

    class Config:
        from_attributes = True


class AwarenessFeedResponse(BaseModel):
    posts: List[AwarenessResponse]
    total: int
    page: int
    page_size: int
    has_next: bool


class AwarenessFeedFilter(BaseModel):
    category: Optional[AwarenessCategory] = None
    page: int = 1
    page_size: int = 10
