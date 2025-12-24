from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, status
from models.sos import SOSEvent
from models.user import User
from models.contact import Contact
from services.location_services import upsert_live_location, get_live_location
from routes.auth import get_db, get_current_user


# Create SOS event
def trigger_sos(db: Session, user: User):

    # Fetch user's live location
    location = get_live_location(db, user.id)
    if not location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Live location not found")
    
    # Fetch user's emergency contacts
    contacts = db.query(Contact).filter(Contact.user_id == user.id).all()
    if not contacts:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No emergency contacts found")
    
    # Create SOS event
    sos_event = SOSEvent(
        user_id=user.id,
        latitude=location.latitude,
        longitude=location.longitude
    )
    db.add(sos_event)
    db.commit()
    db.refresh(sos_event)
    
    return contacts, location