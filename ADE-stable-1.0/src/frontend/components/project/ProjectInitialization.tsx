import React, { useState } from 'react';
import {
  Box,
  Stepper,
  Step,
  StepLabel,
  Button,
  Typography,
  Paper,
  Container,
  Grid,
  Alert,
  CircularProgress
} from '@mui/material';
import { ProjectSpecification, UserPreferences } from '../../../core/models/agent/types';
import { TechnicalDecisions } from './consultation/TechnicalDecisions';
import { SecurityImplications } from './consultation/SecurityImplications';
import { ResourceAllocation } from './consultation/ResourceAllocation';
import { BackupStrategy } from './consultation/BackupStrategy';
import { UserPreferencesForm } from './consultation/UserPreferencesForm';

interface ProjectInitializationProps {
  specification: ProjectSpecification;
  onComplete: (preferences: UserPreferences) => void;
  onCancel: () => void;
}

const steps = [
  'Technical Decisions',
  'Security Implications',
  'Resource Allocation',
  'Backup Strategy',
  'User Preferences'
];

export const ProjectInitialization: React.FC<ProjectInitializationProps> = ({
  specification,
  onComplete,
  onCancel
}) => {
  const [activeStep, setActiveStep] = useState(0);
  const [preferences, setPreferences] = useState<Partial<UserPreferences>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleNext = async () => {
    try {
      setLoading(true);
      setError(null);

      // Validate current step
      const isValid = await validateCurrentStep();
      if (!isValid) {
        return;
      }

      if (activeStep === steps.length - 1) {
        // Final step - complete the process
        await handleComplete();
      } else {
        setActiveStep((prevStep) => prevStep + 1);
      }
    } catch (error) {
      setError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleBack = () => {
    setActiveStep((prevStep) => prevStep - 1);
  };

  const handleComplete = async () => {
    try {
      setLoading(true);
      setError(null);

      // Validate all preferences
      const isValid = await validateAllPreferences();
      if (!isValid) {
        return;
      }

      // Call the completion handler
      onComplete(preferences as UserPreferences);
    } catch (error) {
      setError(error instanceof Error ? error.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const validateCurrentStep = async (): Promise<boolean> => {
    // Implement step-specific validation
    return true;
  };

  const validateAllPreferences = async (): Promise<boolean> => {
    // Implement overall preferences validation
    return true;
  };

  const renderStepContent = (step: number) => {
    switch (step) {
      case 0:
        return (
          <TechnicalDecisions
            specification={specification}
            onUpdate={(updates) => setPreferences({ ...preferences, ...updates })}
          />
        );
      case 1:
        return (
          <SecurityImplications
            security={specification.security}
            onUpdate={(updates) => setPreferences({ ...preferences, ...updates })}
          />
        );
      case 2:
        return (
          <ResourceAllocation
            performance={specification.performance}
            onUpdate={(updates) => setPreferences({ ...preferences, ...updates })}
          />
        );
      case 3:
        return (
          <BackupStrategy
            development={specification.development}
            onUpdate={(updates) => setPreferences({ ...preferences, ...updates })}
          />
        );
      case 4:
        return (
          <UserPreferencesForm
            preferences={preferences}
            onUpdate={setPreferences}
          />
        );
      default:
        return null;
    }
  };

  return (
    <Container maxWidth="lg">
      <Paper elevation={3} sx={{ p: 4, mt: 4 }}>
        <Typography variant="h4" gutterBottom>
          Project Initialization
        </Typography>

        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>

        <Box sx={{ mb: 4 }}>
          {loading ? (
            <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
              <CircularProgress />
            </Box>
          ) : (
            renderStepContent(activeStep)
          )}
        </Box>

        <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Button
            variant="outlined"
            onClick={onCancel}
            disabled={loading}
          >
            Cancel
          </Button>
          <Box>
            <Button
              variant="outlined"
              onClick={handleBack}
              disabled={activeStep === 0 || loading}
              sx={{ mr: 1 }}
            >
              Back
            </Button>
            <Button
              variant="contained"
              onClick={handleNext}
              disabled={loading}
            >
              {activeStep === steps.length - 1 ? 'Complete' : 'Next'}
            </Button>
          </Box>
        </Box>
      </Paper>
    </Container>
  );
}; 