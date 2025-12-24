from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship, Session
from datetime import datetime, timedelta
from models.location import LiveLocation

def upsert_live_location(db: Session, user_id: int, latitude: float, longitude: float):
    location = db.query(LiveLocation).filter(LiveLocation.user_id == user_id).first()
    if location:
        location.latitude = latitude
        location.longitude = longitude
        location.update_at = datetime.utcnow() + timedelta(hours=5, minutes=30)
    else:
        location = LiveLocation(
            user_id=user_id,
            latitude=latitude,
            longitude=longitude,
            update_at=datetime.utcnow() + timedelta(hours=5, minutes=30)
        )
        db.add(location)
    db.commit()
    db.refresh(location)
    return location

def get_live_location(db: Session, user_id: int):  
    return db.query(LiveLocation).filter(LiveLocation.user_id == user_id).first()