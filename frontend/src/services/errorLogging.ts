/**
 * Error Logging Service
 * 
 * This service provides a unified interface for logging errors from the frontend
 * to the ADE platform's error logging system. It handles communication with the 
 * error logging server and provides utility functions for error categorization.
 */

// Error categories supported by the ADE platform
export type ErrorCategory = 'AGENT' | 'API' | 'FRONTEND' | 'BACKEND' | 'INTEGRATION' | 'SYSTEM';

// Error severity levels
export type ErrorSeverity = 'CRITICAL' | 'ERROR' | 'WARNING' | 'INFO';

// Error log interface
export interface ErrorLog {
  timestamp: string;
  error_type: string;
  message: string;
  category: ErrorCategory;
  severity: ErrorSeverity;
  component: string;
  context?: any;
  stack_trace?: string;
}

// Configuration for the error logging service
const config = {
  apiUrl: process.env.REACT_APP_ERROR_LOGGING_API_URL || '/api/error-logs',
  enableConsoleLogging: process.env.NODE_ENV === 'development',
  batchSize: 10, // Number of errors to accumulate before sending batch
  flushInterval: 10000, // Flush queued errors every 10 seconds
};

// Queue for batching error logs
let errorQueue: ErrorLog[] = [];
let flushTimerId: NodeJS.Timeout | null = null;

/**
 * Initialize the error logging service
 */
export const initErrorLogging = () => {
  // Set up periodic flushing of error queue
  if (flushTimerId === null) {
    flushTimerId = setInterval(flushErrorQueue, config.flushInterval);
    
    // Add window unload event to flush any remaining errors
    window.addEventListener('beforeunload', flushErrorQueue);
    
    console.log('[ErrorLogging] Service initialized');
  }
  
  return {
    logError,
    logFrontendError,
    logAgentError,
    logApiError,
    flushErrorQueue,
  };
};

/**
 * Log an error to the ADE platform's error logging system
 */
export const logError = async (
  category: ErrorCategory,
  severity: ErrorSeverity,
  message: string,
  context?: any,
  errorType?: string,
  component?: string
): Promise<void> => {
  const errorLog: ErrorLog = {
    timestamp: new Date().toISOString(),
    error_type: errorType || 'General Error',
    message,
    category,
    severity,
    component: component || 'Unknown',
    context,
  };
  
  // Add error to queue
  errorQueue.push(errorLog);
  
  // If in development, also log to console
  if (config.enableConsoleLogging) {
    console.error(`[${category}][${severity}] ${message}`, context);
  }
  
  // If queue exceeds batch size, flush it
  if (errorQueue.length >= config.batchSize) {
    flushErrorQueue();
  }
};

/**
 * Flush the error queue by sending all accumulated errors to the logging server
 */
export const flushErrorQueue = async (): Promise<void> => {
  if (errorQueue.length === 0) return;
  
  const errorsToSend = [...errorQueue];
  errorQueue = [];
  
  try {
    // Send errors to the error logging API
    const response = await fetch(config.apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        logs: errorsToSend,
      }),
    });
    
    if (!response.ok) {
      throw new Error(`Error logging API returned ${response.status}: ${response.statusText}`);
    }
    
    if (config.enableConsoleLogging) {
      console.log(`[ErrorLogging] Successfully sent ${errorsToSend.length} error logs`);
    }
  } catch (error) {
    // If sending fails, add errors back to queue for retry
    errorQueue = [...errorsToSend, ...errorQueue];
    
    if (config.enableConsoleLogging) {
      console.error('[ErrorLogging] Failed to send error logs:', error);
    }
  }
};

/**
 * Utility function for logging frontend errors
 */
export const logFrontendError = (
  message: string,
  severity: ErrorSeverity = 'ERROR',
  component: string = 'Frontend',
  context?: any,
  errorType?: string
): void => {
  logError('FRONTEND', severity, message, context, errorType, component);
};

/**
 * Utility function for logging agent errors
 */
export const logAgentError = (
  message: string,
  severity: ErrorSeverity = 'ERROR',
  component: string = 'AgentSystem',
  context?: any,
  errorType?: string
): void => {
  logError('AGENT', severity, message, context, errorType, component);
};

/**
 * Utility function for logging API errors
 */
export const logApiError = (
  message: string,
  severity: ErrorSeverity = 'ERROR',
  component: string = 'ApiClient',
  context?: any,
  errorType?: string
): void => {
  logError('API', severity, message, context, errorType, component);
};

// Initialize error logging when module is imported
export default initErrorLogging();
