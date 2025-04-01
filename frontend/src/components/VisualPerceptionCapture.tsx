import React, { useEffect, useState, useCallback } from 'react';
import axios from 'axios';
import { Box, Button, Typography, Paper, CircularProgress, Divider, Chip, Alert } from '@mui/material';
import { PhotoCamera, Autorenew, Stop, VisibilityOff } from '@mui/icons-material';
import html2canvas from 'html2canvas';

// Define types for html2canvas instead of augmenting the module
interface Html2CanvasOptions {
  logging?: boolean;
  useCORS?: boolean;
  allowTaint?: boolean;
  backgroundColor?: string | null;
}

interface AnalysisResult {
  recognized_state: string;
  error_messages?: string[];
  status_messages?: string[];
  text_content?: string;
  ui_elements?: UIElement[];
  confidence: number;
  timestamp: string;
}

interface UIElement {
  id: string;
  type: string;
  bounds: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
}

interface VisualPerceptionCaptureProps {
  targetSelector?: string;
  captureInterval?: number;
  autoCapture?: boolean;
  onAnalysisResult?: (result: AnalysisResult) => void;
  apiEndpoint?: string;
  showControls?: boolean;
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left' | 'floating';
}

/**
 * VisualPerceptionCapture component
 * 
 * This component captures screenshots of the current view and sends them
 * to the Visual Perception MCP for analysis. It can be used for debugging
 * and to provide enhanced assistance capabilities.
 */
const VisualPerceptionCapture: React.FC<VisualPerceptionCaptureProps> = ({
  targetSelector = '#root',
  captureInterval = 5000,
  autoCapture = false,
  onAnalysisResult = null,
  apiEndpoint = '/api/mcp/visual/analyze',
  showControls = true,
  position = 'bottom-right'
}) => {
  const [lastAnalysis, setLastAnalysis] = useState<AnalysisResult | null>(null);
  const [isCapturing, setIsCapturing] = useState<boolean>(autoCapture);
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [isMinimized, setIsMinimized] = useState<boolean>(false);

  // Function to capture screenshot using html2canvas
  const captureScreenshot = useCallback(async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Get the target element
      const targetElement = document.querySelector(targetSelector);
      if (!targetElement) {
        throw new Error(`Target element not found: ${targetSelector}`);
      }
      
      // Capture the screenshot
      const canvas = await html2canvas(targetElement, {
        logging: false,
        useCORS: true,
        allowTaint: true,
        backgroundColor: null
      });
      
      // Convert to base64
      const imageData = canvas.toDataURL('image/png');
      
      // Send to the API
      const response = await axios.post(apiEndpoint, {
        image_data: imageData,
        context: {
          url: window.location.href,
          timestamp: new Date().toISOString(),
          viewport: {
            width: window.innerWidth,
            height: window.innerHeight
          }
        }
      });
      
      // Update state with analysis results
      setLastAnalysis(response.data);
      setError(null);
      
      // Call the callback if provided
      if (onAnalysisResult && typeof onAnalysisResult === 'function') {
        onAnalysisResult(response.data);
      }
      
      return response.data;
    } catch (err) {
      console.error('Error capturing or analyzing screenshot:', err);
      const errorMessage = err instanceof Error ? err.message : 'Unknown error occurred';
      setError(errorMessage);
      return null;
    } finally {
      setIsLoading(false);
    }
  }, [targetSelector, apiEndpoint, onAnalysisResult]);

  // Set up interval for auto-capture
  useEffect(() => {
    let intervalId: NodeJS.Timeout | null = null;
    
    if (isCapturing) {
      intervalId = setInterval(captureScreenshot, captureInterval);
    }
    
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [isCapturing, captureInterval, captureScreenshot]);

  // Get position styles
  const getPositionStyles = () => {
    switch (position) {
      case 'top-right':
        return { top: 16, right: 16 };
      case 'top-left':
        return { top: 16, left: 16 };
      case 'bottom-right':
        return { bottom: 16, right: 16 };
      case 'bottom-left':
        return { bottom: 16, left: 16 };
      case 'floating':
        return { bottom: '50%', right: '50%', transform: 'translate(50%, 50%)' };
      default:
        return { bottom: 16, right: 16 };
    }
  };

  // Toggle auto-capture
  const toggleAutoCapture = () => {
    setIsCapturing(prev => !prev);
  };

  // Toggle minimized state
  const toggleMinimized = () => {
    setIsMinimized(prev => !prev);
  };

  if (!showControls && !lastAnalysis) {
    return null;
  }

  return (
    <Paper
      elevation={3}
      sx={{
        position: 'fixed',
        zIndex: 9999,
        width: isMinimized ? 'auto' : 300,
        maxHeight: isMinimized ? 'auto' : 400,
        overflow: 'auto',
        padding: isMinimized ? 1 : 2,
        backgroundColor: 'background.paper',
        borderRadius: 2,
        ...getPositionStyles()
      }}
    >
      {isMinimized ? (
        <Button 
          size="small" 
          onClick={toggleMinimized}
          startIcon={<PhotoCamera />}
        >
          Visual Perception
        </Button>
      ) : (
        <>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
            <Typography variant="subtitle1" fontWeight="bold">
              Visual Perception MCP
            </Typography>
            <Button 
              size="small" 
              onClick={toggleMinimized}
              sx={{ minWidth: 'auto', p: 0.5 }}
            >
              <VisibilityOff fontSize="small" />
            </Button>
          </Box>
          
          {showControls && (
            <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
              <Button 
                variant="contained" 
                color="primary"
                onClick={captureScreenshot}
                disabled={isLoading}
                startIcon={<PhotoCamera />}
                size="small"
              >
                Capture
              </Button>
              <Button 
                variant="outlined" 
                color={isCapturing ? "error" : "primary"}
                onClick={toggleAutoCapture}
                disabled={isLoading}
                startIcon={isCapturing ? <Stop /> : <Autorenew />}
                size="small"
              >
                {isCapturing ? 'Stop Auto' : 'Auto Capture'}
              </Button>
            </Box>
          )}
          
          {isLoading && (
            <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
              <CircularProgress size={24} />
            </Box>
          )}
          
          {error && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {error}
            </Alert>
          )}
          
          {lastAnalysis && (
            <Box sx={{ mt: 2, p: 1, bgcolor: 'background.paper', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Analysis Results
              </Typography>
              
              <Typography variant="body2" color="text.secondary" gutterBottom>
                State: <Chip size="small" label={lastAnalysis.recognized_state} color={
                  lastAnalysis.recognized_state === 'normal' ? 'success' : 
                  lastAnalysis.recognized_state === 'error_state' ? 'error' : 'warning'
                } />
              </Typography>
              
              {lastAnalysis.status_messages && lastAnalysis.status_messages.length > 0 && (
                <Box sx={{ mt: 1, mb: 1 }}>
                  <Typography variant="caption" fontWeight="bold" color="text.secondary">
                    Status:
                  </Typography>
                  <Box component="ul" sx={{ m: 0, pl: 2 }}>
                    {lastAnalysis.status_messages.map((msg: string, i: number) => (
                      <Typography key={i} variant="caption" component="li">
                        {msg}
                      </Typography>
                    ))}
                  </Box>
                </Box>
              )}
              
              {lastAnalysis.error_messages && lastAnalysis.error_messages.length > 0 && (
                <Box sx={{ mt: 1, mb: 1 }}>
                  <Typography variant="caption" fontWeight="bold" color="error">
                    Detected Errors:
                  </Typography>
                  <Box component="ul" sx={{ m: 0, pl: 2 }}>
                    {lastAnalysis.error_messages.map((msg: string, i: number) => (
                      <Typography key={i} variant="caption" component="li">
                        {msg}
                      </Typography>
                    ))}
                  </Box>
                </Box>
              )}
              
              <Typography variant="caption" fontWeight="bold" color="text.secondary">
                UI Elements: {lastAnalysis.ui_elements?.length}
              </Typography>
              
              <Box sx={{ mt: 1 }}>
                <Typography variant="caption" fontWeight="bold" color="text.secondary">
                  Extracted Text:
                </Typography>
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    p: 1, 
                    mt: 0.5, 
                    maxHeight: 100, 
                    overflow: 'auto',
                    backgroundColor: 'background.default' 
                  }}
                >
                  <Typography variant="caption" component="pre" sx={{ m: 0, whiteSpace: 'pre-wrap' }}>
                    {lastAnalysis.text_content || "No text detected"}
                  </Typography>
                </Paper>
              </Box>
            </Box>
          )}
        </>
      )}
    </Paper>
  );
};

export default VisualPerceptionCapture;
