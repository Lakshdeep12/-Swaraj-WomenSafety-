"""
Centralized dependency injection module
Avoids circular imports by defining all dependencies here
"""
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import Depends
from app.database import SessionLocal


def get_db():
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
