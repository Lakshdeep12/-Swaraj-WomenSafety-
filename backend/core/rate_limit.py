"""
Rate Limiting and Security Utilities
Production-ready rate limiting and authorization decorators
"""
from functools import wraps
from typing import Optional, Callable, Any
from datetime import datetime, timedelta
from collections import defaultdict
import time

from core.config import get_settings
from core.exceptions import RateLimitError, SOSCooldownError
from core.logging_config import get_logger, audit_logger

settings = get_settings()
logger = get_logger(__name__)


class RateLimiter:
    """Token bucket rate limiter"""
    
    def __init__(self, calls: int = 100, period: int = 60):
        self.calls = calls
        self.period = period
        self.requests = defaultdict(list)
    
    def is_allowed(self, key: str) -> tuple[bool, Optional[int]]:
        """Check if request is allowed"""
        now = time.time()
        cutoff = now - self.period
        
        # Clean old requests
        self.requests[key] = [req_time for req_time in self.requests[key] if req_time > cutoff]
        
        # Check if limit exceeded
        if len(self.requests[key]) >= self.calls:
            retry_after = int(self.requests[key][0] + self.period - now) + 1
            return False, retry_after
        
        # Add current request
        self.requests[key].append(now)
        return True, None


class SOSCooldownTracker:
    """Track SOS trigger cooldowns per user"""
    
    def __init__(self, cooldown_minutes: int = 15):
        self.cooldown_minutes = cooldown_minutes
        self.sos_triggers = {}  # user_id -> timestamp
    
    def can_trigger_sos(self, user_id: int) -> tuple[bool, Optional[int]]:
        """Check if user can trigger SOS"""
        now = datetime.utcnow()
        last_sos = self.sos_triggers.get(user_id)
        
        if last_sos is None:
            return True, None
        
        cooldown_end = last_sos + timedelta(minutes=self.cooldown_minutes)
        
        if now < cooldown_end:
            retry_after = int((cooldown_end - now).total_seconds())
            return False, retry_after
        
        return True, None
    
    def record_sos(self, user_id: int):
        """Record SOS trigger"""
        self.sos_triggers[user_id] = datetime.utcnow()


# Global instances
default_limiter = RateLimiter(
    calls=settings.RATE_LIMIT_CALLS,
    period=settings.RATE_LIMIT_PERIOD,
)

sos_limiter = RateLimiter(
    calls=settings.SOS_RATE_LIMIT_CALLS,
    period=settings.SOS_RATE_LIMIT_PERIOD,
)

sos_cooldown = SOSCooldownTracker(
    cooldown_minutes=settings.SOS_COOLDOWN_MINUTES,
)

ml_limiter = RateLimiter(
    calls=settings.ML_RATE_LIMIT_CALLS,
    period=settings.ML_RATE_LIMIT_PERIOD,
)


def rate_limit(limiter: Optional[RateLimiter] = None) -> Callable:
    """
    Rate limiting decorator
    
    Args:
        limiter: RateLimiter instance to use (defaults to default_limiter)
    """
    if limiter is None:
        limiter = default_limiter
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            # Extract user ID from kwargs
            user_id = kwargs.get("current_user")
            
            if not user_id:
                # Fallback to IP or request ID
                request = kwargs.get("request")
                key = request.client.host if request and request.client else "unknown"
            else:
                key = f"user_{user_id.id}"
            
            allowed, retry_after = limiter.is_allowed(key)
            
            if not allowed:
                audit_logger.log_rate_limit_exceeded(
                    user_id=user_id.id if user_id else None,
                    endpoint=func.__name__,
                    request_id=kwargs.get("request_id", "unknown"),
                )
                raise RateLimitError(retry_after=retry_after)
            
            return await func(*args, **kwargs)
        
        def sync_wrapper(*args, **kwargs) -> Any:
            # Extract user ID from kwargs
            user_id = kwargs.get("current_user")
            
            if not user_id:
                request = kwargs.get("request")
                key = request.client.host if request and request.client else "unknown"
            else:
                key = f"user_{user_id.id}"
            
            allowed, retry_after = limiter.is_allowed(key)
            
            if not allowed:
                audit_logger.log_rate_limit_exceeded(
                    user_id=user_id.id if user_id else None,
                    endpoint=func.__name__,
                    request_id=kwargs.get("request_id", "unknown"),
                )
                raise RateLimitError(retry_after=retry_after)
            
            return func(*args, **kwargs)
        
        # Return appropriate wrapper
        if hasattr(func, "__code__") and "await" in func.__code__.co_names:
            return async_wrapper
        return sync_wrapper
    
    return decorator


def sos_rate_limit() -> Callable:
    """SOS-specific rate limiting decorator"""
    return rate_limit(sos_limiter)


def check_sos_cooldown(user_id: int) -> None:
    """Check and enforce SOS cooldown"""
    allowed, retry_after = sos_cooldown.can_trigger_sos(user_id)
    
    if not allowed:
        raise SOSCooldownError(retry_after=retry_after)


def record_sos_trigger(user_id: int) -> None:
    """Record SOS trigger for cooldown tracking"""
    sos_cooldown.record_sos(user_id)


def ml_rate_limit() -> Callable:
    """ML endpoint rate limiting decorator"""
    return rate_limit(ml_limiter)
