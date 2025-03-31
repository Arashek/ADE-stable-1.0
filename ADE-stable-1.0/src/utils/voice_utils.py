from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum
import numpy as np
from datetime import datetime

class VoiceQualityLevel(Enum):
    """Voice quality levels"""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"

class VoiceRecognitionStatus(Enum):
    """Voice recognition status"""
    IDLE = "idle"
    LISTENING = "listening"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ERROR = "error"

@dataclass
class VoiceQualityMetrics:
    """Voice quality metrics"""
    clarity: float
    volume: float
    noise_level: float
    processing_time: float
    quality_level: VoiceQualityLevel
    timestamp: datetime = datetime.now()

@dataclass
class VoiceRecognitionResult:
    """Voice recognition result"""
    text: str
    confidence: float
    language: str
    is_final: bool
    alternatives: List[str]
    timestamp: datetime = datetime.now()

@dataclass
class VoiceSynthesisResult:
    """Voice synthesis result"""
    audio_data: bytes
    duration: float
    quality: float
    format: str
    timestamp: datetime = datetime.now()

@dataclass
class WakeWordResult:
    """Wake word detection result"""
    detected: bool
    confidence: float
    wake_word: str
    timestamp: datetime = datetime.now()

class VoicePromptTemplate:
    """Template for voice prompts"""
    def __init__(
        self,
        template_id: str,
        text: str,
        variables: List[str],
        options: Dict[str, Any] = None
    ):
        self.template_id = template_id
        self.text = text
        self.variables = variables
        self.options = options or {}
    
    def format(self, **kwargs) -> str:
        """Format template with variables"""
        try:
            return self.text.format(**kwargs)
        except KeyError as e:
            raise ValueError(f"Missing required variable: {str(e)}")
        except Exception as e:
            raise ValueError(f"Template formatting failed: {str(e)}")

class VoiceError(Exception):
    """Base class for voice processing errors"""
    def __init__(self, message: str, error_type: str, details: Dict[str, Any] = None):
        super().__init__(message)
        self.error_type = error_type
        self.details = details or {}
        self.timestamp = datetime.now()

class RecognitionError(VoiceError):
    """Voice recognition error"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, "recognition", details)

class SynthesisError(VoiceError):
    """Voice synthesis error"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, "synthesis", details)

class WakeWordError(VoiceError):
    """Wake word detection error"""
    def __init__(self, message: str, details: Dict[str, Any] = None):
        super().__init__(message, "wake_word", details)

def calculate_voice_quality(
    audio_data: np.ndarray,
    sample_rate: int
) -> VoiceQualityMetrics:
    """Calculate voice quality metrics from audio data"""
    try:
        # Calculate clarity (using spectral flatness)
        spectrum = np.abs(np.fft.fft(audio_data))
        spectral_flatness = np.exp(np.mean(np.log(spectrum + 1e-10)))
        clarity = 1.0 - spectral_flatness
        
        # Calculate volume (RMS)
        volume = np.sqrt(np.mean(audio_data**2))
        
        # Calculate noise level (using signal-to-noise ratio)
        noise_floor = np.percentile(np.abs(audio_data), 10)
        signal_peak = np.max(np.abs(audio_data))
        noise_level = noise_floor / signal_peak if signal_peak > 0 else 0
        
        # Determine quality level
        if clarity > 0.8 and volume > 0.7 and noise_level < 0.1:
            quality_level = VoiceQualityLevel.EXCELLENT
        elif clarity > 0.6 and volume > 0.5 and noise_level < 0.2:
            quality_level = VoiceQualityLevel.GOOD
        elif clarity > 0.4 and volume > 0.3 and noise_level < 0.3:
            quality_level = VoiceQualityLevel.FAIR
        else:
            quality_level = VoiceQualityLevel.POOR
        
        return VoiceQualityMetrics(
            clarity=float(clarity),
            volume=float(volume),
            noise_level=float(noise_level),
            processing_time=0.0,  # Set by caller
            quality_level=quality_level
        )
        
    except Exception as e:
        raise VoiceError(f"Voice quality calculation failed: {str(e)}", "quality_calculation")

def validate_audio_data(
    audio_data: bytes,
    sample_rate: int,
    channels: int
) -> bool:
    """Validate audio data format and quality"""
    try:
        # Convert to numpy array
        audio_array = np.frombuffer(audio_data, dtype=np.float32)
        
        # Check data length
        if len(audio_array) == 0:
            return False
        
        # Check for NaN or infinite values
        if np.any(np.isnan(audio_array)) or np.any(np.isinf(audio_array)):
            return False
        
        # Check for silent audio
        if np.all(audio_array == 0):
            return False
        
        # Check for clipping
        if np.any(np.abs(audio_array) > 1.0):
            return False
        
        return True
        
    except Exception:
        return False

def normalize_audio(
    audio_data: np.ndarray,
    target_volume: float = 0.8
) -> np.ndarray:
    """Normalize audio volume"""
    try:
        # Calculate current volume
        current_volume = np.max(np.abs(audio_data))
        
        if current_volume > 0:
            # Calculate scaling factor
            scale = target_volume / current_volume
            
            # Apply scaling
            normalized = audio_data * scale
            
            # Clip to prevent overflow
            return np.clip(normalized, -1.0, 1.0)
        
        return audio_data
        
    except Exception as e:
        raise VoiceError(f"Audio normalization failed: {str(e)}", "normalization")

def resample_audio(
    audio_data: np.ndarray,
    current_rate: int,
    target_rate: int
) -> np.ndarray:
    """Resample audio to target sample rate"""
    try:
        # Calculate resampling ratio
        ratio = target_rate / current_rate
        
        # Calculate new length
        new_length = int(len(audio_data) * ratio)
        
        # Create time points
        old_time = np.linspace(0, 1, len(audio_data))
        new_time = np.linspace(0, 1, new_length)
        
        # Interpolate
        return np.interp(new_time, old_time, audio_data)
        
    except Exception as e:
        raise VoiceError(f"Audio resampling failed: {str(e)}", "resampling") 