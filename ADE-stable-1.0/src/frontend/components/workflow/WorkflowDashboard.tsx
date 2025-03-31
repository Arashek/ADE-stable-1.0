import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  IconButton,
  Tooltip,
  Divider
} from '@mui/material';
import {
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  SkipNext as SkipIcon,
  Refresh as RefreshIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon
} from '@mui/icons-material';
import { WorkflowStatus, WorkflowResult, WorkflowConfig } from '../../../core/models/project/DevelopmentWorkflowManager';

interface WorkflowDashboardProps {
  containerId: string;
  config: WorkflowConfig;
  onStartWorkflow: () => Promise<void>;
  onStopWorkflow: () => Promise<void>;
  onRefresh: () => Promise<void>;
}

export const WorkflowDashboard: React.FC<WorkflowDashboardProps> = ({
  containerId,
  config,
  onStartWorkflow,
  onStopWorkflow,
  onRefresh
}) => {
  const [status, setStatus] = useState<WorkflowStatus>({
    status: 'idle',
    progress: 0,
    lastUpdated: new Date()
  });
  const [result, setResult] = useState<WorkflowResult | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        setLoading(true);
        await onRefresh();
      } catch (error) {
        console.error('Failed to fetch workflow status:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, [onRefresh]);

  const handleStart = async () => {
    try {
      setLoading(true);
      await onStartWorkflow();
    } catch (error) {
      console.error('Failed to start workflow:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleStop = async () => {
    try {
      setLoading(true);
      await onStopWorkflow();
    } catch (error) {
      console.error('Failed to stop workflow:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: WorkflowStatus['status']) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'failed':
        return 'error';
      case 'running':
        return 'primary';
      default:
        return 'default';
    }
  };

  const getStageIcon = (status: 'success' | 'failure' | 'skipped') => {
    switch (status) {
      case 'success':
        return <SuccessIcon color="success" />;
      case 'failure':
        return <ErrorIcon color="error" />;
      case 'skipped':
        return <SkipIcon color="action" />;
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Status Card */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
                  Workflow Status
                </Typography>
                <Box>
                  <Tooltip title="Start Workflow">
                    <IconButton
                      onClick={handleStart}
                      disabled={loading || status.status === 'running'}
                      color="primary"
                    >
                      <PlayIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Stop Workflow">
                    <IconButton
                      onClick={handleStop}
                      disabled={loading || status.status !== 'running'}
                      color="error"
                    >
                      <StopIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Refresh">
                    <IconButton
                      onClick={onRefresh}
                      disabled={loading}
                      color="primary"
                    >
                      <RefreshIcon />
                    </IconButton>
                  </Tooltip>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                <Chip
                  label={status.status.toUpperCase()}
                  color={getStatusColor(status.status)}
                  sx={{ mr: 2 }}
                />
                <Typography variant="body2" color="text.secondary">
                  Last Updated: {status.lastUpdated.toLocaleString()}
                </Typography>
              </Box>
              <LinearProgress
                variant="determinate"
                value={status.progress}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </CardContent>
          </Card>
        </Grid>

        {/* Stages Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="div" sx={{ mb: 2 }}>
                Workflow Stages
              </Typography>
              <List>
                {result?.stages.map((stage, index) => (
                  <React.Fragment key={index}>
                    <ListItem>
                      <ListItemIcon>
                        {getStageIcon(stage.status)}
                      </ListItemIcon>
                      <ListItemText
                        primary={stage.name}
                        secondary={`Duration: ${stage.duration}ms`}
                      />
                    </ListItem>
                    {index < result.stages.length - 1 && <Divider />}
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Summary Card */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="div" sx={{ mb: 2 }}>
                Workflow Summary
              </Typography>
              {result && (
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Overall Status"
                      secondary={
                        <Chip
                          label={result.success ? 'SUCCESS' : 'FAILED'}
                          color={result.success ? 'success' : 'error'}
                        />
                      }
                    />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText
                      primary="Test Results"
                      secondary={`${result.summary.passedTests} / ${result.summary.totalTests} tests passed`}
                    />
                  </ListItem>
                  <Divider />
                  <ListItem>
                    <ListItemText
                      primary="Coverage"
                      secondary={`${result.summary.coverage}%`}
                    />
                  </ListItem>
                  {result.summary.deploymentStatus && (
                    <>
                      <Divider />
                      <ListItem>
                        <ListItemText
                          primary="Deployment Status"
                          secondary={
                            <Chip
                              label={result.summary.deploymentStatus.toUpperCase()}
                              color={
                                result.summary.deploymentStatus === 'completed'
                                  ? 'success'
                                  : 'error'
                              }
                            />
                          }
                        />
                      </ListItem>
                    </>
                  )}
                </List>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Configuration Card */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Typography variant="h6" component="div" sx={{ mb: 2 }}>
                Workflow Configuration
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Version Control
                  </Typography>
                  <Typography variant="body2">
                    Repository: {config.versionControl.repository}
                  </Typography>
                  <Typography variant="body2">
                    Branch: {config.versionControl.branch}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    CI/CD
                  </Typography>
                  <Typography variant="body2">
                    CI Enabled: {config.ci.enabled ? 'Yes' : 'No'}
                  </Typography>
                  <Typography variant="body2">
                    CD Enabled: {config.cd.enabled ? 'Yes' : 'No'}
                  </Typography>
                  <Typography variant="body2">
                    Deployment Strategy: {config.cd.deploymentStrategy}
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Testing
                  </Typography>
                  <Typography variant="body2">
                    Environment: {config.testing.environment}
                  </Typography>
                  <Typography variant="body2">
                    Coverage Threshold: {config.testing.coverageThreshold}%
                  </Typography>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Typography variant="subtitle2" color="text.secondary">
                    Test Suites
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    {config.testing.testSuites.map((suite) => (
                      <Chip key={suite} label={suite} size="small" />
                    ))}
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}; 