import speech_recognition as sr
from pydub import AudioSegment
import numpy as np
from typing import Dict, Any, Optional, List
import logging
from pathlib import Path
import os
import tempfile
import asyncio
import whisper
import torch
from functools import lru_cache
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor

class VoiceTranscriptionService:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.recognizer = sr.Recognizer()
        self.whisper_model = None
        self.executor = ThreadPoolExecutor(max_workers=2)
        self.cache_dir = Path(tempfile.gettempdir()) / "voice_transcription_cache"
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize Whisper model (small version for efficiency)
        try:
            self.whisper_model = whisper.load_model("small")
        except Exception as e:
            self.logger.warning(f"Failed to load Whisper model: {str(e)}")
            
        self.supported_languages = {
            "en-US": "English (US)",
            "en-GB": "English (UK)",
            "es-ES": "Spanish",
            "fr-FR": "French",
            "de-DE": "German",
            "it-IT": "Italian",
            "pt-PT": "Portuguese",
            "ru-RU": "Russian",
            "ja-JP": "Japanese",
            "ko-KR": "Korean",
            "zh-CN": "Chinese (Simplified)"
        }
        
    @lru_cache(maxsize=100)
    def _get_cached_transcription(self, audio_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached transcription result"""
        cache_file = self.cache_dir / f"{audio_hash}.json"
        if cache_file.exists():
            try:
                with open(cache_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return None
        return None
        
    def _save_to_cache(self, audio_hash: str, result: Dict[str, Any]) -> None:
        """Save transcription result to cache"""
        cache_file = self.cache_dir / f"{audio_hash}.json"
        try:
            with open(cache_file, 'w') as f:
                json.dump(result, f)
        except Exception as e:
            self.logger.warning(f"Failed to save to cache: {str(e)}")
            
    def _calculate_audio_hash(self, audio_path: Path) -> str:
        """Calculate hash of audio file for caching"""
        with open(audio_path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
            
    async def transcribe_audio(
        self,
        audio_path: Path,
        language: str = "en-US",
        use_cache: bool = True,
        fallback_to_whisper: bool = True
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text with fallback options
        """
        try:
            # Validate language
            if language not in self.supported_languages:
                raise ValueError(f"Unsupported language: {language}")

            # Check cache first
            if use_cache:
                audio_hash = self._calculate_audio_hash(audio_path)
                cached_result = self._get_cached_transcription(audio_hash)
                if cached_result:
                    return cached_result

            # Convert audio to WAV format if needed
            wav_path = await self._convert_to_wav(audio_path)
            
            try:
                # Try Google Speech Recognition first
                result = await self._transcribe_with_google(wav_path, language)
            except Exception as e:
                self.logger.warning(f"Google Speech Recognition failed: {str(e)}")
                
                if fallback_to_whisper and self.whisper_model:
                    # Fallback to Whisper
                    result = await self._transcribe_with_whisper(wav_path, language)
                else:
                    raise
            
            # Clean up temporary file
            if wav_path != audio_path:
                os.remove(wav_path)
                
            # Cache the result
            if use_cache:
                self._save_to_cache(audio_hash, result)
                
            return result
                
        except Exception as e:
            self.logger.error(f"Audio transcription failed: {str(e)}")
            raise
            
    async def _transcribe_with_google(
        self,
        wav_path: Path,
        language: str
    ) -> Dict[str, Any]:
        """Transcribe using Google Speech Recognition"""
        with sr.AudioFile(str(wav_path)) as source:
            audio = self.recognizer.record(source)
            self.recognizer.adjust_for_ambient_noise(audio)
            
            text = self.recognizer.recognize_google(
                audio,
                language=language,
                show_all=True
            )
            
            if isinstance(text, dict):
                alternatives = text.get('alternative', [])
                if alternatives:
                    return {
                        "text": alternatives[0].get('transcript', ''),
                        "confidence": alternatives[0].get('confidence', 0),
                        "alternatives": [
                            {
                                "text": alt.get('transcript', ''),
                                "confidence": alt.get('confidence', 0)
                            }
                            for alt in alternatives[1:]
                        ],
                        "language": language,
                        "provider": "google"
                    }
                else:
                    raise ValueError("No transcription alternatives found")
            else:
                return {
                    "text": text,
                    "confidence": 1.0,
                    "alternatives": [],
                    "language": language,
                    "provider": "google"
                }
                
    async def _transcribe_with_whisper(
        self,
        wav_path: Path,
        language: str
    ) -> Dict[str, Any]:
        """Transcribe using Whisper model"""
        if not self.whisper_model:
            raise RuntimeError("Whisper model not loaded")
            
        # Run Whisper in a separate thread to avoid blocking
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(
            self.executor,
            self._run_whisper_transcription,
            str(wav_path),
            language
        )
        
        return {
            "text": result["text"],
            "confidence": result["confidence"],
            "alternatives": [],
            "language": language,
            "provider": "whisper"
        }
        
    def _run_whisper_transcription(
        self,
        audio_path: str,
        language: str
    ) -> Dict[str, Any]:
        """Run Whisper transcription in a separate thread"""
        try:
            result = self.whisper_model.transcribe(
                audio_path,
                language=language,
                fp16=torch.cuda.is_available()  # Use GPU if available
            )
            
            return {
                "text": result["text"],
                "confidence": result.get("confidence", 0.8)  # Whisper doesn't provide confidence
            }
        except Exception as e:
            self.logger.error(f"Whisper transcription failed: {str(e)}")
            raise
            
    async def _convert_to_wav(self, audio_path: Path) -> Path:
        """
        Convert audio file to WAV format if needed
        """
        try:
            if audio_path.suffix.lower() == '.wav':
                return audio_path
                
            # Create temporary file
            temp_dir = tempfile.gettempdir()
            temp_path = Path(temp_dir) / f"{audio_path.stem}.wav"
            
            # Convert audio using pydub
            audio = AudioSegment.from_file(str(audio_path))
            
            # Optimize audio for transcription
            audio = self._optimize_audio(audio)
            
            audio.export(str(temp_path), format="wav")
            
            return temp_path
            
        except Exception as e:
            self.logger.error(f"Audio conversion failed: {str(e)}")
            raise
            
    def _optimize_audio(self, audio: AudioSegment) -> AudioSegment:
        """Optimize audio for transcription"""
        # Convert to mono
        audio = audio.set_channels(1)
        
        # Set sample rate to 16kHz (optimal for speech recognition)
        audio = audio.set_frame_rate(16000)
        
        # Normalize volume
        audio = audio.normalize()
        
        # Apply noise reduction if needed
        if self._needs_noise_reduction(audio):
            audio = self._apply_noise_reduction(audio)
            
        return audio
        
    def _needs_noise_reduction(self, audio: AudioSegment) -> bool:
        """Check if audio needs noise reduction"""
        # Convert to numpy array for analysis
        samples = np.array(audio.get_array_of_samples())
        
        # Calculate signal-to-noise ratio
        signal = np.abs(samples)
        noise = np.abs(samples - np.mean(samples))
        snr = np.mean(signal) / (np.mean(noise) + 1e-6)
        
        return snr < 10  # Threshold for noise reduction
        
    def _apply_noise_reduction(self, audio: AudioSegment) -> AudioSegment:
        """Apply noise reduction to audio"""
        # Convert to numpy array
        samples = np.array(audio.get_array_of_samples())
        
        # Apply simple noise reduction
        noise_threshold = np.std(samples) * 0.1
        samples[np.abs(samples) < noise_threshold] = 0
        
        # Convert back to AudioSegment
        return AudioSegment(
            samples.tobytes(),
            frame_rate=audio.frame_rate,
            sample_width=audio.sample_width,
            channels=audio.channels
        )
        
    async def detect_language(self, audio_path: Path) -> str:
        """
        Detect the language of speech in an audio file
        """
        try:
            # Convert to WAV if needed
            wav_path = await self._convert_to_wav(audio_path)
            
            # Try Google Speech Recognition first
            with sr.AudioFile(str(wav_path)) as source:
                audio = self.recognizer.record(source)
                result = self.recognizer.recognize_google(
                    audio,
                    show_all=True
                )
                
                if isinstance(result, dict) and 'alternative' in result:
                    detected_lang = result['alternative'][0].get('language', 'en-US')
                    return self._map_language_code(detected_lang)
                    
            # Fallback to Whisper if available
            if self.whisper_model:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    self.whisper_model.detect_language,
                    str(wav_path)
                )
                return self._map_language_code(result)
                
            return "en-US"  # Default to English if detection fails
            
        except Exception as e:
            self.logger.error(f"Language detection failed: {str(e)}")
            return "en-US"
            
    def _map_language_code(self, detected_lang: str) -> str:
        """
        Map detected language code to supported language code
        """
        # Simple mapping of common language codes
        lang_mapping = {
            "en": "en-US",
            "es": "es-ES",
            "fr": "fr-FR",
            "de": "de-DE",
            "it": "it-IT",
            "pt": "pt-PT",
            "ru": "ru-RU",
            "ja": "ja-JP",
            "ko": "ko-KR",
            "zh": "zh-CN"
        }
        
        base_lang = detected_lang.split('-')[0]
        return lang_mapping.get(base_lang, "en-US")
        
    def get_supported_languages(self) -> Dict[str, str]:
        """
        Get dictionary of supported languages
        """
        return self.supported_languages
        
    async def transcribe_with_timestamps(
        self,
        audio_path: Path,
        language: str = "en-US"
    ) -> Dict[str, Any]:
        """
        Transcribe audio with word-level timestamps
        """
        try:
            # Convert to WAV if needed
            wav_path = await self._convert_to_wav(audio_path)
            
            # Try Google Speech Recognition first
            with sr.AudioFile(str(wav_path)) as source:
                audio = self.recognizer.record(source)
                result = self.recognizer.recognize_google(
                    audio,
                    language=language,
                    show_all=True
                )
                
                if isinstance(result, dict) and 'alternative' in result:
                    # Process word-level timestamps
                    words = []
                    for word_info in result['alternative'][0].get('words', []):
                        words.append({
                            "word": word_info.get('word', ''),
                            "start_time": word_info.get('start_time', 0),
                            "end_time": word_info.get('end_time', 0),
                            "confidence": word_info.get('confidence', 0)
                        })
                    
                    return {
                        "text": result['alternative'][0].get('transcript', ''),
                        "confidence": result['alternative'][0].get('confidence', 0),
                        "words": words,
                        "language": language,
                        "provider": "google"
                    }
                    
            # Fallback to Whisper if available
            if self.whisper_model:
                loop = asyncio.get_event_loop()
                result = await loop.run_in_executor(
                    self.executor,
                    self.whisper_model.transcribe,
                    str(wav_path),
                    language,
                    True  # Enable word timestamps
                )
                
                return {
                    "text": result["text"],
                    "confidence": result.get("confidence", 0.8),
                    "words": result.get("words", []),
                    "language": language,
                    "provider": "whisper"
                }
                
            raise ValueError("No transcription results found")
                
        except Exception as e:
            self.logger.error(f"Timestamp transcription failed: {str(e)}")
            raise 