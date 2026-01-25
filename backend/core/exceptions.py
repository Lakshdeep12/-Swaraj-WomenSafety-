"""
Centralized Exception Handling
Custom exceptions for the application
"""
from typing import Optional, List, Any
from enum import Enum


class ErrorCode(str, Enum):
    """Standard error codes"""
    # Authentication errors
    AUTHENTICATION_FAILED = "AUTHENTICATION_FAILED"
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    INVALID_TOKEN = "INVALID_TOKEN"
    UNAUTHORIZED = "UNAUTHORIZED"
    
    # Authorization errors
    FORBIDDEN = "FORBIDDEN"
    INSUFFICIENT_PERMISSIONS = "INSUFFICIENT_PERMISSIONS"
    
    # Validation errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    MISSING_REQUIRED_FIELD = "MISSING_REQUIRED_FIELD"
    
    # Resource errors
    NOT_FOUND = "NOT_FOUND"
    RESOURCE_ALREADY_EXISTS = "RESOURCE_ALREADY_EXISTS"
    RESOURCE_CONFLICT = "RESOURCE_CONFLICT"
    
    # Rate limiting
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    TOO_MANY_REQUESTS = "TOO_MANY_REQUESTS"
    SOS_COOLDOWN_ACTIVE = "SOS_COOLDOWN_ACTIVE"
    
    # ML errors
    ML_INFERENCE_ERROR = "ML_INFERENCE_ERROR"
    MODEL_NOT_FOUND = "MODEL_NOT_FOUND"
    INVALID_MODEL_INPUT = "INVALID_MODEL_INPUT"
    ML_SERVICE_UNAVAILABLE = "ML_SERVICE_UNAVAILABLE"
    
    # Location errors
    LOCATION_SERVICE_ERROR = "LOCATION_SERVICE_ERROR"
    INVALID_COORDINATES = "INVALID_COORDINATES"
    LOCATION_NOT_FOUND = "LOCATION_NOT_FOUND"
    
    # SOS errors
    SOS_TRIGGER_ERROR = "SOS_TRIGGER_ERROR"
    NO_EMERGENCY_CONTACTS = "NO_EMERGENCY_CONTACTS"
    SOS_ALREADY_ACTIVE = "SOS_ALREADY_ACTIVE"
    
    # Database errors
    DATABASE_ERROR = "DATABASE_ERROR"
    DATABASE_INTEGRITY_ERROR = "DATABASE_INTEGRITY_ERROR"
    
    # Notification errors
    NOTIFICATION_ERROR = "NOTIFICATION_ERROR"
    NOTIFICATION_FAILED = "NOTIFICATION_FAILED"
    
    # General errors
    INTERNAL_SERVER_ERROR = "INTERNAL_SERVER_ERROR"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    OPERATION_TIMEOUT = "OPERATION_TIMEOUT"
    OPERATION_FAILED = "OPERATION_FAILED"


class AshaPlatformException(Exception):
    """Base exception for Asha-Alita platform"""
    
    def __init__(
        self,
        message: str,
        error_code: ErrorCode = ErrorCode.INTERNAL_SERVER_ERROR,
        status_code: int = 500,
        details: Optional[Any] = None,
    ):
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class AuthenticationError(AshaPlatformException):
    """Authentication failed"""
    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.AUTHENTICATION_FAILED,
            status_code=401,
            details=details,
        )


class InvalidCredentialsError(AshaPlatformException):
    """Invalid credentials provided"""
    def __init__(self, message: str = "Invalid email or password", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_CREDENTIALS,
            status_code=401,
            details=details,
        )


class TokenExpiredError(AshaPlatformException):
    """JWT token expired"""
    def __init__(self, message: str = "Token has expired", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.TOKEN_EXPIRED,
            status_code=401,
            details=details,
        )


class InvalidTokenError(AshaPlatformException):
    """Invalid JWT token"""
    def __init__(self, message: str = "Invalid token", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_TOKEN,
            status_code=401,
            details=details,
        )


class UnauthorizedError(AshaPlatformException):
    """Unauthorized access"""
    def __init__(self, message: str = "Unauthorized", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.UNAUTHORIZED,
            status_code=401,
            details=details,
        )


class ForbiddenError(AshaPlatformException):
    """Forbidden access"""
    def __init__(self, message: str = "Forbidden", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.FORBIDDEN,
            status_code=403,
            details=details,
        )


class InsufficientPermissionsError(AshaPlatformException):
    """Insufficient permissions for operation"""
    def __init__(self, message: str = "Insufficient permissions", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INSUFFICIENT_PERMISSIONS,
            status_code=403,
            details=details,
        )


class ValidationError(AshaPlatformException):
    """Validation error"""
    def __init__(self, message: str = "Validation failed", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.VALIDATION_ERROR,
            status_code=422,
            details=details,
        )


class InvalidInputError(AshaPlatformException):
    """Invalid input provided"""
    def __init__(self, message: str = "Invalid input", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.INVALID_INPUT,
            status_code=400,
            details=details,
        )


class ResourceNotFoundError(AshaPlatformException):
    """Resource not found"""
    def __init__(self, message: str = "Resource not found", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.NOT_FOUND,
            status_code=404,
            details=details,
        )


class ResourceAlreadyExistsError(AshaPlatformException):
    """Resource already exists"""
    def __init__(self, message: str = "Resource already exists", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.RESOURCE_ALREADY_EXISTS,
            status_code=409,
            details=details,
        )


class RateLimitError(AshaPlatformException):
    """Rate limit exceeded"""
    def __init__(
        self,
        message: str = "Rate limit exceeded",
        retry_after: Optional[int] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.RATE_LIMIT_EXCEEDED,
            status_code=429,
            details=details or {"retry_after": retry_after},
        )


class SOSCooldownError(AshaPlatformException):
    """SOS triggered too recently"""
    def __init__(
        self,
        message: str = "SOS cooldown period active",
        retry_after: Optional[int] = None,
        details: Optional[Any] = None,
    ):
        super().__init__(
            message=message,
            error_code=ErrorCode.SOS_COOLDOWN_ACTIVE,
            status_code=429,
            details=details or {"retry_after": retry_after},
        )


class NoEmergencyContactsError(AshaPlatformException):
    """No emergency contacts configured"""
    def __init__(self, message: str = "No emergency contacts configured", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.NO_EMERGENCY_CONTACTS,
            status_code=400,
            details=details,
        )


class MLInferenceError(AshaPlatformException):
    """ML model inference error"""
    def __init__(self, message: str = "ML inference failed", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.ML_INFERENCE_ERROR,
            status_code=500,
            details=details,
        )


class ModelNotFoundError(AshaPlatformException):
    """ML model not found"""
    def __init__(self, message: str = "Model not found", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.MODEL_NOT_FOUND,
            status_code=503,
            details=details,
        )


class DatabaseError(AshaPlatformException):
    """Database operation error"""
    def __init__(self, message: str = "Database error", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.DATABASE_ERROR,
            status_code=500,
            details=details,
        )


class NotificationError(AshaPlatformException):
    """Notification service error"""
    def __init__(self, message: str = "Notification failed", details: Optional[Any] = None):
        super().__init__(
            message=message,
            error_code=ErrorCode.NOTIFICATION_ERROR,
            status_code=500,
            details=details,
        )
