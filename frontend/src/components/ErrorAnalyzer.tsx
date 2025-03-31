import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  LinearProgress,
  Tooltip,
  Divider,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Card,
  CardContent,
  CardActions
} from '@mui/material';
import {
  BugReport as BugReportIcon,
  Build as BuildIcon,
  Security as SecurityIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon
} from '@mui/icons-material';

interface Error {
  id: string;
  title: string;
  description: string;
  type: 'runtime' | 'compilation' | 'security' | 'performance' | 'dependency';
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'open' | 'in_progress' | 'resolved' | 'prevented';
  timestamp: string;
  stackTrace?: string;
  aiAnalysis: {
    rootCause: string;
    impact: string;
    recoverySteps: string[];
    preventionMeasures: string[];
    similarIssues: Array<{
      title: string;
      link: string;
      resolution: string;
    }>;
  };
}

interface ErrorAnalyzerProps {
  projectId: string;
}

const ErrorAnalyzer: React.FC<ErrorAnalyzerProps> = ({ projectId }) => {
  const [errors, setErrors] = useState<Error[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedError, setSelectedError] = useState<Error | null>(null);
  const [newError, setNewError] = useState<Partial<Error>>({
    title: '',
    description: '',
    type: 'runtime',
    severity: 'medium',
    status: 'open',
    timestamp: new Date().toISOString(),
    aiAnalysis: {
      rootCause: '',
      impact: '',
      recoverySteps: [],
      preventionMeasures: [],
      similarIssues: []
    }
  });
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    fetchErrors();
  }, [projectId]);

  const fetchErrors = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/errors?projectId=${projectId}`);
      const data = await response.json();
      setErrors(data.errors);
    } catch (err) {
      setError('Failed to fetch errors');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateError = async () => {
    try {
      // First, get AI analysis of the error
      const analysisResponse = await fetch('/api/errors/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: newError.title,
          description: newError.description,
          type: newError.type,
          stackTrace: newError.stackTrace
        }),
      });
      const analysis = await analysisResponse.json();

      // Create error with AI analysis
      const response = await fetch('/api/errors', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newError,
          projectId,
          aiAnalysis: analysis
        }),
      });

      if (response.ok) {
        const createdError = await response.json();
        setErrors(prev => [...prev, createdError]);
        setOpenDialog(false);
        setNewError({
          title: '',
          description: '',
          type: 'runtime',
          severity: 'medium',
          status: 'open',
          timestamp: new Date().toISOString(),
          aiAnalysis: {
            rootCause: '',
            impact: '',
            recoverySteps: [],
            preventionMeasures: [],
            similarIssues: []
          }
        });
      } else {
        throw new Error('Failed to create error');
      }
    } catch (err) {
      setError('Failed to create error');
    }
  };

  const handleAnalyzeError = async (errorId: string) => {
    try {
      const response = await fetch(`/api/errors/${errorId}/analyze`, {
        method: 'POST',
      });
      if (response.ok) {
        const analysis = await response.json();
        setErrors(prev => prev.map(error => 
          error.id === errorId 
            ? { ...error, aiAnalysis: analysis }
            : error
        ));
      } else {
        throw new Error('Failed to analyze error');
      }
    } catch (err) {
      setError('Failed to analyze error');
    }
  };

  const handleRecoverError = async (errorId: string) => {
    try {
      const response = await fetch(`/api/errors/${errorId}/recover`, {
        method: 'POST',
      });
      if (response.ok) {
        const recovery = await response.json();
        setErrors(prev => prev.map(error => 
          error.id === errorId 
            ? { ...error, status: 'resolved', aiAnalysis: { ...error.aiAnalysis, recoverySteps: recovery.steps } }
            : error
        ));
      } else {
        throw new Error('Failed to recover from error');
      }
    } catch (err) {
      setError('Failed to recover from error');
    }
  };

  const handlePreventError = async (errorId: string) => {
    try {
      const response = await fetch(`/api/errors/${errorId}/prevent`, {
        method: 'POST',
      });
      if (response.ok) {
        const prevention = await response.json();
        setErrors(prev => prev.map(error => 
          error.id === errorId 
            ? { ...error, status: 'prevented', aiAnalysis: { ...error.aiAnalysis, preventionMeasures: prevention.measures } }
            : error
        ));
      } else {
        throw new Error('Failed to prevent error');
      }
    } catch (err) {
      setError('Failed to prevent error');
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'resolved':
        return <CheckCircleIcon color="success" />;
      case 'prevented':
        return <SecurityIcon color="success" />;
      case 'in_progress':
        return <InfoIcon color="info" />;
      default:
        return <ErrorIcon color="error" />;
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
            <Typography variant="h4">Error Analysis & Management</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenDialog(true)}
            >
              Report Error
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

        {/* Error List */}
        <Grid item xs={12}>
          <Paper>
            <List>
              {errors.map((error) => (
                <React.Fragment key={error.id}>
                  <ListItem>
                    <ListItemIcon>
                      {getStatusIcon(error.status)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {error.title}
                          <Chip
                            size="small"
                            label={error.severity}
                            color={getSeverityColor(error.severity)}
                            icon={<WarningIcon />}
                          />
                        </Box>
                      }
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            {error.description}
                          </Typography>
                          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                            <Chip
                              size="small"
                              label={error.type}
                              icon={<BugReportIcon />}
                            />
                            <Chip
                              size="small"
                              label={new Date(error.timestamp).toLocaleString()}
                              icon={<InfoIcon />}
                            />
                          </Box>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Tooltip title="Analyze Error">
                        <IconButton
                          edge="end"
                          onClick={() => handleAnalyzeError(error.id)}
                          sx={{ mr: 1 }}
                        >
                          <InfoIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Recover">
                        <IconButton
                          edge="end"
                          onClick={() => handleRecoverError(error.id)}
                          sx={{ mr: 1 }}
                        >
                          <RefreshIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Prevent">
                        <IconButton
                          edge="end"
                          onClick={() => handlePreventError(error.id)}
                          sx={{ mr: 1 }}
                        >
                          <SecurityIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Edit Error">
                        <IconButton
                          edge="end"
                          onClick={() => {
                            setSelectedError(error);
                            setOpenDialog(true);
                          }}
                          sx={{ mr: 1 }}
                        >
                          <EditIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete Error">
                        <IconButton
                          edge="end"
                          onClick={() => {
                            // Implement delete functionality
                          }}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </ListItemSecondaryAction>
                  </ListItem>

                  {/* AI Analysis */}
                  {error.aiAnalysis && (
                    <Card sx={{ ml: 4, mb: 2 }}>
                      <CardContent>
                        <Typography variant="h6" gutterBottom>
                          AI Analysis
                        </Typography>
                        <Grid container spacing={2}>
                          <Grid item xs={12}>
                            <Typography variant="subtitle1" color="primary">
                              Root Cause
                            </Typography>
                            <Typography variant="body2">
                              {error.aiAnalysis.rootCause}
                            </Typography>
                          </Grid>
                          <Grid item xs={12}>
                            <Typography variant="subtitle1" color="primary">
                              Impact
                            </Typography>
                            <Typography variant="body2">
                              {error.aiAnalysis.impact}
                            </Typography>
                          </Grid>
                          <Grid item xs={12}>
                            <Typography variant="subtitle1" color="primary">
                              Recovery Steps
                            </Typography>
                            <List>
                              {error.aiAnalysis.recoverySteps.map((step, index) => (
                                <ListItem key={index}>
                                  <ListItemIcon>
                                    <BuildIcon />
                                  </ListItemIcon>
                                  <ListItemText primary={step} />
                                </ListItem>
                              ))}
                            </List>
                          </Grid>
                          <Grid item xs={12}>
                            <Typography variant="subtitle1" color="primary">
                              Prevention Measures
                            </Typography>
                            <List>
                              {error.aiAnalysis.preventionMeasures.map((measure, index) => (
                                <ListItem key={index}>
                                  <ListItemIcon>
                                    <SecurityIcon />
                                  </ListItemIcon>
                                  <ListItemText primary={measure} />
                                </ListItem>
                              ))}
                            </List>
                          </Grid>
                          {error.aiAnalysis.similarIssues.length > 0 && (
                            <Grid item xs={12}>
                              <Typography variant="subtitle1" color="primary">
                                Similar Issues
                              </Typography>
                              <List>
                                {error.aiAnalysis.similarIssues.map((issue, index) => (
                                  <ListItem key={index}>
                                    <ListItemIcon>
                                      <InfoIcon />
                                    </ListItemIcon>
                                    <ListItemText
                                      primary={issue.title}
                                      secondary={
                                        <Box>
                                          <Typography variant="body2">
                                            {issue.resolution}
                                          </Typography>
                                          <Button
                                            size="small"
                                            href={issue.link}
                                            target="_blank"
                                            rel="noopener noreferrer"
                                          >
                                            View Details
                                          </Button>
                                        </Box>
                                      }
                                    />
                                  </ListItem>
                                ))}
                              </List>
                            </Grid>
                          )}
                        </Grid>
                      </CardContent>
                    </Card>
                  )}
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* Error Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedError ? 'Edit Error' : 'Report New Error'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Title"
                value={newError.title}
                onChange={(e) => setNewError({ ...newError, title: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={4}
                value={newError.description}
                onChange={(e) => setNewError({ ...newError, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={newError.type}
                  label="Type"
                  onChange={(e) => setNewError({ ...newError, type: e.target.value as Error['type'] })}
                >
                  <MenuItem value="runtime">Runtime</MenuItem>
                  <MenuItem value="compilation">Compilation</MenuItem>
                  <MenuItem value="security">Security</MenuItem>
                  <MenuItem value="performance">Performance</MenuItem>
                  <MenuItem value="dependency">Dependency</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Severity</InputLabel>
                <Select
                  value={newError.severity}
                  label="Severity"
                  onChange={(e) => setNewError({ ...newError, severity: e.target.value as Error['severity'] })}
                >
                  <MenuItem value="critical">Critical</MenuItem>
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Stack Trace"
                multiline
                rows={4}
                value={newError.stackTrace}
                onChange={(e) => setNewError({ ...newError, stackTrace: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateError} variant="contained" color="primary">
            {selectedError ? 'Save Changes' : 'Report Error'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ErrorAnalyzer; 