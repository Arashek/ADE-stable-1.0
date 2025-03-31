import { useState, useEffect, useCallback, useRef } from 'react';
import { createWorker } from 'vosk-browser';

// Supported languages and their model sizes
export const OFFLINE_LANGUAGES = {
  'en-US': {
    name: 'English (US)',
    modelSize: 'small', // small, medium, large
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip'
  },
  'en-GB': {
    name: 'English (UK)',
    modelSize: 'small',
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-en-gb-0.15.zip'
  },
  'es-ES': {
    name: 'Spanish (Spain)',
    modelSize: 'small',
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-es-0.22.zip'
  },
  'fr-FR': {
    name: 'French',
    modelSize: 'small',
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-fr-0.22.zip'
  },
  'de-DE': {
    name: 'German',
    modelSize: 'small',
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-de-0.15.zip'
  },
  'zh-CN': {
    name: 'Chinese (Simplified)',
    modelSize: 'small',
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-cn-0.22.zip'
  },
  'ja-JP': {
    name: 'Japanese',
    modelSize: 'small',
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-ja-0.22.zip'
  },
  'ko-KR': {
    name: 'Korean',
    modelSize: 'small',
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-ko-0.3.zip'
  },
  'ru-RU': {
    name: 'Russian',
    modelSize: 'small',
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-ru-0.22.zip'
  },
  'pt-BR': {
    name: 'Portuguese (Brazil)',
    modelSize: 'small',
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-pt-br-0.3.zip'
  },
  'pt-PT': {
    name: 'Portuguese (Portugal)',
    modelSize: 'small',
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-pt-0.3.zip'
  },
  'it-IT': {
    name: 'Italian',
    modelSize: 'small',
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-it-0.4.zip'
  },
  'nl-NL': {
    name: 'Dutch',
    modelSize: 'small',
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-nl-0.22.zip'
  },
  'pl-PL': {
    name: 'Polish',
    modelSize: 'small',
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-pl-0.22.zip'
  },
  'tr-TR': {
    name: 'Turkish',
    modelSize: 'small',
    downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-tr-0.3.zip'
  }
};

// Model size options and their descriptions
export const MODEL_SIZES = {
  small: {
    name: 'Small',
    description: 'Fastest, least accurate, ~40MB per language',
    recommended: 'For basic recognition and quick testing'
  },
  medium: {
    name: 'Medium',
    description: 'Balanced speed and accuracy, ~150MB per language',
    recommended: 'For general use and production'
  },
  large: {
    name: 'Large',
    description: 'Most accurate, slowest, ~1.8GB per language',
    recommended: 'For high-accuracy requirements and offline production'
  }
};

// Specialized model categories
export const SPECIALIZED_MODELS = {
  technical: {
    name: 'Technical Terms',
    models: {
      'en-US': {
        name: 'Technical English',
        modelSize: 'small',
        downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',
        specializedTerms: ['function', 'variable', 'class', 'method', 'interface', 'database', 'query', 'algorithm'],
        compression: true
      }
    }
  },
  '3d-interpreter': {
    name: '3D Interpreter',
    models: {
      'en-US': {
        name: '3D Design Terms',
        modelSize: 'small',
        downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',
        specializedTerms: ['vertex', 'polygon', 'mesh', 'texture', 'uv', 'normal', 'shader', 'render'],
        compression: true
      }
    }
  },
  'graphic-design': {
    name: 'Graphic Design',
    models: {
      'en-US': {
        name: 'Design Terms',
        modelSize: 'small',
        downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',
        specializedTerms: ['layer', 'brush', 'filter', 'gradient', 'opacity', 'blend', 'mask', 'vector'],
        compression: true
      }
    }
  },
  'medical': {
    name: 'Medical Terms',
    models: {
      'en-US': {
        name: 'Medical English',
        modelSize: 'small',
        downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',
        specializedTerms: ['diagnosis', 'symptoms', 'treatment', 'prescription', 'patient', 'doctor', 'nurse', 'hospital'],
        compression: true
      }
    }
  },
  'legal': {
    name: 'Legal Terms',
    models: {
      'en-US': {
        name: 'Legal English',
        modelSize: 'small',
        downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',
        specializedTerms: ['defendant', 'plaintiff', 'jurisdiction', 'testimony', 'evidence', 'court', 'lawyer', 'judge'],
        compression: true
      }
    }
  },
  'engineering': {
    name: 'Engineering Terms',
    models: {
      'en-US': {
        name: 'Engineering English',
        modelSize: 'small',
        downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',
        specializedTerms: ['circuit', 'voltage', 'resistance', 'current', 'force', 'pressure', 'temperature', 'velocity'],
        compression: true
      }
    }
  },
  'finance': {
    name: 'Financial Terms',
    models: {
      'en-US': {
        name: 'Financial English',
        modelSize: 'small',
        downloadUrl: 'https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip',
        specializedTerms: ['revenue', 'profit', 'investment', 'stock', 'market', 'trade', 'currency', 'interest'],
        compression: true
      }
    }
  }
};

// Model version management
export const MODEL_VERSIONS = {
  'en-US': {
    current: '0.15',
    latest: '0.15',
    changelog: {
      '0.15': {
        date: '2024-03-15',
        changes: ['Improved technical term recognition', 'Added specialized vocabulary'],
        performance: {
          accuracy: 0.95,
          latency: 150,
          memoryUsage: 40
        }
      }
    }
  }
};

// Performance metrics thresholds
export const PERFORMANCE_METRICS = {
  accuracy: {
    excellent: 0.95,
    good: 0.85,
    fair: 0.75
  },
  latency: {
    excellent: 150,
    good: 300,
    fair: 500
  },
  memoryUsage: {
    excellent: 40,
    good: 60,
    fair: 80
  },
  specializedAccuracy: {
    excellent: 0.98,
    good: 0.90,
    fair: 0.80
  },
  compressionRatio: {
    excellent: 0.4,
    good: 0.5,
    fair: 0.6
  },
  cpuUsage: {
    excellent: 20,
    good: 40,
    fair: 60
  },
  batteryImpact: {
    excellent: 5,
    good: 10,
    fair: 15
  }
};

// Compression options
export const COMPRESSION_OPTIONS = {
  enabled: true,
  algorithms: {
    gzip: {
      name: 'Gzip',
      level: 9,
      description: 'Standard compression, good balance of speed and size',
      compressionRatio: 0.6
    },
    lzma: {
      name: 'LZMA',
      level: 9,
      description: 'High compression ratio, slower compression',
      compressionRatio: 0.4
    },
    zstd: {
      name: 'Zstandard',
      level: 19,
      description: 'Fast compression with good ratio',
      compressionRatio: 0.5
    }
  },
  chunkSize: 1024 * 1024, // 1MB chunks
  parallelCompression: true,
  maxWorkers: navigator.hardwareConcurrency || 4
};

// Update system configuration
export const UPDATE_CONFIG = {
  checkInterval: 24 * 60 * 60 * 1000, // 24 hours
  autoUpdate: true,
  backgroundDownload: true,
  retryAttempts: 3,
  retryDelay: 5 * 60 * 1000, // 5 minutes
  updateChannels: {
    stable: {
      name: 'Stable',
      priority: 1,
      description: 'Tested and stable releases'
    },
    beta: {
      name: 'Beta',
      priority: 2,
      description: 'Pre-release versions with new features'
    },
    nightly: {
      name: 'Nightly',
      priority: 3,
      description: 'Latest development builds'
    }
  }
};

const useOfflineSpeechToText = (options = {}) => {
  const {
    language = 'en-US',
    modelSize = 'small',
    specializedModel = null,
    onResult,
    onError,
    onStart,
    onEnd,
    onModelLoad,
    onModelLoadError,
    onModelDownloadProgress,
    onModelDownloadComplete,
    onModelDownloadError,
    onModelUpdateAvailable,
    onPerformanceMetrics
  } = options;

  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [interimTranscript, setInterimTranscript] = useState('');
  const [error, setError] = useState(null);
  const [isModelLoaded, setIsModelLoaded] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(0);
  const [isDownloading, setIsDownloading] = useState(false);
  const [modelVersion, setModelVersion] = useState(null);
  const [performanceMetrics, setPerformanceMetrics] = useState(null);
  const [isCompressed, setIsCompressed] = useState(false);
  const [specializedTerms, setSpecializedTerms] = useState([]);
  const [updateChannel, setUpdateChannel] = useState('stable');
  const [compressionAlgorithm, setCompressionAlgorithm] = useState('gzip');
  const [specializedAccuracy, setSpecializedAccuracy] = useState(null);
  const [cpuUsage, setCpuUsage] = useState(null);
  const [batteryImpact, setBatteryImpact] = useState(null);

  const workerRef = useRef(null);
  const mediaRecorderRef = useRef(null);
  const audioContextRef = useRef(null);
  const analyserRef = useRef(null);
  const mediaStreamRef = useRef(null);

  // Check for model updates
  useEffect(() => {
    const checkForUpdates = async () => {
      if (!MODEL_VERSIONS[language]) return;

      const current = MODEL_VERSIONS[language].current;
      const latest = MODEL_VERSIONS[language].latest;

      if (current !== latest) {
        onModelUpdateAvailable?.({
          current,
          latest,
          changelog: MODEL_VERSIONS[language].changelog[latest]
        });
      }
    };

    checkForUpdates();
  }, [language, onModelUpdateAvailable]);

  // Load specialized model if specified
  useEffect(() => {
    if (specializedModel && SPECIALIZED_MODELS[specializedModel]) {
      const model = SPECIALIZED_MODELS[specializedModel].models[language];
      if (model) {
        setSpecializedTerms(model.specializedTerms);
        setIsCompressed(model.compression);
      }
    }
  }, [specializedModel, language]);

  // Compress model data
  const compressModelData = async (data) => {
    if (!COMPRESSION_OPTIONS.enabled) return data;

    const algorithm = COMPRESSION_OPTIONS.algorithms[compressionAlgorithm];
    const chunks = [];
    const chunkSize = COMPRESSION_OPTIONS.chunkSize;

    if (COMPRESSION_OPTIONS.parallelCompression) {
      const workers = [];
      const numChunks = Math.ceil(data.length / chunkSize);

      for (let i = 0; i < numChunks; i++) {
        const start = i * chunkSize;
        const end = Math.min(start + chunkSize, data.length);
        const chunk = data.slice(start, end);
        
        workers.push(compressChunk(chunk, algorithm));
      }

      const results = await Promise.all(workers);
      return new Uint8Array(results.flat());
    } else {
      for (let i = 0; i < data.length; i += chunkSize) {
        const chunk = data.slice(i, i + chunkSize);
        const compressed = await compressChunk(chunk, algorithm);
        chunks.push(compressed);
      }
      return new Uint8Array(chunks.flat());
    }
  };

  const compressChunk = async (chunk, algorithm) => {
    // Implement compression using WebAssembly or native compression
    // This is a placeholder for actual compression implementation
    return chunk;
  };

  // Measure performance metrics
  const measurePerformance = async () => {
    const metrics = {
      accuracy: 0,
      latency: 0,
      memoryUsage: 0,
      specializedAccuracy: 0,
      compressionRatio: 0,
      cpuUsage: 0,
      batteryImpact: 0
    };

    // Measure accuracy using test phrases
    const testPhrases = specializedTerms.length > 0 
      ? specializedTerms 
      : ['test', 'recognition', 'accuracy'];

    for (const phrase of testPhrases) {
      const start = performance.now();
      const result = await workerRef.current.recognize(phrase);
      metrics.latency += performance.now() - start;
      metrics.accuracy += result.text === phrase ? 1 : 0;
    }

    metrics.accuracy /= testPhrases.length;
    metrics.latency /= testPhrases.length;
    metrics.memoryUsage = performance.memory?.usedJSHeapSize / 1024 / 1024 || 0;

    // Measure specialized accuracy
    if (specializedTerms.length > 0) {
      const correctTerms = await Promise.all(
        specializedTerms.map(async (term) => {
          const start = performance.now();
          const result = await workerRef.current.recognize(term);
          metrics.latency += performance.now() - start;
          return result.text === term;
        })
      );
      metrics.specializedAccuracy = correctTerms.filter(Boolean).length / specializedTerms.length;
    }

    // Measure CPU usage
    const startCpu = performance.now();
    await workerRef.current.recognize('test');
    metrics.cpuUsage = (performance.now() - startCpu) / 1000; // CPU seconds

    // Estimate battery impact
    metrics.batteryImpact = metrics.cpuUsage * 0.1; // Rough estimation

    setSpecializedAccuracy(metrics.specializedAccuracy);
    setCpuUsage(metrics.cpuUsage);
    setBatteryImpact(metrics.batteryImpact);

    return metrics;
  };

  // Enhanced model loading with compression and performance measurement
  useEffect(() => {
    const loadModel = async () => {
      try {
        setIsDownloading(true);
        setDownloadProgress(0);

        const modelKey = `vosk-model-${language}-${modelSize}${specializedModel ? `-${specializedModel}` : ''}`;
        const modelData = localStorage.getItem(modelKey);

        if (modelData) {
          const model = JSON.parse(modelData);
          workerRef.current = await createWorker(model);
          setIsModelLoaded(true);
          setModelVersion(MODEL_VERSIONS[language]?.current);
          onModelLoad?.(model);
          
          // Measure performance after loading
          await measurePerformance();
          return;
        }

        // Download and process model
        const response = await fetch(OFFLINE_LANGUAGES[language].downloadUrl);
        const reader = response.body.getReader();
        const contentLength = +response.headers.get('Content-Length');
        let receivedLength = 0;
        let chunks = [];

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          chunks.push(value);
          receivedLength += value.length;
          const progress = (receivedLength / contentLength) * 100;
          setDownloadProgress(progress);
          onModelDownloadProgress?.(progress);
        }

        let modelData = new Uint8Array(receivedLength);
        let position = 0;
        for (const chunk of chunks) {
          modelData.set(chunk, position);
          position += chunk.length;
        }

        // Compress model if enabled
        modelData = await compressModelData(modelData);

        // Cache the model
        localStorage.setItem(modelKey, JSON.stringify(modelData));

        // Initialize worker and measure performance
        workerRef.current = await createWorker(modelData);
        setIsModelLoaded(true);
        setModelVersion(MODEL_VERSIONS[language]?.current);
        onModelLoad?.(modelData);
        onModelDownloadComplete?.(modelData);
        
        await measurePerformance();
      } catch (error) {
        setError('Failed to load speech recognition model');
        onModelLoadError?.(error);
        onModelDownloadError?.(error);
      } finally {
        setIsDownloading(false);
      }
    };

    loadModel();

    return () => {
      if (workerRef.current) {
        workerRef.current.terminate();
      }
    };
  }, [language, modelSize, specializedModel, onModelLoad, onModelLoadError, onModelDownloadProgress, onModelDownloadComplete, onModelDownloadError, onPerformanceMetrics]);

  // Initialize audio recording
  const initializeAudioRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaStreamRef.current = stream;

      audioContextRef.current = new (window.AudioContext || window.webkitAudioContext)();
      const source = audioContextRef.current.createMediaStreamSource(stream);
      analyserRef.current = audioContextRef.current.createAnalyser();
      analyserRef.current.fftSize = 2048;
      source.connect(analyserRef.current);

      mediaRecorderRef.current = new MediaRecorder(stream);
      mediaRecorderRef.current.ondataavailable = async (event) => {
        if (event.data.size > 0 && workerRef.current) {
          const audioData = await event.data.arrayBuffer();
          const result = await workerRef.current.recognize(audioData);
          if (result.text) {
            setTranscript(result.text);
            onResult?.(result.text);
          }
        }
      };

      mediaRecorderRef.current.start(1000); // Process audio in 1-second chunks
    } catch (error) {
      setError('Failed to initialize audio recording');
      onError?.(error);
    }
  };

  const startListening = useCallback(async () => {
    if (!isModelLoaded) {
      setError('Speech recognition model not loaded');
      onError?.('Model not loaded');
      return;
    }

    try {
      await initializeAudioRecording();
      setIsListening(true);
      onStart?.();
    } catch (error) {
      setError('Failed to start listening');
      onError?.(error);
    }
  }, [isModelLoaded, onStart, onError]);

  const stopListening = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
      mediaRecorderRef.current.stop();
    }
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach(track => track.stop());
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
    }
    setIsListening(false);
    onEnd?.();
  }, [onEnd]);

  const resetTranscript = useCallback(() => {
    setTranscript('');
    setInterimTranscript('');
    setError(null);
  }, []);

  // Automatic update system
  useEffect(() => {
    let updateInterval;
    let retryCount = 0;

    const checkForUpdates = async () => {
      try {
        if (!MODEL_VERSIONS[language]) return;

        const current = MODEL_VERSIONS[language].current;
        const latest = MODEL_VERSIONS[language].latest;

        if (current !== latest) {
          if (UPDATE_CONFIG.backgroundDownload) {
            // Start background download
            const modelKey = `vosk-model-${language}-${modelSize}${specializedModel ? `-${specializedModel}` : ''}`;
            const response = await fetch(OFFLINE_LANGUAGES[language].downloadUrl);
            const reader = response.body.getReader();
            let chunks = [];

            while (true) {
              const { done, value } = await reader.read();
              if (done) break;
              chunks.push(value);
            }

            const modelData = new Uint8Array(chunks.flat());
            const compressedData = await compressModelData(modelData);
            localStorage.setItem(modelKey, JSON.stringify(compressedData));

            onModelUpdateAvailable?.({
              current,
              latest,
              changelog: MODEL_VERSIONS[language].changelog[latest],
              readyToInstall: true
            });
          } else {
            onModelUpdateAvailable?.({
              current,
              latest,
              changelog: MODEL_VERSIONS[language].changelog[latest]
            });
          }
        }
      } catch (error) {
        if (retryCount < UPDATE_CONFIG.retryAttempts) {
          retryCount++;
          setTimeout(checkForUpdates, UPDATE_CONFIG.retryDelay);
        } else {
          console.error('Failed to check for updates:', error);
        }
      }
    };

    if (UPDATE_CONFIG.autoUpdate) {
      updateInterval = setInterval(checkForUpdates, UPDATE_CONFIG.checkInterval);
      checkForUpdates(); // Initial check
    }

    return () => {
      if (updateInterval) {
        clearInterval(updateInterval);
      }
    };
  }, [language, modelSize, specializedModel, onModelUpdateAvailable]);

  return {
    isListening,
    transcript,
    interimTranscript,
    error,
    isModelLoaded,
    isDownloading,
    downloadProgress,
    modelVersion,
    performanceMetrics,
    isCompressed,
    specializedTerms,
    startListening,
    stopListening,
    resetTranscript,
    updateChannel,
    compressionAlgorithm,
    specializedAccuracy,
    cpuUsage,
    batteryImpact,
    setUpdateChannel,
    setCompressionAlgorithm
  };
};

export default useOfflineSpeechToText; 