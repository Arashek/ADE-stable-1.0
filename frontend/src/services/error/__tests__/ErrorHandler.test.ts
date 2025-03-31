import { ErrorHandler } from '../ErrorHandler';
import { ErrorDetails } from '../ErrorHandler';

describe('ErrorHandler', () => {
  let errorHandler: ErrorHandler;

  beforeEach(() => {
    // Reset the singleton instance before each test
    (ErrorHandler as any).instance = null;
    errorHandler = ErrorHandler.getInstance();
  });

  describe('Singleton Pattern', () => {
    it('should return the same instance when getInstance is called multiple times', () => {
      const instance1 = ErrorHandler.getInstance();
      const instance2 = ErrorHandler.getInstance();
      expect(instance1).toBe(instance2);
    });
  });

  describe('handleError', () => {
    it('should handle Error objects', () => {
      const error = new Error('Test error');
      errorHandler.handleError(error);

      const errors = errorHandler.getErrors();
      expect(errors).toHaveLength(1);
      expect(errors[0].message).toBe('Test error');
      expect(errors[0].stack).toBeDefined();
      expect(errors[0].severity).toBe('low');
      expect(errors[0].category).toBe('general');
    });

    it('should handle non-Error objects', () => {
      const error = 'String error';
      errorHandler.handleError(error);

      const errors = errorHandler.getErrors();
      expect(errors).toHaveLength(1);
      expect(errors[0].message).toBe('String error');
      expect(errors[0].stack).toBeUndefined();
    });

    it('should handle errors with context', () => {
      const error = new Error('Test error');
      const context = { userId: '123', action: 'test' };
      errorHandler.handleError(error, context);

      const errors = errorHandler.getErrors();
      expect(errors[0].context).toEqual(context);
    });

    it('should limit the number of stored errors', () => {
      for (let i = 0; i < 1100; i++) {
        errorHandler.handleError(new Error(`Error ${i}`));
      }

      const errors = errorHandler.getErrors();
      expect(errors.length).toBeLessThanOrEqual(1000);
    });
  });

  describe('Error Filtering', () => {
    beforeEach(() => {
      errorHandler.handleError(new Error('Editor error'), { component: 'editor' });
      errorHandler.handleError(new Error('Refactoring error'), { component: 'refactoring' });
      errorHandler.handleError(new Error('Debugging error'), { component: 'debugging' });
      errorHandler.handleError(new Error('Security error'), { component: 'security' });
    });

    it('should filter errors by category', () => {
      const editorErrors = errorHandler.getErrorsByCategory('editor');
      const refactoringErrors = errorHandler.getErrorsByCategory('refactoring');
      const debuggingErrors = errorHandler.getErrorsByCategory('debugging');
      const securityErrors = errorHandler.getErrorsByCategory('security');

      expect(editorErrors.length).toBeGreaterThan(0);
      expect(refactoringErrors.length).toBeGreaterThan(0);
      expect(debuggingErrors.length).toBeGreaterThan(0);
      expect(securityErrors.length).toBeGreaterThan(0);
    });

    it('should filter errors by severity', () => {
      const lowErrors = errorHandler.getErrorsBySeverity('low');
      const mediumErrors = errorHandler.getErrorsBySeverity('medium');
      const highErrors = errorHandler.getErrorsBySeverity('high');
      const criticalErrors = errorHandler.getErrorsBySeverity('critical');

      expect(lowErrors.length).toBeGreaterThan(0);
      expect(mediumErrors.length).toBe(0);
      expect(highErrors.length).toBe(0);
      expect(criticalErrors.length).toBe(0);
    });
  });

  describe('Error Reporting', () => {
    beforeEach(() => {
      errorHandler.handleError(new Error('Critical error'), { severity: 'critical' });
      errorHandler.handleError(new Error('High severity error'), { severity: 'high' });
      errorHandler.handleError(new Error('Medium severity error'), { severity: 'medium' });
      errorHandler.handleError(new Error('Low severity error'), { severity: 'low' });
    });

    it('should generate error report with correct summary', () => {
      const report = errorHandler.generateReport();

      expect(report.errors.length).toBe(4);
      expect(report.summary.total).toBe(4);
      expect(report.summary.bySeverity).toBeDefined();
      expect(report.summary.byCategory).toBeDefined();
    });

    it('should correctly categorize errors in report', () => {
      const report = errorHandler.generateReport();

      expect(report.summary.bySeverity['critical']).toBe(1);
      expect(report.summary.bySeverity['high']).toBe(1);
      expect(report.summary.bySeverity['medium']).toBe(1);
      expect(report.summary.bySeverity['low']).toBe(1);
    });
  });

  describe('Error Recovery', () => {
    it('should attempt recovery for critical errors', () => {
      const consoleSpy = jest.spyOn(console, 'log');
      const error = new Error('Critical system error');
      errorHandler.handleError(error, { severity: 'critical' });

      expect(consoleSpy).toHaveBeenCalledWith('Attempting general recovery...');
    });

    it('should attempt category-specific recovery', () => {
      const consoleSpy = jest.spyOn(console, 'log');
      const error = new Error('Editor critical error');
      errorHandler.handleError(error, { severity: 'critical', component: 'editor' });

      expect(consoleSpy).toHaveBeenCalledWith('Attempting to recover editor state...');
    });
  });

  describe('Error Observables', () => {
    it('should emit errors through observable', (done) => {
      const error = new Error('Test error');
      let receivedError: ErrorDetails | undefined;

      errorHandler.getErrorsObservable().subscribe({
        next: (errorDetails) => {
          receivedError = errorDetails;
          done();
        }
      });

      errorHandler.handleError(error);

      expect(receivedError).toBeDefined();
      expect(receivedError?.message).toBe('Test error');
    });
  });
}); 