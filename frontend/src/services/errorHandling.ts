import axios from 'axios';

/**
 * Error categories for better organization and filtering
 */
export enum ErrorCategory {
  FRONTEND = 'FRONTEND',
  BACKEND = 'BACKEND',
  API = 'API',
  DATABASE = 'DATABASE',
  SYSTEM = 'SYSTEM',
  AGENT = 'AGENT',
  USER = 'USER',
  OTHER = 'OTHER'
}

/**
 * Error severity levels
 */
export enum ErrorSeverity {
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL'
}

/**
 * Error log interface
 */
export interface ErrorLog {
  id?: string;
  timestamp?: string;
  message: string;
  category: ErrorCategory;
  severity: ErrorSeverity;
  component: string;
  context?: Record<string, any>;
  stack_trace?: string | null;
}

// Constants
const API_URL = 'http://localhost:8000';
const ERROR_STORAGE_KEY = 'ade_error_logs';
const MAX_LOCAL_LOGS = 100;

/**
 * Log an error to the backend error logging system
 * Falls back to localStorage if the backend is unavailable
 */
export const logError = async (
  message: string,
  category: ErrorCategory = ErrorCategory.FRONTEND,
  severity: ErrorSeverity = ErrorSeverity.ERROR,
  component: string = 'unknown',
  context: Record<string, any> = {},
  stackTrace: string | null = null
): Promise<void> => {
  const errorLog: ErrorLog = {
    message,
    category,
    severity,
    component,
    context,
    stack_trace: stackTrace,
    timestamp: new Date().toISOString()
  };

  try {
    // First try to log to the backend
    await axios.post(`${API_URL}/api/errors/log`, errorLog);
  } catch (error) {
    console.warn('Error logging to backend, falling back to local storage', error);
    
    // Store in localStorage as backup
    try {
      const storedLogs = JSON.parse(localStorage.getItem(ERROR_STORAGE_KEY) || '[]');
      
      // Add new log and limit the size
      storedLogs.unshift(errorLog);
      if (storedLogs.length > MAX_LOCAL_LOGS) {
        storedLogs.length = MAX_LOCAL_LOGS;
      }
      
      localStorage.setItem(ERROR_STORAGE_KEY, JSON.stringify(storedLogs));
    } catch (storageError) {
      console.error('Failed to store error in localStorage', storageError);
    }
  }
  
  // Also log to console for development
  const consoleMethod = 
    severity === ErrorSeverity.CRITICAL || severity === ErrorSeverity.ERROR
      ? console.error
      : severity === ErrorSeverity.WARNING
      ? console.warn
      : console.info;
  
  consoleMethod(`[${severity}][${category}][${component}] ${message}`, context, stackTrace);
};

/**
 * Get errors from local storage (fallback when backend is unavailable)
 */
export const getLocalErrors = (): ErrorLog[] => {
  try {
    return JSON.parse(localStorage.getItem(ERROR_STORAGE_KEY) || '[]');
  } catch (error) {
    console.error('Failed to retrieve local error logs', error);
    return [];
  }
};

/**
 * Clear local error logs
 */
export const clearLocalErrors = (): void => {
  localStorage.removeItem(ERROR_STORAGE_KEY);
};

export default {
  logError,
  getLocalErrors,
  clearLocalErrors,
  ErrorCategory,
  ErrorSeverity
};
