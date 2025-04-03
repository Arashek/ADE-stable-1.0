import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Alert,
  AlertTitle,
  Divider,
  Chip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Send as SendIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  Code as CodeIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  CheckCircle as CheckCircleIcon
} from '@mui/icons-material';
import { SyntaxHighlighter } from 'react-syntax-highlighter';
import { docco } from 'react-syntax-highlighter/dist/esm/styles/hljs';

import promptService from '../services/promptService';
import errorHandler from '../services/errorHandling';

// Processing steps
const PROCESSING_STEPS = [
  { label: 'Submit Prompt', description: 'Send prompt for processing' },
  { label: 'Analyze Requirements', description: 'Extracting requirements and specifications' },
  { label: 'Design Architecture', description: 'Designing application architecture' },
  { label: 'Generate Code', description: 'Generating application code' },
  { label: 'Finalize', description: 'Finalizing and optimizing generated application' }
];

const PromptProcessor = () => {
  // State
  const [prompt, setPrompt] = useState('');
  const [processing, setProcessing] = useState(false);
  const [activeStep, setActiveStep] = useState(0);
  const [taskId, setTaskId] = useState(null);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [statusUpdates, setStatusUpdates] = useState([]);
  
  // Reset the form
  const handleReset = () => {
    setPrompt('');
    setProcessing(false);
    setActiveStep(0);
    setTaskId(null);
    setResult(null);
    setError(null);
    setStatusUpdates([]);
  };
  
  // Submit the prompt
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!prompt.trim()) {
      return;
    }
    
    setProcessing(true);
    setActiveStep(0);
    setError(null);
    setStatusUpdates([]);
    
    try {
      // Add initial status update
      addStatusUpdate({
        level: 'info',
        message: 'Starting prompt processing',
        details: { prompt: prompt.substring(0, 100) + (prompt.length > 100 ? '...' : '') }
      });
      
      // Process the prompt
      promptService.processPromptToCompletion(
        prompt,
        { timeout: 120000 },
        handleStatusUpdate
      ).then(finalResult => {
        setProcessing(false);
        
        if (finalResult.stage === 'completed') {
          setResult(finalResult.result);
          setActiveStep(PROCESSING_STEPS.length);
          
          // Add final status update
          addStatusUpdate({
            level: 'success',
            message: 'Prompt processing completed successfully',
            details: finalResult.result
          });
        } else {
          setError(finalResult.error || 'Unknown error occurred');
          
          // Add error status update
          addStatusUpdate({
            level: 'error',
            message: `Processing failed: ${finalResult.error}`,
            details: finalResult.details
          });
        }
      });
    } catch (err) {
      setProcessing(false);
      setError(err.message);
      
      // Log error
      errorHandler.logError(
        `Error processing prompt: ${err.message}`,
        errorHandler.ErrorCategory.FRONTEND,
        errorHandler.ErrorSeverity.ERROR,
        'PromptProcessor',
        { promptPreview: prompt.substring(0, 100) },
        err.stack
      );
      
      // Add error status update
      addStatusUpdate({
        level: 'error',
        message: `Error: ${err.message}`,
        details: { stack: err.stack }
      });
    }
  };
  
  // Handle status updates during processing
  const handleStatusUpdate = (update) => {
    setTaskId(update.taskId);
    
    // Update step based on status
    if (update.stage === 'submitted') {
      setActiveStep(1);
    } else if (update.stage === 'processing') {
      // Map status to step
      const statusToStep = {
        'analyzing': 1,
        'designing': 2,
        'generating': 3,
        'finalizing': 4
      };
      
      setActiveStep(statusToStep[update.status] || activeStep);
    }
    
    // Add status update
    addStatusUpdate({
      level: 'info',
      message: update.message || `Status: ${update.status}`,
      details: update
    });
  };
  
  // Add a status update
  const addStatusUpdate = (update) => {
    const updatedStatus = {
      ...update,
      timestamp: new Date().toISOString()
    };
    
    setStatusUpdates(prevUpdates => [updatedStatus, ...prevUpdates]);
  };
  
  // Status update item
  const StatusUpdateItem = ({ update }) => {
    // Icon based on level
    const getIcon = () => {
      switch (update.level) {
        case 'error':
          return <ErrorIcon color="error" />;
        case 'warning':
          return <WarningIcon color="warning" />;
        case 'success':
          return <CheckCircleIcon color="success" />;
        default:
          return <InfoIcon color="info" />;
      }
    };
    
    // Formatted time
    const time = new Date(update.timestamp).toLocaleTimeString();
    
    return (
      <Box mb={1}>
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Box display="flex" alignItems="center" width="100%">
              {getIcon()}
              <Typography variant="body2" ml={1} flexGrow={1}>
                {update.message}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {time}
              </Typography>
            </Box>
          </AccordionSummary>
          <AccordionDetails>
            {update.details && (
              <Box>
                <Typography variant="caption" color="text.secondary">
                  Details:
                </Typography>
                <Box bgcolor="background.paper" p={1} borderRadius={1} mt={1} mb={1} overflow="auto">
                  <pre style={{ margin: 0 }}>
                    {JSON.stringify(update.details, null, 2)}
                  </pre>
                </Box>
              </Box>
            )}
          </AccordionDetails>
        </Accordion>
      </Box>
    );
  };
  
  return (
    <Box>
      <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
        <Typography variant="h5" component="h2" gutterBottom>
          ADE Prompt Processor
        </Typography>
        
        <form onSubmit={handleSubmit}>
          <TextField
            label="Enter your prompt"
            multiline
            rows={4}
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            fullWidth
            disabled={processing}
            placeholder="Describe the application you want to create..."
            margin="normal"
            variant="outlined"
            required
          />
          
          <Box mt={2} display="flex" justifyContent="space-between">
            <Button
              variant="outlined"
              color="secondary"
              onClick={handleReset}
              disabled={processing}
            >
              Reset
            </Button>
            
            <Button
              type="submit"
              variant="contained"
              color="primary"
              disabled={!prompt.trim() || processing}
              endIcon={processing ? <CircularProgress size={20} /> : <SendIcon />}
            >
              {processing ? 'Processing...' : 'Process Prompt'}
            </Button>
          </Box>
        </form>
      </Paper>
      
      {/* Processing status */}
      {(processing || result || error) && (
        <Paper elevation={3} sx={{ p: 3, mb: 3 }}>
          <Typography variant="h6" gutterBottom>
            Processing Status
            {taskId && (
              <Chip 
                label={`Task ID: ${taskId}`} 
                size="small" 
                color="primary" 
                sx={{ ml: 2 }} 
              />
            )}
          </Typography>
          
          <Stepper activeStep={activeStep} alternativeLabel sx={{ mt: 3, mb: 3 }}>
            {PROCESSING_STEPS.map((step, index) => (
              <Step key={step.label}>
                <StepLabel>
                  {step.label}
                  <Typography variant="caption" display="block">
                    {step.description}
                  </Typography>
                </StepLabel>
              </Step>
            ))}
          </Stepper>
          
          {error && (
            <Alert severity="error" sx={{ mt: 2 }}>
              <AlertTitle>Error</AlertTitle>
              {error}
            </Alert>
          )}
          
          {result && (
            <Box mt={3}>
              <Typography variant="h6" gutterBottom>
                Result
              </Typography>
              
              {result.code && (
                <Box mt={2}>
                  <Typography variant="subtitle1" gutterBottom>
                    Generated Code:
                  </Typography>
                  <SyntaxHighlighter language="javascript" style={docco}>
                    {result.code}
                  </SyntaxHighlighter>
                </Box>
              )}
            </Box>
          )}
        </Paper>
      )}
      
      {/* Status updates */}
      {statusUpdates.length > 0 && (
        <Paper elevation={3} sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Processing Log
            <Tooltip title="Detailed log of all processing steps and status updates">
              <IconButton size="small" sx={{ ml: 1 }}>
                <InfoIcon fontSize="small" />
              </IconButton>
            </Tooltip>
          </Typography>
          
          <Divider sx={{ mb: 2 }} />
          
          <Box maxHeight="300px" overflow="auto">
            {statusUpdates.map((update, index) => (
              <StatusUpdateItem key={index} update={update} />
            ))}
          </Box>
        </Paper>
      )}
    </Box>
  );
};

export default PromptProcessor;
