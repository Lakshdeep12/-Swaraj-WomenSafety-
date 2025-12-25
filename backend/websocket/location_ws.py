from fastapi import WebSocket, WebSocketDisconnect, WebSocketException, HTTPException
from typing import Annotated
from .manager import manager
from services.location_services import upsert_live_location
from routes.auth import get_db, SECRET_KEY, ALGORITHM
from models.user import User
from models.contact import Contact
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from datetime import datetime, timedelta
import logging
import math
from pydantic import ValidationError
from schemas.location import LocationUpdate
import json

logger = logging.getLogger(__name__)

last_location = {}

def haversine_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

async def get_current_user_from_token(token: str, db: Session):
    credentials_exception = HTTPException(
        status_code=401,
        detail="Could not validate credentials",
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("user_id")
        if username is None or user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = db.query(User).filter(User.email == username).first()
    if user is None:
        raise credentials_exception
    return user

async def location_websocket_endpoint(websocket: WebSocket, user_id: int):
    # Extract token from Authorization header or query parameters
    token = None
    auth_header = websocket.headers.get("Authorization")
    if auth_header and auth_header.startswith("Bearer "):
        token = auth_header[7:]
    if not token:
        token = websocket.query_params.get("token")
    
    if not token:
        await websocket.close(code=1008, reason="No token provided")
        return
    
    db = next(get_db())
    try:
        user = await get_current_user_from_token(token, db)
    except HTTPException:
        await websocket.close(code=1008, reason="Invalid token")
        return
    
    if user.id != user_id:
        await websocket.close(code=1008, reason="User ID mismatch")
        return

    group = f"user:{user_id}"
    await manager.connect(websocket, group)
    logger.info(f"User {user.username} connected to location WS as {group}")

    try:
        while True:
            try:
                data = await websocket.receive_json()
                location_update = LocationUpdate(**data)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for user {user.username}: {e}")
                await websocket.close(code=1003, reason="Invalid JSON")
                manager.disconnect(websocket, group)
                return
            except ValidationError as e:
                logger.error(f"Validation error for user {user.username}: {e}")
                await websocket.close(code=1003, reason="Invalid data")
                manager.disconnect(websocket, group)
                return
            except Exception as e:
                logger.error(f"Unexpected error in receive for user {user.username}: {e}")
                await websocket.close(code=1011, reason="Internal server error")
                manager.disconnect(websocket, group)
                return

            latitude = location_update.latitude
            longitude = location_update.longitude
            timestamp = location_update.timestamp or datetime.utcnow().isoformat()

            # Check if location has changed significantly (more than 10 meters) or time elapsed
            user_id = user.id
            current_time = datetime.utcnow()
            if user_id in last_location:
                last_lat, last_lon, last_time = last_location[user_id]
                distance = haversine_distance(last_lat, last_lon, latitude, longitude)
                time_diff = (current_time - last_time).total_seconds()
                if distance < 0.01 and time_diff < 30:  # 10 meters, 30 seconds
                    continue  # Skip update

            last_location[user_id] = (latitude, longitude, current_time)

            # Store the location data
            location = upsert_live_location(db, user.id, latitude, longitude)
            logger.info(f"Updated location for user {user.id}: {latitude}, {longitude}")

            # Update last known location cache
            manager.update_last_location(user.id, {"latitude": latitude, "longitude": longitude, "timestamp": timestamp})

            # Broadcast to emergency contacts, SOS responders, and admin dashboard
            message = {
                "type": "location_update",
                "user_id": user.id,
                "username": user.username,
                "latitude": latitude,
                "longitude": longitude,
                "timestamp": timestamp
            }
            await manager.broadcast_to_group(message, f"emergency_contacts:{user.id}")
            await manager.broadcast_to_group(message, "sos_responders")
            await manager.broadcast_to_group(message, "admin_dashboard")

    except WebSocketDisconnect:
        logger.info(f"User {user.username} disconnected from location WS")
        manager.disconnect(websocket, group)
    except Exception as e:
        logger.error(f"Error in WS for user {user.username}: {e}")
        await websocket.close(code=1011, reason="Internal server error")
        manager.disconnect(websocket, group)
    finally:
        db.close()