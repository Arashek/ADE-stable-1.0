import pytest
import asyncio
import numpy as np
from typing import Dict, Any, Generator
from datetime import datetime

from ...services.voice.voice_processor import VoiceProcessor
from ...services.voice.ios_voice_processor import IOSVoiceProcessor
from ...utils.voice_utils import (
    VoiceQualityMetrics,
    VoiceRecognitionResult,
    VoiceSynthesisResult,
    VoiceQualityLevel
)

@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def voice_processor() -> VoiceProcessor:
    """Create a voice processor instance"""
    processor = IOSVoiceProcessor()
    return processor

@pytest.fixture(scope="session")
def test_data() -> Dict[str, Any]:
    """Create test data for voice accessibility testing"""
    return {
        "sample_text": "This is a test sentence for voice accessibility testing.",
        "sample_audio": _generate_sample_audio(),
        "wake_word": "Hey Assistant",
        "languages": ["en-US", "es-ES", "fr-FR", "de-DE"],
        "noise_levels": [0.1, 0.3, 0.5, 0.7],
        "response_times": [0.1, 0.2, 0.3, 0.4, 0.5]
    }

@pytest.fixture(scope="session")
def quality_metrics() -> VoiceQualityMetrics:
    """Create sample voice quality metrics"""
    return VoiceQualityMetrics(
        quality_level=VoiceQualityLevel.EXCELLENT,
        signal_to_noise_ratio=25.0,
        volume_std=0.1,
        timestamp=datetime.now()
    )

@pytest.fixture(scope="session")
def recognition_result() -> VoiceRecognitionResult:
    """Create sample voice recognition result"""
    return VoiceRecognitionResult(
        text="This is a test sentence for voice accessibility testing.",
        confidence=0.95,
        timestamp=datetime.now()
    )

@pytest.fixture(scope="session")
def synthesis_result() -> VoiceSynthesisResult:
    """Create sample speech synthesis result"""
    return VoiceSynthesisResult(
        audio_data=_generate_sample_audio(),
        duration=1.0,
        timestamp=datetime.now()
    )

def _generate_sample_audio() -> np.ndarray:
    """Generate sample audio data for testing"""
    # Generate a 1-second sine wave at 440Hz
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    return np.sin(2 * np.pi * 440 * t)

@pytest.fixture(scope="session")
def test_config() -> Dict[str, Any]:
    """Create test configuration"""
    return {
        "recognition": {
            "accuracy_threshold": 0.9,
            "latency_threshold": 0.5,  # seconds
            "noise_handling_threshold": 0.7
        },
        "synthesis": {
            "quality_threshold": 0.8,
            "latency_threshold": 0.3,  # seconds
            "clarity_threshold": 0.8
        },
        "wake_word": {
            "accuracy_threshold": 0.95,
            "false_positive_threshold": 0.05,
            "latency_threshold": 0.2  # seconds
        },
        "quality": {
            "audio_quality_threshold": 0.8,
            "noise_reduction_threshold": 0.7,
            "normalization_threshold": 0.8
        },
        "error_handling": {
            "recovery_threshold": 0.8,
            "feedback_quality_threshold": 0.8,
            "degradation_threshold": 0.6
        },
        "response_time": {
            "recognition_threshold": 0.5,  # seconds
            "synthesis_threshold": 0.3,  # seconds
            "system_threshold": 1.0  # seconds
        },
        "language": {
            "detection_threshold": 0.9,
            "support_threshold": 0.8,
            "switching_threshold": 0.7
        },
        "feedback": {
            "clarity_threshold": 0.8,
            "timing_threshold": 0.3,  # seconds
            "consistency_threshold": 0.8
        }
    }

@pytest.fixture(scope="session")
def test_results() -> Dict[str, Any]:
    """Create sample test results"""
    return {
        "timestamp": datetime.now(),
        "checks": {
            "voice_recognition": {
                "name": "voice_recognition",
                "score": 0.9,
                "details": [
                    {
                        "name": "recognition_accuracy",
                        "score": 0.95,
                        "details": {
                            "expected": "Test text",
                            "actual": "Test text",
                            "accuracy": 1.0
                        }
                    },
                    {
                        "name": "recognition_latency",
                        "score": 0.8,
                        "details": {
                            "latency": 0.2,
                            "threshold": 0.5
                        }
                    }
                ]
            },
            "speech_synthesis": {
                "name": "speech_synthesis",
                "score": 0.85,
                "details": [
                    {
                        "name": "synthesis_quality",
                        "score": 0.9,
                        "details": {
                            "metrics": {
                                "quality_level": "EXCELLENT",
                                "signal_to_noise_ratio": 25.0,
                                "volume_std": 0.1
                            }
                        }
                    }
                ]
            }
        },
        "overall_score": 0.875
    } 