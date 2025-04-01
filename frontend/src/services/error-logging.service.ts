/**
 * Error Logging Service for ADE Frontend
 * 
 * This service provides comprehensive error logging, reporting, and handling 
 * functionality for the ADE frontend application. It captures unhandled 
 * exceptions, API errors, and user-reported issues, then sends them to the 
 * backend for centralized logging and analysis.
 */

import { api } from './api';

export enum ErrorCategory {
  AUTHENTICATION = 'AUTHENTICATION',
  AUTHORIZATION = 'AUTHORIZATION',
  API = 'API',
  VALIDATION = 'VALIDATION',
  UI = 'UI',
  STATE = 'STATE',
  RENDERING = 'RENDERING',
  PERFORMANCE = 'PERFORMANCE',
  NETWORK = 'NETWORK',
  INTEGRATION = 'INTEGRATION',
  UNKNOWN = 'UNKNOWN'
}

export enum ErrorSeverity {
  DEBUG = 'DEBUG',
  INFO = 'INFO',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
  CRITICAL = 'CRITICAL'
}

interface ErrorContext {
  [key: string]: any;
}

interface ErrorLogRequest {
  message: string;
  error_type?: string;
  category: string;
  severity: string;
  component: string;
  source?: string;
  stack_trace?: string;
  user_id?: string;
  request_id?: string;
  context?: ErrorContext;
}

interface ErrorLogResponse {
  error_id: string;
  timestamp: string;
  status: string;
}

class ErrorLoggingService {
  private readonly apiEndpoint = '/api/error-logging/log';
  private readonly consoleErrorOriginal: typeof console.error;
  private readonly windowOnErrorOriginal: typeof window.onerror;
  private readonly windowOnUnhandledRejectionOriginal: typeof window.onunhandledrejection;
  
  constructor() {
    // Store original console methods for fallback
    this.consoleErrorOriginal = console.error;
    this.windowOnErrorOriginal = window.onerror;
    this.windowOnUnhandledRejectionOriginal = window.onunhandledrejection;
    
    // Initialize global error handlers
    this.setupGlobalErrorHandlers();
  }
  
  /**
   * Set up global error handlers to capture unhandled exceptions
   */
  private setupGlobalErrorHandlers(): void {
    // Override console.error
    console.error = (...args: any[]) => {
      // Call original console.error
      this.consoleErrorOriginal.apply(console, args);
      
      // If the first argument is an Error object, log it
      if (args[0] instanceof Error) {
        this.logError({
          message: args[0].message,
          error_type: args[0].name,
          category: ErrorCategory.UNKNOWN,
          severity: ErrorSeverity.ERROR,
          component: 'console',
          stack_trace: args[0].stack,
          context: { console: true, args: args.slice(1).map(arg => String(arg)) }
        });
      }
    };
    
    // Handle uncaught errors
    window.onerror = (message, source, lineno, colno, error) => {
      // Call original handler if it exists
      if (this.windowOnErrorOriginal) {
        this.windowOnErrorOriginal.call(window, message, source, lineno, colno, error);
      }
      
      this.logError({
        message: String(message),
        error_type: error ? error.name : 'Error',
        category: ErrorCategory.UNKNOWN,
        severity: ErrorSeverity.ERROR,
        component: 'window',
        source: source?.toString(),
        stack_trace: error?.stack,
        context: { lineno, colno }
      });
      
      // Don't prevent default handling
      return false;
    };
    
    // Handle unhandled promise rejections
    window.onunhandledrejection = (event: PromiseRejectionEvent) => {
      // Call original handler if it exists
      if (this.windowOnUnhandledRejectionOriginal) {
        this.windowOnUnhandledRejectionOriginal.call(window, event);
      }
      
      const reason = event.reason;
      const message = reason instanceof Error ? reason.message : String(reason);
      const stack = reason instanceof Error ? reason.stack : undefined;
      
      this.logError({
        message,
        error_type: 'UnhandledRejection',
        category: ErrorCategory.UNKNOWN,
        severity: ErrorSeverity.ERROR,
        component: 'promise',
        stack_trace: stack,
        context: { unhandledRejection: true }
      });
    };
  }
  
  /**
   * Log an error to the backend
   * @param errorData Error data to log
   * @returns Promise with the error ID or undefined if logging failed
   */
  public async logError(
    errorData: ErrorLogRequest
  ): Promise<string | undefined> {
    try {
      // Ensure component is set
      errorData.component = errorData.component || 'frontend';
      
      // Log locally to console in development
      if (process.env.NODE_ENV === 'development') {
        this.consoleErrorOriginal(
          `[${errorData.severity}] ${errorData.category}: ${errorData.message}`,
          errorData
        );
      }
      
      // Send to backend
      const response = await api.post<ErrorLogResponse>(
        this.apiEndpoint,
        errorData
      );
      
      return response.data.error_id;
    } catch (error) {
      // Use original console.error to avoid infinite loop
      this.consoleErrorOriginal(
        'Failed to log error to backend:',
        error,
        'Original error:',
        errorData
      );
      return undefined;
    }
  }
  
  /**
   * Log an API error
   * @param error Error object or message
   * @param endpoint API endpoint that caused the error
   * @param requestData Request data that caused the error
   * @returns Promise with the error ID or undefined if logging failed
   */
  public async logApiError(
    error: Error | string,
    endpoint: string,
    requestData?: any
  ): Promise<string | undefined> {
    const message = error instanceof Error ? error.message : error;
    const stack = error instanceof Error ? error.stack : undefined;
    
    return this.logError({
      message,
      error_type: error instanceof Error ? error.name : 'APIError',
      category: ErrorCategory.API,
      severity: ErrorSeverity.ERROR,
      component: 'api',
      source: endpoint,
      stack_trace: stack,
      context: { endpoint, requestData }
    });
  }
  
  /**
   * Log a validation error
   * @param error Error object or message
   * @param fieldName Name of the field that failed validation
   * @param value Value that failed validation
   * @returns Promise with the error ID or undefined if logging failed
   */
  public async logValidationError(
    error: Error | string,
    fieldName: string,
    value?: any
  ): Promise<string | undefined> {
    const message = error instanceof Error ? error.message : error;
    
    return this.logError({
      message,
      error_type: 'ValidationError',
      category: ErrorCategory.VALIDATION,
      severity: ErrorSeverity.WARNING,
      component: 'validation',
      source: fieldName,
      context: { fieldName, value }
    });
  }
  
  /**
   * Log a UI interaction error
   * @param error Error object or message
   * @param componentName Name of the component where the error occurred
   * @param action User action that triggered the error
   * @returns Promise with the error ID or undefined if logging failed
   */
  public async logUIError(
    error: Error | string,
    componentName: string,
    action: string
  ): Promise<string | undefined> {
    const message = error instanceof Error ? error.message : error;
    const stack = error instanceof Error ? error.stack : undefined;
    
    return this.logError({
      message,
      error_type: error instanceof Error ? error.name : 'UIError',
      category: ErrorCategory.UI,
      severity: ErrorSeverity.ERROR,
      component: componentName,
      stack_trace: stack,
      context: { componentName, action }
    });
  }
  
  /**
   * Clean up by restoring original error handlers
   */
  public cleanup(): void {
    console.error = this.consoleErrorOriginal;
    window.onerror = this.windowOnErrorOriginal;
    window.onunhandledrejection = this.windowOnUnhandledRejectionOriginal;
  }
}

// Create singleton instance
export const errorLoggingService = new ErrorLoggingService();

export default errorLoggingService;
