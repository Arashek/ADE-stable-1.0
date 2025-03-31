import React, { useState, useMemo, useCallback, Suspense, ErrorBoundary, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Tooltip,
  IconButton,
  Card,
  CardContent,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  CircularProgress,
  Alert,
  useTheme,
  useMediaQuery,
  Button,
  Snackbar,
  Slider,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Info as InfoIcon,
  Timeline as TimelineIcon,
  Category as CategoryIcon,
  TrendingUp as TrendingUpIcon,
  Memory as MemoryIcon,
  AccessibilityNew as AccessibilityIcon,
  BugReport as BugReportIcon,
  VolumeUp as VolumeUpIcon,
  Speed as SpeedIcon,
  DevicesOther as DevicesOtherIcon
} from '@mui/icons-material';
import { ResponsiveHeatMap } from '@nivo/heatmap';
import { ResponsiveTreeMap } from '@nivo/treemap';
import { useTheme as useMuiTheme } from '@mui/material/styles';

// Lazy load visualization components
const HeatMap = React.lazy(() => import('./visualizations/HeatMap'));
const TreeMap = React.lazy(() => import('./visualizations/TreeMap'));

// Error boundary component
class VisualizationErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Visualization error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <Alert severity="error" sx={{ mt: 2 }}>
          Error rendering visualization: {this.state.error?.message}
        </Alert>
      );
    }

    return this.props.children;
  }
}

// Keyboard shortcut handler
const useKeyboardShortcuts = (onVisualizationChange) => {
  useEffect(() => {
    const handleKeyPress = (event) => {
      if (event.altKey) {
        switch (event.key.toLowerCase()) {
          case 'h':
            event.preventDefault();
            onVisualizationChange('heatmap');
            break;
          case 't':
            event.preventDefault();
            onVisualizationChange('treemap');
            break;
          default:
            break;
        }
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [onVisualizationChange]);
};

// Enhanced text-to-speech hook
const useTextToSpeech = () => {
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [speechRate, setSpeechRate] = useState(1);
  const [speechPitch, setSpeechPitch] = useState(1);
  const [speechVolume, setSpeechVolume] = useState(1);
  const [selectedVoice, setSelectedVoice] = useState(null);
  const [selectedLanguage, setSelectedLanguage] = useState('en-US');
  const [availableVoices, setAvailableVoices] = useState([]);
  const [availableLanguages, setAvailableLanguages] = useState([]);
  const utteranceRef = useRef(null);

  useEffect(() => {
    const loadVoices = () => {
      if (window.speechSynthesis) {
        const voices = window.speechSynthesis.getVoices();
        setAvailableVoices(voices);
        
        // Get unique languages
        const languages = [...new Set(voices.map(voice => voice.lang))];
        setAvailableLanguages(languages);

        // Set default voice
        if (voices.length > 0) {
          const defaultVoice = voices.find(voice => voice.lang === 'en-US') || voices[0];
          setSelectedVoice(defaultVoice);
        }
      }
    };

    // Load voices when they become available
    if (window.speechSynthesis) {
      loadVoices();
      window.speechSynthesis.onvoiceschanged = loadVoices;
    }

    return () => {
      if (window.speechSynthesis) {
        window.speechSynthesis.onvoiceschanged = null;
      }
    };
  }, []);

  const speak = useCallback((text) => {
    if (window.speechSynthesis && selectedVoice) {
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.rate = speechRate;
      utterance.pitch = speechPitch;
      utterance.volume = speechVolume;
      utterance.voice = selectedVoice;
      utterance.lang = selectedLanguage;
      utteranceRef.current = utterance;

      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);

      window.speechSynthesis.speak(utterance);
      setIsSpeaking(true);
    }
  }, [speechRate, speechPitch, speechVolume, selectedVoice, selectedLanguage]);

  const stopSpeaking = useCallback(() => {
    if (window.speechSynthesis) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  }, []);

  return {
    isSpeaking,
    speak,
    stopSpeaking,
    setSpeechRate,
    setSpeechPitch,
    setSpeechVolume,
    selectedVoice,
    setSelectedVoice,
    selectedLanguage,
    setSelectedLanguage,
    availableVoices,
    availableLanguages
  };
};

// Enhanced performance optimization hook
const usePerformanceOptimization = (entries, visualizationType) => {
  const [isOptimized, setIsOptimized] = useState(false);
  const [optimizationLevel, setOptimizationLevel] = useState('none');
  const [memoryWarning, setMemoryWarning] = useState(null);
  const [renderTime, setRenderTime] = useState(null);
  const [deviceType, setDeviceType] = useState('desktop');
  const workerRef = useRef(null);
  const frameRef = useRef(null);

  useEffect(() => {
    const detectDeviceType = () => {
      const ua = navigator.userAgent;
      if (/(tablet|ipad|playbook|silk)|(android(?!.*mobi))/i.test(ua)) {
        return 'tablet';
      }
      if (/Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua)) {
        return 'mobile';
      }
      return 'desktop';
    };

    const optimizeRendering = () => {
      const currentDeviceType = detectDeviceType();
      setDeviceType(currentDeviceType);

      if (entries.length > 10000) {
        // Check memory usage
        if (window.performance?.memory) {
          const memoryUsage = window.performance.memory;
          const usageRatio = memoryUsage.usedJSHeapSize / memoryUsage.jsHeapSizeLimit;

          // Device-specific optimization thresholds
          const thresholds = {
            mobile: { aggressive: 0.7, moderate: 0.5 },
            tablet: { aggressive: 0.8, moderate: 0.6 },
            desktop: { aggressive: 0.9, moderate: 0.7 }
          };

          const deviceThresholds = thresholds[currentDeviceType];
          const isLowEndDevice = navigator.deviceMemory < 4;

          if (usageRatio > deviceThresholds.aggressive || isLowEndDevice) {
            setOptimizationLevel('aggressive');
            setMemoryWarning('Critical memory usage detected. Applying aggressive optimization.');
          } else if (usageRatio > deviceThresholds.moderate) {
            setOptimizationLevel('moderate');
            setMemoryWarning('High memory usage detected. Applying moderate optimization.');
          } else {
            setOptimizationLevel('light');
            setMemoryWarning('Moderate memory usage detected. Applying light optimization.');
          }
          setIsOptimized(true);
        }

        // Use requestAnimationFrame for smooth rendering
        if (frameRef.current) {
          cancelAnimationFrame(frameRef.current);
        }

        frameRef.current = requestAnimationFrame(() => {
          const startTime = performance.now();
          // Perform rendering
          const endTime = performance.now();
          setRenderTime(endTime - startTime);
        });
      } else {
        setIsOptimized(false);
        setOptimizationLevel('none');
        setMemoryWarning(null);
        setRenderTime(null);
      }
    };

    optimizeRendering();
    return () => {
      if (frameRef.current) {
        cancelAnimationFrame(frameRef.current);
      }
      if (workerRef.current) {
        workerRef.current.terminate();
      }
    };
  }, [entries, visualizationType]);

  return { isOptimized, optimizationLevel, memoryWarning, renderTime, deviceType };
};

// Enhanced browser compatibility check
const useBrowserCompatibility = () => {
  const [isCompatible, setIsCompatible] = useState(true);
  const [warnings, setWarnings] = useState([]);
  const [features, setFeatures] = useState({});
  const [deviceCapabilities, setDeviceCapabilities] = useState({});
  const [browserInfo, setBrowserInfo] = useState({});

  useEffect(() => {
    const checkCompatibility = () => {
      const newWarnings = [];
      const newFeatures = {};
      const newCapabilities = {};
      const newBrowserInfo = {};

      // Check for required APIs
      if (!window.performance) {
        newWarnings.push('Performance API not supported');
        newFeatures.performanceAPI = false;
      } else {
        newFeatures.performanceAPI = true;
      }

      if (!window.ResizeObserver) {
        newWarnings.push('ResizeObserver not supported');
        newFeatures.resizeObserver = false;
      } else {
        newFeatures.resizeObserver = true;
      }

      // Check for Web Workers
      if (!window.Worker) {
        newWarnings.push('Web Workers not supported');
        newFeatures.webWorkers = false;
      } else {
        newFeatures.webWorkers = true;
      }

      // Check for WebGL support
      const canvas = document.createElement('canvas');
      const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
      if (!gl) {
        newWarnings.push('WebGL not supported');
        newFeatures.webgl = false;
      } else {
        newFeatures.webgl = true;
      }

      // Check for modern JavaScript features
      try {
        eval('async () => {}');
        newFeatures.asyncAwait = true;
      } catch {
        newWarnings.push('Async/Await not supported');
        newFeatures.asyncAwait = false;
      }

      // Check for Speech Synthesis
      if (!window.speechSynthesis) {
        newWarnings.push('Speech Synthesis not supported');
        newFeatures.speechSynthesis = false;
      } else {
        newFeatures.speechSynthesis = true;
      }

      // Check for Intersection Observer
      if (!window.IntersectionObserver) {
        newWarnings.push('Intersection Observer not supported');
        newFeatures.intersectionObserver = false;
      } else {
        newFeatures.intersectionObserver = true;
      }

      // Check for Service Workers
      if (!('serviceWorker' in navigator)) {
        newWarnings.push('Service Workers not supported');
        newFeatures.serviceWorker = false;
      } else {
        newFeatures.serviceWorker = true;
      }

      // Check for WebRTC
      if (!window.RTCPeerConnection) {
        newWarnings.push('WebRTC not supported');
        newFeatures.webRTC = false;
      } else {
        newFeatures.webRTC = true;
      }

      // Check device capabilities
      newCapabilities.deviceMemory = navigator.deviceMemory || 4;
      newCapabilities.hardwareConcurrency = navigator.hardwareConcurrency || 4;
      newCapabilities.connection = navigator.connection || { effectiveType: '4g' };
      newCapabilities.touchPoints = navigator.maxTouchPoints || 0;
      newCapabilities.battery = navigator.getBattery ? true : false;

      // Get browser information
      const ua = navigator.userAgent;
      newBrowserInfo.browser = /chrome/i.test(ua) ? 'Chrome' :
                              /firefox/i.test(ua) ? 'Firefox' :
                              /safari/i.test(ua) ? 'Safari' :
                              /edge/i.test(ua) ? 'Edge' :
                              /opera/i.test(ua) ? 'Opera' : 'Unknown';
      newBrowserInfo.version = ua.match(/(chrome|firefox|safari|edge|opera)\/?\s*([\d.]+)/i)?.[2] || 'Unknown';
      newBrowserInfo.platform = navigator.platform;
      newBrowserInfo.mobile = /Mobile|Android|iP(hone|od)|IEMobile|BlackBerry|Kindle|Silk-Accelerated|(hpw|web)OS|Opera M(obi|ini)/.test(ua);

      // Check for low-end devices
      if (newCapabilities.deviceMemory < 4 || newCapabilities.hardwareConcurrency < 4) {
        newWarnings.push('Device may have limited performance capabilities');
      }

      // Check network conditions
      if (newCapabilities.connection.effectiveType === '2g' || newCapabilities.connection.effectiveType === '3g') {
        newWarnings.push('Slow network connection detected');
      }

      setWarnings(newWarnings);
      setFeatures(newFeatures);
      setDeviceCapabilities(newCapabilities);
      setBrowserInfo(newBrowserInfo);
      setIsCompatible(newWarnings.length === 0);
    };

    checkCompatibility();
  }, []);

  return { isCompatible, warnings, features, deviceCapabilities, browserInfo };
};

// Enhanced accessibility hook
const useAccessibility = () => {
  const [isReducedMotion, setIsReducedMotion] = useState(false);
  const [isHighContrast, setIsHighContrast] = useState(false);
  const [fontSize, setFontSize] = useState(16);
  const [colorBlindMode, setColorBlindMode] = useState(false);
  const [lineHeight, setLineHeight] = useState(1.5);
  const [letterSpacing, setLetterSpacing] = useState(0);
  const [textSpacing, setTextSpacing] = useState(1);
  const [cursorSize, setCursorSize] = useState(1);
  const [focusHighlight, setFocusHighlight] = useState(true);
  const [screenReaderMode, setScreenReaderMode] = useState(false);
  const [keyboardNavigation, setKeyboardNavigation] = useState(true);

  useEffect(() => {
    // Check for reduced motion preference
    const motionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
    setIsReducedMotion(motionQuery.matches);

    // Check for high contrast mode
    const contrastQuery = window.matchMedia('(prefers-contrast: high)');
    setIsHighContrast(contrastQuery.matches);

    // Check for system font size
    const rootFontSize = parseFloat(getComputedStyle(document.documentElement).fontSize);
    setFontSize(rootFontSize);

    const handleMotionChange = (e) => setIsReducedMotion(e.matches);
    const handleContrastChange = (e) => setIsHighContrast(e.matches);

    motionQuery.addEventListener('change', handleMotionChange);
    contrastQuery.addEventListener('change', handleContrastChange);

    return () => {
      motionQuery.removeEventListener('change', handleMotionChange);
      contrastQuery.removeEventListener('change', handleContrastChange);
    };
  }, []);

  return {
    isReducedMotion,
    isHighContrast,
    fontSize,
    colorBlindMode,
    setColorBlindMode,
    lineHeight,
    setLineHeight,
    letterSpacing,
    setLetterSpacing,
    textSpacing,
    setTextSpacing,
    cursorSize,
    setCursorSize,
    focusHighlight,
    setFocusHighlight,
    screenReaderMode,
    setScreenReaderMode,
    keyboardNavigation,
    setKeyboardNavigation
  };
};

const AdvancedVisualizations = ({ entries, stats, timeRange }) => {
  const theme = useMuiTheme();
  const [visualizationType, setVisualizationType] = useState('heatmap');
  const [error, setError] = useState(null);
  const [showAccessibilityMenu, setShowAccessibilityMenu] = useState(false);
  const containerRef = useRef(null);

  // Enhanced hooks
  const { isOptimized, optimizationLevel, memoryWarning, renderTime, deviceType } = usePerformanceOptimization(entries, visualizationType);
  const { isCompatible, warnings, features, deviceCapabilities, browserInfo } = useBrowserCompatibility();
  const {
    isReducedMotion,
    isHighContrast,
    fontSize,
    colorBlindMode,
    setColorBlindMode,
    lineHeight,
    setLineHeight,
    letterSpacing,
    setLetterSpacing,
    textSpacing,
    setTextSpacing,
    cursorSize,
    setCursorSize,
    focusHighlight,
    setFocusHighlight,
    screenReaderMode,
    setScreenReaderMode,
    keyboardNavigation,
    setKeyboardNavigation
  } = useAccessibility();
  const {
    isSpeaking,
    speak,
    stopSpeaking,
    setSpeechRate,
    setSpeechPitch,
    setSpeechVolume,
    selectedVoice,
    setSelectedVoice,
    selectedLanguage,
    setSelectedLanguage,
    availableVoices,
    availableLanguages
  } = useTextToSpeech();

  // Keyboard shortcuts
  useKeyboardShortcuts(setVisualizationType);

  // Memoized data processing with enhanced optimization
  const processedData = useMemo(() => {
    try {
      if (isOptimized) {
        const optimizedEntries = entries.slice(0, 
          optimizationLevel === 'aggressive' ? 5000 :
          optimizationLevel === 'moderate' ? 7500 : 10000
        );

        if (features.webWorkers && workerRef.current) {
          // Use Web Worker for data processing
          return new Promise((resolve, reject) => {
            workerRef.current.postMessage({
              type: visualizationType,
              data: optimizedEntries,
              timeRange
            });

            workerRef.current.onmessage = (e) => {
              resolve(e.data);
            };

            workerRef.current.onerror = (error) => {
              reject(error);
            };
          });
        }

        return visualizationType === 'heatmap'
          ? processHeatMapData(optimizedEntries, timeRange)
          : processTreeMapData(optimizedEntries);
      }

      return visualizationType === 'heatmap'
        ? processHeatMapData(entries, timeRange)
        : processTreeMapData(entries);
    } catch (err) {
      setError(err);
      return null;
    }
  }, [entries, timeRange, visualizationType, isOptimized, optimizationLevel, features.webWorkers]);

  // Error handling callback
  const handleError = useCallback((error) => {
    setError(error);
  }, []);

  // Visualization type change handler
  const handleVisualizationChange = useCallback((event) => {
    setVisualizationType(event.target.value);
    setError(null);
  }, []);

  // Text-to-speech handlers
  const handleSpeakVisualization = useCallback(() => {
    const description = visualizationType === 'heatmap'
      ? 'Activity Heat Map showing the distribution of knowledge creation across different times and days.'
      : 'Knowledge Tree Map showing the hierarchical structure of knowledge based on tags and their relationships.';
    
    speak(description);
  }, [visualizationType, speak]);

  const handleStopSpeaking = useCallback(() => {
    stopSpeaking();
  }, [stopSpeaking]);

  // Loading fallback component
  const LoadingFallback = () => (
    <Box 
      display="flex" 
      justifyContent="center" 
      alignItems="center" 
      minHeight={400}
      role="status"
      aria-label="Loading visualization"
    >
      <CircularProgress />
    </Box>
  );

  return (
    <Card 
      sx={{ 
        p: 3, 
        height: '100%',
        ...(isHighContrast && {
          border: `2px solid ${theme.palette.primary.main}`,
          backgroundColor: theme.palette.background.paper
        })
      }}
    >
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography 
          variant="h6" 
          component="h2" 
          id="visualization-title"
          sx={{ fontSize: `${fontSize * 1.25}px` }}
        >
          Advanced Visualizations
        </Typography>
        <Box display="flex" alignItems="center" gap={1}>
          <IconButton
            onClick={() => setShowAccessibilityMenu(!showAccessibilityMenu)}
            aria-label="Accessibility settings"
            data-testid="accessibility-menu-button"
          >
            <AccessibilityIcon />
          </IconButton>
          <FormControl size="small" sx={{ minWidth: 200 }}>
            <InputLabel id="visualization-type-label">Visualization Type</InputLabel>
            <Select
              labelId="visualization-type-label"
              value={visualizationType}
              onChange={handleVisualizationChange}
              label="Visualization Type"
              aria-label="Select visualization type"
              aria-describedby="visualization-description"
            >
              <MenuItem value="heatmap">Activity Heat Map</MenuItem>
              <MenuItem value="treemap">Knowledge Tree Map</MenuItem>
            </Select>
          </FormControl>
          <Tooltip 
            title={
              visualizationType === 'heatmap'
                ? 'Shows the distribution of knowledge creation across different times and days'
                : 'Visualizes the hierarchical structure of knowledge based on tags and their relationships'
            }
            aria-label="Information about visualization"
          >
            <IconButton aria-label="Information about visualization">
              <InfoIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {warnings.map((warning, index) => (
        <Alert 
          key={index} 
          severity="warning" 
          sx={{ mb: 2 }}
          role="alert"
        >
          {warning}
        </Alert>
      ))}

      {memoryWarning && (
        <Alert 
          severity="warning" 
          sx={{ mb: 2 }}
          role="alert"
          icon={<MemoryIcon />}
        >
          {memoryWarning}
        </Alert>
      )}

      {error && (
        <Alert 
          severity="error" 
          sx={{ mb: 2 }}
          role="alert"
        >
          {error.message}
        </Alert>
      )}

      <Box 
        ref={containerRef}
        sx={{ 
          height: 400,
          position: 'relative',
          '& > *': { height: '100%' },
          animation: isReducedMotion ? 'none' : undefined,
          transition: isReducedMotion ? 'none' : undefined,
          ...(isHighContrast && {
            '& *': {
              outline: `2px solid ${theme.palette.primary.main}`
            }
          })
        }}
        data-testid={`${visualizationType}-container`}
        role="img"
        aria-label={visualizationType === 'heatmap' ? 'Activity Heat Map' : 'Knowledge Tree Map'}
        aria-live="polite"
        aria-atomic="true"
        aria-describedby="visualization-description"
      >
        <ErrorBoundary FallbackComponent={VisualizationErrorBoundary}>
          <Suspense fallback={<LoadingFallback />}>
            {visualizationType === 'heatmap' ? (
              <HeatMap
                data={processedData}
                onError={handleError}
                data-testid="heatmap-visualization"
                isOptimized={isOptimized}
                colorBlindMode={colorBlindMode}
              />
            ) : (
              <TreeMap
                data={processedData}
                onError={handleError}
                data-testid="treemap-visualization"
                isOptimized={isOptimized}
                colorBlindMode={colorBlindMode}
              />
            )}
          </Suspense>
        </ErrorBoundary>
      </Box>

      {showAccessibilityMenu && (
        <Box 
          sx={{ 
            mt: 2, 
            p: 2, 
            border: '1px solid',
            borderColor: 'divider',
            borderRadius: 1
          }}
          role="dialog"
          aria-label="Accessibility settings"
        >
          <Typography variant="subtitle1" gutterBottom>
            Accessibility Settings
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Button
                variant={colorBlindMode ? "contained" : "outlined"}
                onClick={() => setColorBlindMode(!colorBlindMode)}
                startIcon={<AccessibilityIcon />}
                aria-pressed={colorBlindMode}
              >
                Color Blind Mode
              </Button>
            </Grid>
            <Grid item xs={12}>
              <Typography gutterBottom>Text Size</Typography>
              <Slider
                value={fontSize}
                onChange={(_, value) => setFontSize(value)}
                min={12}
                max={24}
                step={1}
                aria-label="Text size"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography gutterBottom>Line Height</Typography>
              <Slider
                value={lineHeight}
                onChange={(_, value) => setLineHeight(value)}
                min={1}
                max={2}
                step={0.1}
                aria-label="Line height"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography gutterBottom>Letter Spacing</Typography>
              <Slider
                value={letterSpacing}
                onChange={(_, value) => setLetterSpacing(value)}
                min={-1}
                max={2}
                step={0.1}
                aria-label="Letter spacing"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography gutterBottom>Text Spacing</Typography>
              <Slider
                value={textSpacing}
                onChange={(_, value) => setTextSpacing(value)}
                min={1}
                max={2}
                step={0.1}
                aria-label="Text spacing"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography gutterBottom>Cursor Size</Typography>
              <Slider
                value={cursorSize}
                onChange={(_, value) => setCursorSize(value)}
                min={1}
                max={3}
                step={0.1}
                aria-label="Cursor size"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={focusHighlight}
                    onChange={(e) => setFocusHighlight(e.target.checked)}
                    aria-label="Focus highlight"
                  />
                }
                label="Focus Highlight"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={screenReaderMode}
                    onChange={(e) => setScreenReaderMode(e.target.checked)}
                    aria-label="Screen reader mode"
                  />
                }
                label="Screen Reader Mode"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    checked={keyboardNavigation}
                    onChange={(e) => setKeyboardNavigation(e.target.checked)}
                    aria-label="Keyboard navigation"
                  />
                }
                label="Keyboard Navigation"
              />
            </Grid>
            {features.speechSynthesis && (
              <>
                <Grid item xs={12}>
                  <Button
                    variant={isSpeaking ? "contained" : "outlined"}
                    onClick={isSpeaking ? handleStopSpeaking : handleSpeakVisualization}
                    startIcon={<VolumeUpIcon />}
                    aria-pressed={isSpeaking}
                  >
                    {isSpeaking ? 'Stop Speaking' : 'Read Visualization'}
                  </Button>
                </Grid>
                <Grid item xs={12}>
                  <Typography gutterBottom>Voice</Typography>
                  <Select
                    value={selectedVoice?.name || ''}
                    onChange={(e) => {
                      const voice = availableVoices.find(v => v.name === e.target.value);
                      setSelectedVoice(voice);
                    }}
                    fullWidth
                    aria-label="Select voice"
                  >
                    {availableVoices.map((voice) => (
                      <MenuItem key={voice.name} value={voice.name}>
                        {voice.name} ({voice.lang})
                      </MenuItem>
                    ))}
                  </Select>
                </Grid>
                <Grid item xs={12}>
                  <Typography gutterBottom>Language</Typography>
                  <Select
                    value={selectedLanguage}
                    onChange={(e) => setSelectedLanguage(e.target.value)}
                    fullWidth
                    aria-label="Select language"
                  >
                    {availableLanguages.map((lang) => (
                      <MenuItem key={lang} value={lang}>
                        {lang}
                      </MenuItem>
                    ))}
                  </Select>
                </Grid>
                <Grid item xs={12}>
                  <Typography gutterBottom>Speech Rate</Typography>
                  <Slider
                    value={speechRate}
                    onChange={(_, value) => setSpeechRate(value)}
                    min={0.5}
                    max={2}
                    step={0.1}
                    aria-label="Speech rate"
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography gutterBottom>Speech Pitch</Typography>
                  <Slider
                    value={speechPitch}
                    onChange={(_, value) => setSpeechPitch(value)}
                    min={0.5}
                    max={2}
                    step={0.1}
                    aria-label="Speech pitch"
                  />
                </Grid>
                <Grid item xs={12}>
                  <Typography gutterBottom>Speech Volume</Typography>
                  <Slider
                    value={speechVolume}
                    onChange={(_, value) => setSpeechVolume(value)}
                    min={0}
                    max={1}
                    step={0.1}
                    aria-label="Speech volume"
                  />
                </Grid>
              </>
            )}
          </Grid>
        </Box>
      )}

      <Typography 
        id="visualization-description"
        variant="body2" 
        color="text.secondary" 
        sx={{ 
          mt: 2,
          fontSize: `${fontSize}px`,
          lineHeight: lineHeight,
          letterSpacing: `${letterSpacing}px`,
          '& > *': {
            marginBottom: `${textSpacing}em`
          }
        }}
        role="text"
      >
        {visualizationType === 'heatmap'
          ? 'Shows the distribution of knowledge creation across different times and days. Color intensity indicates frequency of activity.'
          : 'Visualizes the hierarchical structure of knowledge based on tags and their relationships. Size indicates relative importance.'}
      </Typography>

      {isOptimized && (
        <Typography 
          variant="caption" 
          color="text.secondary" 
          sx={{ mt: 1 }}
          role="status"
        >
          Visualization optimized for performance with {optimizationLevel} optimization level
          {renderTime && ` (Render time: ${renderTime.toFixed(2)}ms)`}
        </Typography>
      )}

      {deviceCapabilities.connection && (
        <Typography 
          variant="caption" 
          color="text.secondary" 
          sx={{ mt: 1 }}
          role="status"
        >
          Network: {deviceCapabilities.connection.effectiveType}
        </Typography>
      )}
    </Card>
  );
};

// Data processing functions
const processHeatMapData = (entries, timeRange) => {
  try {
    const data = entries.map(entry => ({
      ...entry,
      created_at: new Date(entry.created_at)
    }));

    // Group by day and hour
    const groupedData = data.reduce((acc, entry) => {
      const date = entry.created_at;
      const day = date.getDay();
      const hour = date.getHours();
      const key = `${day}-${hour}`;
      
      acc[key] = (acc[key] || 0) + 1;
      return acc;
    }, {});

    return {
      data: groupedData,
      timeRange,
      maxValue: Math.max(...Object.values(groupedData))
    };
  } catch (error) {
    throw new Error(`Error processing heatmap data: ${error.message}`);
  }
};

const processTreeMapData = (entries) => {
  try {
    // Process tags and create hierarchical structure
    const tagHierarchy = entries.reduce((acc, entry) => {
      entry.tags.forEach(tag => {
        const parts = tag.split('.');
        let current = acc;
        
        parts.forEach((part, index) => {
          if (!current[part]) {
            current[part] = {
              value: 0,
              children: {}
            };
          }
          current[part].value += entry.importance_score;
          current = current[part].children;
        });
      });
      return acc;
    }, {});

    return {
      data: tagHierarchy,
      totalEntries: entries.length
    };
  } catch (error) {
    throw new Error(`Error processing treemap data: ${error.message}`);
  }
};

export default AdvancedVisualizations; 