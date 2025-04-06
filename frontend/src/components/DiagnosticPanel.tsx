import React, { useState, useEffect } from 'react';
import { Box, Paper, Typography, Alert, Button, Divider, Chip, CircularProgress, Grid } from '@mui/material';
import axios from 'axios';

// This component displays real-time connection status to the backend
const DiagnosticPanel: React.FC = () => {
  const [backendStatus, setBackendStatus] = useState<'connecting' | 'connected' | 'error'>('connecting');
  const [errorMessage, setErrorMessage] = useState<string>('');
  const [apiResponse, setApiResponse] = useState<any>(null);
  const [lastChecked, setLastChecked] = useState<string>('');
  
  // Extract API URL from environment variables or default
  const apiUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
  const currentPort = apiUrl.split(':')[2] || '8000';
  
  const checkBackendConnection = async () => {
    setBackendStatus('connecting');
    setLastChecked(new Date().toLocaleTimeString());
    
    try {
      // Try to reach the /health endpoint or any simple endpoint available
      const response = await axios.get(`${apiUrl}/health`, { timeout: 5000 });
      setBackendStatus('connected');
      setApiResponse(response.data);
      setErrorMessage('');
    } catch (error: any) {
      setBackendStatus('error');
      setApiResponse(null);
      if (error.code === 'ECONNREFUSED' || error.message.includes('Network Error')) {
        setErrorMessage(`Cannot connect to backend at ${apiUrl}. Server may not be running or is on a different port.`);
      } else if (error.response) {
        setErrorMessage(`Backend responded with status ${error.response.status}: ${error.response.statusText}`);
      } else {
        setErrorMessage(`Error: ${error.message}`);
      }
    }
  };

  // Check connection on component mount
  useEffect(() => {
    checkBackendConnection();
    // Set up periodic checking every 10 seconds
    const interval = setInterval(checkBackendConnection, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        ADE Platform Diagnostic Panel
      </Typography>
      <Divider sx={{ mb: 2 }} />
      
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1" gutterBottom>Backend Connection</Typography>
          <Box display="flex" alignItems="center" mb={1}>
            <Chip 
              label={backendStatus === 'connected' ? 'Connected' : backendStatus === 'connecting' ? 'Connecting...' : 'Error'} 
              color={backendStatus === 'connected' ? 'success' : backendStatus === 'connecting' ? 'warning' : 'error'}
              sx={{ mr: 1 }}
            />
            {backendStatus === 'connecting' && <CircularProgress size={20} />}
          </Box>
          
          <Typography variant="body2" color="text.secondary">API URL: {apiUrl}</Typography>
          <Typography variant="body2" color="text.secondary">Current Port: {currentPort}</Typography>
          <Typography variant="body2" color="text.secondary">Last Checked: {lastChecked}</Typography>
          
          {backendStatus === 'error' && (
            <Alert severity="error" sx={{ mt: 2 }}>
              {errorMessage}
            </Alert>
          )}
          
          {backendStatus === 'connected' && (
            <Alert severity="success" sx={{ mt: 2 }}>
              Successfully connected to backend server.
            </Alert>
          )}
          
          <Box mt={2}>
            <Button 
              variant="contained" 
              onClick={checkBackendConnection}
              color="primary"
              size="small"
            >
              Check Connection
            </Button>
          </Box>
        </Grid>
        
        <Grid item xs={12} md={6}>
          <Typography variant="subtitle1" gutterBottom>Response Data</Typography>
          {apiResponse ? (
            <Paper variant="outlined" sx={{ p: 2, maxHeight: '200px', overflow: 'auto' }}>
              <pre style={{ margin: 0 }}>
                {JSON.stringify(apiResponse, null, 2)}
              </pre>
            </Paper>
          ) : (
            <Typography variant="body2" color="text.secondary">
              No response data available
            </Typography>
          )}
        </Grid>
      </Grid>
    </Paper>
  );
};

export default DiagnosticPanel;
