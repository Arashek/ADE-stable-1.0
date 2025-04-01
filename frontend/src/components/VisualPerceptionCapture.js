import React, { useEffect, useState } from 'react';
import axios from 'axios';

/**
 * VisualPerceptionCapture component
 * 
 * This component captures screenshots of the current view and sends them
 * to the Visual Perception MCP for analysis. It can be used for debugging
 * and to provide enhanced assistance capabilities.
 */
const VisualPerceptionCapture = ({ 
  targetSelector = '#root', 
  captureInterval = 5000,
  autoCapture = false,
  onAnalysisResult = null,
  apiEndpoint = '/api/mcp/visual/analyze'
}) => {
  const [lastAnalysis, setLastAnalysis] = useState(null);
  const [isCapturing, setIsCapturing] = useState(autoCapture);
  const [error, setError] = useState(null);

  // Function to capture screenshot using html2canvas
  const captureScreenshot = async () => {
    try {
      // Dynamically import html2canvas to avoid SSR issues
      const html2canvas = (await import('html2canvas')).default;
      
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
      setError(err.message || 'Unknown error occurred');
      return null;
    }
  };

  // Set up interval for auto-capture
  useEffect(() => {
    let intervalId = null;
    
    if (isCapturing) {
      intervalId = setInterval(captureScreenshot, captureInterval);
    }
    
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [isCapturing, captureInterval]);

  // Manual capture trigger
  const triggerCapture = () => {
    return captureScreenshot();
  };

  // Toggle auto-capture
  const toggleAutoCapture = () => {
    setIsCapturing(prev => !prev);
  };

  return (
    <div className="visual-perception-capture">
      <div className="controls">
        <button 
          onClick={triggerCapture}
          className="capture-btn"
        >
          Capture Screenshot
        </button>
        <button 
          onClick={toggleAutoCapture}
          className={`auto-capture-btn ${isCapturing ? 'active' : ''}`}
        >
          {isCapturing ? 'Stop Auto-Capture' : 'Start Auto-Capture'}
        </button>
      </div>
      
      {error && (
        <div className="error-message">
          Error: {error}
        </div>
      )}
      
      {lastAnalysis && (
        <div className="analysis-results">
          <h3>Last Analysis Results</h3>
          <div className="result-item">
            <strong>State:</strong> {lastAnalysis.recognized_state}
          </div>
          <div className="result-item">
            <strong>Time:</strong> {new Date(lastAnalysis.timestamp).toLocaleTimeString()}
          </div>
          
          {lastAnalysis.error_messages && lastAnalysis.error_messages.length > 0 && (
            <div className="result-section">
              <h4>Detected Errors:</h4>
              <ul>
                {lastAnalysis.error_messages.map((msg, i) => (
                  <li key={i}>{msg}</li>
                ))}
              </ul>
            </div>
          )}
          
          {lastAnalysis.status_messages && lastAnalysis.status_messages.length > 0 && (
            <div className="result-section">
              <h4>Status Messages:</h4>
              <ul>
                {lastAnalysis.status_messages.map((msg, i) => (
                  <li key={i}>{msg}</li>
                ))}
              </ul>
            </div>
          )}
          
          <div className="result-section">
            <h4>UI Elements Detected: {lastAnalysis.ui_elements.length}</h4>
          </div>
          
          <details>
            <summary>Full Text Content</summary>
            <pre>{lastAnalysis.text_content}</pre>
          </details>
        </div>
      )}
    </div>
  );
};

export default VisualPerceptionCapture;
