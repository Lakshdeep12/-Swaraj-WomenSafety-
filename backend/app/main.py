from fastapi import FastAPI
import uvicorn
from app.database import engine, SessionLocal, Base
from typing import Annotated
from sqlalchemy.orm import Session
from routes.auth import router as auth_router
from routes.contacts import router as contacts_router
from routes.location import router as location_router
from routes.sos import router as sos_router
from fastapi import Depends, HTTPException, status
from routes.auth import get_current_user
from models.user import User

app = FastAPI()
Base.metadata.create_all(bind=engine)

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

@app.get("/", status_code=status.HTTP_200_OK, tags=["Default"])
async def user(user: user_dependency, db: db_dependency):
    print("Request to /")
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Unauthorized Access")
    return {"user": user}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)