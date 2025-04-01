import React, { Component, ErrorInfo, ReactNode } from 'react';
import { Box, Typography, Button, Paper, Divider } from '@mui/material';
import { Warning as WarningIcon } from '@mui/icons-material';
import errorLoggingService, { ErrorCategory } from '../../services/error-logging.service';

interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?: ReactNode;
  componentName: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

/**
 * ErrorBoundary component to catch JavaScript errors in child component trees,
 * log those errors, and display a fallback UI instead of the component tree that crashed.
 */
class ErrorBoundary extends Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    // Update state so the next render will show the fallback UI
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo): void {
    // Log the error to our error logging service
    errorLoggingService.logError({
      message: error.message,
      error_type: error.name,
      category: ErrorCategory.RENDERING,
      severity: 'ERROR',
      component: this.props.componentName,
      stack_trace: error.stack,
      context: {
        componentStack: errorInfo.componentStack,
      },
    });
  }

  handleRetry = (): void => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  render(): ReactNode {
    if (this.state.hasError) {
      // Custom fallback UI
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default fallback UI
      return (
        <Paper 
          elevation={3} 
          sx={{ 
            p: 3, 
            m: 2, 
            backgroundColor: '#fff8e1', 
            borderLeft: '4px solid #ff9800' 
          }}
        >
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <WarningIcon color="warning" sx={{ mr: 1 }} />
            <Typography variant="h6" component="h2">
              Something went wrong
            </Typography>
          </Box>
          <Divider sx={{ mb: 2 }} />
          <Typography variant="body2" color="text.secondary" gutterBottom>
            We've encountered an error in the {this.props.componentName} component.
          </Typography>
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <Box sx={{ mt: 2, mb: 2 }}>
              <Typography variant="subtitle2">Error Details (Development Only):</Typography>
              <Paper sx={{ p: 2, bgcolor: 'grey.100', maxHeight: '200px', overflow: 'auto' }}>
                <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
                  {this.state.error.toString()}
                </Typography>
              </Paper>
            </Box>
          )}
          <Box sx={{ mt: 2 }}>
            <Button 
              variant="outlined" 
              color="primary" 
              onClick={this.handleRetry}
            >
              Retry
            </Button>
          </Box>
        </Paper>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
