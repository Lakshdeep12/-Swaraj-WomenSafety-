from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
# from core.get_db import get_db
# from core.get_current_user import get_current_user
from routes.auth import get_db, get_current_user   
from schemas.location import LocationUpdate, LocationResponse
from services.location_services import upsert_live_location, get_live_location
from services.sos_services import trigger_sos
from services.notification_services import send_location_alerts
from models.user import User
from typing import Annotated

router = APIRouter(prefix="/api/sos", tags=["SOS"])


@router.post("/trigger")
def trigger_sos_alert(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    try:
        contacts, location = trigger_sos(db, current_user)
        
        for contact in contacts:
            send_location_alerts( 
                contact,
                location,
                f"Emergency Alert: {current_user.name} has triggered an SOS alert from location ({location.latitude}, {location.longitude}). Please reach out to them immediately."
                f"Location Link: https://www.google.com/maps?q={location.latitude},{location.longitude}"
            )
        return{
            "status": "success",
            "message": f"SOS alert triggered and notifications sent to {len(contacts)} contacts.",
            "location": f"{location.latitude}, {location.longitude}" 
        }
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))