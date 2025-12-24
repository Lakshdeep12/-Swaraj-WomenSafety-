from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from routes.auth import get_db, get_current_user
from schemas.location import LocationUpdate, LocationResponse
from services.location_services import upsert_live_location, get_live_location
from models.user import User
from typing import Annotated
from fastapi import status

router = APIRouter(prefix="/api/location", tags=["Location"])

@router.post("/update", response_model=dict)
def update_location(
    location_data: LocationUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    location = upsert_live_location(
        db=db,
        user_id=current_user.id,
        latitude=location_data.latitude,
        longitude=location_data.longitude
    )
    return {"message": "Location updated successfully", "location": location}

@router.get("/{user_id}", response_model=LocationResponse)
def fetch_location(
    user_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)]
):
    # Assuming only the user themselves or contacts can fetch, but for now, allow any authenticated user
    location = get_live_location(db=db, user_id=user_id)
    if location is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Location not found")
    return location