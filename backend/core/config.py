"""
Centralized Configuration Management
Secure environment-based configuration with validation
"""
from pydantic_settings import BaseSettings
from pydantic import ConfigDict, field_validator
from functools import lru_cache
import os
from typing import Optional


class Settings(BaseSettings):
    """Production-ready settings with environment-based configuration"""
    
    model_config = ConfigDict(env_file=".env", case_sensitive=True)
    
    # ============= App Configuration =============
    APP_NAME: str = "Asha-Alita Women Safety Platform"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = ENVIRONMENT == "development"
    
    # ============= Server Configuration =============
    SERVER_HOST: str = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT: int = int(os.getenv("SERVER_PORT", "8000"))
    RELOAD: bool = DEBUG
    
    # ============= Database Configuration =============
    # ============= Database Configuration =============
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///./asha_alita.db"
    )

    @field_validator("DATABASE_URL")
    @classmethod
    def check_database_url(cls, v: str) -> str:
        if v and v.startswith("postgres://"):
            return v.replace("postgres://", "postgresql://", 1)
        return v

    DB_ECHO: bool = DEBUG
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "20"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "40"))
    
    # ============= Security Configuration =============
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "dev-secret-key-change-in-production"
    )
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("TOKEN_EXPIRE", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE", "7"))
    
    # ============= CORS Configuration =============
    CORS_ORIGINS: list = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else ([
        "http://localhost:3000",
        "http://localhost:8080",
        "http://localhost:5173",
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ] if ENVIRONMENT == "development" else [
        "https://asha-alita.com",
    ])
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list = ["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"]
    CORS_ALLOW_HEADERS: list = ["*"]
    
    # ============= Rate Limiting Configuration =============
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_CALLS: int = int(os.getenv("RATE_LIMIT_CALLS", "100"))
    RATE_LIMIT_PERIOD: int = int(os.getenv("RATE_LIMIT_PERIOD", "60"))  # seconds
    
    # SOS-specific rate limiting
    SOS_RATE_LIMIT_CALLS: int = 5
    SOS_RATE_LIMIT_PERIOD: int = 3600  # 1 hour
    SOS_COOLDOWN_MINUTES: int = 15
    
    # ML endpoint rate limiting
    ML_RATE_LIMIT_CALLS: int = 30
    ML_RATE_LIMIT_PERIOD: int = 60
    
    # ============= Logging Configuration =============
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = "json"  # json or standard
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE", "logs/app.log")
    AUDIT_LOG_FILE: str = os.getenv("AUDIT_LOG_FILE", "logs/audit.log")
    
    # ============= ML Model Configuration =============
    STRESS_MODEL_PATH: str = os.getenv("STRESS_MODEL_PATH", "models/stress_detection.pkl")
    SAFE_ROUTE_MODEL_PATH: str = os.getenv("SAFE_ROUTE_MODEL_PATH", "models/safe_route.pkl")
    ML_INFERENCE_TIMEOUT: int = 30  # seconds
    ML_BATCH_SIZE: int = 32
    
    # ============= Location Services =============
    GOOGLE_MAPS_API_KEY: str = os.getenv("GOOGLE_MAPS_API_KEY", "")
    MAX_LOCATION_HISTORY: int = 1000
    LOCATION_UPDATE_INTERVAL: int = 30  # seconds
    
    # ============= Notification Configuration =============
    NOTIFICATION_SERVICE: str = os.getenv("NOTIFICATION_SERVICE", "email")
    EMAIL_HOST: str = os.getenv("EMAIL_HOST", "smtp.gmail.com")
    EMAIL_PORT: int = 587
    EMAIL_USERNAME: str = os.getenv("EMAIL_USERNAME", "")
    EMAIL_PASSWORD: str = os.getenv("EMAIL_PASSWORD", "")
    
    # ============= WebSocket Configuration =============
    WEBSOCKET_HEARTBEAT_INTERVAL: int = 30
    WEBSOCKET_MESSAGE_QUEUE_SIZE: int = 100
    
    # ============= Admin Configuration =============
    ADMIN_EMAIL: str = os.getenv("ADMIN_EMAIL", "admin@asha-alita.com")
    ADMIN_PHONE: str = os.getenv("ADMIN_PHONE", "+1234567890")
    
    # ============= Feature Flags =============
    ENABLE_ML_STRESS_DETECTION: bool = True
    ENABLE_SAFE_ROUTE: bool = True
    ENABLE_BLOCKCHAIN_AUDIT: bool = False  # Future enhancement
    ENABLE_TWILIO_SMS: bool = False


@lru_cache()
def get_settings() -> Settings:
    """Singleton pattern for settings"""
    return Settings()
