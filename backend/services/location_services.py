from sqlalchemy import Column, Float, ForeignKey, Integer
from sqlalchemy.orm import relationship, Session
from datetime import datetime, timedelta
from models.location import LiveLocation
from app.database import SessionLocal


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

async def save_live_location(user_id: int, data: dict):
    print(f"[TRACKING] User {user_id}: {data}")
    # Here you can implement saving to the database if needed