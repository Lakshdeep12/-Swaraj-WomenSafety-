"""
Standardized API Response Models
Global response format for all endpoints
"""
from typing import TypeVar, Generic, Optional, Any, List
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum

T = TypeVar('T')


class ResponseStatus(str, Enum):
    """Standard response statuses"""
    SUCCESS = "success"
    ERROR = "error"
    WARNING = "warning"
    PENDING = "pending"


class APIResponse(BaseModel, Generic[T]):
    """
    Standard API response wrapper
    All endpoints return this format for consistency
    """
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str
    data: Optional[T] = None
    meta: Optional[dict] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    error_code: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Operation completed successfully",
                "data": {},
                "meta": {"version": "1.0.0"},
                "timestamp": "2024-01-24T10:30:00Z",
                "request_id": "req_12345",
                "error_code": None
            }
        }
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Paginated response wrapper"""
    status: ResponseStatus = ResponseStatus.SUCCESS
    message: str
    data: List[T]
    pagination: dict = Field(
        default_factory=lambda: {
            "total": 0,
            "page": 1,
            "page_size": 10,
            "total_pages": 0
        }
    )
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "success",
                "message": "Data retrieved successfully",
                "data": [],
                "pagination": {
                    "total": 100,
                    "page": 1,
                    "page_size": 10,
                    "total_pages": 10
                },
                "timestamp": "2024-01-24T10:30:00Z"
            }
        }
    )


class ErrorDetail(BaseModel):
    """Detailed error information"""
    field: Optional[str] = None
    message: str
    error_code: str


class ErrorResponse(BaseModel):
    """Detailed error response"""
    status: ResponseStatus = ResponseStatus.ERROR
    message: str
    error_code: str
    details: Optional[List[ErrorDetail]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    request_id: Optional[str] = None
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "error",
                "message": "Validation failed",
                "error_code": "VALIDATION_ERROR",
                "details": [
                    {
                        "field": "email",
                        "message": "Invalid email format",
                        "error_code": "INVALID_EMAIL"
                    }
                ],
                "timestamp": "2024-01-24T10:30:00Z",
                "request_id": "req_12345"
            }
        }
    )


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    version: str
    environment: str
    database: str = "connected"
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    uptime_seconds: float = 0
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "status": "healthy",
                "version": "1.0.0",
                "environment": "production",
                "database": "connected",
                "timestamp": "2024-01-24T10:30:00Z",
                "uptime_seconds": 3600.5
            }
        }
    )


def create_response(
    data: Optional[T] = None,
    message: str = "Operation successful",
    status: ResponseStatus = ResponseStatus.SUCCESS,
    meta: Optional[dict] = None,
    error_code: Optional[str] = None,
    request_id: Optional[str] = None,
) -> APIResponse[T]:
    """Helper function to create standardized API response"""
    return APIResponse(
        status=status,
        message=message,
        data=data,
        meta=meta,
        error_code=error_code,
        request_id=request_id,
    )


def create_error_response(
    message: str,
    error_code: str,
    details: Optional[List[ErrorDetail]] = None,
    request_id: Optional[str] = None,
) -> ErrorResponse:
    """Helper function to create standardized error response"""
    return ErrorResponse(
        message=message,
        error_code=error_code,
        details=details,
        request_id=request_id,
    )


def create_paginated_response(
    data: List[T],
    total: int,
    page: int,
    page_size: int,
    message: str = "Data retrieved successfully",
) -> PaginatedResponse[T]:
    """Helper function to create paginated response"""
    total_pages = (total + page_size - 1) // page_size
    return PaginatedResponse(
        status=ResponseStatus.SUCCESS,
        message=message,
        data=data,
        pagination={
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": total_pages
        }
    )
