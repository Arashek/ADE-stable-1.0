import pytest
import asyncio
import numpy as np
from datetime import datetime
from typing import Dict, Any, List

from ...services.voice.voice_processor import VoiceProcessor
from ...services.voice.ios_voice_processor import IOSVoiceProcessor
from ...utils.voice_utils import (
    VoiceQualityMetrics,
    VoiceRecognitionResult,
    VoiceSynthesisResult,
    WakeWordResult,
    VoiceQualityLevel,
    VoiceError,
    RecognitionError,
    SynthesisError,
    WakeWordError
)

@pytest.fixture
def voice_processor():
    """Create a voice processor instance"""
    return IOSVoiceProcessor()

@pytest.fixture
def sample_audio_data():
    """Create sample audio data for testing"""
    # Generate a 1-second sine wave at 440Hz
    sample_rate = 16000
    duration = 1.0
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio_data = np.sin(2 * np.pi * 440 * t)
    return audio_data.tobytes()

@pytest.fixture
def sample_text():
    """Create sample text for testing"""
    return "Hello, this is a test of the voice processing system."

@pytest.mark.asyncio
async def test_voice_processor_initialization(voice_processor):
    """Test voice processor initialization"""
    await voice_processor.initialize()
    status = await voice_processor.get_status()
    
    assert status["platform"] == "ios"
    assert "metrics" in status
    assert "prompt_library_size" in status
    assert "error_handlers" in status

@pytest.mark.asyncio
async def test_voice_recognition(voice_processor, sample_audio_data):
    """Test voice recognition functionality"""
    # Create a list to store recognition results
    results: List[VoiceRecognitionResult] = []
    
    async def recognition_callback(result: VoiceRecognitionResult):
        results.append(result)
    
    # Start voice recognition
    await voice_processor.start_voice_recognition(recognition_callback)
    
    # Simulate audio input
    await asyncio.sleep(1.0)  # Wait for recognition to process
    
    # Stop voice recognition
    await voice_processor.stop_voice_recognition()
    
    # Verify results
    assert len(results) > 0
    assert isinstance(results[0], VoiceRecognitionResult)
    assert results[0].text is not None
    assert 0 <= results[0].confidence <= 1.0

@pytest.mark.asyncio
async def test_speech_synthesis(voice_processor, sample_text):
    """Test speech synthesis functionality"""
    # Configure synthesis options
    options = {
        "rate": 0.5,
        "pitch": 1.0,
        "volume": 1.0,
        "language": "en-US"
    }
    
    # Perform speech synthesis
    result = await voice_processor.synthesize_speech(sample_text, options)
    
    # Verify result
    assert isinstance(result, VoiceSynthesisResult)
    assert result.audio_data is not None
    assert result.duration > 0
    assert 0 <= result.quality <= 1.0
    assert result.format == "ios_audio"

@pytest.mark.asyncio
async def test_wake_word_detection(voice_processor, sample_audio_data):
    """Test wake word detection functionality"""
    # Perform wake word detection
    result = await voice_processor.detect_wake_word(sample_audio_data)
    
    # Verify result
    assert isinstance(result, WakeWordResult)
    assert isinstance(result.detected, bool)
    assert 0 <= result.confidence <= 1.0
    assert result.wake_word is not None

@pytest.mark.asyncio
async def test_voice_quality_analysis(voice_processor, sample_audio_data):
    """Test voice quality analysis functionality"""
    # Perform quality analysis
    metrics = await voice_processor.analyze_voice_quality(sample_audio_data)
    
    # Verify metrics
    assert isinstance(metrics, VoiceQualityMetrics)
    assert 0 <= metrics.clarity <= 1.0
    assert 0 <= metrics.volume <= 1.0
    assert 0 <= metrics.noise_level <= 1.0
    assert metrics.processing_time >= 0
    assert isinstance(metrics.quality_level, VoiceQualityLevel)

@pytest.mark.asyncio
async def test_voice_prompt_management(voice_processor):
    """Test voice prompt management functionality"""
    # Add a voice prompt
    prompt_id = "test_prompt"
    prompt_text = "This is a test prompt"
    prompt_options = {"rate": 0.5, "pitch": 1.0}
    
    await voice_processor.add_voice_prompt(prompt_id, prompt_text, prompt_options)
    
    # Get the prompt
    prompt = await voice_processor.get_voice_prompt(prompt_id)
    
    # Verify prompt
    assert prompt is not None
    assert prompt["text"] == prompt_text
    assert prompt["options"] == prompt_options
    assert "created_at" in prompt

@pytest.mark.asyncio
async def test_error_handling(voice_processor):
    """Test error handling functionality"""
    # Create error handler
    error_handled = False
    
    async def error_handler(error: Exception):
        nonlocal error_handled
        error_handled = True
    
    # Register error handler
    await voice_processor.register_error_handler("test_error", error_handler)
    
    # Simulate error
    try:
        await voice_processor.start_voice_recognition(None)
    except RecognitionError:
        pass
    
    # Verify error handling
    assert error_handled

@pytest.mark.asyncio
async def test_metrics_tracking(voice_processor, sample_audio_data):
    """Test metrics tracking functionality"""
    # Get initial metrics
    initial_metrics = voice_processor.metrics
    
    # Perform some operations
    await voice_processor.analyze_voice_quality(sample_audio_data)
    
    # Get updated metrics
    updated_metrics = voice_processor.metrics
    
    # Verify metrics updates
    assert updated_metrics["processing_latency"] >= initial_metrics["processing_latency"]

@pytest.mark.asyncio
async def test_concurrent_operations(voice_processor, sample_audio_data):
    """Test concurrent voice processing operations"""
    # Create tasks for concurrent operations
    tasks = [
        voice_processor.analyze_voice_quality(sample_audio_data),
        voice_processor.detect_wake_word(sample_audio_data)
    ]
    
    # Run tasks concurrently
    results = await asyncio.gather(*tasks)
    
    # Verify results
    assert len(results) == 2
    assert isinstance(results[0], VoiceQualityMetrics)
    assert isinstance(results[1], WakeWordResult)

@pytest.mark.asyncio
async def test_voice_processor_cleanup(voice_processor):
    """Test voice processor cleanup"""
    # Start voice recognition
    await voice_processor.start_voice_recognition(lambda x: None)
    
    # Stop voice recognition
    await voice_processor.stop_voice_recognition()
    
    # Verify cleanup
    assert not voice_processor.is_recording
    assert voice_processor.recognition_task is None

@pytest.mark.asyncio
async def test_invalid_input_handling(voice_processor):
    """Test handling of invalid inputs"""
    # Test invalid audio data
    with pytest.raises(VoiceError):
        await voice_processor.analyze_voice_quality(b"")
    
    # Test invalid text
    with pytest.raises(SynthesisError):
        await voice_processor.synthesize_speech("")
    
    # Test invalid wake word detection
    with pytest.raises(WakeWordError):
        await voice_processor.detect_wake_word(b"") 