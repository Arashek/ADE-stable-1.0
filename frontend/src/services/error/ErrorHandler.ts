import { Observable, Subject } from 'rxjs';
import { PerformanceMonitor } from '../monitoring/PerformanceMonitor';

export interface ErrorDetails {
  message: string;
  stack?: string;
  code?: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  category: 'editor' | 'refactoring' | 'debugging' | 'security' | 'general';
  timestamp: number;
  context?: Record<string, any>;
}

export interface ErrorReport {
  errors: ErrorDetails[];
  summary: {
    total: number;
    bySeverity: Record<ErrorDetails['severity'], number>;
    byCategory: Record<ErrorDetails['category'], number>;
  };
}

export class ErrorHandler {
  private static instance: ErrorHandler;
  private errors: ErrorDetails[] = [];
  private errorsSubject = new Subject<ErrorDetails>();
  private readonly MAX_ERRORS = 1000;
  private performanceMonitor: PerformanceMonitor;

  private constructor() {
    this.performanceMonitor = PerformanceMonitor.getInstance();
    this.setupErrorListeners();
  }

  public static getInstance(): ErrorHandler {
    if (!ErrorHandler.instance) {
      ErrorHandler.instance = new ErrorHandler();
    }
    return ErrorHandler.instance;
  }

  private setupErrorListeners(): void {
    // Listen for unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError(event.reason);
    });

    // Listen for global errors
    window.addEventListener('error', (event) => {
      this.handleError(event.error);
    });
  }

  public handleError(error: Error | unknown, context?: Record<string, any>): void {
    const errorDetails: ErrorDetails = {
      message: error instanceof Error ? error.message : String(error),
      stack: error instanceof Error ? error.stack : undefined,
      code: this.extractErrorCode(error),
      severity: this.determineSeverity(error),
      category: this.determineCategory(error),
      timestamp: Date.now(),
      context
    };

    this.errors.push(errorDetails);
    this.errorsSubject.next(errorDetails);

    // Keep only the most recent errors
    if (this.errors.length > this.MAX_ERRORS) {
      this.errors = this.errors.slice(-this.MAX_ERRORS);
    }

    // Record error in performance metrics
    this.performanceMonitor.recordMetric({
      name: `error_${errorDetails.category}`,
      value: 1,
      category: 'general'
    });

    // Log error to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Error details:', errorDetails);
    }

    // Handle critical errors
    if (errorDetails.severity === 'critical') {
      this.handleCriticalError(errorDetails);
    }
  }

  public getErrors(): ErrorDetails[] {
    return [...this.errors];
  }

  public getErrorsByCategory(category: ErrorDetails['category']): ErrorDetails[] {
    return this.errors.filter(e => e.category === category);
  }

  public getErrorsBySeverity(severity: ErrorDetails['severity']): ErrorDetails[] {
    return this.errors.filter(e => e.severity === severity);
  }

  public getErrorsObservable(): Observable<ErrorDetails> {
    return this.errorsSubject.asObservable();
  }

  public generateReport(): ErrorReport {
    const bySeverity = this.errors.reduce((acc, error) => {
      acc[error.severity] = (acc[error.severity] || 0) + 1;
      return acc;
    }, {} as Record<ErrorDetails['severity'], number>);

    const byCategory = this.errors.reduce((acc, error) => {
      acc[error.category] = (acc[error.category] || 0) + 1;
      return acc;
    }, {} as Record<ErrorDetails['category'], number>);

    return {
      errors: this.errors,
      summary: {
        total: this.errors.length,
        bySeverity,
        byCategory
      }
    };
  }

  private extractErrorCode(error: unknown): string | undefined {
    if (error instanceof Error && 'code' in error) {
      return (error as any).code;
    }
    return undefined;
  }

  private determineSeverity(error: unknown): ErrorDetails['severity'] {
    if (error instanceof Error) {
      // Check for specific error types or messages that indicate severity
      if (error.message.includes('critical') || error.message.includes('fatal')) {
        return 'critical';
      }
      if (error.message.includes('high') || error.message.includes('severe')) {
        return 'high';
      }
      if (error.message.includes('medium')) {
        return 'medium';
      }
    }
    return 'low';
  }

  private determineCategory(error: unknown): ErrorDetails['category'] {
    if (error instanceof Error) {
      // Check error message or stack trace for category indicators
      const message = error.message.toLowerCase();
      if (message.includes('editor') || message.includes('monaco')) {
        return 'editor';
      }
      if (message.includes('refactor')) {
        return 'refactoring';
      }
      if (message.includes('debug') || message.includes('breakpoint')) {
        return 'debugging';
      }
      if (message.includes('security') || message.includes('vulnerability')) {
        return 'security';
      }
    }
    return 'general';
  }

  private handleCriticalError(error: ErrorDetails): void {
    // Log to error reporting service
    this.logToErrorService(error);

    // Show user-friendly error message
    this.showErrorMessage(error);

    // Attempt to recover if possible
    this.attemptRecovery(error);
  }

  private logToErrorService(error: ErrorDetails): void {
    // This would typically send the error to a service like Sentry
    // For now, we'll just log to console
    console.error('Critical error reported:', error);
  }

  private showErrorMessage(error: ErrorDetails): void {
    // This would typically show a user-friendly error message
    // For now, we'll just log to console
    console.error('User-facing error message:', error.message);
  }

  private attemptRecovery(error: ErrorDetails): void {
    // Attempt to recover from the error based on its category
    switch (error.category) {
      case 'editor':
        this.recoverEditor(error);
        break;
      case 'refactoring':
        this.recoverRefactoring(error);
        break;
      case 'debugging':
        this.recoverDebugging(error);
        break;
      case 'security':
        this.recoverSecurity(error);
        break;
      default:
        this.recoverGeneral(error);
    }
  }

  private recoverEditor(error: ErrorDetails): void {
    // Attempt to recover editor state
    console.log('Attempting to recover editor state...');
  }

  private recoverRefactoring(error: ErrorDetails): void {
    // Attempt to recover refactoring state
    console.log('Attempting to recover refactoring state...');
  }

  private recoverDebugging(error: ErrorDetails): void {
    // Attempt to recover debugging state
    console.log('Attempting to recover debugging state...');
  }

  private recoverSecurity(error: ErrorDetails): void {
    // Attempt to recover security state
    console.log('Attempting to recover security state...');
  }

  private recoverGeneral(error: ErrorDetails): void {
    // Attempt general recovery
    console.log('Attempting general recovery...');
  }
} 