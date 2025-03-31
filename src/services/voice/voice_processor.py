from typing import Dict, Any, List, Optional, Callable
import logging
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime

from ...providers.base import BaseProvider
from ...utils.voice_utils import (
    VoiceQualityMetrics,
    VoiceRecognitionResult,
    VoiceSynthesisResult,
    WakeWordResult
)

logger = logging.getLogger(__name__)

class VoiceProcessor(BaseProvider):
    """Service for handling voice processing capabilities"""
    
    def __init__(self, platform: str):
        super().__init__()
        self.platform = platform
        self.voice_handlers: Dict[str, Any] = {}
        self.wake_word_detector = None
        self.voice_quality_analyzer = None
        self.voice_recognition_engine = None
        self.voice_synthesis_engine = None
        
        # Initialize metrics
        self.metrics = {
            "recognition_accuracy": 0.0,
            "synthesis_quality": 0.0,
            "wake_word_accuracy": 0.0,
            "processing_latency": 0.0,
            "error_rate": 0.0
        }
        
        # Initialize voice prompt library
        self.prompt_library: Dict[str, str] = {}
        
        # Initialize error handlers
        self.error_handlers: Dict[str, Callable] = {}
    
    async def initialize(self) -> None:
        """Initialize voice processing components"""
        try:
            # Initialize platform-specific components
            await self._initialize_platform_components()
            
            # Initialize wake word detection
            await self._initialize_wake_word_detection()
            
            # Initialize voice quality analysis
            await self._initialize_voice_quality_analysis()
            
            # Load voice prompt library
            await self._load_voice_prompt_library()
            
            logger.info(f"Voice processor initialized for {self.platform}")
            
        except Exception as e:
            logger.error(f"Voice processor initialization failed: {str(e)}")
            raise
    
    @abstractmethod
    async def _initialize_platform_components(self) -> None:
        """Initialize platform-specific voice components"""
        pass
    
    async def start_voice_recognition(self, callback: Callable[[VoiceRecognitionResult], None]) -> None:
        """Start voice recognition with callback"""
        try:
            # Initialize recognition engine
            await self.voice_recognition_engine.initialize()
            
            # Start recognition with callback
            await self.voice_recognition_engine.start_recognition(callback)
            
        except Exception as e:
            logger.error(f"Voice recognition start failed: {str(e)}")
            await self._handle_error("recognition_start", e)
    
    async def stop_voice_recognition(self) -> None:
        """Stop voice recognition"""
        try:
            await self.voice_recognition_engine.stop_recognition()
        except Exception as e:
            logger.error(f"Voice recognition stop failed: {str(e)}")
            await self._handle_error("recognition_stop", e)
    
    async def synthesize_speech(self, text: str, options: Dict[str, Any] = None) -> VoiceSynthesisResult:
        """Synthesize speech from text"""
        try:
            # Validate text
            if not text or not isinstance(text, str):
                raise ValueError("Invalid text for synthesis")
            
            # Get synthesis options
            synthesis_options = options or {}
            
            # Perform synthesis
            result = await self.voice_synthesis_engine.synthesize(
                text=text,
                options=synthesis_options
            )
            
            # Update metrics
            await self._update_synthesis_metrics(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Speech synthesis failed: {str(e)}")
            await self._handle_error("synthesis", e)
            raise
    
    async def detect_wake_word(self, audio_data: bytes) -> WakeWordResult:
        """Detect wake word in audio data"""
        try:
            # Validate audio data
            if not audio_data:
                raise ValueError("Invalid audio data")
            
            # Perform wake word detection
            result = await self.wake_word_detector.detect(audio_data)
            
            # Update metrics
            await self._update_wake_word_metrics(result)
            
            return result
            
        except Exception as e:
            logger.error(f"Wake word detection failed: {str(e)}")
            await self._handle_error("wake_word", e)
            raise
    
    async def analyze_voice_quality(self, audio_data: bytes) -> VoiceQualityMetrics:
        """Analyze voice quality of audio data"""
        try:
            # Validate audio data
            if not audio_data:
                raise ValueError("Invalid audio data")
            
            # Perform quality analysis
            metrics = await self.voice_quality_analyzer.analyze(audio_data)
            
            # Update metrics
            await self._update_quality_metrics(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"Voice quality analysis failed: {str(e)}")
            await self._handle_error("quality_analysis", e)
            raise
    
    async def add_voice_prompt(self, prompt_id: str, text: str, options: Dict[str, Any] = None) -> None:
        """Add a voice prompt to the library"""
        try:
            # Validate prompt
            if not prompt_id or not text:
                raise ValueError("Invalid prompt data")
            
            # Store prompt
            self.prompt_library[prompt_id] = {
                "text": text,
                "options": options or {},
                "created_at": datetime.now()
            }
            
            logger.info(f"Added voice prompt: {prompt_id}")
            
        except Exception as e:
            logger.error(f"Voice prompt addition failed: {str(e)}")
            await self._handle_error("prompt_addition", e)
    
    async def get_voice_prompt(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Get a voice prompt from the library"""
        return self.prompt_library.get(prompt_id)
    
    async def register_error_handler(self, error_type: str, handler: Callable) -> None:
        """Register an error handler"""
        self.error_handlers[error_type] = handler
    
    async def _handle_error(self, error_type: str, error: Exception) -> None:
        """Handle voice processing errors"""
        try:
            # Get error handler
            handler = self.error_handlers.get(error_type)
            
            if handler:
                # Call error handler
                await handler(error)
            else:
                # Log error
                logger.error(f"Unhandled error of type {error_type}: {str(error)}")
            
            # Update error metrics
            self.metrics["error_rate"] += 1
            
        except Exception as e:
            logger.error(f"Error handling failed: {str(e)}")
    
    async def _update_recognition_metrics(self, result: VoiceRecognitionResult) -> None:
        """Update voice recognition metrics"""
        try:
            # Calculate accuracy
            accuracy = result.accuracy if hasattr(result, "accuracy") else 0.0
            
            # Update metrics
            self.metrics["recognition_accuracy"] = (
                (self.metrics["recognition_accuracy"] + accuracy) / 2
            )
            
        except Exception as e:
            logger.error(f"Recognition metrics update failed: {str(e)}")
    
    async def _update_synthesis_metrics(self, result: VoiceSynthesisResult) -> None:
        """Update voice synthesis metrics"""
        try:
            # Calculate quality
            quality = result.quality if hasattr(result, "quality") else 0.0
            
            # Update metrics
            self.metrics["synthesis_quality"] = (
                (self.metrics["synthesis_quality"] + quality) / 2
            )
            
        except Exception as e:
            logger.error(f"Synthesis metrics update failed: {str(e)}")
    
    async def _update_wake_word_metrics(self, result: WakeWordResult) -> None:
        """Update wake word detection metrics"""
        try:
            # Calculate accuracy
            accuracy = result.accuracy if hasattr(result, "accuracy") else 0.0
            
            # Update metrics
            self.metrics["wake_word_accuracy"] = (
                (self.metrics["wake_word_accuracy"] + accuracy) / 2
            )
            
        except Exception as e:
            logger.error(f"Wake word metrics update failed: {str(e)}")
    
    async def _update_quality_metrics(self, metrics: VoiceQualityMetrics) -> None:
        """Update voice quality metrics"""
        try:
            # Update processing latency
            if hasattr(metrics, "processing_time"):
                self.metrics["processing_latency"] = (
                    (self.metrics["processing_latency"] + metrics.processing_time) / 2
                )
            
        except Exception as e:
            logger.error(f"Quality metrics update failed: {str(e)}")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get voice processor status"""
        return {
            "platform": self.platform,
            "metrics": self.metrics,
            "prompt_library_size": len(self.prompt_library),
            "error_handlers": list(self.error_handlers.keys())
        } 