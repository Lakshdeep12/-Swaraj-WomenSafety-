from typing import List
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class MentorshipTopic(str, Enum):
    LEGAL_ADVICE = "legal_advice"
    EMOTIONAL_SUPPORT = "emotional_support"
    SAFETY_PLANNING = "safety_planning"
    REPORTING_GUIDANCE = "reporting_guidance"


class MentorshipStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    CLOSED = "closed"


class MessageRole(str, Enum):
    user = "user"
    mentor = "mentor"


class MentorshipMessage(BaseModel):
    id: int
    sender_id: int
    role: MessageRole
    message: str
    created_at: datetime


class MentorshipSessionBase(BaseModel):
    topic: MentorshipTopic


class MentorshipMessageCreate(BaseModel):
    message: str = Field(..., max_length=1000)


class MentorshipSessionResponse(BaseModel):
    id: int
    user_id: int
    mentor_id: int
    mentor_name: str
    topic: MentorshipTopic
    status: MentorshipStatus
    created_at: datetime
    messages: List[MentorshipMessage] = []


class UserSessionsResponse(BaseModel):
    sessions: List[MentorshipSessionResponse]
    total: int
    active_count: int
