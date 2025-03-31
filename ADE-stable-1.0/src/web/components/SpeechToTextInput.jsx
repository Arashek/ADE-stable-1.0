import React, { useState, useEffect } from 'react';
import {
  TextField,
  IconButton,
  Tooltip,
  CircularProgress,
  Box,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Slider,
  FormControlLabel,
  Switch,
  Alert,
  Snackbar,
  Chip
} from '@mui/material';
import {
  Mic as MicIcon,
  MicOff as MicOffIcon,
  Clear as ClearIcon,
  Settings as SettingsIcon,
  AccessibilityNew as AccessibilityIcon,
  Language as LanguageIcon,
  VolumeUp as VolumeUpIcon,
  Timer as TimerIcon,
  Speed as SpeedIcon,
  Update as UpdateIcon,
  Compression as CompressionIcon,
  Memory as MemoryIcon,
  BatteryChargingFull as BatteryIcon,
  Cpu as CpuIcon
} from '@mui/icons-material';
import useSpeechToText, { SUPPORTED_LANGUAGES, SPEECH_ERRORS } from '../hooks/useSpeechToText';
import useOfflineSpeechToText, {
  OFFLINE_LANGUAGES,
  MODEL_SIZES,
  SPECIALIZED_MODELS,
  MODEL_VERSIONS,
  PERFORMANCE_METRICS,
  COMPRESSION_OPTIONS,
  UPDATE_CONFIG
} from '../hooks/useOfflineSpeechToText';
import { PrivacySettings, PrivacyLevel, AttributionType, CustomPrivacyParameter } from '../models/PrivacySettings';

const SpeechToTextInput = ({
  value,
  onChange,
  onBlur,
  onFocus,
  label,
  placeholder,
  fullWidth,
  multiline,
  rows,
  error,
  helperText,
  disabled,
  continuous = false,
  interimResults = true,
  language = 'en-US',
  maxDuration = 60000,
  timeout = 5000,
  noiseReduction = true,
  voiceActivityDetection = true,
  silenceThreshold = 0.1,
  noiseThreshold = 0.05,
  onTimeout,
  onMaxDurationReached,
  onLanguageChange,
  onVoiceChange,
  onVoiceActivityStart,
  onVoiceActivityEnd,
  onNoiseDetected,
  offlineMode = false,
  modelSize = 'small',
  onModelLoad,
  onModelLoadError,
  onModelDownloadProgress,
  onModelDownloadComplete,
  onModelDownloadError,
  onModelSizeChange,
  specializedModel = null,
  onModelUpdateAvailable,
  onPerformanceMetrics,
  updateChannel = 'stable',
  compressionAlgorithm = 'gzip',
  onUpdateChannelChange,
  onCompressionAlgorithmChange,
  sx,
  ...props
}) => {
  const [inputValue, setInputValue] = useState(value || '');
  const [isFocused, setIsFocused] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [showAccessibility, setShowAccessibility] = useState(false);
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [fontSize, setFontSize] = useState(16);
  const [lineHeight, setLineHeight] = useState(1.5);
  const [letterSpacing, setLetterSpacing] = useState(0);
  const [highContrast, setHighContrast] = useState(false);
  const [reducedMotion, setReducedMotion] = useState(false);
  const [screenReaderMode, setScreenReaderMode] = useState(false);
  const [showNoiseLevel, setShowNoiseLevel] = useState(false);
  const [showModelProgress, setShowModelProgress] = useState(false);
  const [showPerformance, setShowPerformance] = useState(false);
  const [showUpdateDialog, setShowUpdateDialog] = useState(false);
  const [updateInfo, setUpdateInfo] = useState(null);
  const [showCompressionInfo, setShowCompressionInfo] = useState(false);
  const [showUpdateSettings, setShowUpdateSettings] = useState(false);

  const {
    isListening: isOnlineListening,
    transcript: onlineTranscript,
    interimTranscript: onlineInterimTranscript,
    error: onlineError,
    startListening: startOnlineListening,
    stopListening: stopOnlineListening,
    resetTranscript: resetOnlineTranscript,
    changeLanguage,
    changeVoice,
    availableVoices,
    selectedVoice,
    supportedLanguages,
    lastSpeechTime,
    isVoiceActive,
    noiseLevel,
    modelVersion,
    performanceMetrics,
    isCompressed,
    specializedTerms,
    updateChannel: currentUpdateChannel,
    compressionAlgorithm: currentCompressionAlgorithm,
    specializedAccuracy,
    cpuUsage,
    batteryImpact,
    setUpdateChannel,
    setCompressionAlgorithm
  } = useOfflineSpeechToText({
    language,
    modelSize,
    specializedModel,
    onResult: (finalTranscript, currentInterim) => {
      const newValue = finalTranscript || currentInterim;
      setInputValue(newValue);
      onChange?.(newValue);
    },
    onError: (error) => {
      setErrorMessage(error);
      setShowError(true);
    },
    onStart: () => {
      setShowNoiseLevel(true);
    },
    onEnd: () => {
      setShowNoiseLevel(false);
    },
    onModelLoad: () => {
      setShowModelProgress(false);
      onModelLoad?.();
    },
    onModelLoadError: (error) => {
      setShowModelProgress(false);
      setErrorMessage('Failed to load offline speech recognition model');
      setShowError(true);
      onModelLoadError?.(error);
    },
    onModelDownloadProgress: (progress) => {
      setShowModelProgress(true);
      onModelDownloadProgress?.(progress);
    },
    onModelDownloadComplete: () => {
      setShowModelProgress(false);
      onModelDownloadComplete?.();
    },
    onModelDownloadError: (error) => {
      setShowModelProgress(false);
      setErrorMessage('Failed to download speech recognition model');
      setShowError(true);
      onModelDownloadError?.(error);
    },
    onModelUpdateAvailable: (info) => {
      setUpdateInfo(info);
      setShowUpdateDialog(true);
      onModelUpdateAvailable?.(info);
    },
    onPerformanceMetrics: (metrics) => {
      onPerformanceMetrics?.(metrics);
    },
    updateChannel,
    compressionAlgorithm
  });

  const isListening = offlineMode ? isOnlineListening : isOnlineListening;
  const transcript = offlineMode ? onlineTranscript : onlineTranscript;
  const interimTranscript = offlineMode ? onlineInterimTranscript : onlineInterimTranscript;
  const error = offlineMode ? onlineError : onlineError;

  useEffect(() => {
    if (value !== undefined && value !== inputValue) {
      setInputValue(value);
    }
  }, [value]);

  const handleFocus = (event) => {
    setIsFocused(true);
    onFocus?.(event);
  };

  const handleBlur = (event) => {
    setIsFocused(false);
    onBlur?.(event);
  };

  const handleChange = (event) => {
    const newValue = event.target.value;
    setInputValue(newValue);
    onChange?.(newValue);
  };

  const handleClear = () => {
    setInputValue('');
    onChange?.('');
    if (offlineMode) {
      resetOnlineTranscript();
    } else {
      resetOnlineTranscript();
    }
  };

  const handleMicClick = () => {
    if (isListening) {
      if (offlineMode) {
        stopOnlineListening();
      } else {
        stopOnlineListening();
      }
    } else {
      if (offlineMode && !isModelLoaded) {
        setErrorMessage('Offline speech recognition model not loaded');
        setShowError(true);
        return;
      }
      if (offlineMode) {
        startOnlineListening();
      } else {
        startOnlineListening();
      }
    }
  };

  const handleLanguageChange = (event) => {
    changeLanguage(event.target.value);
  };

  const handleVoiceChange = (event) => {
    const voice = availableVoices.find(v => v.name === event.target.value);
    changeVoice(voice);
  };

  const handleErrorClose = () => {
    setShowError(false);
  };

  const inputStyles = {
    fontSize: `${fontSize}px`,
    lineHeight: lineHeight,
    letterSpacing: `${letterSpacing}px`,
    ...(highContrast && {
      backgroundColor: '#000',
      color: '#fff',
      '& .MuiInputBase-input': {
        color: '#fff',
      },
      '& .MuiInputLabel-root': {
        color: '#fff',
      },
    }),
    ...(reducedMotion && {
      transition: 'none',
    }),
  };

  const getPerformanceStatus = (metric, value) => {
    const thresholds = PERFORMANCE_METRICS[metric];
    if (value >= thresholds.excellent) return 'excellent';
    if (value >= thresholds.good) return 'good';
    if (value >= thresholds.fair) return 'fair';
    return 'poor';
  };

  const getPerformanceColor = (status) => {
    switch (status) {
      case 'excellent': return 'success.main';
      case 'good': return 'info.main';
      case 'fair': return 'warning.main';
      case 'poor': return 'error.main';
      default: return 'text.secondary';
    }
  };

  // Create default settings
  const settings = PrivacySettings();

  // Customize settings
  settings.privacy_level = PrivacyLevel.HIGH;
  settings.attribution_type = AttributionType.ANONYMOUS;
  settings.excluded_projects = ["sensitive_project"];
  settings.excluded_languages = ["internal_lang"];

  // Add custom parameter
  settings.custom_parameters["noise_factor"] = CustomPrivacyParameter(
    name="noise_factor",
    value=0.1,
    min_value=0.0,
    max_value=1.0,
    description="Amount of noise to add for differential privacy"
  );

  // Check privacy settings
  if (settings.can_share_pattern_type(PatternType.SOLUTION)) {
    const epsilon = settings.epsilon;  // Get differential privacy parameter
    if (!settings.is_project_excluded("my_project")) {
      // Share pattern...
    }
  }

  return (
    <Box sx={{ position: 'relative', ...sx }}>
      <TextField
        value={inputValue}
        onChange={handleChange}
        onFocus={handleFocus}
        onBlur={handleBlur}
        label={label}
        placeholder={placeholder}
        fullWidth={fullWidth}
        multiline={multiline}
        rows={rows}
        error={error || !!error}
        helperText={helperText || error}
        disabled={disabled}
        sx={inputStyles}
        InputProps={{
          endAdornment: (
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              {inputValue && (
                <Tooltip title="Clear input">
                  <IconButton
                    size="small"
                    onClick={handleClear}
                    disabled={disabled}
                    aria-label="Clear input"
                  >
                    <ClearIcon />
                  </IconButton>
                </Tooltip>
              )}
              <Tooltip title="Accessibility settings">
                <IconButton
                  size="small"
                  onClick={() => setShowAccessibility(true)}
                  disabled={disabled}
                  aria-label="Accessibility settings"
                >
                  <AccessibilityIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Speech settings">
                <IconButton
                  size="small"
                  onClick={() => setShowSettings(true)}
                  disabled={disabled}
                  aria-label="Speech settings"
                >
                  <SettingsIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title={isListening ? "Stop recording" : "Start recording"}>
                <IconButton
                  size="small"
                  onClick={handleMicClick}
                  disabled={disabled}
                  color={isListening ? "error" : "default"}
                  aria-label={isListening ? "Stop recording" : "Start recording"}
                >
                  {isListening ? <MicOffIcon /> : <MicIcon />}
                </IconButton>
              </Tooltip>
            </Box>
          )
        }}
        {...props}
      />
      {isListening && (
        <Box
          sx={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            mt: 1,
            p: 1,
            bgcolor: 'background.paper',
            borderRadius: 1,
            boxShadow: 3,
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}
          role="status"
          aria-live="polite"
        >
          <CircularProgress size={16} />
          <Typography variant="caption" color="text.secondary">
            Listening... {offlineMode && '(Offline Mode)'}
          </Typography>
          {showNoiseLevel && (
            <Box sx={{ ml: 'auto', display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="caption" color="text.secondary">
                Noise Level: {(noiseLevel * 100).toFixed(1)}%
              </Typography>
              <Box
                sx={{
                  width: 40,
                  height: 4,
                  bgcolor: 'grey.200',
                  borderRadius: 1,
                  overflow: 'hidden'
                }}
              >
                <Box
                  sx={{
                    width: `${Math.min(noiseLevel * 100, 100)}%`,
                    height: '100%',
                    bgcolor: noiseLevel > noiseThreshold ? 'error.main' : 'success.main',
                    transition: 'width 0.2s ease-in-out'
                  }}
                />
              </Box>
            </Box>
          )}
        </Box>
      )}
      {showModelProgress && (
        <Box
          sx={{
            position: 'absolute',
            top: '100%',
            left: 0,
            right: 0,
            mt: 1,
            p: 1,
            bgcolor: 'background.paper',
            borderRadius: 1,
            boxShadow: 3,
            display: 'flex',
            alignItems: 'center',
            gap: 1
          }}
        >
          <CircularProgress size={16} />
          <Typography variant="caption" color="text.secondary">
            Downloading speech recognition model: {downloadProgress.toFixed(1)}%
          </Typography>
        </Box>
      )}
      {interimTranscript && !isListening && (
        <Typography
          variant="caption"
          color="text.secondary"
          sx={{ mt: 0.5, display: 'block' }}
          role="status"
          aria-live="polite"
        >
          Interim: {interimTranscript}
        </Typography>
      )}

      {/* Enhanced Performance Metrics Dialog */}
      <Dialog
        open={showPerformance}
        onClose={() => setShowPerformance(false)}
        aria-labelledby="performance-dialog-title"
        aria-describedby="performance-dialog-description"
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle id="performance-dialog-title">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SpeedIcon />
            Performance Metrics
          </Box>
        </DialogTitle>
        <DialogContent>
          {performanceMetrics && (
            <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 3 }}>
              {/* General Performance */}
              <Box>
                <Typography variant="h6" gutterBottom>General Performance</Typography>
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2 }}>
                  <Box>
                    <Typography variant="subtitle2">Accuracy</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography>
                        {(performanceMetrics.accuracy * 100).toFixed(1)}%
                      </Typography>
                      <Typography
                        color={getPerformanceColor(getPerformanceStatus('accuracy', performanceMetrics.accuracy))}
                      >
                        ({getPerformanceStatus('accuracy', performanceMetrics.accuracy)})
                      </Typography>
                    </Box>
                  </Box>
                  <Box>
                    <Typography variant="subtitle2">Latency</Typography>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography>
                        {performanceMetrics.latency.toFixed(1)}ms
                      </Typography>
                      <Typography
                        color={getPerformanceColor(getPerformanceStatus('latency', performanceMetrics.latency))}
                      >
                        ({getPerformanceStatus('latency', performanceMetrics.latency)})
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </Box>

              {/* Resource Usage */}
              <Box>
                <Typography variant="h6" gutterBottom>Resource Usage</Typography>
                <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2 }}>
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <CpuIcon fontSize="small" />
                      <Typography variant="subtitle2">CPU Usage</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography>
                        {cpuUsage?.toFixed(1)}%
                      </Typography>
                      <Typography
                        color={getPerformanceColor(getPerformanceStatus('cpuUsage', cpuUsage))}
                      >
                        ({getPerformanceStatus('cpuUsage', cpuUsage)})
                      </Typography>
                    </Box>
                  </Box>
                  <Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <BatteryIcon fontSize="small" />
                      <Typography variant="subtitle2">Battery Impact</Typography>
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography>
                        {batteryImpact?.toFixed(1)}%
                      </Typography>
                      <Typography
                        color={getPerformanceColor(getPerformanceStatus('batteryImpact', batteryImpact))}
                      >
                        ({getPerformanceStatus('batteryImpact', batteryImpact)})
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              </Box>

              {/* Specialized Model Performance */}
              {specializedTerms.length > 0 && (
                <Box>
                  <Typography variant="h6" gutterBottom>Specialized Model Performance</Typography>
                  <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2 }}>
                    <Box>
                      <Typography variant="subtitle2">Specialized Accuracy</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography>
                          {(specializedAccuracy * 100).toFixed(1)}%
                        </Typography>
                        <Typography
                          color={getPerformanceColor(getPerformanceStatus('specializedAccuracy', specializedAccuracy))}
                        >
                          ({getPerformanceStatus('specializedAccuracy', specializedAccuracy)})
                        </Typography>
                      </Box>
                    </Box>
                    <Box>
                      <Typography variant="subtitle2">Specialized Terms</Typography>
                      <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                        {specializedTerms.map((term) => (
                          <Chip
                            key={term}
                            label={term}
                            size="small"
                            variant="outlined"
                          />
                        ))}
                      </Box>
                    </Box>
                  </Box>
                </Box>
              )}

              {/* Compression Performance */}
              {isCompressed && (
                <Box>
                  <Typography variant="h6" gutterBottom>Compression Performance</Typography>
                  <Box sx={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: 2 }}>
                    <Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <CompressionIcon fontSize="small" />
                        <Typography variant="subtitle2">Compression Ratio</Typography>
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography>
                          {(performanceMetrics.compressionRatio * 100).toFixed(1)}%
                        </Typography>
                        <Typography
                          color={getPerformanceColor(getPerformanceStatus('compressionRatio', performanceMetrics.compressionRatio))}
                        >
                          ({getPerformanceStatus('compressionRatio', performanceMetrics.compressionRatio)})
                        </Typography>
                      </Box>
                    </Box>
                    <Box>
                      <Typography variant="subtitle2">Algorithm</Typography>
                      <Typography>
                        {COMPRESSION_OPTIONS.algorithms[compressionAlgorithm].name}
                      </Typography>
                    </Box>
                  </Box>
                </Box>
              )}
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowPerformance(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Update Settings Dialog */}
      <Dialog
        open={showUpdateSettings}
        onClose={() => setShowUpdateSettings(false)}
        aria-labelledby="update-settings-dialog-title"
        aria-describedby="update-settings-dialog-description"
      >
        <DialogTitle id="update-settings-dialog-title">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <UpdateIcon />
            Update Settings
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControl fullWidth>
              <InputLabel id="update-channel-label">Update Channel</InputLabel>
              <Select
                labelId="update-channel-label"
                value={currentUpdateChannel}
                onChange={(e) => {
                  setUpdateChannel(e.target.value);
                  onUpdateChannelChange?.(e.target.value);
                }}
                label="Update Channel"
              >
                {Object.entries(UPDATE_CONFIG.updateChannels).map(([key, channel]) => (
                  <MenuItem key={key} value={key}>
                    <Box>
                      <Typography>{channel.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {channel.description}
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControlLabel
              control={
                <Switch
                  checked={UPDATE_CONFIG.autoUpdate}
                  onChange={(e) => {
                    // This would be implemented in the hook
                  }}
                />
              }
              label="Automatic Updates"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={UPDATE_CONFIG.backgroundDownload}
                  onChange={(e) => {
                    // This would be implemented in the hook
                  }}
                />
              }
              label="Background Download"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowUpdateSettings(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Compression Settings Dialog */}
      <Dialog
        open={showCompressionInfo}
        onClose={() => setShowCompressionInfo(false)}
        aria-labelledby="compression-info-dialog-title"
        aria-describedby="compression-info-dialog-description"
      >
        <DialogTitle id="compression-info-dialog-title">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <CompressionIcon />
            Compression Settings
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControl fullWidth>
              <InputLabel id="compression-algorithm-label">Compression Algorithm</InputLabel>
              <Select
                labelId="compression-algorithm-label"
                value={currentCompressionAlgorithm}
                onChange={(e) => {
                  setCompressionAlgorithm(e.target.value);
                  onCompressionAlgorithmChange?.(e.target.value);
                }}
                label="Compression Algorithm"
              >
                {Object.entries(COMPRESSION_OPTIONS.algorithms).map(([key, algorithm]) => (
                  <MenuItem key={key} value={key}>
                    <Box>
                      <Typography>{algorithm.name}</Typography>
                      <Typography variant="caption" color="text.secondary">
                        {algorithm.description}
                      </Typography>
                      <Typography variant="caption" display="block" color="text.secondary">
                        Compression Ratio: {(algorithm.compressionRatio * 100).toFixed(0)}%
                      </Typography>
                    </Box>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            <FormControlLabel
              control={
                <Switch
                  checked={COMPRESSION_OPTIONS.parallelCompression}
                  onChange={(e) => {
                    // This would be implemented in the hook
                  }}
                />
              }
              label={
                <Box>
                  <Typography>Parallel Compression</Typography>
                  <Typography variant="caption" color="text.secondary">
                    Uses multiple CPU cores for faster compression
                  </Typography>
                </Box>
              }
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCompressionInfo(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Model Update Dialog */}
      <Dialog
        open={showUpdateDialog}
        onClose={() => setShowUpdateDialog(false)}
        aria-labelledby="update-dialog-title"
        aria-describedby="update-dialog-description"
      >
        <DialogTitle id="update-dialog-title">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <UpdateIcon />
            Model Update Available
          </Box>
        </DialogTitle>
        <DialogContent>
          {updateInfo && (
            <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Typography>
                A new version ({updateInfo.latest}) of the speech recognition model is available.
                Current version: {updateInfo.current}
              </Typography>
              <Typography variant="subtitle2">Changes:</Typography>
              <ul>
                {updateInfo.changelog.changes.map((change, index) => (
                  <li key={index}>{change}</li>
                ))}
              </ul>
              <Typography variant="subtitle2">Performance:</Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Typography>
                  Accuracy: {(updateInfo.changelog.performance.accuracy * 100).toFixed(1)}%
                </Typography>
                <Typography>
                  Latency: {updateInfo.changelog.performance.latency}ms
                </Typography>
                <Typography>
                  Memory Usage: {updateInfo.changelog.performance.memoryUsage}MB
                </Typography>
              </Box>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowUpdateDialog(false)}>Later</Button>
          <Button
            variant="contained"
            onClick={() => {
              setShowUpdateDialog(false);
              // Trigger model update
              // This would be implemented in the hook
            }}
          >
            Update Now
          </Button>
        </DialogActions>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog
        open={showSettings}
        onClose={() => setShowSettings(false)}
        aria-labelledby="settings-dialog-title"
        aria-describedby="settings-dialog-description"
      >
        <DialogTitle id="settings-dialog-title">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <SettingsIcon />
            Speech Settings
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <FormControlLabel
              control={
                <Switch
                  checked={offlineMode}
                  onChange={(e) => {
                    if (e.target.checked && !isModelLoaded) {
                      setShowModelProgress(true);
                    }
                  }}
                />
              }
              label="Offline Mode"
            />

            {offlineMode && (
              <FormControl fullWidth>
                <InputLabel id="model-size-label">Model Size</InputLabel>
                <Select
                  labelId="model-size-label"
                  value={modelSize}
                  onChange={(e) => {
                    const newSize = e.target.value;
                    setShowModelProgress(true);
                    onModelSizeChange?.(newSize);
                  }}
                  label="Model Size"
                >
                  {Object.entries(MODEL_SIZES).map(([size, info]) => (
                    <MenuItem key={size} value={size}>
                      <Box>
                        <Typography>{info.name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {info.description}
                        </Typography>
                        <Typography variant="caption" display="block" color="text.secondary">
                          Recommended: {info.recommended}
                        </Typography>
                      </Box>
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}

            <FormControl fullWidth>
              <InputLabel id="language-label">Language</InputLabel>
              <Select
                labelId="language-label"
                value={language}
                onChange={handleLanguageChange}
                label="Language"
              >
                {Object.entries(offlineMode ? OFFLINE_LANGUAGES : supportedLanguages).map(([code, info]) => (
                  <MenuItem key={code} value={code}>
                    {offlineMode ? info.name : info}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {!offlineMode && (
              <FormControl fullWidth>
                <InputLabel id="voice-label">Voice</InputLabel>
                <Select
                  labelId="voice-label"
                  value={selectedVoice?.name || ''}
                  onChange={handleVoiceChange}
                  label="Voice"
                >
                  {availableVoices.map((voice) => (
                    <MenuItem key={voice.name} value={voice.name}>
                      {voice.name} ({voice.lang})
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            )}

            <Box>
              <Typography gutterBottom>Voice Activity Detection</Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={voiceActivityDetection}
                    onChange={(e) => onVoiceActivityStart?.(e.target.checked)}
                  />
                }
                label="Enable Voice Activity Detection"
              />
              {voiceActivityDetection && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Silence Threshold
                  </Typography>
                  <Slider
                    value={silenceThreshold}
                    onChange={(_, value) => onVoiceActivityStart?.(value)}
                    min={0.01}
                    max={0.5}
                    step={0.01}
                    marks
                    valueLabelDisplay="auto"
                  />
                </Box>
              )}
            </Box>

            <Box>
              <Typography gutterBottom>Noise Reduction</Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={noiseReduction}
                    onChange={(e) => onNoiseDetected?.(e.target.checked)}
                  />
                }
                label="Enable Noise Reduction"
              />
              {noiseReduction && (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="caption" color="text.secondary">
                    Noise Threshold
                  </Typography>
                  <Slider
                    value={noiseThreshold}
                    onChange={(_, value) => onNoiseDetected?.(value)}
                    min={0.01}
                    max={0.5}
                    step={0.01}
                    marks
                    valueLabelDisplay="auto"
                  />
                </Box>
              )}
            </Box>

            <Box>
              <Typography gutterBottom>Maximum Duration (seconds)</Typography>
              <Slider
                value={maxDuration / 1000}
                onChange={(_, value) => onMaxDurationReached?.(value * 1000)}
                min={10}
                max={300}
                step={10}
                marks
                valueLabelDisplay="auto"
              />
            </Box>

            <Box>
              <Typography gutterBottom>Timeout (seconds)</Typography>
              <Slider
                value={timeout / 1000}
                onChange={(_, value) => onTimeout?.(value * 1000)}
                min={1}
                max={30}
                step={1}
                marks
                valueLabelDisplay="auto"
              />
            </Box>

            <FormControlLabel
              control={
                <Switch
                  checked={continuous}
                  onChange={(e) => onLanguageChange?.(e.target.checked)}
                />
              }
              label="Continuous Recording"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={interimResults}
                  onChange={(e) => onVoiceChange?.(e.target.checked)}
                />
              }
              label="Show Interim Results"
            />

            {offlineMode && (
              <>
                <FormControl fullWidth>
                  <InputLabel id="specialized-model-label">Specialized Model</InputLabel>
                  <Select
                    labelId="specialized-model-label"
                    value={specializedModel || ''}
                    onChange={(e) => {
                      const newModel = e.target.value;
                      if (newModel) {
                        setShowModelProgress(true);
                      }
                    }}
                    label="Specialized Model"
                  >
                    <MenuItem value="">None (General Purpose)</MenuItem>
                    {Object.entries(SPECIALIZED_MODELS).map(([key, model]) => (
                      <MenuItem key={key} value={key}>
                        <Box>
                          <Typography>{model.name}</Typography>
                          <Typography variant="caption" color="text.secondary">
                            {model.models[language]?.specializedTerms.length || 0} specialized terms
                          </Typography>
                        </Box>
                      </MenuItem>
                    ))}
                  </Select>
                </FormControl>

                <FormControlLabel
                  control={
                    <Switch
                      checked={isCompressed}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setShowModelProgress(true);
                        }
                      }}
                    />
                  }
                  label={
                    <Box>
                      <Typography>Model Compression</Typography>
                      <Typography variant="caption" color="text.secondary">
                        Reduces model size by ~60% (may affect performance)
                      </Typography>
                    </Box>
                  }
                />

                <Button
                  startIcon={<SpeedIcon />}
                  onClick={() => setShowPerformance(true)}
                >
                  View Performance Metrics
                </Button>
              </>
            )}
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Accessibility Dialog */}
      <Dialog
        open={showAccessibility}
        onClose={() => setShowAccessibility(false)}
        aria-labelledby="accessibility-dialog-title"
        aria-describedby="accessibility-dialog-description"
      >
        <DialogTitle id="accessibility-dialog-title">
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <AccessibilityIcon />
            Accessibility Settings
          </Box>
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
            <Box>
              <Typography gutterBottom>Font Size</Typography>
              <Slider
                value={fontSize}
                onChange={(_, value) => setFontSize(value)}
                min={12}
                max={24}
                step={1}
                marks
                valueLabelDisplay="auto"
              />
            </Box>

            <Box>
              <Typography gutterBottom>Line Height</Typography>
              <Slider
                value={lineHeight}
                onChange={(_, value) => setLineHeight(value)}
                min={1}
                max={2}
                step={0.1}
                marks
                valueLabelDisplay="auto"
              />
            </Box>

            <Box>
              <Typography gutterBottom>Letter Spacing</Typography>
              <Slider
                value={letterSpacing}
                onChange={(_, value) => setLetterSpacing(value)}
                min={-1}
                max={2}
                step={0.1}
                marks
                valueLabelDisplay="auto"
              />
            </Box>

            <FormControlLabel
              control={
                <Switch
                  checked={highContrast}
                  onChange={(e) => setHighContrast(e.target.checked)}
                />
              }
              label="High Contrast Mode"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={reducedMotion}
                  onChange={(e) => setReducedMotion(e.target.checked)}
                />
              }
              label="Reduced Motion"
            />

            <FormControlLabel
              control={
                <Switch
                  checked={screenReaderMode}
                  onChange={(e) => setScreenReaderMode(e.target.checked)}
                />
              }
              label="Screen Reader Mode"
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAccessibility(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Error Snackbar */}
      <Snackbar
        open={showError}
        autoHideDuration={6000}
        onClose={handleErrorClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleErrorClose} severity="error" sx={{ width: '100%' }}>
          {errorMessage}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default SpeechToTextInput; 