from fastapi import WebSocket
from typing import List, Dict, Set
from fastapi import Depends
from models.user import User
from routes.auth import get_current_user
from sqlalchemy.orm import Session
from models.contact import Contact

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}  # group to list of websockets
        self.last_known_locations: Dict[int, dict] = {}  # user_id to location dict

    async def connect(self, websocket: WebSocket, group: str):
        await websocket.accept()
        if group not in self.active_connections:
            self.active_connections[group] = []
        self.active_connections[group].append(websocket)

    def disconnect(self, websocket: WebSocket, group: str):
        if group in self.active_connections:
            self.active_connections[group].remove(websocket)
            if not self.active_connections[group]:
                del self.active_connections[group]

    async def broadcast_to_group(self, message: dict, group: str):
        if group in self.active_connections:
            for connection in self.active_connections[group]:
                await connection.send_json(message)

    def update_last_location(self, user_id: int, location: dict):
        self.last_known_locations[user_id] = location

    async def send_last_locations_to_client(self, websocket: WebSocket, user_id: int = None):
        if user_id:
            if user_id in self.last_known_locations:
                loc = self.last_known_locations[user_id]
                await websocket.send_json({"type": "last_known_location", "user_id": user_id, **loc})
        else:
            for uid, loc in self.last_known_locations.items():
                await websocket.send_json({"type": "last_known_location", "user_id": uid, **loc})

manager = ConnectionManager()