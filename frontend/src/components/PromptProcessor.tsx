import React, { useState } from 'react';
import {
  Box,
  Button,
  Card,
  CardContent,
  CircularProgress,
  Divider,
  FormControl,
  Grid,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  TextField,
  Typography
} from '@mui/material';
import axios from 'axios';
import { logError, ErrorCategory, ErrorSeverity } from '../services/errorHandling';

// Types
interface PromptResult {
  success: boolean;
  result?: string;
  error?: string;
  processingTime?: number;
}

/**
 * PromptProcessor component
 * Provides interface for submitting prompts to various agents and viewing results
 */
const PromptProcessor: React.FC = () => {
  // State
  const [prompt, setPrompt] = useState<string>('');
  const [agent, setAgent] = useState<string>('assistant');
  const [loading, setLoading] = useState<boolean>(false);
  const [result, setResult] = useState<PromptResult | null>(null);

  // Handle prompt change
  const handlePromptChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setPrompt(event.target.value);
  };

  // Handle agent change
  const handleAgentChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setAgent(event.target.value as string);
  };

  // Submit prompt to backend
  const handleSubmit = async () => {
    if (!prompt.trim()) {
      setResult({
        success: false,
        error: 'Prompt cannot be empty'
      });
      return;
    }

    setLoading(true);
    setResult(null);

    try {
      const startTime = Date.now();
      const response = await axios.post('http://localhost:8000/api/process-prompt', {
        prompt,
        agent,
        options: {
          maxTokens: 500,
          temperature: 0.7
        }
      });

      const processingTime = (Date.now() - startTime) / 1000; // in seconds
      
      setResult({
        success: true,
        result: response.data.result,
        processingTime
      });
      
      // Log successful processing
      logError(
        `Prompt processed successfully in ${processingTime.toFixed(2)}s`,
        ErrorCategory.FRONTEND,
        ErrorSeverity.INFO,
        'PromptProcessor',
        { 
          agent, 
          promptLength: prompt.length,
          responseLength: response.data.result.length 
        }
      );
    } catch (error) {
      console.error('Error processing prompt:', error);
      
      // Log error
      if (error instanceof Error) {
        logError(
          `Error processing prompt: ${error.message}`,
          ErrorCategory.API,
          ErrorSeverity.ERROR,
          'PromptProcessor',
          { agent, promptLength: prompt.length },
          error.stack
        );
        
        setResult({
          success: false,
          error: `Error: ${error.message}`
        });
      } else {
        setResult({
          success: false,
          error: 'Unknown error occurred'
        });
      }
    } finally {
      setLoading(false);
    }
  };

  // Clear form
  const handleClear = () => {
    setPrompt('');
    setResult(null);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Prompt Processing Workflow
      </Typography>
      <Typography variant="body1" paragraph>
        Submit prompts to various specialized agents in the ADE platform and view the results.
      </Typography>
      
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper elevation={0} variant="outlined" sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Input
            </Typography>
            
            <FormControl fullWidth margin="normal">
              <InputLabel id="agent-select-label">Select Agent</InputLabel>
              <Select
                labelId="agent-select-label"
                id="agent-select"
                value={agent}
                label="Select Agent"
                onChange={handleAgentChange}
              >
                <MenuItem value="assistant">AI Assistant</MenuItem>
                <MenuItem value="designer">UI/UX Designer</MenuItem>
                <MenuItem value="developer">Code Developer</MenuItem>
                <MenuItem value="architect">System Architect</MenuItem>
                <MenuItem value="validator">Validator</MenuItem>
                <MenuItem value="security">Security Expert</MenuItem>
              </Select>
            </FormControl>
            
            <TextField
              fullWidth
              multiline
              rows={6}
              margin="normal"
              label="Enter your prompt"
              variant="outlined"
              value={prompt}
              onChange={handlePromptChange}
              placeholder="Describe what you want the agent to help you with..."
            />
            
            <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
              <Button
                variant="contained"
                color="primary"
                onClick={handleSubmit}
                disabled={loading || !prompt.trim()}
              >
                {loading ? <CircularProgress size={24} /> : 'Process Prompt'}
              </Button>
              <Button
                variant="outlined"
                onClick={handleClear}
                disabled={loading || (!prompt && !result)}
              >
                Clear
              </Button>
            </Box>
          </Paper>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Paper elevation={0} variant="outlined" sx={{ p: 3, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Result
            </Typography>
            
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 4 }}>
                <CircularProgress />
              </Box>
            ) : result ? (
              <Box>
                <Card variant="outlined" sx={{ mb: 2, bgcolor: result.success ? 'success.50' : 'error.50' }}>
                  <CardContent>
                    <Typography variant="subtitle2" color={result.success ? 'success.main' : 'error.main'}>
                      {result.success ? 'Success' : 'Error'}
                    </Typography>
                    <Divider sx={{ my: 1 }} />
                    {result.success ? (
                      <>
                        <Typography variant="body2" paragraph>
                          {result.result}
                        </Typography>
                        {result.processingTime && (
                          <Typography variant="caption" color="text.secondary">
                            Processed in {result.processingTime.toFixed(2)} seconds
                          </Typography>
                        )}
                      </>
                    ) : (
                      <Typography variant="body2" color="error">
                        {result.error}
                      </Typography>
                    )}
                  </CardContent>
                </Card>
              </Box>
            ) : (
              <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '200px' }}>
                <Typography variant="body1" color="text.secondary">
                  Submit a prompt to see results here
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PromptProcessor;
