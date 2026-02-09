from fastapi import FastAPI, WebSocket, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import (
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
    get_redoc_html,
)
from typing import Annotated
from sqlalchemy.orm import Session
import uvicorn
import logging

# Core imports
from core.config import get_settings
from core.logging_config import app_logger, get_logger
from core.exception_handlers import register_exception_handlers, ExceptionHandlerMiddleware
from core.response import create_response, ResponseStatus
from core.security import SecurityHeaders
from app.database import engine, SessionLocal, Base
from app.dependencies import get_db, db_dependency
from routes.auth import router as auth_router, get_current_user
from routes.contacts import router as contacts_router
from routes.location import router as location_router
from routes.sos import router as sos_router
from routes.awareness import router as awareness_router
from routes.reactions import router as reactions_router
from routes import mentorship
from routes.health import router as health_router
# from routes.ml import router as ml_router  # TODO: Fix model dependencies
from models.user import User
from websocket.location_ws import location_websocket_endpoint
from websocket.contacts_ws import contacts_websocket_endpoint
from websocket.sos_ws import sos_websocket_endpoint
from websocket.admin_ws import admin_websocket_endpoint
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


settings = get_settings()
logger = get_logger(__name__)

# Custom docs configuration to avoid CDN dependencies
app = FastAPI(
    title=settings.APP_NAME,
    description="Production-ready backend for women safety platform with ML integration",
    version=settings.APP_VERSION,
    docs_url=None,  # Disable default docs
    redoc_url=None,  # Disable default redoc
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

Base.metadata.create_all(bind=engine)

# app.add_middleware(ExceptionHandlerMiddleware)  # TODO: Fix exception handler

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["localhost", "127.0.0.1", "*.asha-alita.com"],
)

register_exception_handlers(app)


# ============================================================================
# CUSTOM DOCUMENTATION ROUTES
# ============================================================================

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """Custom Swagger UI endpoint with CDN"""
    return get_swagger_ui_html(
        title=f"{settings.APP_NAME} - Swagger UI",
        openapi_url="/openapi.json",
    )


@app.get("/docs/oauth2-redirect", include_in_schema=False)
async def swagger_ui_redirect():
    """OAuth2 redirect for Swagger UI"""
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    """ReDoc documentation endpoint"""
    return get_redoc_html(
        title=f"{settings.APP_NAME} - ReDoc",
        openapi_url="/openapi.json",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@latest/bundles/redoc.standalone.js",
    )


user_dependency = Annotated[User, Depends(get_current_user)]

@app.on_event("startup")
async def startup_event():
    """Application startup event"""
    app_logger.info(
        f"Starting {settings.APP_NAME}",
        extra={
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
        },
    )
    # ML services initialization disabled - models need fixing
    # if settings.ENABLE_ML_STRESS_DETECTION:
    #     try:
    #         from services.ml_stress_detection import get_stress_detection_service
    #         service = get_stress_detection_service()
    #         app_logger.info("Stress detection service initialized")
    #     except Exception as e:
    #         app_logger.warning(f"Failed to initialize stress detection: {str(e)}")
    
    # if settings.ENABLE_SAFE_ROUTE:
    #     try:
    #         from services.ml_safe_route import get_safe_route_service
    #         service = get_safe_route_service()
    #         app_logger.info("Safe route service initialized")
    #     except Exception as e:
    #         app_logger.warning(f"Failed to initialize safe route service: {str(e)}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event"""
    app_logger.info(f"Shutting down {settings.APP_NAME}")

app.include_router(auth_router)

app.include_router(health_router)

# app.include_router(ml_router)  # TODO: Fix model dependencies

app.include_router(contacts_router, prefix="/api", tags=["Contacts"])
app.include_router(location_router)
app.include_router(sos_router)
app.include_router(awareness_router)
app.include_router(reactions_router)
app.include_router(mentorship.router)

@app.get("/", status_code=status.HTTP_200_OK, tags=["Default"])
async def root(user: user_dependency, db: db_dependency):
    """
    Root endpoint - requires authentication
    
    Returns user information and API documentation links
    """
    if user is None:
        from core.exceptions import UnauthorizedError
        raise UnauthorizedError("Authentication required")
    
    return create_response(
        data={
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role.value,
            },
            "api_version": settings.APP_VERSION,
            "documentation": "/api/docs" if settings.DEBUG else "Contact administrator",
        },
        message=f"Welcome {user.name}",
    )


@app.get("/api/version", tags=["Default"])
async def get_version():
    """Get API version"""
    return {
        "version": settings.APP_VERSION,
        "app_name": settings.APP_NAME,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/ping", tags=["Default"])
async def ping():
    """Simple ping endpoint for testing server availability"""
    return {"status": "pong", "message": "Server is running"}


@app.websocket("/ws/location/{user_id}")
async def ws_location(websocket: WebSocket, user_id: int):
    """WebSocket for real-time location streaming"""
    await location_websocket_endpoint(websocket, user_id)


@app.websocket("/ws/contacts/{user_id}")
async def ws_contacts(websocket: WebSocket, user_id: int):
    """WebSocket for emergency contacts notifications"""
    await contacts_websocket_endpoint(websocket, user_id)


@app.websocket("/ws/sos")
async def ws_sos(websocket: WebSocket):
    """WebSocket for real-time SOS alerts"""
    await sos_websocket_endpoint(websocket)


@app.websocket("/ws/admin")
async def ws_admin(websocket: WebSocket):
    """WebSocket for admin monitoring dashboard"""
    await admin_websocket_endpoint(websocket)


# ============================================================================
# RESPONSE MIDDLEWARE
# ============================================================================

@app.middleware("http")
async def add_security_headers(request, call_next):
    """Add security headers to all responses"""
    response = await call_next(request)
    response = SecurityHeaders.add_security_headers(response)
    return response
if __name__ == "__main__":
    app_logger.info(
        f"Starting Alita Backend",
        extra={
            "host": settings.SERVER_HOST,
            "port": settings.SERVER_PORT,
            "environment": settings.ENVIRONMENT,
        },
    )
    
    uvicorn.run(
        app,
        host=settings.SERVER_HOST,
        port=settings.SERVER_PORT,
        reload=settings.RELOAD,
        log_level=settings.LOG_LEVEL.lower(),
    )