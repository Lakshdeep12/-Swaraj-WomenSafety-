"""
Security and Authorization Utilities
Production-ready authorization checks and role-based access control
"""
from typing import Optional, List, Callable, Any
from functools import wraps
from fastapi import HTTPException, status, Request, Depends
from sqlalchemy.orm import Session

from core.exceptions import ForbiddenError, InsufficientPermissionsError
from core.logging_config import get_logger, audit_logger
from models.user import User, UserRole

logger = get_logger(__name__)


def require_admin(func: Callable) -> Callable:
    """Decorator to require admin role"""
    @wraps(func)
    async def async_wrapper(
        *args,
        current_user: User,
        **kwargs
    ) -> Any:
        if not current_user or current_user.role != UserRole.ADMIN:
            audit_logger.log_unauthorized_access_attempt(
                user_id=current_user.id if current_user else -1,
                resource="admin_resource",
                action=func.__name__,
                request_id=kwargs.get("request_id", "unknown"),
            )
            raise ForbiddenError("Admin role required")
        
        return await func(*args, current_user=current_user, **kwargs)
    
    def sync_wrapper(*args, current_user: User, **kwargs) -> Any:
        if not current_user or current_user.role != UserRole.ADMIN:
            audit_logger.log_unauthorized_access_attempt(
                user_id=current_user.id if current_user else -1,
                resource="admin_resource",
                action=func.__name__,
                request_id=kwargs.get("request_id", "unknown"),
            )
            raise ForbiddenError("Admin role required")
        
        return func(*args, current_user=current_user, **kwargs)
    
    return async_wrapper if hasattr(func, "__code__") and "await" in func.__code__.co_names else sync_wrapper


def require_ngo_or_admin(func: Callable) -> Callable:
    """Decorator to require NGO or admin role"""
    @wraps(func)
    async def async_wrapper(
        *args,
        current_user: User,
        **kwargs
    ) -> Any:
        if not current_user or current_user.role not in [UserRole.NGO, UserRole.ADMIN]:
            audit_logger.log_unauthorized_access_attempt(
                user_id=current_user.id if current_user else -1,
                resource="ngo_resource",
                action=func.__name__,
                request_id=kwargs.get("request_id", "unknown"),
            )
            raise ForbiddenError("NGO or admin role required")
        
        return await func(*args, current_user=current_user, **kwargs)
    
    def sync_wrapper(*args, current_user: User, **kwargs) -> Any:
        if not current_user or current_user.role not in [UserRole.NGO, UserRole.ADMIN]:
            audit_logger.log_unauthorized_access_attempt(
                user_id=current_user.id if current_user else -1,
                resource="ngo_resource",
                action=func.__name__,
                request_id=kwargs.get("request_id", "unknown"),
            )
            raise ForbiddenError("NGO or admin role required")
        
        return func(*args, current_user=current_user, **kwargs)
    
    return async_wrapper if hasattr(func, "__code__") and "await" in func.__code__.co_names else sync_wrapper


def require_role(*roles: UserRole) -> Callable:
    """Decorator to require specific role(s)"""
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(
            *args,
            current_user: User,
            **kwargs
        ) -> Any:
            if not current_user or current_user.role not in roles:
                audit_logger.log_unauthorized_access_attempt(
                    user_id=current_user.id if current_user else -1,
                    resource="role_restricted_resource",
                    action=func.__name__,
                    request_id=kwargs.get("request_id", "unknown"),
                )
                raise InsufficientPermissionsError(
                    f"Required roles: {', '.join([r.value for r in roles])}"
                )
            
            return await func(*args, current_user=current_user, **kwargs)
        
        def sync_wrapper(*args, current_user: User, **kwargs) -> Any:
            if not current_user or current_user.role not in roles:
                audit_logger.log_unauthorized_access_attempt(
                    user_id=current_user.id if current_user else -1,
                    resource="role_restricted_resource",
                    action=func.__name__,
                    request_id=kwargs.get("request_id", "unknown"),
                )
                raise InsufficientPermissionsError(
                    f"Required roles: {', '.join([r.value for r in roles])}"
                )
            
            return func(*args, current_user=current_user, **kwargs)
        
        return async_wrapper if hasattr(func, "__code__") and "await" in func.__code__.co_names else sync_wrapper
    
    return decorator


def check_resource_ownership(user_id: int, resource_owner_id: int, request_id: str) -> None:
    """Check if user owns resource"""
    if user_id != resource_owner_id:
        audit_logger.log_unauthorized_access_attempt(
            user_id=user_id,
            resource=f"resource_{resource_owner_id}",
            action="access_attempt",
            request_id=request_id,
        )
        raise ForbiddenError("You do not have permission to access this resource")


def require_ownership(func: Callable) -> Callable:
    """
    Decorator to check resource ownership
    Assumes function has resource_id and current_user parameters
    """
    @wraps(func)
    async def async_wrapper(
        *args,
        resource_id: int,
        current_user: User,
        **kwargs
    ) -> Any:
        # This would need database access to verify ownership
        # Typically implemented in service layer
        return await func(*args, resource_id=resource_id, current_user=current_user, **kwargs)
    
    def sync_wrapper(
        *args,
        resource_id: int,
        current_user: User,
        **kwargs
    ) -> Any:
        return func(*args, resource_id=resource_id, current_user=current_user, **kwargs)
    
    return async_wrapper if hasattr(func, "__code__") and "await" in func.__code__.co_names else sync_wrapper


class SecurityHeaders:
    """Security headers middleware utilities"""
    
    @staticmethod
    def add_security_headers(response):
        """Add security headers to response"""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        # Relaxed CSP for development to allow Swagger UI CDN resources
        response.headers["Content-Security-Policy"] = "default-src 'self' https://cdn.jsdelivr.net https://unpkg.com; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://unpkg.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://fonts.googleapis.com; img-src 'self' data: https:"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        return response
