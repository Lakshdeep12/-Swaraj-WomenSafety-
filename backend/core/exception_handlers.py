"""
Centralized Exception Handler Middleware
Catches all exceptions and returns standardized responses
"""
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from typing import Union
from uuid import uuid4
import logging
import time

from core.exceptions import AshaPlatformException, ErrorCode
from core.response import ErrorResponse, ErrorDetail
from core.logging_config import get_logger

logger = get_logger(__name__)


class ExceptionHandlerMiddleware:
    """Middleware to handle exceptions globally"""
    
    def __init__(self, app: FastAPI):
        self.app = app
    
    async def __call__(self, request: Request, call_next):
        request_id = str(uuid4())
        request.state.request_id = request_id
        
        start_time = time.time()
        
        try:
            response = await call_next(request)
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id
            return response
        except Exception as exc:
            process_time = time.time() - start_time
            return await handle_exception(request, exc, request_id, process_time)


async def handle_exception(
    request: Request,
    exc: Exception,
    request_id: str,
    process_time: float,
) -> JSONResponse:
    """Handle exception and return standardized response"""
    
    # Log the exception
    logger.error(
        f"Exception occurred",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "exception_type": type(exc).__name__,
            "exception_message": str(exc),
            "process_time": process_time,
        },
        exc_info=True,
    )
    
    # Handle custom AshaPlatformException
    if isinstance(exc, AshaPlatformException):
        error_response = ErrorResponse(
            message=exc.message,
            error_code=exc.error_code.value,
            details=exc.details if isinstance(exc.details, list) else None,
            request_id=request_id,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(exclude_none=True),
        )
    
    # Handle validation errors
    if isinstance(exc, RequestValidationError):
        details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", [])[1:])
            details.append(
                ErrorDetail(
                    field=field or None,
                    message=error.get("msg", "Validation error"),
                    error_code="VALIDATION_ERROR",
                )
            )
        error_response = ErrorResponse(
            message="Request validation failed",
            error_code=ErrorCode.VALIDATION_ERROR.value,
            details=details,
            request_id=request_id,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump(exclude_none=True),
        )
    
    # Handle generic exceptions
    error_response = ErrorResponse(
        message="An unexpected error occurred",
        error_code=ErrorCode.INTERNAL_SERVER_ERROR.value,
        request_id=request_id,
    )
    
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response.model_dump(exclude_none=True),
    )


def register_exception_handlers(app: FastAPI):
    """Register all exception handlers"""
    
    @app.exception_handler(AshaPlatformException)
    async def asha_platform_exception_handler(request: Request, exc: AshaPlatformException):
        request_id = getattr(request.state, "request_id", str(uuid4()))
        logger.warning(
            f"AshaPlatformException: {exc.error_code}",
            extra={
                "request_id": request_id,
                "error_code": exc.error_code,
                "message": exc.message,
            },
        )
        error_response = ErrorResponse(
            message=exc.message,
            error_code=exc.error_code.value,
            details=exc.details if isinstance(exc.details, list) else None,
            request_id=request_id,
        )
        return JSONResponse(
            status_code=exc.status_code,
            content=error_response.model_dump(exclude_none=True),
        )
    
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        request_id = getattr(request.state, "request_id", str(uuid4()))
        details = []
        for error in exc.errors():
            field = ".".join(str(loc) for loc in error.get("loc", [])[1:])
            details.append(
                ErrorDetail(
                    field=field or None,
                    message=error.get("msg", "Validation error"),
                    error_code="VALIDATION_ERROR",
                )
            )
        error_response = ErrorResponse(
            message="Request validation failed",
            error_code=ErrorCode.VALIDATION_ERROR.value,
            details=details,
            request_id=request_id,
        )
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content=error_response.model_dump(exclude_none=True),
        )
    
    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        request_id = getattr(request.state, "request_id", str(uuid4()))
        logger.critical(
            f"Unhandled exception: {type(exc).__name__}",
            extra={
                "request_id": request_id,
                "exception": str(exc),
            },
            exc_info=True,
        )
        error_response = ErrorResponse(
            message="An unexpected error occurred",
            error_code=ErrorCode.INTERNAL_SERVER_ERROR.value,
            request_id=request_id,
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=error_response.model_dump(exclude_none=True),
        )
