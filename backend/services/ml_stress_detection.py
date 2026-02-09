"""
ML Service Layer - Stress Detection
Isolated ML inference for voice stress detection
Production-ready with async support and error handling
"""
import asyncio
import pickle
import numpy as np
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import logging

from core.config import get_settings
from core.exceptions import ModelNotFoundError, MLInferenceError
from core.logging_config import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Thread pool for ML inference (non-blocking)
ml_executor = ThreadPoolExecutor(max_workers=4)


class StressDetectionModel:
    """Stress detection ML model wrapper"""
    
    def __init__(self):
        self.model = None
        self.model_path = settings.STRESS_MODEL_PATH
        self.is_loaded = False
    
    def load_model(self) -> None:
        """Load stress detection model from disk"""
        try:
            model_file = Path(self.model_path)
            
            if not model_file.exists():
                raise ModelNotFoundError(
                    f"Stress detection model not found at {self.model_path}"
                )
            
            with open(model_file, "rb") as f:
                self.model = pickle.load(f)
            
            self.is_loaded = True
            logger.info(f"Stress detection model loaded from {self.model_path}")
        
        except Exception as e:
            logger.error(f"Failed to load stress detection model: {str(e)}")
            raise ModelNotFoundError(f"Failed to load model: {str(e)}")
    
    def ensure_loaded(self) -> None:
        """Ensure model is loaded"""
        if not self.is_loaded:
            self.load_model()
    
    def extract_features(self, audio_data: bytes) -> np.ndarray:
        """
        Extract features from audio data
        
        In production, you would use librosa or similar library
        to extract MFCC, spectral features, etc.
        
        For now, this is a placeholder
        """
        # TODO: Implement actual feature extraction
        # This would typically involve:
        # - Converting audio bytes to numpy array
        # - Computing MFCCs
        # - Computing spectral features
        # - Zero-crossing rate
        # - Energy features
        # - etc.
        
        # For demo: create dummy features
        return np.random.random(13)  # Dummy 13-dimensional feature vector
    
    def predict(self, features: np.ndarray) -> Tuple[float, bool]:
        """
        Run inference on features
        
        Returns:
            (stress_score, distress_detected)
        """
        self.ensure_loaded()
        
        try:
            # Reshape features if needed
            if features.ndim == 1:
                features = features.reshape(1, -1)
            
            # Run prediction
            stress_score = float(self.model.predict_proba(features)[0][1])
            
            # Threshold for distress detection
            distress_threshold = 0.7
            distress_detected = stress_score >= distress_threshold
            
            logger.debug(f"Stress detection prediction: score={stress_score}, distress={distress_detected}")
            
            return stress_score, distress_detected
        
        except Exception as e:
            logger.error(f"Error during stress detection inference: {str(e)}")
            raise MLInferenceError(f"Stress detection inference failed: {str(e)}")
    
    def batch_predict(self, features_list: list) -> list:
        """Batch inference for multiple samples"""
        self.ensure_loaded()
        
        try:
            features_array = np.array(features_list)
            
            if features_array.ndim == 1:
                features_array = features_array.reshape(1, -1)
            
            predictions = self.model.predict_proba(features_array)
            
            results = []
            for pred in predictions:
                stress_score = float(pred[1])
                distress_detected = stress_score >= 0.7
                results.append({
                    "stress_score": stress_score,
                    "distress_detected": distress_detected,
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Error during batch stress detection: {str(e)}")
            raise MLInferenceError(f"Batch inference failed: {str(e)}")


class StressDetectionService:
    """Service for stress detection with async support"""
    
    def __init__(self):
        self.model = StressDetectionModel()
        self.model.load_model()
    
    async def analyze_audio(
        self,
        audio_data: bytes,
        timeout: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Analyze audio for stress signals (async)
        
        Args:
            audio_data: Raw audio bytes
            timeout: Inference timeout in seconds
        
        Returns:
            {
                "stress_score": 0.0-1.0,
                "distress_detected": bool,
                "confidence": 0.0-1.0,
                "recommendation": "str",
                "severity": "low|medium|high|critical"
            }
        """
        try:
            # Run inference in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            
            timeout_val = timeout or settings.ML_INFERENCE_TIMEOUT
            
            # Extract features (could also be async)
            features = await asyncio.wait_for(
                loop.run_in_executor(ml_executor, self.model.extract_features, audio_data),
                timeout=timeout_val
            )
            
            # Run inference
            stress_score, distress_detected = await asyncio.wait_for(
                loop.run_in_executor(ml_executor, self.model.predict, features),
                timeout=timeout_val
            )
            
            # Determine severity
            if stress_score >= 0.9:
                severity = "critical"
            elif stress_score >= 0.7:
                severity = "high"
            elif stress_score >= 0.5:
                severity = "medium"
            else:
                severity = "low"
            
            # Generate recommendation
            recommendation = self._get_recommendation(severity, distress_detected)
            
            result = {
                "stress_score": stress_score,
                "distress_detected": distress_detected,
                "confidence": min(stress_score, 1.0 - stress_score) * 2,  # Confidence metric
                "severity": severity,
                "recommendation": recommendation,
            }
            
            logger.info(f"Audio analysis completed: {result}")
            return result
        
        except asyncio.TimeoutError:
            logger.error("Stress detection inference timeout")
            raise MLInferenceError("Inference timeout exceeded")
        
        except Exception as e:
            logger.error(f"Error analyzing audio: {str(e)}")
            raise MLInferenceError(f"Audio analysis failed: {str(e)}")
    
    async def analyze_audio_stream(
        self,
        audio_stream_chunks: list,
    ) -> Dict[str, Any]:
        """
        Analyze streaming audio chunks
        
        Args:
            audio_stream_chunks: List of audio chunk bytes
        
        Returns:
            Aggregated stress analysis
        """
        try:
            # Combine chunks
            combined_audio = b"".join(audio_stream_chunks)
            
            # Run analysis
            return await self.analyze_audio(combined_audio)
        
        except Exception as e:
            logger.error(f"Error analyzing audio stream: {str(e)}")
            raise MLInferenceError(f"Stream analysis failed: {str(e)}")
    
    def _get_recommendation(self, severity: str, distress_detected: bool) -> str:
        """Generate recommendation based on analysis"""
        recommendations = {
            ("critical", True): "IMMEDIATE SOS TRIGGERED - Emergency services alerted",
            ("critical", False): "High stress detected - Consider reaching out for support",
            ("high", True): "Distress detected - SOS recommended",
            ("high", False): "High stress levels - Contact emergency contacts",
            ("medium", False): "Moderate stress detected - Consider calling support",
            ("low", False): "Stress levels normal - Continue with caution",
        }
        
        return recommendations.get(
            (severity, distress_detected),
            "Continue monitoring stress levels",
        )


# Global instance
stress_detection_service: Optional[StressDetectionService] = None


def get_stress_detection_service() -> StressDetectionService:
    """Get or create stress detection service instance"""
    global stress_detection_service
    
    if stress_detection_service is None:
        stress_detection_service = StressDetectionService()
    
    return stress_detection_service
