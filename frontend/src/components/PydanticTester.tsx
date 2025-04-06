import React, { useState, useEffect } from 'react';
import { 
  Box, 
  Paper, 
  Typography, 
  Button, 
  Divider, 
  Accordion, 
  AccordionSummary, 
  AccordionDetails, 
  CircularProgress,
  Alert,
  Snackbar
} from '@mui/material';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import axios from 'axios';

/**
 * Component for testing Pydantic V2 compatibility in the ADE multi-agent system.
 * This tests the model and agent service types that were updated for Pydantic V2.
 */
const PydanticTester: React.FC = () => {
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [modelSchema, setModelSchema] = useState<any>(null);
  const [agentSchema, setAgentSchema] = useState<any>(null);
  const [validationResult, setValidationResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [snackbarOpen, setSnackbarOpen] = useState<boolean>(false);
  
  // API base URL from environment or default
  const apiUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8003';
  
  const fetchModelSchema = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${apiUrl}/pydantic-test/model-schema`);
      setModelSchema(response.data);
    } catch (error: any) {
      console.error('Error fetching model schema:', error);
      setError(`Error fetching model schema: ${error.message}`);
      setSnackbarOpen(true);
    } finally {
      setIsLoading(false);
    }
  };
  
  const fetchAgentSchema = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await axios.get(`${apiUrl}/pydantic-test/agent-schema`);
      setAgentSchema(response.data);
    } catch (error: any) {
      console.error('Error fetching agent schema:', error);
      setError(`Error fetching agent schema: ${error.message}`);
      setSnackbarOpen(true);
    } finally {
      setIsLoading(false);
    }
  };
  
  const testModelValidation = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Using the example data from the model's schema
      const testData = {
        prompt: "Generate a Python function to calculate Fibonacci numbers",
        task_type: "code_generation",
        temperature: 0.7,
        max_tokens: 2000,
        context: {
          language: "python",
          version: "3.9"
        }
      };
      
      const response = await axios.post(`${apiUrl}/pydantic-test/validate-model-request`, testData);
      setValidationResult(response.data);
    } catch (error: any) {
      console.error('Error validating model request:', error);
      setError(`Error validating model request: ${error.message}`);
      setSnackbarOpen(true);
    } finally {
      setIsLoading(false);
    }
  };
  
  const testAgentValidation = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      // Using the example data from the agent's schema
      const testData = {
        request_type: "create_project",
        project: {
          name: "MyProject",
          description: "A web application with user authentication",
          tech_stack: {
            frontend: "react",
            backend: "fastapi",
            database: "mongodb"
          }
        }
      };
      
      const response = await axios.post(`${apiUrl}/pydantic-test/validate-agent-request`, testData);
      setValidationResult(response.data);
    } catch (error: any) {
      console.error('Error validating agent request:', error);
      setError(`Error validating agent request: ${error.message}`);
      setSnackbarOpen(true);
    } finally {
      setIsLoading(false);
    }
  };
  
  const handleSnackbarClose = () => {
    setSnackbarOpen(false);
  };
  
  return (
    <Paper elevation={2} sx={{ p: 3, borderRadius: 2, mb: 3 }}>
      <Typography variant="h6" gutterBottom>
        Pydantic V2 Compatibility Tester
      </Typography>
      <Typography variant="body2" color="text.secondary" paragraph>
        Test that our Pydantic V2 compatibility fixes are working correctly in the multi-agent system.
      </Typography>
      <Divider sx={{ mb: 2 }} />
      
      <Box sx={{ mb: 2 }}>
        <Button 
          variant="contained" 
          onClick={fetchModelSchema} 
          disabled={isLoading}
          sx={{ mr: 1, mb: { xs: 1, md: 0 } }}
        >
          Test Model Schema
        </Button>
        <Button 
          variant="contained" 
          onClick={fetchAgentSchema} 
          disabled={isLoading}
          sx={{ mr: 1, mb: { xs: 1, md: 0 } }}
        >
          Test Agent Schema
        </Button>
        <Button 
          variant="outlined" 
          onClick={testModelValidation} 
          disabled={isLoading}
          sx={{ mr: 1, mb: { xs: 1, md: 0 } }}
        >
          Validate Model Request
        </Button>
        <Button 
          variant="outlined" 
          onClick={testAgentValidation} 
          disabled={isLoading}
          sx={{ mb: { xs: 1, md: 0 } }}
        >
          Validate Agent Request
        </Button>
      </Box>
      
      {isLoading && (
        <Box display="flex" alignItems="center" justifyContent="center" my={4}>
          <CircularProgress size={40} />
          <Typography variant="body2" color="text.secondary" sx={{ ml: 2 }}>
            Testing Pydantic compatibility...
          </Typography>
        </Box>
      )}
      
      {modelSchema && (
        <Accordion sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">Model Schema Test Results</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
              <pre>{JSON.stringify(modelSchema, null, 2)}</pre>
            </Box>
          </AccordionDetails>
        </Accordion>
      )}
      
      {agentSchema && (
        <Accordion sx={{ mb: 2 }}>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">Agent Schema Test Results</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
              <pre>{JSON.stringify(agentSchema, null, 2)}</pre>
            </Box>
          </AccordionDetails>
        </Accordion>
      )}
      
      {validationResult && (
        <Accordion>
          <AccordionSummary expandIcon={<ExpandMoreIcon />}>
            <Typography variant="subtitle1">Validation Test Results</Typography>
          </AccordionSummary>
          <AccordionDetails>
            <Box sx={{ maxHeight: 300, overflow: 'auto' }}>
              <pre>{JSON.stringify(validationResult, null, 2)}</pre>
            </Box>
          </AccordionDetails>
        </Accordion>
      )}
      
      <Snackbar 
        open={snackbarOpen} 
        autoHideDuration={6000} 
        onClose={handleSnackbarClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleSnackbarClose} severity="error" sx={{ width: '100%' }}>
          {error}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

export default PydanticTester;
