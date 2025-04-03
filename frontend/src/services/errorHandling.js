/**
 * Error Handling Service for ADE Platform
 * 
 * This service provides standardized error handling functionality for the frontend components,
 * integrating with the backend error logging system.
 */

import axios from 'axios';

// Error categories matching the backend
export const ErrorCategory = {
  AGENT: "AGENT",
  API: "API",
  AUTH: "AUTH",
  DATABASE: "DATABASE",
  FRONTEND: "FRONTEND",
  IMPORT: "IMPORT",
  SYSTEM: "SYSTEM",
  COORDINATION: "COORDINATION",
  UNKNOWN: "UNKNOWN"
};

// Error severity levels matching the backend
export const ErrorSeverity = {
  CRITICAL: "CRITICAL",
  ERROR: "ERROR",
  WARNING: "WARNING",
  INFO: "INFO"
};

// Base URL for error logging API
const ERROR_API_URL = 'http://localhost:8000/api/errors';

/**
 * Log an error to the backend error logging system
 * 
 * @param {string} message - Error message
 * @param {string} category - Error category
 * @param {string} severity - Error severity
 * @param {string} component - Component where the error occurred
 * @param {object} context - Additional context information
 * @param {string} stackTrace - Error stack trace if available
 * @returns {Promise} - Promise that resolves when the error is logged
 */
export const logError = async (
  message,
  category = ErrorCategory.FRONTEND,
  severity = ErrorSeverity.ERROR,
  component = 'unknown',
  context = {},
  stackTrace = null
) => {
  try {
    // Try to log to backend
    const response = await axios.post(ERROR_API_URL, {
      message,
      category,
      severity,
      component,
      context,
      stack_trace: stackTrace
    });
    
    return response.data;
  } catch (error) {
    // If backend logging fails, log to console
    console.error('Error logging failed:', error);
    console.error('Original error:', { message, category, severity, component, context });
    
    // Store in localStorage as fallback
    storeErrorLocally({
      message,
      category,
      severity,
      component,
      context,
      stack_trace: stackTrace,
      timestamp: new Date().toISOString()
    });
    
    return null;
  }
};

/**
 * Store error in localStorage as fallback when backend is unavailable
 * 
 * @param {object} errorData - Error data to store
 */
const storeErrorLocally = (errorData) => {
  try {
    // Get existing errors or initialize empty array
    const storedErrors = JSON.parse(localStorage.getItem('ade_error_logs') || '[]');
    
    // Add new error and limit to 100 entries
    storedErrors.push(errorData);
    if (storedErrors.length > 100) {
      storedErrors.shift(); // Remove oldest error
    }
    
    // Save back to localStorage
    localStorage.setItem('ade_error_logs', JSON.stringify(storedErrors));
  } catch (e) {
    console.error('Failed to store error locally:', e);
  }
};

/**
 * Get locally stored errors
 * 
 * @returns {Array} Array of locally stored errors
 */
export const getLocalErrors = () => {
  try {
    return JSON.parse(localStorage.getItem('ade_error_logs') || '[]');
  } catch (e) {
    console.error('Failed to retrieve local errors:', e);
    return [];
  }
};

/**
 * Sync locally stored errors with the backend when connection is restored
 * 
 * @returns {Promise} Promise that resolves when sync is complete
 */
export const syncLocalErrors = async () => {
  const localErrors = getLocalErrors();
  
  if (localErrors.length === 0) {
    return { synced: 0 };
  }
  
  let syncedCount = 0;
  const failedErrors = [];
  
  for (const errorData of localErrors) {
    try {
      await axios.post(ERROR_API_URL, errorData);
      syncedCount++;
    } catch (e) {
      failedErrors.push(errorData);
    }
  }
  
  // Update localStorage with only failed errors
  localStorage.setItem('ade_error_logs', JSON.stringify(failedErrors));
  
  return {
    synced: syncedCount,
    failed: failedErrors.length
  };
};

/**
 * Higher-order function to wrap API calls with standardized error handling
 * 
 * @param {Function} apiCall - Async function that makes an API call
 * @param {string} component - Component name for error logging
 * @param {Function} onError - Optional callback for custom error handling
 * @returns {Function} Wrapped function with error handling
 */
export const withErrorHandling = (apiCall, component, onError) => {
  return async (...args) => {
    try {
      return await apiCall(...args);
    } catch (error) {
      // Extract relevant information
      const errorMessage = error.response?.data?.message || error.message || 'Unknown error';
      const statusCode = error.response?.status;
      const errorContext = {
        apiArgs: args,
        statusCode,
        responseData: error.response?.data
      };
      
      // Determine severity based on status code
      let severity = ErrorSeverity.ERROR;
      if (statusCode >= 500) {
        severity = ErrorSeverity.CRITICAL;
      } else if (statusCode === 401 || statusCode === 403) {
        severity = ErrorSeverity.WARNING;
      }
      
      // Log the error
      await logError(
        errorMessage,
        ErrorCategory.API,
        severity,
        component,
        errorContext,
        error.stack
      );
      
      // Call custom error handler if provided
      if (typeof onError === 'function') {
        onError(error, errorContext);
      }
      
      // Re-throw for caller to handle
      throw error;
    }
  };
};

/**
 * Create an error boundary utility for React components
 * 
 * @param {string} componentName - Name of the component
 * @param {Function} fallback - Optional fallback renderer function
 * @returns {object} Error boundary methods
 */
export const createErrorBoundary = (componentName, fallback) => {
  return {
    componentDidCatch: (error, errorInfo) => {
      logError(
        error.message,
        ErrorCategory.FRONTEND,
        ErrorSeverity.ERROR,
        componentName,
        { reactErrorInfo: errorInfo },
        error.stack
      );
    },
    fallback: fallback || ((error) => (
      <div className="error-boundary">
        <h3>Something went wrong</h3>
        <p>{error.message}</p>
      </div>
    ))
  };
};

export default {
  logError,
  getLocalErrors,
  syncLocalErrors,
  withErrorHandling,
  createErrorBoundary,
  ErrorCategory,
  ErrorSeverity
};
