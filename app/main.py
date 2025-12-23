from fastapi import FastAPI
import uvicorn
from app.database import engine, SessionLocal, Base
from typing import Annotated
from sqlalchemy.orm import Session
from routes.auth import router as auth_router
from fastapi import Depends, HTTPException, status
from routes.auth import get_current_user


app = FastAPI()
Base.metadata.create_all(bind=engine)
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]

app.include_router(auth_router)


@app.get("/",status_code=status.HTTP_200_OK)
async def user(user:user_dependency ,db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Unauthorized Access")
    return {"user": user}