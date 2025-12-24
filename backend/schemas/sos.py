from pydantic import BaseModel, Field
from typing import Optional,Annotated
from fastapi import Depends
from sqlalchemy.orm import Session
from models.user import User

class SOSResponse(BaseModel):
    name: str = Field(..., description="Name of the user sending SOS")
    phone: str = Field(..., description="Phone number of the user sending SOS")
    status: str = Field(..., description="Status of the SOS request")
    message: str = Field(..., description="Additional message regarding the SOS request")
    latitude: float = Field(..., description="Latitude of the SOS location")
    longitude: float = Field(..., description="Longitude of the SOS location")

    class Config:
        from_attributes = True