from typing import List
from pydantic import BaseModel
from enum import Enum
from datetime import datetime


class MentorRole(str, Enum):
    NGO = "NGO"
    LAWYER = "Lawyer"
    PSYCHOLOGIST = "Psychologist"


class MentorBase(BaseModel):
    name: str
    role: MentorRole


class MentorCreate(MentorBase):
    pass


class MentorResponse(MentorBase):
    id: int
    verified: bool
    active_status: bool
    created_at: datetime
    active_sessions: int = 0

    class Config:
        from_attributes = True
