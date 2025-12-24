from pydantic import BaseModel, EmailStr
from typing import Optional, Annotated

class ContactCreate(BaseModel):
    name: str
    email: EmailStr
    phone_number: str
    relation: str | None = None
    message: str

class ContactResponse(BaseModel):
    id: int
    user_id: int
    name: str
    email: EmailStr
    phone_number: str
    relation: Optional[str] = None
    message: str

    class Config:
        from_attributes = True