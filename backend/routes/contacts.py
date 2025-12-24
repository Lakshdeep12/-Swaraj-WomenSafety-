from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated, List
from app.database import SessionLocal
from schemas.contact import ContactCreate, ContactResponse
from services.contacts_services import create_contact, get_contacts_by_user
from routes.auth import get_current_user
from models.user import User

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]

@router.post("/contacts", response_model=ContactResponse)
async def add_contact(
    contact: ContactCreate,
    db: db_dependency,
    current_user: user_dependency
):
    """
    Add a new emergency contact for the authenticated user.
    The user_id is derived from the JWT token.
    """
    try:
        db_contact = create_contact(db, contact, current_user.id)
        return db_contact
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to create contact: {str(e)}")

@router.get("/contacts", response_model=List[ContactResponse])
async def get_contacts(
    db: db_dependency,
    current_user: user_dependency
):
    """
    Get all emergency contacts for the authenticated user.
    The user_id is derived from the JWT token.
    """
    try:
        contacts = get_contacts_by_user(db, current_user.id)
        return contacts
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to retrieve contacts: {str(e)}")