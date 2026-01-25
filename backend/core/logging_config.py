"""
Structured Logging Configuration
Production-ready logging with JSON format and audit trails
"""
import logging
import json
import sys
from datetime import datetime
from typing import Optional, Any, Dict
from pathlib import Path
from pythonjsonlogger import jsonlogger

from core.config import get_settings

settings = get_settings()


class AuditLogger:
    """Audit logger for critical operations"""
    
    def __init__(self, name: str = "audit"):
        self.logger = logging.getLogger(name)
        self._setup_audit_logger()
    
    def _setup_audit_logger(self):
        """Setup audit logger"""
        Path(settings.AUDIT_LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
        
        handler = logging.FileHandler(settings.AUDIT_LOG_FILE)
        formatter = jsonlogger.JsonFormatter()
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
    
    def log_sos_trigger(
        self,
        user_id: int,
        latitude: float,
        longitude: float,
        contacts_notified: int,
        request_id: str,
    ):
        """Log SOS trigger event"""
        self.logger.info(
            "SOS Triggered",
            extra={
                "event_type": "SOS_TRIGGER",
                "user_id": user_id,
                "latitude": latitude,
                "longitude": longitude,
                "contacts_notified": contacts_notified,
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
    
    def log_authentication(
        self,
        user_id: Optional[int],
        email: str,
        success: bool,
        request_id: str,
    ):
        """Log authentication event"""
        self.logger.info(
            "Authentication Event",
            extra={
                "event_type": "AUTHENTICATION",
                "user_id": user_id,
                "email": email,
                "success": success,
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
    
    def log_unauthorized_access_attempt(
        self,
        user_id: int,
        resource: str,
        action: str,
        request_id: str,
    ):
        """Log unauthorized access attempt"""
        self.logger.warning(
            "Unauthorized Access Attempt",
            extra={
                "event_type": "UNAUTHORIZED_ACCESS",
                "user_id": user_id,
                "resource": resource,
                "action": action,
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
    
    def log_rate_limit_exceeded(
        self,
        user_id: Optional[int],
        endpoint: str,
        request_id: str,
    ):
        """Log rate limit exceeded"""
        self.logger.warning(
            "Rate Limit Exceeded",
            extra={
                "event_type": "RATE_LIMIT_EXCEEDED",
                "user_id": user_id,
                "endpoint": endpoint,
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
    
    def log_data_access(
        self,
        user_id: int,
        resource_type: str,
        resource_id: int,
        action: str,
        request_id: str,
    ):
        """Log data access"""
        self.logger.info(
            "Data Access",
            extra={
                "event_type": "DATA_ACCESS",
                "user_id": user_id,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "action": action,
                "request_id": request_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context"""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        super().add_fields(log_record, record, message_dict)
        log_record["timestamp"] = datetime.utcnow().isoformat()
        log_record["level"] = record.levelname
        log_record["logger"] = record.name
        log_record["module"] = record.module


def get_logger(name: str) -> logging.Logger:
    """Get or create logger with proper configuration"""
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        
        # Determine format based on settings
        if settings.LOG_FORMAT == "json":
            formatter = CustomJsonFormatter()
        else:
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
        
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        
        # File handler if specified
        if settings.LOG_FILE:
            Path(settings.LOG_FILE).parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(settings.LOG_FILE)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
        
        # Set log level
        log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
        logger.setLevel(log_level)
    
    return logger


def setup_logging():
    """Initialize logging system"""
    logger = get_logger(__name__)
    logger.info(
        f"Logging initialized",
        extra={
            "environment": settings.ENVIRONMENT,
            "log_level": settings.LOG_LEVEL,
            "log_format": settings.LOG_FORMAT,
        },
    )
    return logger


# Global instances
audit_logger = AuditLogger()
app_logger = setup_logging()
