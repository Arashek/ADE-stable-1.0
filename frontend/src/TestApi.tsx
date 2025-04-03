import React, { useState } from 'react';
import axios from 'axios';
import {
  Box,
  Button,
  TextField,
  Typography,
  Paper,
  Container,
  CircularProgress,
  Alert,
  AlertTitle,
  Snackbar
} from '@mui/material';

const API_URL = 'http://localhost:8000';

const TestApi: React.FC = () => {
  const [prompt, setPrompt] = useState('');
  const [response, setResponse] = useState<any>(null);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    
    try {
      // Call the prompt API
      const result = await axios.post(`${API_URL}/api/prompt`, {
        prompt,
        context: {}
      });
      
      setResponse(result.data);
      setTaskId(result.data.task_id);
      setSuccess(true);
      
    } catch (err: any) {
      console.error('Error submitting prompt:', err);
      setError(err.message || 'An error occurred while submitting the prompt');
    } finally {
      setLoading(false);
    }
  };

  const checkStatus = async () => {
    if (!taskId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      // Call the status API
      const result = await axios.get(`${API_URL}/api/prompt/${taskId}`);
      setResponse(result.data);
      setSuccess(true);
      
    } catch (err: any) {
      console.error('Error checking status:', err);
      setError(err.message || 'An error occurred while checking the status');
    } finally {
      setLoading(false);
    }
  };

  const handleCloseSnackbar = () => {
    setSuccess(false);
  };

  return (
    <Container maxWidth="md">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom>
          ADE Platform API Test
        </Typography>
        
        <Box component="form" onSubmit={handleSubmit} sx={{ mt: 3 }}>
          <TextField
            fullWidth
            label="Enter your prompt"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
            margin="normal"
            multiline
            rows={4}
            variant="outlined"
            required
          />
          
          <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
            <Button 
              type="submit" 
              variant="contained" 
              color="primary"
              disabled={loading || !prompt}
            >
              {loading ? <CircularProgress size={24} /> : 'Submit Prompt'}
            </Button>
            
            {taskId && (
              <Button
                variant="outlined"
                color="secondary"
                onClick={checkStatus}
                disabled={loading}
              >
                Check Status
              </Button>
            )}
          </Box>
        </Box>
        
        {error && (
          <Alert severity="error" sx={{ mt: 3 }}>
            <AlertTitle>Error</AlertTitle>
            {error}
          </Alert>
        )}
        
        {response && (
          <Box sx={{ mt: 3 }}>
            <Typography variant="h6" gutterBottom>
              Response:
            </Typography>
            <Paper elevation={1} sx={{ p: 2, bgcolor: 'background.default' }}>
              <pre style={{ whiteSpace: 'pre-wrap', wordBreak: 'break-all' }}>
                {JSON.stringify(response, null, 2)}
              </pre>
            </Paper>
          </Box>
        )}
      </Paper>
      
      <Snackbar
        open={success}
        autoHideDuration={6000}
        onClose={handleCloseSnackbar}
      >
        <Alert onClose={handleCloseSnackbar} severity="success">
          API request completed successfully!
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default TestApi;
