import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Button,
  Card,
  CardContent,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Alert,
  LinearProgress,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  IconButton,
  Tooltip,
  Divider,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Assignment as TaskIcon,
  Code as CodeIcon,
  RateReview as ReviewIcon,
  BugReport as TestIcon,
  Description as DocIcon,
  BugReport as BugIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Timeline as TimelineIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

interface CoordinationFlowProps {
  projectId: string;
  context: 'web' | 'mobile' | 'desktop' | 'backend' | 'frontend' | 'fullstack' | 'ai' | 'iot' | 'embedded';
}

interface FlowStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  agentType: string;
  dependencies: string[];
  results?: any;
  error?: string;
  startTime?: string;
  endTime?: string;
}

interface CoordinationTemplate {
  id: string;
  name: string;
  description: string;
  context: string[];
  steps: FlowStep[];
  priority: 'high' | 'medium' | 'low';
}

const CoordinationFlow: React.FC<CoordinationFlowProps> = ({ projectId, context }) => {
  const [activeStep, setActiveStep] = useState(0);
  const [flowSteps, setFlowSteps] = useState<FlowStep[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openTemplateDialog, setOpenTemplateDialog] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<CoordinationTemplate | null>(null);
  const [expandedStep, setExpandedStep] = useState<string | false>(false);

  // Context-specific coordination templates
  const coordinationTemplates: CoordinationTemplate[] = [
    {
      id: 'web_dev',
      name: 'Web Development Flow',
      description: 'Standard web application development workflow',
      context: ['web', 'frontend', 'fullstack'],
      steps: [
        {
          id: 'planning',
          title: 'Project Planning',
          description: 'Define requirements and architecture',
          status: 'pending',
          agentType: 'task_planner',
          dependencies: [],
        },
        {
          id: 'frontend',
          title: 'Frontend Development',
          description: 'Implement user interface and interactions',
          status: 'pending',
          agentType: 'code_generator',
          dependencies: ['planning'],
        },
        {
          id: 'backend',
          title: 'Backend Development',
          description: 'Implement server-side logic and APIs',
          status: 'pending',
          agentType: 'code_generator',
          dependencies: ['planning'],
        },
        {
          id: 'testing',
          title: 'Testing',
          description: 'Run unit and integration tests',
          status: 'pending',
          agentType: 'tester',
          dependencies: ['frontend', 'backend'],
        },
        {
          id: 'review',
          title: 'Code Review',
          description: 'Review code quality and best practices',
          status: 'pending',
          agentType: 'reviewer',
          dependencies: ['frontend', 'backend'],
        },
        {
          id: 'documentation',
          title: 'Documentation',
          description: 'Generate and update documentation',
          status: 'pending',
          agentType: 'documentation',
          dependencies: ['frontend', 'backend'],
        },
      ],
      priority: 'high',
    },
    {
      id: 'mobile_dev',
      name: 'Mobile Development Flow',
      description: 'Mobile application development workflow',
      context: ['mobile'],
      steps: [
        {
          id: 'planning',
          title: 'Project Planning',
          description: 'Define mobile app requirements and architecture',
          status: 'pending',
          agentType: 'task_planner',
          dependencies: [],
        },
        {
          id: 'ui_design',
          title: 'UI/UX Design',
          description: 'Design mobile interface and user flows',
          status: 'pending',
          agentType: 'code_generator',
          dependencies: ['planning'],
        },
        {
          id: 'development',
          title: 'App Development',
          description: 'Implement mobile app features',
          status: 'pending',
          agentType: 'code_generator',
          dependencies: ['ui_design'],
        },
        {
          id: 'testing',
          title: 'Testing',
          description: 'Run mobile-specific tests',
          status: 'pending',
          agentType: 'tester',
          dependencies: ['development'],
        },
        {
          id: 'optimization',
          title: 'Performance Optimization',
          description: 'Optimize app performance and resources',
          status: 'pending',
          agentType: 'code_generator',
          dependencies: ['development'],
        },
      ],
      priority: 'high',
    },
    {
      id: 'ai_dev',
      name: 'AI Development Flow',
      description: 'AI/ML model development workflow',
      context: ['ai'],
      steps: [
        {
          id: 'planning',
          title: 'Project Planning',
          description: 'Define AI model requirements and architecture',
          status: 'pending',
          agentType: 'task_planner',
          dependencies: [],
        },
        {
          id: 'data_prep',
          title: 'Data Preparation',
          description: 'Prepare and preprocess training data',
          status: 'pending',
          agentType: 'code_generator',
          dependencies: ['planning'],
        },
        {
          id: 'model_dev',
          title: 'Model Development',
          description: 'Develop and train AI model',
          status: 'pending',
          agentType: 'code_generator',
          dependencies: ['data_prep'],
        },
        {
          id: 'evaluation',
          title: 'Model Evaluation',
          description: 'Evaluate model performance',
          status: 'pending',
          agentType: 'tester',
          dependencies: ['model_dev'],
        },
        {
          id: 'optimization',
          title: 'Model Optimization',
          description: 'Optimize model performance',
          status: 'pending',
          agentType: 'code_generator',
          dependencies: ['evaluation'],
        },
      ],
      priority: 'high',
    },
    // Add more templates for other contexts...
  ];

  useEffect(() => {
    // Find appropriate template based on context
    const template = coordinationTemplates.find(t => t.context.includes(context));
    if (template) {
      setSelectedTemplate(template);
      setFlowSteps(template.steps);
    }
  }, [context]);

  const handleStartStep = async (stepId: string) => {
    try {
      const response = await fetch(`/api/coordination/step/${stepId}/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ projectId }),
      });

      if (response.ok) {
        const updatedStep = await response.json();
        setFlowSteps(prev => prev.map(step =>
          step.id === stepId ? updatedStep : step
        ));
      } else {
        throw new Error('Failed to start step');
      }
    } catch (err) {
      setError('Failed to start step');
    }
  };

  const handleCompleteStep = async (stepId: string) => {
    try {
      const response = await fetch(`/api/coordination/step/${stepId}/complete`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ projectId }),
      });

      if (response.ok) {
        const updatedStep = await response.json();
        setFlowSteps(prev => prev.map(step =>
          step.id === stepId ? updatedStep : step
        ));
      } else {
        throw new Error('Failed to complete step');
      }
    } catch (err) {
      setError('Failed to complete step');
    }
  };

  const handleError = async (stepId: string) => {
    try {
      const response = await fetch(`/api/coordination/step/${stepId}/error`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ projectId }),
      });

      if (response.ok) {
        const diagnosis = await response.json();
        setFlowSteps(prev => prev.map(step =>
          step.id === stepId ? { ...step, error: diagnosis } : step
        ));
      } else {
        throw new Error('Failed to handle error');
      }
    } catch (err) {
      setError('Failed to handle error');
    }
  };

  const getStepStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'primary';
      case 'failed':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getStepIcon = (agentType: string) => {
    switch (agentType) {
      case 'task_planner':
        return <TaskIcon />;
      case 'code_generator':
        return <CodeIcon />;
      case 'reviewer':
        return <ReviewIcon />;
      case 'tester':
        return <TestIcon />;
      case 'documentation':
        return <DocIcon />;
      case 'error_handler':
        return <BugIcon />;
      default:
        return <InfoIcon />;
    }
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">
              Coordination Flow - {context.charAt(0).toUpperCase() + context.slice(1)} Development
            </Typography>
            <Button
              variant="contained"
              startIcon={<SettingsIcon />}
              onClick={() => setOpenTemplateDialog(true)}
            >
              Customize Flow
            </Button>
          </Box>
        </Grid>

        {/* Error Alert */}
        {error && (
          <Grid item xs={12}>
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          </Grid>
        )}

        {/* Flow Steps */}
        <Grid item xs={12}>
          <Paper>
            <Stepper activeStep={activeStep} orientation="vertical">
              {flowSteps.map((step, index) => (
                <Step key={step.id}>
                  <StepLabel>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {step.title}
                      <Chip
                        size="small"
                        label={step.status}
                        color={getStepStatusColor(step.status)}
                      />
                    </Box>
                  </StepLabel>
                  <StepContent>
                    <Box sx={{ mb: 2 }}>
                      <Typography variant="body2" color="text.secondary">
                        {step.description}
                      </Typography>
                      <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                        <Chip
                          size="small"
                          icon={getStepIcon(step.agentType)}
                          label={step.agentType.replace('_', ' ')}
                          color="primary"
                        />
                        {step.dependencies.length > 0 && (
                          <Chip
                            size="small"
                            label={`Dependencies: ${step.dependencies.join(', ')}`}
                            color="secondary"
                          />
                        )}
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      {step.status === 'pending' && (
                        <Button
                          variant="contained"
                          startIcon={<StartIcon />}
                          onClick={() => handleStartStep(step.id)}
                        >
                          Start
                        </Button>
                      )}
                      {step.status === 'in_progress' && (
                        <Button
                          variant="contained"
                          color="success"
                          startIcon={<CheckCircleIcon />}
                          onClick={() => handleCompleteStep(step.id)}
                        >
                          Complete
                        </Button>
                      )}
                      {step.status === 'failed' && (
                        <Button
                          variant="contained"
                          color="error"
                          startIcon={<ErrorIcon />}
                          onClick={() => handleError(step.id)}
                        >
                          Diagnose Error
                        </Button>
                      )}
                    </Box>
                  </StepContent>
                </Step>
              ))}
            </Stepper>
          </Paper>
        </Grid>
      </Grid>

      {/* Template Customization Dialog */}
      <Dialog open={openTemplateDialog} onClose={() => setOpenTemplateDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>Customize Coordination Flow</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Template</InputLabel>
                <Select
                  value={selectedTemplate?.id || ''}
                  label="Template"
                  onChange={(e) => {
                    const template = coordinationTemplates.find(t => t.id === e.target.value);
                    if (template) {
                      setSelectedTemplate(template);
                      setFlowSteps(template.steps);
                    }
                  }}
                >
                  {coordinationTemplates.map(template => (
                    <MenuItem key={template.id} value={template.id}>
                      {template.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            {selectedTemplate && (
              <>
                <Grid item xs={12}>
                  <Typography variant="subtitle1" gutterBottom>
                    Steps
                  </Typography>
                  <List>
                    {selectedTemplate.steps.map((step, index) => (
                      <ListItem key={step.id}>
                        <ListItemIcon>
                          {getStepIcon(step.agentType)}
                        </ListItemIcon>
                        <ListItemText
                          primary={step.title}
                          secondary={step.description}
                        />
                      </ListItem>
                    ))}
                  </List>
                </Grid>
              </>
            )}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenTemplateDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CoordinationFlow; 