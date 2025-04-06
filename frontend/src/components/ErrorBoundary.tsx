import React, { useState, useEffect } from 'react';
import { Box, Typography, Button, Paper } from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';
import { performanceMonitor } from '../services/performance';

interface ErrorBoundaryProps {
  children: React.ReactNode;
  componentName?: string;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
  errorInfo: React.ErrorInfo | null;
}

const ErrorBoundary: React.FC<ErrorBoundaryProps> = ({ children }) => {
  const [hasError, setHasError] = useState(false);
  const [error, setError] = useState<Error | null>(null);
  const [errorInfo, setErrorInfo] = useState<React.ErrorInfo | null>(null);

  useEffect(() => {
    if (hasError) {
      // Record error in performance metrics
      performanceMonitor.recordMetric('error-boundary', 1);
      performanceMonitor.recordMetric('error-boundary-' + error?.name, 1);

      // Log error to error reporting service
      console.error('Uncaught error:', error, errorInfo);
    }
  }, [hasError, error, errorInfo]);

  const handleRefresh = () => {
    // Record refresh attempt
    performanceMonitor.recordMetric('error-boundary-refresh', 1);
    window.location.reload();
  };

  const handleError = (error: Error, errorInfo: React.ErrorInfo) => {
    setHasError(true);
    setError(error);
    setErrorInfo(errorInfo);
  };

  return (
    <React.ErrorBoundary onError={handleError}>
      {hasError ? (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'center',
            alignItems: 'center',
            height: '100vh',
            bgcolor: 'background.default'
          }}
        >
          <Paper
            elevation={3}
            sx={{
              p: 4,
              maxWidth: 600,
              textAlign: 'center'
            }}
          >
            <Typography variant="h5" gutterBottom color="error">
              Something went wrong
            </Typography>
            <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
              We apologize for the inconvenience. Please try refreshing the page.
            </Typography>
            {process.env.NODE_ENV === 'development' && error && (
              <Box sx={{ mb: 3, textAlign: 'left' }}>
                <Typography variant="subtitle2" color="error" sx={{ mb: 1 }}>
                  Error Details:
                </Typography>
                <Paper
                  variant="outlined"
                  sx={{
                    p: 2,
                    bgcolor: 'grey.100',
                    overflowX: 'auto'
                  }}
                >
                  <pre style={{ margin: 0 }}>
                    {error.toString()}
                    {errorInfo?.componentStack}
                  </pre>
                </Paper>
              </Box>
            )}
            <Button
              variant="contained"
              startIcon={<RefreshIcon />}
              onClick={handleRefresh}
            >
              Refresh Page
            </Button>
          </Paper>
        </Box>
      ) : (
        children
      )}
    </React.ErrorBoundary>
  );
};

export default ErrorBoundary;