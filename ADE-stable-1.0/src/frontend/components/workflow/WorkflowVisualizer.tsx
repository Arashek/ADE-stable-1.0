import React, { useEffect, useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  Collapse,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  CheckCircle,
  Error,
  SkipNext,
  ExpandMore,
  ExpandLess,
  Timer,
  Speed,
  Assessment
} from '@mui/icons-material';
import { WorkflowStatus, WorkflowResult, WorkflowStage } from '../../../core/models/project/DevelopmentWorkflowManager';

interface WorkflowVisualizerProps {
  containerId: string;
  status: WorkflowStatus;
  result: WorkflowResult | null;
  onStart: () => void;
  onStop: () => void;
}

const StageStatusIcon: React.FC<{ status: 'success' | 'failure' | 'skipped' }> = ({ status }) => {
  switch (status) {
    case 'success':
      return <CheckCircle color="success" />;
    case 'failure':
      return <Error color="error" />;
    case 'skipped':
      return <SkipNext color="action" />;
    default:
      return null;
  }
};

const StageCard: React.FC<{ stage: WorkflowStage }> = ({ stage }) => {
  const [expanded, setExpanded] = useState(false);

  return (
    <Card variant="outlined" sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" alignItems="center" justifyContent="space-between">
          <Box display="flex" alignItems="center">
            <StageStatusIcon status={stage.status} />
            <Typography variant="h6" sx={{ ml: 1 }}>
              {stage.name}
            </Typography>
          </Box>
          <Box display="flex" alignItems="center">
            <Tooltip title="Duration">
              <Box display="flex" alignItems="center" sx={{ mr: 2 }}>
                <Timer fontSize="small" sx={{ mr: 0.5 }} />
                <Typography variant="body2">
                  {(stage.duration / 1000).toFixed(2)}s
                </Typography>
              </Box>
            </Tooltip>
            <IconButton onClick={() => setExpanded(!expanded)}>
              {expanded ? <ExpandLess /> : <ExpandMore />}
            </IconButton>
          </Box>
        </Box>
      </CardContent>
      <Collapse in={expanded}>
        <Divider />
        <Box sx={{ p: 2, bgcolor: 'grey.50' }}>
          <Typography variant="body2" component="pre" sx={{ whiteSpace: 'pre-wrap' }}>
            {stage.output}
          </Typography>
        </Box>
      </Collapse>
    </Card>
  );
};

export const WorkflowVisualizer: React.FC<WorkflowVisualizerProps> = ({
  containerId,
  status,
  result,
  onStart,
  onStop
}) => {
  const progress = status.progress;
  const isRunning = status.status === 'running';

  return (
    <Box>
      <Card sx={{ mb: 3 }}>
        <CardContent>
          <Grid container spacing={2} alignItems="center">
            <Grid item xs={12} md={6}>
              <Typography variant="h5" gutterBottom>
                Workflow Status
              </Typography>
              <Box display="flex" alignItems="center" gap={2}>
                <Chip
                  label={status.status.toUpperCase()}
                  color={
                    status.status === 'completed'
                      ? 'success'
                      : status.status === 'failed'
                      ? 'error'
                      : status.status === 'running'
                      ? 'primary'
                      : 'default'
                  }
                />
                {status.currentStage && (
                  <Typography variant="body2" color="text.secondary">
                    Current Stage: {status.currentStage}
                  </Typography>
                )}
              </Box>
            </Grid>
            <Grid item xs={12} md={6}>
              <Box display="flex" justifyContent="flex-end" gap={1}>
                <Tooltip title={isRunning ? 'Stop Workflow' : 'Start Workflow'}>
                  <IconButton
                    color={isRunning ? 'error' : 'primary'}
                    onClick={isRunning ? onStop : onStart}
                  >
                    {isRunning ? <Stop /> : <PlayArrow />}
                  </IconButton>
                </Tooltip>
              </Box>
            </Grid>
          </Grid>
          <Box sx={{ mt: 2 }}>
            <LinearProgress
              variant="determinate"
              value={progress}
              sx={{ height: 8, borderRadius: 4 }}
            />
            <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
              Progress: {Math.round(progress)}%
            </Typography>
          </Box>
        </CardContent>
      </Card>

      {result && (
        <Card>
          <CardContent>
            <Typography variant="h5" gutterBottom>
              Workflow Results
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Box display="flex" alignItems="center" gap={1}>
                  <Assessment />
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Total Duration
                    </Typography>
                    <Typography variant="h6">
                      {(result.summary.totalDuration / 1000).toFixed(2)}s
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box display="flex" alignItems="center" gap={1}>
                  <Speed />
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Parallel Executions
                    </Typography>
                    <Typography variant="h6">
                      {result.summary.parallelExecutions}
                    </Typography>
                  </Box>
                </Box>
              </Grid>
              <Grid item xs={12} md={4}>
                <Box display="flex" alignItems="center" gap={1}>
                  <Assessment />
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      Test Coverage
                    </Typography>
                    <Typography variant="h6">
                      {result.summary.coverage}%
                    </Typography>
                  </Box>
                </Box>
              </Grid>
            </Grid>

            <Typography variant="h6" sx={{ mt: 3, mb: 2 }}>
              Stages
            </Typography>
            <List>
              {result.stages.map((stage, index) => (
                <React.Fragment key={stage.name}>
                  <StageCard stage={stage} />
                  {index < result.stages.length - 1 && <Divider />}
                </React.Fragment>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
    </Box>
  );
}; 