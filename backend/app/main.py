from fastapi import FastAPI
import uvicorn
from app.database import engine, SessionLocal, Base
from typing import Annotated
from sqlalchemy.orm import Session
from routes.auth import router as auth_router
from routes.contacts import router as contacts_router
from routes.location import router as location_router
from routes.sos import router as sos_router
from routes.awareness import router as awareness_router
from routes.reactions import router as reactions_router
from fastapi import Depends, HTTPException, status
from routes.auth import get_current_user
from models.user import User
from fastapi import WebSocket
from websocket.location_ws import location_websocket_endpoint
from websocket.contacts_ws import contacts_websocket_endpoint
from websocket.sos_ws import sos_websocket_endpoint
from websocket.admin_ws import admin_websocket_endpoint
from routes import mentorship

app = FastAPI()
Base.metadata.create_all(bind=engine)


app.include_router(mentorship.router)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[User, Depends(get_current_user)]

app.include_router(auth_router)
app.include_router(contacts_router, prefix="/api", tags=["Contacts"])
app.include_router(location_router)
app.include_router(sos_router)
app.include_router(awareness_router)
app.include_router(reactions_router)

@app.get("/", status_code=status.HTTP_200_OK, tags=["Default"])
async def user(user: user_dependency, db: db_dependency):
    print("Request to /")
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized Access")
    return {"user": user}

@app.websocket("/ws/location/{user_id}")
async def ws_location(websocket: WebSocket, user_id: int):
    await location_websocket_endpoint(websocket, user_id)

@app.websocket("/ws/contacts/{user_id}")
async def ws_contacts(websocket: WebSocket, user_id: int):
    await contacts_websocket_endpoint(websocket, user_id)

@app.websocket("/ws/sos")
async def ws_sos(websocket: WebSocket):
    await sos_websocket_endpoint(websocket)

@app.websocket("/ws/admin")
async def ws_admin(websocket: WebSocket):
    await admin_websocket_endpoint(websocket)



if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)