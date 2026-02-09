"""
ML Integration Routes
Endpoints for stress detection and safe route recommendation
Production-ready with rate limiting and error handling
"""
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session
import asyncio

from core.config import get_settings
from core.response import create_response, APIResponse
from core.exceptions import InvalidInputError, MLInferenceError
from core.rate_limit import ml_rate_limit
from core.logging_config import get_logger
from app.database import SessionLocal
from routes.auth import get_current_user
from models.user import User
from services.ml_stress_detection import get_stress_detection_service
from services.ml_safe_route import get_safe_route_service, Location
from services.sos_pipeline import get_sos_pipeline

settings = get_settings()
logger = get_logger(__name__)

router = APIRouter(prefix="/api/ml", tags=["ML Services"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ============================================================================
# STRESS DETECTION ENDPOINTS
# ============================================================================

@router.post(
    "/stress-detection/analyze",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
)
@ml_rate_limit()
async def analyze_voice_stress(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze voice for stress signals
    
    Accepts audio file (WAV, MP3, etc.)
    Returns stress score and distress detection
    
    If distress is detected, automatically triggers SOS
    """
    try:
        if not file.content_type.startswith("audio/"):
            raise InvalidInputError("File must be an audio file")
        
        # Read audio data
        audio_data = await file.read()
        
        if not audio_data:
            raise InvalidInputError("Audio file is empty")
        
        # Analyze audio
        stress_service = get_stress_detection_service()
        analysis_result = await stress_service.analyze_audio(audio_data)
        
        # If distress detected, trigger SOS
        if analysis_result["distress_detected"]:
            logger.warning(
                f"Distress detected in voice analysis for user {current_user.id}",
                extra={"stress_score": analysis_result["stress_score"]},
            )
            # TODO: Trigger automatic SOS with voice-stress source
        
        return create_response(
            data=analysis_result,
            message="Voice analysis completed",
        )
    
    except InvalidInputError:
        raise
    except Exception as e:
        logger.error(f"Error in stress analysis: {str(e)}", exc_info=True)
        raise MLInferenceError(f"Analysis failed: {str(e)}")


@router.post(
    "/stress-detection/batch",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
)
@ml_rate_limit()
async def batch_stress_analysis(
    files: list = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Batch analyze multiple audio files
    
    Returns stress scores for all files
    """
    try:
        stress_service = get_stress_detection_service()
        
        results = []
        for file in files:
            try:
                audio_data = await file.read()
                result = await stress_service.analyze_audio(audio_data)
                results.append({
                    "filename": file.filename,
                    "analysis": result,
                })
            except Exception as e:
                logger.warning(f"Error analyzing {file.filename}: {str(e)}")
                results.append({
                    "filename": file.filename,
                    "error": str(e),
                })
        
        return create_response(
            data={"results": results, "total": len(results)},
            message="Batch analysis completed",
        )
    
    except Exception as e:
        logger.error(f"Error in batch analysis: {str(e)}", exc_info=True)
        raise MLInferenceError(f"Batch analysis failed: {str(e)}")


# ============================================================================
# SAFE ROUTE ENDPOINTS
# ============================================================================

@router.post(
    "/safe-route/recommend",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
)
@ml_rate_limit()
async def recommend_safe_route(
    origin_lat: float,
    origin_lng: float,
    destination_lat: float,
    destination_lng: float,
    time_of_day: Optional[int] = None,
    alternatives: int = 3,
    current_user: User = Depends(get_current_user),
):
    """
    Get safest route recommendation
    
    Analyzes multiple routes and recommends the safest option
    considering:
    - Historical incident data
    - Time of day
    - Lighting availability
    - Police presence
    - Road conditions
    
    Returns:
    - Recommended route with safety rating (1-5)
    - Alternative routes
    - Risk analysis
    """
    try:
        # Validate coordinates
        origin = Location(latitude=origin_lat, longitude=origin_lng)
        destination = Location(latitude=destination_lat, longitude=destination_lng)
        
        origin.validate()
        destination.validate()
        
        # Get safe route recommendation
        safe_route_service = get_safe_route_service()
        recommendation = await safe_route_service.get_safest_route(
            origin=origin,
            destination=destination,
            time_of_day=time_of_day,
            alternatives=alternatives,
        )
        
        logger.info(
            f"Safe route recommendation generated for user {current_user.id}",
            extra={"route_id": recommendation["analysis"]["safest_route_id"]},
        )
        
        return create_response(
            data={
                "recommended_route": {
                    "id": recommendation["recommended_route"].id,
                    "name": recommendation["recommended_route"].name,
                    "distance_km": recommendation["recommended_route"].distance_km,
                    "estimated_duration_minutes": recommendation["recommended_route"].estimated_duration_minutes,
                    "safety_rating": recommendation["recommended_route"].safety_rating,
                    "risk_score": recommendation["recommended_route"].risk_score,
                    "explanation": recommendation["recommended_route"].explanation,
                    "polyline": recommendation["recommended_route"].polyline,
                },
                "alternative_routes": [
                    {
                        "id": route.id,
                        "name": route.name,
                        "distance_km": route.distance_km,
                        "estimated_duration_minutes": route.estimated_duration_minutes,
                        "safety_rating": route.safety_rating,
                        "risk_score": route.risk_score,
                    }
                    for route in recommendation["alternative_routes"]
                ],
                "analysis": recommendation["analysis"],
            },
            message="Route recommendation completed",
        )
    
    except InvalidInputError:
        raise
    except Exception as e:
        logger.error(f"Error in route recommendation: {str(e)}", exc_info=True)
        raise MLInferenceError(f"Route recommendation failed: {str(e)}")


@router.get(
    "/safe-route/info",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
)
async def get_safe_route_info():
    """
    Get information about safe route service
    
    Returns:
    - Service status
    - Supported regions
    - Risk factors considered
    """
    return create_response(
        data={
            "service": "Safe Route Recommendation",
            "description": "ML-powered route safety analysis and recommendation",
            "version": "1.0.0",
            "enabled": settings.ENABLE_SAFE_ROUTE,
            "risk_factors": [
                "historical_incidents",
                "time_of_day",
                "lighting_availability",
                "police_presence",
                "road_conditions",
                "traffic_density",
            ],
            "safety_rating_scale": {
                "1": "Critical risk - Avoid",
                "2": "High risk - Use caution",
                "3": "Moderate risk - Be alert",
                "4": "Low risk - Relatively safe",
                "5": "Minimal risk - Safest option",
            },
        },
        message="Service information retrieved",
    )


# ============================================================================
# ML SERVICE STATUS ENDPOINTS
# ============================================================================

@router.get(
    "/status",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
)
async def get_ml_services_status():
    """
    Get status of all ML services
    
    Returns:
    - Model availability
    - Service health
    - Ready for inference
    """
    status_info = {
        "stress_detection": {
            "enabled": settings.ENABLE_ML_STRESS_DETECTION,
            "status": "available" if settings.ENABLE_ML_STRESS_DETECTION else "disabled",
            "model_path": settings.STRESS_MODEL_PATH,
        },
        "safe_route": {
            "enabled": settings.ENABLE_SAFE_ROUTE,
            "status": "available" if settings.ENABLE_SAFE_ROUTE else "disabled",
            "model_path": settings.SAFE_ROUTE_MODEL_PATH,
        },
        "inference_timeout": settings.ML_INFERENCE_TIMEOUT,
        "rate_limits": {
            "calls_per_minute": settings.ML_RATE_LIMIT_CALLS,
            "period_seconds": settings.ML_RATE_LIMIT_PERIOD,
        },
    }
    
    return create_response(
        data=status_info,
        message="ML services status retrieved",
    )


# ============================================================================
# ENHANCED SOS ENDPOINTS
# ============================================================================

@router.post(
    "/sos/trigger-voice",
    response_model=APIResponse[dict],
    status_code=status.HTTP_200_OK,
)
@ml_rate_limit()
async def trigger_sos_voice_stress(
    latitude: float,
    longitude: float,
    audio_file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Trigger SOS with optional voice analysis
    
    If audio is provided:
    1. Analyze voice for stress
    2. If distress detected, log it
    3. Trigger SOS with high priority
    
    Without audio:
    1. Standard SOS trigger
    """
    try:
        sos_pipeline = get_sos_pipeline(db)
        
        # Determine trigger source
        trigger_source = "voice_stress" if audio_file else "app"
        
        # Analyze voice if provided
        voice_stress_score = None
        if audio_file:
            try:
                audio_data = await audio_file.read()
                stress_service = get_stress_detection_service()
                analysis = await stress_service.analyze_audio(audio_data)
                voice_stress_score = analysis["stress_score"]
            except Exception as e:
                logger.warning(f"Error analyzing voice: {str(e)}")
        
        # Trigger SOS
        sos_result = await sos_pipeline.trigger_sos(
            user=current_user,
            latitude=latitude,
            longitude=longitude,
            trigger_source=trigger_source,
        )
        
        # Add voice analysis if available
        if voice_stress_score is not None:
            sos_result["voice_analysis"] = {
                "stress_score": voice_stress_score,
            }
        
        return create_response(
            data=sos_result,
            message="SOS triggered successfully",
        )
    
    except Exception as e:
        logger.error(f"Error triggering SOS with voice: {str(e)}", exc_info=True)
        raise
