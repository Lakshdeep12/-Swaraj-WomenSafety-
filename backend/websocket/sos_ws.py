from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from typing import Annotated
from .manager import manager
from routes.auth import get_db, SECRET_KEY, ALGORITHM
from models.user import User
from sqlalchemy.orm import Session
from jose import JWTError, jwt
import logging
import json

logger = logging.getLogger(__name__)

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

async def sos_websocket_endpoint(websocket: WebSocket):
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
    
    # For now, allow any authenticated user as SOS responder
    # In a real app, check if user has SOS responder role
    group = "sos_responders"
    await manager.connect(websocket, group)
    logger.info(f"User {user.username} connected to SOS WS as {group}")

    # Send all last known locations
    await manager.send_last_locations_to_client(websocket)

    try:
        while True:
            try:
                data = await websocket.receive_json()
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for user {user.username}: {e}")
                await websocket.close(code=1003, reason="Invalid JSON")
                manager.disconnect(websocket, group)
                return
            except Exception as e:
                logger.error(f"Unexpected error in receive for user {user.username}: {e}")
                await websocket.close(code=1011, reason="Internal server error")
                manager.disconnect(websocket, group)
                return
            await websocket.send_json({"status": "connected"})
    except WebSocketDisconnect:
        logger.info(f"User {user.username} disconnected from SOS WS")
        manager.disconnect(websocket, group)
    finally:
        db.close()