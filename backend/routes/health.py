from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from datetime import datetime
import time
import psutil
from typing import Dict, Any, Optional
from core.config import get_settings
from core.response import HealthCheckResponse, create_response, APIResponse
from app.database import SessionLocal
from core.logging_config import get_logger

logger = get_logger(__name__)
settings = get_settings()

router = APIRouter(prefix="/health", tags=["Health & Monitoring"])

app_start_time = time.time()
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get(
    "/status",
    tags=["Health & Monitoring"],
)
async def health_status(db: Session = Depends(get_db)):
    """Health status endpoint"""
    try:
        # Check database connectivity with a simple query
        from sqlalchemy import text
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as e:
        logger.error(f"Database health check failed: {str(e)}")
        db_status = "disconnected"
    
    # Calculate uptime
    uptime = time.time() - app_start_time
    
    # Determine overall status
    overall_status = "healthy" if db_status == "connected" else "degraded"
    
    return {
        "status": overall_status,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "database": db_status,
        "uptime_seconds": uptime,
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get(
    "/detailed",
    tags=["Health & Monitoring"],
)
async def detailed_health_check(db: Session = Depends(get_db)):
    """
    Detailed system health check with metrics
    
    Returns comprehensive system information:
    - Database connectivity and query time
    - System resources (CPU, memory)
    - Service modules status
    - Recent error rates
    """
    health_info = {
        "service": {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "uptime_seconds": time.time() - app_start_time,
        },
        "database": await _check_database_health(db),
        "system_resources": _get_system_resources(),
        "modules": {
            "ml_stress_detection": _check_module_status("ml_stress_detection"),
            "safe_route": _check_module_status("safe_route"),
            "websocket": _check_module_status("websocket"),
            "notifications": _check_module_status("notifications"),
        },
        "timestamp": datetime.utcnow().isoformat(),
    }
    
    return health_info


@router.get("/ready", status_code=status.HTTP_200_OK, tags=["Health & Monitoring"])
async def readiness_check(db: Session = Depends(get_db)):
    """
    Kubernetes-style readiness probe
    
    Returns 200 if service is ready to accept traffic
    """
    try:
        # Check database
        db.execute("SELECT 1")
        
        return {
            "status": "ready",
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Readiness check failed: {str(e)}")
        return {
            "status": "not_ready",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/live", status_code=status.HTTP_200_OK, tags=["Health & Monitoring"])
async def liveness_check():
    """
    Kubernetes-style liveness probe
    
    Returns 200 if service is alive
    """
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
    }


@router.get(
    "/metrics",
    tags=["Health & Monitoring"],
)
async def get_metrics():
    """
    Get system metrics for monitoring
    
    Returns:
    - CPU usage
    - Memory usage
    - Disk usage
    - Request counts (placeholder)
    """
    metrics = {
        "timestamp": datetime.utcnow().isoformat(),
        "cpu": {
            "percent": psutil.cpu_percent(interval=0.1),
            "count": psutil.cpu_count(),
        },
        "memory": {
            "total_mb": psutil.virtual_memory().total / (1024 * 1024),
            "available_mb": psutil.virtual_memory().available / (1024 * 1024),
            "percent": psutil.virtual_memory().percent,
        },
        "disk": {
            "total_gb": psutil.disk_usage("/").total / (1024**3),
            "free_gb": psutil.disk_usage("/").free / (1024**3),
            "percent": psutil.disk_usage("/").percent,
        },
        "uptime_seconds": time.time() - app_start_time,
    }
    
    return create_response(
        data=metrics,
        message="Metrics retrieved",
    )


# Helper functions

async def _check_database_health(db: Session) -> Dict[str, Any]:
    """Check database connectivity and performance"""
    try:
        start_time = time.time()
        db.execute("SELECT 1")
        query_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return {
            "status": "connected",
            "query_time_ms": query_time,
            "timestamp": datetime.utcnow().isoformat(),
        }
    except Exception as e:
        logger.error(f"Database health check error: {str(e)}")
        return {
            "status": "disconnected",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


def _get_system_resources() -> Dict[str, Any]:
    """Get system resource utilization"""
    try:
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage("/")
        
        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_mb": memory.available / (1024 * 1024),
            "disk_percent": disk.percent,
            "disk_free_gb": disk.free / (1024**3),
        }
    except Exception as e:
        logger.error(f"Error getting system resources: {str(e)}")
        return {}


def _check_module_status(module_name: str) -> Dict[str, Any]:
    """Check if a module is available"""
    module_checks = {
        "ml_stress_detection": _check_ml_module("stress_detection"),
        "safe_route": _check_ml_module("safe_route"),
        "websocket": {"status": "available"},
        "notifications": {"status": "available"},
    }
    
    return module_checks.get(module_name, {"status": "unknown"})


def _check_ml_module(module_type: str) -> Dict[str, Any]:
    """Check ML module availability"""
    try:
        from pathlib import Path
        
        if module_type == "stress_detection":
            model_path = Path(settings.STRESS_MODEL_PATH)
        elif module_type == "safe_route":
            model_path = Path(settings.SAFE_ROUTE_MODEL_PATH)
        else:
            return {"status": "unknown"}
        
        if model_path.exists():
            return {
                "status": "available",
                "model_path": str(model_path),
                "file_size_mb": model_path.stat().st_size / (1024 * 1024),
            }
        else:
            return {
                "status": "missing",
                "model_path": str(model_path),
                "note": "Model file not found",
            }
    
    except Exception as e:
        logger.error(f"Error checking ML module {module_type}: {str(e)}")
        return {
            "status": "error",
            "error": str(e),
        }
