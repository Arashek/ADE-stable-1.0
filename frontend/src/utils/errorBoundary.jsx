import React, { Component } from 'react';
import { logError, ErrorCategory, ErrorSeverity } from '../services/errorHandling';
import ErrorDisplay from '../components/ErrorDisplay';

/**
 * Error Boundary component to catch JavaScript errors anywhere in child component tree
 * Integrates with our error logging system
 */
class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = { 
      error: null,
      errorInfo: null,
      hasError: false
    };
  }
  
  componentDidCatch(error, errorInfo) {
    // Update state with error details
    this.setState({
      error: error,
      errorInfo: errorInfo,
      hasError: true
    });
    
    // Log error to our tracking system
    this.logErrorToSystem(error, errorInfo);
  }
  
  async logErrorToSystem(error, errorInfo) {
    try {
      const { componentName = 'unknown', context = {} } = this.props;
      
      await logError(
        error.message || 'React component error',
        ErrorCategory.FRONTEND,
        ErrorSeverity.ERROR,
        componentName,
        {
          componentStack: errorInfo?.componentStack,
          ...context
        },
        error.stack
      );
      
      console.log('Error logged to tracking system');
    } catch (loggingError) {
      console.error('Failed to log error to tracking system:', loggingError);
    }
  }
  
  // Reset the error state to allow the component to try rendering again
  resetErrorBoundary = () => {
    this.setState({
      error: null,
      errorInfo: null,
      hasError: false
    });
    
    // Call the provided reset handler if available
    if (typeof this.props.onReset === 'function') {
      this.props.onReset();
    }
  };
  
  render() {
    const { error, errorInfo, hasError } = this.state;
    const { fallback, children } = this.props;
    
    // If there's an error, render the fallback UI or our default error display
    if (hasError) {
      // Use custom fallback if provided
      if (fallback) {
        if (typeof fallback === 'function') {
          return fallback({ error, errorInfo, resetErrorBoundary: this.resetErrorBoundary });
        }
        return fallback;
      }
      
      // Otherwise use our default error display
      return (
        <ErrorDisplay
          error={error}
          title={`Component Error: ${this.props.componentName || 'Unknown'}`}
          severity="error"
          component={this.props.componentName}
          context={{ componentStack: errorInfo?.componentStack }}
          onClose={this.resetErrorBoundary}
        />
      );
    }
    
    // No error, render children normally
    return children;
  }
}

/**
 * Higher Order Component that wraps a component with an ErrorBoundary
 * 
 * @param {React.Component} Component - Component to wrap
 * @param {object} options - Error boundary options
 * @returns {React.Component} - Wrapped component with error boundary
 */
export const withErrorBoundary = (Component, options = {}) => {
  const WrappedComponent = (props) => (
    <ErrorBoundary
      componentName={options.componentName || Component.displayName || Component.name}
      context={options.context}
      fallback={options.fallback}
      onReset={options.onReset}
    >
      <Component {...props} />
    </ErrorBoundary>
  );
  
  // Copy the display name for easier debugging
  WrappedComponent.displayName = `WithErrorBoundary(${Component.displayName || Component.name || 'Component'})`;
  
  return WrappedComponent;
};

/**
 * Hook to create an error handling context for functional components
 * 
 * @param {object} options - Error handling options
 * @returns {object} - Error handling functions and state
 */
export const useErrorHandler = (options = {}) => {
  const [error, setError] = React.useState(null);
  const componentName = options.componentName || 'UnknownComponent';
  
  // Report error to the logging system
  const reportError = React.useCallback(async (err, additionalContext = {}) => {
    if (!err) return;
    
    try {
      await logError(
        err.message || String(err),
        ErrorCategory.FRONTEND,
        ErrorSeverity.ERROR,
        componentName,
        {
          ...options.context,
          ...additionalContext
        },
        err.stack
      );
    } catch (loggingError) {
      console.error('Failed to log error to tracking system:', loggingError);
    }
  }, [componentName, options.context]);
  
  // Handle errors with state update and reporting
  const handleError = React.useCallback((err, additionalContext = {}) => {
    setError(err);
    reportError(err, additionalContext);
  }, [reportError]);
  
  // Reset error state
  const resetError = React.useCallback(() => {
    setError(null);
  }, []);
  
  return {
    error,
    setError,
    handleError,
    resetError,
    reportError
  };
};

export default ErrorBoundary;
