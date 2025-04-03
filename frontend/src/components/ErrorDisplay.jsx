import React, { useState } from 'react';
import {
  Alert,
  AlertTitle,
  Box,
  Button,
  Chip,
  Collapse,
  Divider,
  IconButton,
  Paper,
  Typography,
  useTheme
} from '@mui/material';
import {
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Close as CloseIcon,
  ExpandMore as ExpandMoreIcon,
  BugReport as BugReportIcon
} from '@mui/icons-material';
import { logError } from '../services/errorHandling';

/**
 * Error Display component for user-friendly error visualization
 * Integrates with the error logging service
 */
const ErrorDisplay = ({ 
  error, 
  title = 'An error occurred',
  severity = 'error',
  onClose,
  component = 'unknown',
  context = {},
  showReportButton = true,
  expanded = false,
  showStack = true,
  marginBottom = 3
}) => {
  const theme = useTheme();
  const [isExpanded, setIsExpanded] = useState(expanded);
  
  // Handle reporting an error
  const handleReportError = () => {
    if (!error) return;
    
    // Log the error to our error tracking system
    logError(
      error.message || String(error),
      'FRONTEND',
      severity.toUpperCase(),
      component,
      context,
      error.stack
    ).then(() => {
      // Show confirmation
      alert('Error has been reported to the development team.');
    }).catch(reportError => {
      console.error('Failed to report error:', reportError);
      alert('Could not report error. Please try again later.');
    });
  };
  
  // Extract error details
  const errorMessage = error?.message || String(error);
  const errorStack = error?.stack;
  
  // Generate technical details
  const technicalDetails = {
    timestamp: new Date().toISOString(),
    component,
    ...context,
    browserInfo: {
      userAgent: navigator.userAgent,
      language: navigator.language,
      platform: navigator.platform
    }
  };
  
  // Define color and icon based on severity
  const getSeverityProps = () => {
    switch (severity) {
      case 'error':
        return { 
          icon: <ErrorIcon />, 
          color: theme.palette.error.main,
          backgroundColor: theme.palette.error.light
        };
      case 'warning':
        return { 
          icon: <WarningIcon />, 
          color: theme.palette.warning.main,
          backgroundColor: theme.palette.warning.light
        };
      default:
        return { 
          icon: <InfoIcon />, 
          color: theme.palette.info.main,
          backgroundColor: theme.palette.info.light
        };
    }
  };
  
  const { icon, color, backgroundColor } = getSeverityProps();
  
  if (!error) return null;
  
  return (
    <Paper 
      elevation={3} 
      sx={{ 
        mb: marginBottom,
        borderLeft: `4px solid ${color}`,
        overflow: 'hidden'
      }}
    >
      <Alert 
        severity={severity}
        icon={icon}
        action={
          <Box>
            {showReportButton && (
              <IconButton
                color="inherit"
                size="small"
                onClick={handleReportError}
                title="Report this error"
              >
                <BugReportIcon fontSize="inherit" />
              </IconButton>
            )}
            
            <IconButton
              color="inherit"
              size="small"
              onClick={() => setIsExpanded(!isExpanded)}
              title={isExpanded ? 'Show less' : 'Show more'}
              sx={{
                transform: isExpanded ? 'rotate(180deg)' : 'rotate(0deg)',
                transition: theme.transitions.create('transform')
              }}
            >
              <ExpandMoreIcon fontSize="inherit" />
            </IconButton>
            
            {onClose && (
              <IconButton
                color="inherit"
                size="small"
                onClick={onClose}
                title="Dismiss"
              >
                <CloseIcon fontSize="inherit" />
              </IconButton>
            )}
          </Box>
        }
      >
        <AlertTitle>{title}</AlertTitle>
        {errorMessage}
      </Alert>
      
      <Collapse in={isExpanded}>
        <Box p={2} bgcolor={backgroundColor} sx={{ opacity: 0.9 }}>
          <Typography variant="subtitle2" gutterBottom>
            Technical Details
          </Typography>
          
          <Box display="flex" flexWrap="wrap" gap={0.5} mb={1}>
            {Object.entries(context).map(([key, value]) => (
              <Chip 
                key={key} 
                size="small" 
                label={`${key}: ${typeof value === 'object' ? JSON.stringify(value) : value}`} 
                variant="outlined"
              />
            ))}
          </Box>
          
          {showStack && errorStack && (
            <>
              <Divider sx={{ my: 1 }} />
              <Typography variant="subtitle2" gutterBottom>
                Stack Trace
              </Typography>
              <Box 
                component="pre" 
                bgcolor={theme.palette.background.default}
                p={1.5} 
                borderRadius={1}
                sx={{ 
                  fontSize: '0.75rem',
                  overflow: 'auto',
                  maxHeight: '200px'
                }}
              >
                {errorStack}
              </Box>
            </>
          )}
          
          <Box mt={2} display="flex" justifyContent="space-between">
            <Button size="small" onClick={() => setIsExpanded(false)}>
              Hide Details
            </Button>
            
            {showReportButton && (
              <Button 
                size="small"
                variant="outlined"
                startIcon={<BugReportIcon />}
                onClick={handleReportError}
              >
                Report Issue
              </Button>
            )}
          </Box>
        </Box>
      </Collapse>
    </Paper>
  );
};

export default ErrorDisplay;
