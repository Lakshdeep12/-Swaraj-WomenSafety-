from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime

class LocationUpdate(BaseModel):
    latitude: float = Field(..., ge=-90, le=90, description="Latitude of the location")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude of the location")
    timestamp: Optional[str] = Field(None, description="Timestamp of the location update")

    @field_validator('timestamp')
    @classmethod
    def validate_timestamp(cls, v):
        if v is not None:
            try:
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Invalid timestamp format')
        return v

class LocationResponse(BaseModel):
    user_id: int = Field(..., description="ID of the user")
    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")

    class Config:
        from_attributes = True