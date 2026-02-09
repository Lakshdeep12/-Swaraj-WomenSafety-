"""
ML Service Layer - Safe Route Engine
Isolated ML inference for route safety optimization
Production-ready with async support and error handling
"""
import asyncio
import pickle
import numpy as np
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
import logging

from core.config import get_settings
from core.exceptions import ModelNotFoundError, MLInferenceError, InvalidInputError
from core.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Thread pool for ML inference
ml_executor = ThreadPoolExecutor(max_workers=4)


@dataclass
class Location:
    """Location data class"""
    latitude: float
    longitude: float
    
    def validate(self) -> None:
        """Validate coordinates"""
        if not (-90 <= self.latitude <= 90):
            raise InvalidInputError("Latitude must be between -90 and 90")
        if not (-180 <= self.longitude <= 180):
            raise InvalidInputError("Longitude must be between -180 and 180")


@dataclass
class RouteOption:
    """Route option data class"""
    id: str
    name: str
    polyline: str  # Encoded polyline
    distance_km: float
    estimated_duration_minutes: int
    risk_score: float
    safety_rating: int  # 1-5
    explanation: str
    incident_count: int = 0
    average_lighting: float = 0.7  # 0-1
    police_stations_nearby: int = 0


class SafeRouteModel:
    """Safe route ML model wrapper"""
    
    def __init__(self):
        self.model = None
        self.model_path = settings.SAFE_ROUTE_MODEL_PATH
        self.is_loaded = False
    
    def load_model(self) -> None:
        """Load safe route model from disk"""
        try:
            model_file = Path(self.model_path)
            
            if not model_file.exists():
                raise ModelNotFoundError(
                    f"Safe route model not found at {self.model_path}"
                )
            
            with open(model_file, "rb") as f:
                self.model = pickle.load(f)
            
            self.is_loaded = True
            logger.info(f"Safe route model loaded from {self.model_path}")
        
        except Exception as e:
            logger.error(f"Failed to load safe route model: {str(e)}")
            raise ModelNotFoundError(f"Failed to load model: {str(e)}")
    
    def ensure_loaded(self) -> None:
        """Ensure model is loaded"""
        if not self.is_loaded:
            self.load_model()
    
    def compute_risk_score(
        self,
        features: np.ndarray,
    ) -> float:
        """
        Compute risk score for a route (0-1, where 1 is highest risk)
        
        Features should include:
        - Distance
        - Time of day (0-23)
        - Day of week (0-6)
        - Historical incident density
        - Lighting availability
        - Police station proximity
        - etc.
        """
        self.ensure_loaded()
        
        try:
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            # Run inference
            risk_probabilities = self.model.predict_proba(features)
            risk_score = float(risk_probabilities[0][1])
            
            return risk_score
        
        except Exception as e:
            logger.error(f"Error computing risk score: {str(e)}")
            raise MLInferenceError(f"Risk computation failed: {str(e)}")
    
    def rank_routes(
        self,
        routes_features: List[np.ndarray],
    ) -> List[float]:
        """Rank multiple routes by safety"""
        self.ensure_loaded()
        
        try:
            features_array = np.array(routes_features)
            
            risk_scores = []
            for features in features_array:
                risk_score = self.compute_risk_score(features)
                risk_scores.append(risk_score)
            
            return risk_scores
        
        except Exception as e:
            logger.error(f"Error ranking routes: {str(e)}")
            raise MLInferenceError(f"Route ranking failed: {str(e)}")


class SafeRouteService:
    """Service for safe route recommendation with async support"""
    
    def __init__(self):
        self.model = SafeRouteModel()
        try:
            self.model.load_model()
        except Exception as e:
            logger.warning(f"Failed to load safe route model on init: {str(e)}")
    
    async def get_safest_route(
        self,
        origin: Location,
        destination: Location,
        time_of_day: Optional[int] = None,
        alternatives: int = 3,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Get the safest route from origin to destination
        
        Args:
            origin: Starting location
            destination: Ending location
            time_of_day: Hour of day (0-23), defaults to current
            alternatives: Number of alternative routes to consider
            timeout: Inference timeout in seconds
        
        Returns:
            {
                "recommended_route": RouteOption,
                "alternative_routes": List[RouteOption],
                "analysis": {
                    "safest_route_id": str,
                    "safety_summary": str,
                    "time_of_day_factor": float,
                    "incident_density": float,
                }
            }
        """
        try:
            # Validate locations
            origin.validate()
            destination.validate()
            
            # Get candidate routes
            routes = await self._get_candidate_routes(origin, destination)
            
            if not routes:
                raise MLInferenceError("No routes found")
            
            # Prepare features for ML model
            timeout_val = timeout or settings.ML_INFERENCE_TIMEOUT
            
            loop = asyncio.get_event_loop()
            
            # Extract features and compute risk scores
            risk_scores = await asyncio.wait_for(
                loop.run_in_executor(
                    ml_executor,
                    self._compute_route_risks,
                    routes,
                    time_of_day,
                ),
                timeout=timeout_val
            )
            
            # Rank routes by safety
            ranked_routes = self._rank_and_annotate_routes(routes, risk_scores)
            
            # Return safest route and alternatives
            result = {
                "recommended_route": ranked_routes[0],
                "alternative_routes": ranked_routes[1:alternatives],
                "analysis": {
                    "safest_route_id": ranked_routes[0].id,
                    "safety_summary": self._get_safety_summary(ranked_routes[0]),
                    "time_of_day_factor": self._get_time_factor(time_of_day),
                    "incident_density": self._get_incident_density(origin, destination),
                },
            }
            
            logger.info(f"Route recommendation generated: {ranked_routes[0].id}")
            return result
        
        except asyncio.TimeoutError:
            logger.error("Route analysis timeout")
            raise MLInferenceError("Route analysis timeout")
        
        except Exception as e:
            logger.error(f"Error getting safest route: {str(e)}")
            raise
    
    async def _get_candidate_routes(
        self,
        origin: Location,
        destination: Location,
    ) -> List[RouteOption]:
        """Get candidate routes from routing service"""
        # TODO: Integrate with Google Maps API or similar
        # For now, return mock routes
        
        routes = [
            RouteOption(
                id="route_1",
                name="Highway Route",
                polyline="encoded_polyline_1",
                distance_km=15.5,
                estimated_duration_minutes=22,
                risk_score=0.0,
                safety_rating=0,
                explanation="",
                incident_count=2,
                average_lighting=0.8,
                police_stations_nearby=1,
            ),
            RouteOption(
                id="route_2",
                name="Local Streets",
                polyline="encoded_polyline_2",
                distance_km=16.2,
                estimated_duration_minutes=28,
                risk_score=0.0,
                safety_rating=0,
                explanation="",
                incident_count=5,
                average_lighting=0.6,
                police_stations_nearby=0,
            ),
            RouteOption(
                id="route_3",
                name="Scenic Route",
                polyline="encoded_polyline_3",
                distance_km=18.1,
                estimated_duration_minutes=25,
                risk_score=0.0,
                safety_rating=0,
                explanation="",
                incident_count=1,
                average_lighting=0.9,
                police_stations_nearby=2,
            ),
        ]
        
        return routes
    
    def _compute_route_risks(
        self,
        routes: List[RouteOption],
        time_of_day: Optional[int],
    ) -> List[float]:
        """Compute risk scores for routes"""
        risk_scores = []
        
        for route in routes:
            # Create feature vector for ML model
            features = np.array([
                route.distance_km,
                time_of_day or 12,
                route.incident_count,
                route.average_lighting,
                route.police_stations_nearby,
            ])
            
            # Compute risk using model
            try:
                risk_score = self.model.compute_risk_score(features)
            except Exception as e:
                logger.warning(f"Error computing risk for route {route.id}: {str(e)}")
                # Fallback to heuristic scoring
                risk_score = self._heuristic_risk_score(route, time_of_day)
            
            risk_scores.append(risk_score)
        
        return risk_scores
    
    def _heuristic_risk_score(self, route: RouteOption, time_of_day: Optional[int]) -> float:
        """Fallback heuristic risk scoring"""
        hour = time_of_day or 12
        
        # Night hours (22:00 - 06:00) are riskier
        time_factor = 1.5 if (hour < 6 or hour >= 22) else 1.0
        
        # Incident density
        incident_factor = min(route.incident_count / 10.0, 1.0)
        
        # Lighting factor (inversely proportional to safety)
        lighting_factor = 1.0 - route.average_lighting
        
        # Police proximity (reduces risk)
        police_factor = 1.0 - (route.police_stations_nearby * 0.2)
        
        risk_score = (
            (incident_factor * 0.4 + lighting_factor * 0.3 + police_factor * 0.3) * time_factor
        )
        
        return min(risk_score, 1.0)
    
    def _rank_and_annotate_routes(
        self,
        routes: List[RouteOption],
        risk_scores: List[float],
    ) -> List[RouteOption]:
        """Rank routes and add safety ratings"""
        # Pair routes with risk scores
        route_scores = list(zip(routes, risk_scores))
        
        # Sort by risk score (ascending)
        route_scores.sort(key=lambda x: x[1])
        
        # Annotate with safety ratings
        annotated_routes = []
        for route, risk_score in route_scores:
            # Convert risk score to 1-5 safety rating
            safety_rating = 5 - int(risk_score * 5)
            safety_rating = max(1, min(5, safety_rating))
            
            # Generate explanation
            explanation = self._get_route_explanation(route, risk_score)
            
            # Update route
            route.risk_score = risk_score
            route.safety_rating = safety_rating
            route.explanation = explanation
            
            annotated_routes.append(route)
        
        return annotated_routes
    
    def _get_route_explanation(self, route: RouteOption, risk_score: float) -> str:
        """Generate human-readable explanation for route"""
        if risk_score <= 0.3:
            return "Very safe route with good lighting and police presence"
        elif risk_score <= 0.5:
            return "Generally safe route with moderate incidents"
        elif risk_score <= 0.7:
            return "Route has some safety concerns, consider alternatives"
        else:
            return "High-risk route, strongly recommend alternative"
    
    def _get_safety_summary(self, route: RouteOption) -> str:
        """Get safety summary for recommended route"""
        return (
            f"Route {route.name}: Safety rating {route.safety_rating}/5. "
            f"Distance: {route.distance_km}km, ETA: {route.estimated_duration_minutes}min. "
            f"{route.explanation}"
        )
    
    def _get_time_factor(self, time_of_day: Optional[int]) -> float:
        """Get time factor (0-1 where 1 is most risky)"""
        hour = time_of_day or 12
        
        if 6 <= hour < 22:
            return 0.3  # Daytime is safer
        else:
            return 0.8  # Night time is riskier
    
    def _get_incident_density(self, origin: Location, destination: Location) -> float:
        """Get incident density between two locations"""
        # TODO: Query incident database
        return 0.5  # Mock value


# Global instance
safe_route_service: Optional[SafeRouteService] = None


def get_safe_route_service() -> SafeRouteService:
    """Get or create safe route service instance"""
    global safe_route_service
    
    if safe_route_service is None:
        safe_route_service = SafeRouteService()
    
    return safe_route_service
