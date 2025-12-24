from pydantic import BaseModel, Field
from typing import Optional,Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from models.user import User

class LocationUpdate(BaseModel):
    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")

class LocationResponse(BaseModel):
    user_id: int = Field(..., description="ID of the user")
    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")

    class Config:
        from_attributes = True