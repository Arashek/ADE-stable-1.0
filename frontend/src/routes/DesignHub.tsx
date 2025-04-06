import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Box, Typography, Button, Paper, Alert } from '@mui/material';
import { styled } from '@mui/material/styles';
import { ArrowBack as ArrowBackIcon } from '@mui/icons-material';
import { Code as CodeIcon } from '@mui/icons-material';

const StyledContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(3),
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  gap: theme.spacing(3)
}));

/**
 * Simplified DesignHub page that focuses on the core functionality
 * needed for local testing before cloud deployment
 */
const DesignHubPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>();
  const navigate = useNavigate();

  const handleBackToProject = () => {
    navigate(`/projects/${projectId}`);
  };

  const handleGoToCodeEditor = () => {
    navigate(`/editor/${projectId}`);
  };

  return (
    <StyledContainer>
      <Box display="flex" alignItems="center" gap={2}>
        <Button 
          startIcon={<ArrowBackIcon />} 
          onClick={handleBackToProject}
          variant="outlined"
        >
          Back to Project
        </Button>
        <Typography variant="h5">Design System</Typography>
      </Box>

      <Alert severity="info" sx={{ mt: 2 }}>
        The Design Hub has been simplified to focus on the core multi-agent architecture 
        for local testing before cloud deployment on cloudev.ai.
      </Alert>

      <Paper sx={{ p: 3, mt: 2 }}>
        <Typography variant="h6" gutterBottom>
          Design System Overview
        </Typography>
        <Typography paragraph>
          The ADE platform's design system functionality has been streamlined to focus on the essential
          multi-agent architecture that powers the platform. The specialized agents for architecture, 
          code generation, testing, debugging, and optimization are the core components that differentiate
          ADE from other platforms.
        </Typography>
        <Typography paragraph>
          For local testing purposes, you can proceed directly to the code editor to work with the
          multi-agent system.
        </Typography>
        <Button 
          variant="contained" 
          color="primary" 
          startIcon={<CodeIcon />}
          onClick={handleGoToCodeEditor}
          sx={{ mt: 2 }}
        >
          Go to Code Editor
        </Button>
      </Paper>
    </StyledContainer>
  );
};

export default DesignHubPage;
