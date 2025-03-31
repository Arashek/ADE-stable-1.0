import { AxiosError } from 'axios';

export enum ErrorSeverity {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL',
}

export interface ErrorLog {
  timestamp: string;
  severity: ErrorSeverity;
  message: string;
  stack?: string;
  context?: Record<string, any>;
  userId?: string;
}

class ErrorHandler {
  private static instance: ErrorHandler;
  private errorLogs: ErrorLog[] = [];
  private readonly MAX_LOGS = 1000;

  private constructor() {}

  static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  private logError(error: ErrorLog) {
    this.errorLogs.push(error);
    if (this.errorLogs.length > this.MAX_LOGS) {
      this.errorLogs.shift();
    }

    // Send to error tracking service in production
    if (process.env.NODE_ENV === 'production') {
      this.sendToErrorTracking(error);
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error:', error);
    }
  }

  private async sendToErrorTracking(error: ErrorLog) {
    try {
      await fetch('/api/error-tracking', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(error),
      });
    } catch (e) {
      console.error('Failed to send error to tracking service:', e);
    }
  }

  handleError(error: Error | AxiosError, severity: ErrorSeverity = ErrorSeverity.MEDIUM, context?: Record<string, any>) {
    const errorLog: ErrorLog = {
      timestamp: new Date().toISOString(),
      severity,
      message: error.message,
      stack: error.stack,
      context: {
        ...context,
        name: error.name,
        ...(error instanceof AxiosError && {
          status: error.response?.status,
          statusText: error.response?.statusText,
          data: error.response?.data,
        }),
      },
    };

    this.logError(errorLog);

    // Handle critical errors
    if (severity === ErrorSeverity.CRITICAL) {
      this.handleCriticalError(error);
    }
  }

  private handleCriticalError(error: Error) {
    // Implement critical error handling (e.g., user notification, automatic recovery)
    console.error('Critical error occurred:', error);
  }

  getErrorLogs(): ErrorLog[] {
    return [...this.errorLogs];
  }

  clearErrorLogs() {
    this.errorLogs = [];
  }
}

export const errorHandler = ErrorHandler.getInstance(); 