import React from 'react';
import {
  Paper,
  Typography,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Box,
} from '@mui/material';
import {
  Code as BuildIcon,
  Security as SecurityIcon,
  CheckCircle as TestIcon,
  Cloud as DeployIcon,
} from '@mui/icons-material';

// Sample data for demonstration
const steps = [
  {
    label: 'Build',
    description: 'Compiling and building the application',
    icon: <BuildIcon />,
    status: 'completed',
  },
  {
    label: 'Security Scan',
    description: 'Running security vulnerability checks',
    icon: <SecurityIcon />,
    status: 'completed',
  },
  {
    label: 'Testing',
    description: 'Executing automated tests',
    icon: <TestIcon />,
    status: 'active',
  },
  {
    label: 'Deployment',
    description: 'Deploying to production environment',
    icon: <DeployIcon />,
    status: 'pending',
  },
];

const DeploymentPipeline: React.FC = () => {
  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Deployment Pipeline
      </Typography>
      <Stepper orientation="vertical">
        {steps.map((step, index) => (
          <Step key={step.label} active={step.status === 'active'} completed={step.status === 'completed'}>
            <StepLabel icon={step.icon}>{step.label}</StepLabel>
            <StepContent>
              <Typography variant="body2" color="text.secondary">
                {step.description}
              </Typography>
              <Box sx={{ mb: 2, mt: 1 }}>
                <Button
                  variant="contained"
                  size="small"
                  disabled={step.status === 'pending'}
                >
                  {step.status === 'completed' ? 'Rerun' : 'Execute'}
                </Button>
              </Box>
            </StepContent>
          </Step>
        ))}
      </Stepper>
    </Paper>
  );
};

export default DeploymentPipeline; 