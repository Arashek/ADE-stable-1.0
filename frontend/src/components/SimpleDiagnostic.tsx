import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Typography, 
  Paper, 
  Button, 
  Grid, 
  CircularProgress, 
  Alert 
} from '@mui/material';
import axios from 'axios';
import { API_BASE_URL } from '../services/api';

/**
 * A simplified diagnostic component for testing the ADE frontend-backend connection
 * without being affected by TypeScript errors in other components
 */
const SimpleDiagnostic: React.FC = () => {
  const [backendStatus, setBackendStatus] = useState<'connecting' | 'connected' | 'error'>('connecting');
  const [healthData, setHealthData] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    checkBackendConnection();
  }, []);

  const checkBackendConnection = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_BASE_URL}/health`);
      if (response.status === 200) {
        setBackendStatus('connected');
        setHealthData(response.data);
      } else {
        setBackendStatus('error');
        setError(`Unexpected response: ${response.status}`);
      }
    } catch (err: any) {
      setBackendStatus('error');
      setError(err.message || 'Could not connect to backend');
    } finally {
      setLoading(false);
    }
  };

  const testPydanticEndpoint = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${API_BASE_URL}/pydantic/model_schema`);
      if (response.status === 200) {
        setHealthData({ ...healthData, pydanticTest: response.data });
        setBackendStatus('connected');
      } else {
        setError(`Unexpected response: ${response.status}`);
      }
    } catch (err: any) {
      setError(err.message || 'Error testing Pydantic endpoint');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Paper sx={{ p: 3, mb: 3 }}>
      <Typography variant="h5" gutterBottom>
        ADE Platform Diagnostic
      </Typography>
      
      <Box sx={{ mb: 2 }}>
        <Typography variant="h6" gutterBottom>
          Backend Connection Status: 
          <Box component="span" sx={{ ml: 1, color: backendStatus === 'connected' ? 'success.main' : backendStatus === 'connecting' ? 'warning.main' : 'error.main' }}>
            {backendStatus === 'connected' ? 'Connected' : backendStatus === 'connecting' ? 'Connecting...' : 'Error'}
          </Box>
        </Typography>
        
        {error && (
          <Alert severity="error" sx={{ mt: 1 }}>
            {error}
          </Alert>
        )}
      </Box>
      
      <Grid container spacing={2}>
        <Grid item>
          <Button 
            variant="contained" 
            color="primary" 
            onClick={checkBackendConnection}
            disabled={loading}
          >
            {loading ? <CircularProgress size={24} /> : 'Check Backend Health'}
          </Button>
        </Grid>
        <Grid item>
          <Button 
            variant="contained" 
            color="secondary" 
            onClick={testPydanticEndpoint}
            disabled={loading || backendStatus !== 'connected'}
          >
            Test Pydantic Endpoint
          </Button>
        </Grid>
      </Grid>
      
      {healthData && (
        <Box sx={{ mt: 3 }}>
          <Typography variant="h6" gutterBottom>
            System Information
          </Typography>
          
          <Paper variant="outlined" sx={{ p: 2, backgroundColor: '#f5f5f5' }}>
            <pre style={{ margin: 0, whiteSpace: 'pre-wrap', wordBreak: 'break-word' }}>
              {JSON.stringify(healthData, null, 2)}
            </pre>
          </Paper>
        </Box>
      )}
    </Paper>
  );
};

export default SimpleDiagnostic;
