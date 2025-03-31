import { useState, useEffect, useCallback, useRef } from 'react';

// Supported languages with their display names
export const SUPPORTED_LANGUAGES = {
  'en-US': 'English (US)',
  'en-GB': 'English (UK)',
  'es-ES': 'Spanish (Spain)',
  'es-MX': 'Spanish (Mexico)',
  'fr-FR': 'French',
  'de-DE': 'German',
  'it-IT': 'Italian',
  'pt-BR': 'Portuguese (Brazil)',
  'pt-PT': 'Portuguese (Portugal)',
  'ru-RU': 'Russian',
  'ja-JP': 'Japanese',
  'ko-KR': 'Korean',
  'zh-CN': 'Chinese (Simplified)',
  'zh-TW': 'Chinese (Traditional)',
  'ar-SA': 'Arabic',
  'hi-IN': 'Hindi',
  'bn-IN': 'Bengali',
  'tr-TR': 'Turkish',
  'nl-NL': 'Dutch',
  'pl-PL': 'Polish',
  'sv-SE': 'Swedish',
  'da-DK': 'Danish',
  'fi-FI': 'Finnish',
  'el-GR': 'Greek',
  'he-IL': 'Hebrew',
  'id-ID': 'Indonesian',
  'ms-MY': 'Malay',
  'th-TH': 'Thai',
  'vi-VN': 'Vietnamese',
  'ro-RO': 'Romanian',
  'hu-HU': 'Hungarian',
  'cs-CZ': 'Czech',
  'sk-SK': 'Slovak',
  'uk-UA': 'Ukrainian',
  'hr-HR': 'Croatian',
  'ca-ES': 'Catalan',
  'fil-PH': 'Filipino',
  'lv-LV': 'Latvian',
  'lt-LT': 'Lithuanian',
  'sr-RS': 'Serbian',
  'si-LK': 'Sinhala',
  'is-IS': 'Icelandic',
  'et-EE': 'Estonian',
  'fa-IR': 'Persian',
  'ur-PK': 'Urdu',
  'sw-KE': 'Swahili',
  'ta-IN': 'Tamil',
  'te-IN': 'Telugu',
  'mr-IN': 'Marathi',
  'gu-IN': 'Gujarati',
  'kn-IN': 'Kannada',
  'ml-IN': 'Malayalam',
  'ne-NP': 'Nepali',
  'si-LK': 'Sinhala',
  'my-MM': 'Burmese',
  'km-KH': 'Khmer',
  'lo-LA': 'Lao',
  'gl-ES': 'Galician',
  'eu-ES': 'Basque',
  'cy-GB': 'Welsh',
  'hy-AM': 'Armenian',
  'az-AZ': 'Azerbaijani',
  'af-ZA': 'Afrikaans',
  'ka-GE': 'Georgian',
  'be-BY': 'Belarusian',
  'bs-BA': 'Bosnian',
  'bg-BG': 'Bulgarian',
  'kk-KZ': 'Kazakh',
  'mk-MK': 'Macedonian',
  'mn-MN': 'Mongolian',
  'mt-MT': 'Maltese',
  'lb-LU': 'Luxembourgish',
  'mi-NZ': 'Maori',
  'sm-WS': 'Samoan',
  'sq-AL': 'Albanian',
  'am-ET': 'Amharic',
  'zu-ZA': 'Zulu',
  'xh-ZA': 'Xhosa',
  'tn-ZA': 'Tswana',
  'pa-IN': 'Punjabi',
  'or-IN': 'Odia',
  'as-IN': 'Assamese',
  'sa-IN': 'Sanskrit',
  'bo-CN': 'Tibetan',
  'dz-BT': 'Dzongkha',
  'ug-CN': 'Uyghur',
  'ii-CN': 'Sichuan Yi',
  'ak-GH': 'Akan',
  'ln-CD': 'Lingala',
  'mg-MG': 'Malagasy',
  'ny-MW': 'Chichewa',
  'sn-ZW': 'Shona',
  'st-ZA': 'Southern Sotho',
  'rw-RW': 'Kinyarwanda',
  'ps-AF': 'Pashto',
  'tl-PH': 'Tagalog',
  'yo-NG': 'Yoruba',
  'ha-NG': 'Hausa',
  'so-SO': 'Somali',
  'om-ET': 'Oromo',
  'ti-ER': 'Tigrinya',
  'zu-ZA': 'Zulu',
  'xh-ZA': 'Xhosa',
  'tn-ZA': 'Tswana',
  'pa-IN': 'Punjabi',
  'or-IN': 'Odia',
  'as-IN': 'Assamese',
  'sa-IN': 'Sanskrit',
  'bo-CN': 'Tibetan',
  'dz-BT': 'Dzongkha',
  'ug-CN': 'Uyghur',
  'ii-CN': 'Sichuan Yi',
  'ak-GH': 'Akan',
  'ln-CD': 'Lingala',
  'mg-MG': 'Malagasy',
  'ny-MW': 'Chichewa',
  'sn-ZW': 'Shona',
  'st-ZA': 'Southern Sotho',
  'rw-RW': 'Kinyarwanda',
  'ps-AF': 'Pashto',
  'tl-PH': 'Tagalog',
  'yo-NG': 'Yoruba',
  'ha-NG': 'Hausa',
  'so-SO': 'Somali',
  'om-ET': 'Oromo',
  'ti-ER': 'Tigrinya'
};

// Error types and messages
export const SPEECH_ERRORS = {
  ABORTED: 'aborted',
  AUDIO_CAPTURE: 'audio-capture',
  BAD_GRAMMAR: 'bad-grammar',
  LANGUAGE_NOT_SUPPORTED: 'language-not-supported',
  NETWORK: 'network',
  NOT_ALLOWED: 'not-allowed',
  SERVICE_NOT_AVAILABLE: 'service-not-available',
  NO_SPEECH: 'no-speech',
  BROWSER_NOT_SUPPORTED: 'browser-not-supported',
  PERMISSION_DENIED: 'permission-denied',
  QUOTA_EXCEEDED: 'quota-exceeded',
  TIMEOUT: 'timeout',
  UNKNOWN: 'unknown'
};

const ERROR_MESSAGES = {
  [SPEECH_ERRORS.ABORTED]: 'Speech recognition was aborted',
  [SPEECH_ERRORS.AUDIO_CAPTURE]: 'Failed to capture audio',
  [SPEECH_ERRORS.BAD_GRAMMAR]: 'Invalid grammar',
  [SPEECH_ERRORS.LANGUAGE_NOT_SUPPORTED]: 'Selected language is not supported',
  [SPEECH_ERRORS.NETWORK]: 'Network error occurred',
  [SPEECH_ERRORS.NOT_ALLOWED]: 'Speech recognition is not allowed',
  [SPEECH_ERRORS.SERVICE_NOT_AVAILABLE]: 'Speech recognition service is not available',
  [SPEECH_ERRORS.NO_SPEECH]: 'No speech was detected',
  [SPEECH_ERRORS.BROWSER_NOT_SUPPORTED]: 'Speech recognition is not supported in this browser',
  [SPEECH_ERRORS.PERMISSION_DENIED]: 'Permission to use microphone was denied',
  [SPEECH_ERRORS.QUOTA_EXCEEDED]: 'Speech recognition quota exceeded',
  [SPEECH_ERRORS.TIMEOUT]: 'Speech recognition timed out',
  [SPEECH_ERRORS.UNKNOWN]: 'An unknown error occurred'
};

const useSpeechToText = (options = {}) => {
  const {
    continuous = false,
    interimResults = true,
    language = 'en-US',
    onResult,
    onError,
    onStart,
    onEnd,
    maxDuration = 60000, // Maximum duration in milliseconds
    timeout = 5000, // Timeout for no speech in milliseconds
    onTimeout,
    onMaxDurationReached,
    onLanguageChange,
    onVoiceChange,
    noiseReduction = true, // New option for noise reduction
    voiceActivityDetection = true, // New option for voice activity detection
    silenceThreshold = 0.1, // Threshold for voice activity detection (0-1)
    noiseThreshold = 0.05, // Threshold for noise detection (0-1)
    onVoiceActivityStart,
    onVoiceActivityEnd,
    onNoiseDetected
  } = options;

  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState(null);
  const [availableVoices, setAvailableVoices] = useState([]);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [lastSpeechTime, setLastSpeechTime] = useState(null);
  const [isVoiceActive, setIsVoiceActive] = useState(false);
  const [noiseLevel, setNoiseLevel] = useState(0);
  const recognitionRef = useRef(null);
  const timeoutRef = useRef(null);
  const maxDurationRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const mediaStreamRef = useRef(null);

  // Load available voices
  useEffect(() => {
    const loadVoices = () => {
      if (window.speechSynthesis) {
        const voices = window.speechSynthesis.getVoices();
        setAvailableVoices(voices);
        
        // Set default voice for selected language
        const defaultVoice = voices.find(voice => voice.lang === language) || voices[0];
        setSelectedVoice(defaultVoice);
      }
    };

    if (window.speechSynthesis) {
      loadVoices();
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = null;
      }
    };
  }, [language]);

  // Initialize audio analysis for noise reduction and voice activity detection
  useEffect(() => {
    if (noiseReduction || voiceActivityDetection) {
      const initializeAudioAnalysis = async () => {
        try {
          const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
          mediaStreamRef.current = stream;
          
          audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
          const source = audioContextRef.current.createMediaStreamSource(stream);
          analyserRef.current = audioContextRef.current.createAnalyser();
          analyserRef.current.fftSize = 2048;
          source.connect(analyserRef.current);

          const bufferLength = analyserRef.current.frequencyBinCount;
          const dataArray = new Float32Array(bufferLength);

          const analyzeAudio = () => {
            if (!analyserRef.current) return;

            analyserRef.current.getFloatTimeDomainData(dataArray);
            
            // Calculate RMS value for noise level
            let sum = 0;
            for (let i = 0; i < bufferLength; i++) {
              sum += dataArray[i] * dataArray[i];
            }
            const rms = Math.sqrt(sum / bufferLength);
            setNoiseLevel(rms);

            // Voice activity detection
            if (voiceActivityDetection) {
              const isActive = rms > silenceThreshold;
              if (isActive !== isVoiceActive) {
                setIsVoiceActive(isActive);
                if (isActive) {
                  onVoiceActivityStart?.();
                } else {
                  onVoiceActivityEnd?.();
                }
              }
            }

            // Noise detection
            if (noiseReduction && rms > noiseThreshold) {
              onNoiseDetected?.(rms);
            }

            requestAnimationFrame(analyzeAudio);
          };

          analyzeAudio();
        } catch (error) {
          handleError(SPEECH_ERRORS.AUDIO_CAPTURE);
        }
      };

      initializeAudioAnalysis();
    }

    return () => {
      if (mediaStreamRef.current) {
        mediaStreamRef.current.getTracks().forEach(track => track.stop());
      }
      if (audioContextRef.current) {
        audioContextRef.current.close();
      }
    };
  }, [noiseReduction, voiceActivityDetection, silenceThreshold, noiseThreshold, onVoiceActivityStart, onVoiceActivityEnd, onNoiseDetected]);

  // Initialize speech recognition
  useEffect(() => {
    if (window.webkitSpeechRecognition) {
      recognitionRef.current = new window.webkitSpeechRecognition();
      recognitionRef.current.continuous = continuous;
      recognitionRef.current.interimResults = interimResults;
      recognitionRef.current.lang = language;

      recognitionRef.current.onstart = () => {
        setIsListening(true);
        setError(null);
        setLastSpeechTime(Date.now());
        onStart?.();

        // Set up timeout for no speech
        timeoutRef.current = setTimeout(() => {
          if (isListening) {
            handleError(SPEECH_ERRORS.TIMEOUT);
            onTimeout?.();
          }
        }, timeout);

        // Set up max duration timer
        maxDurationRef.current = setTimeout(() => {
          if (isListening) {
            handleError(SPEECH_ERRORS.QUOTA_EXCEEDED);
            onMaxDurationReached?.();
          }
        }, maxDuration);
      };

      recognitionRef.current.onresult = (event) => {
        setLastSpeechTime(Date.now());
        let finalTranscript = '';
        let currentInterim = '';

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          if (event.results[i].isFinal) {
            finalTranscript += transcript + ' ';
          } else {
            currentInterim += transcript;
          }
        }

        setTranscript(finalTranscript.trim());
        setInterimTranscript(currentInterim);
        onResult?.(finalTranscript.trim(), currentInterim);

        // Reset timeout on speech detection
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
          timeoutRef.current = setTimeout(() => {
            if (isListening) {
              handleError(SPEECH_ERRORS.TIMEOUT);
              onTimeout?.();
            }
          }, timeout);
        }
      };

      recognitionRef.current.onerror = (event) => {
        handleError(event.error);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
        if (timeoutRef.current) {
          clearTimeout(timeoutRef.current);
        }
        if (maxDurationRef.current) {
          clearTimeout(maxDurationRef.current);
        }
        onEnd?.();
      };
    } else {
      handleError(SPEECH_ERRORS.BROWSER_NOT_SUPPORTED);
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
      if (maxDurationRef.current) {
        clearTimeout(maxDurationRef.current);
      }
    };
  }, [continuous, interimResults, language, onResult, onError, onStart, onEnd, timeout, maxDuration, onTimeout, onMaxDurationReached]);

  const handleError = (errorType) => {
    const errorMessage = ERROR_MESSAGES[errorType] || ERROR_MESSAGES[SPEECH_ERRORS.UNKNOWN];
    setError(errorMessage);
    onError?.(errorType);
  };

  const startListening = useCallback(() => {
    if (recognitionRef.current) {
      try {
        recognitionRef.current.start();
      } catch (error) {
        handleError(SPEECH_ERRORS.UNKNOWN);
      }
    }
  }, []);

  const stopListening = useCallback(() => {
    if (recognitionRef.current) {
      recognitionRef.current.stop();
    }
  }, []);

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
    setError(null);
  }, []);

  const changeLanguage = useCallback((newLanguage) => {
    if (SUPPORTED_LANGUAGES[newLanguage]) {
      recognitionRef.current.lang = newLanguage;
      onLanguageChange?.(newLanguage);
    } else {
      handleError(SPEECH_ERRORS.LANGUAGE_NOT_SUPPORTED);
    }
  }, [onLanguageChange]);

  const changeVoice = useCallback((voice) => {
    if (voice && availableVoices.includes(voice)) {
      setSelectedVoice(voice);
      onVoiceChange?.(voice);
    }
  }, [availableVoices, onVoiceChange]);

  return {
    isListening,
    transcript,
    interimTranscript,
    error,
    startListening,
    stopListening,
    resetTranscript,
    changeLanguage,
    changeVoice,
    availableVoices,
    selectedVoice,
    supportedLanguages: SUPPORTED_LANGUAGES,
    lastSpeechTime,
    isVoiceActive,
    noiseLevel
  };
};

export default useSpeechToText; 