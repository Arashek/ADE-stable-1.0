import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Tooltip,
  LinearProgress,
  Chip,
  Button,
} from '@mui/material';
import {
  CheckCircle as SuccessIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Refresh as RefreshIcon,
  Download as DownloadIcon,
} from '@mui/icons-material';

interface ResultsPanelProps {
  onRefresh: () => void;
}

interface TaskResult {
  id: string;
  name: string;
  status: 'success' | 'error' | 'warning';
  progress: number;
  duration: number;
  timestamp: Date;
  metrics: {
    cpu: number;
    memory: number;
    responseTime: number;
  };
  errors?: string[];
  warnings?: string[];
}

export const ResultsPanel: React.FC<ResultsPanelProps> = ({ onRefresh }) => {
  const [results, setResults] = useState<TaskResult[]>([
    {
      id: '1',
      name: 'Code Generation Task',
      status: 'success',
      progress: 100,
      duration: 45,
      timestamp: new Date(),
      metrics: {
        cpu: 75,
        memory: 800,
        responseTime: 1200,
      },
    },
    {
      id: '2',
      name: 'Documentation Update',
      status: 'warning',
      progress: 100,
      duration: 30,
      timestamp: new Date(),
      metrics: {
        cpu: 60,
        memory: 600,
        responseTime: 800,
      },
      warnings: ['Some sections need manual review'],
    },
    {
      id: '3',
      name: 'Error Analysis',
      status: 'error',
      progress: 60,
      duration: 20,
      timestamp: new Date(),
      metrics: {
        cpu: 90,
        memory: 1200,
        responseTime: 2000,
      },
      errors: ['Failed to analyze error patterns'],
    },
  ]);

  const getStatusIcon = (status: TaskResult['status']) => {
    switch (status) {
      case 'success':
        return <SuccessIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      default:
        return null;
    }
  };

  const getStatusColor = (status: TaskResult['status']) => {
    switch (status) {
      case 'success':
        return 'success';
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      default:
        return 'default';
    }
  };

  const formatDuration = (seconds: number) => {
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h6">Task Results</Typography>
          <Button
            variant="outlined"
            startIcon={<RefreshIcon />}
            onClick={onRefresh}
          >
            Refresh
          </Button>
        </Box>

        <List>
          {results.map((result) => (
            <ListItem
              key={result.id}
              sx={{
                border: 1,
                borderColor: 'divider',
                borderRadius: 1,
                mb: 2,
              }}
            >
              <ListItemIcon>{getStatusIcon(result.status)}</ListItemIcon>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle1">{result.name}</Typography>
                    <Chip
                      label={result.status.toUpperCase()}
                      size="small"
                      color={getStatusColor(result.status)}
                    />
                  </Box>
                }
                secondary={
                  <Box sx={{ mt: 1 }}>
                    <Grid container spacing={2}>
                      <Grid item xs={12}>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="body2" color="text.secondary">
                            Progress:
                          </Typography>
                          <Box sx={{ flexGrow: 1 }}>
                            <LinearProgress
                              variant="determinate"
                              value={result.progress}
                              color={getStatusColor(result.status)}
                            />
                          </Box>
                          <Typography variant="body2" color="text.secondary">
                            {result.progress}%
                          </Typography>
                        </Box>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2" color="text.secondary">
                          Duration: {formatDuration(result.duration)}
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2" color="text.secondary">
                          CPU: {result.metrics.cpu}%
                        </Typography>
                      </Grid>
                      <Grid item xs={12} sm={4}>
                        <Typography variant="body2" color="text.secondary">
                          Memory: {result.metrics.memory}MB
                        </Typography>
                      </Grid>
                      {result.errors && result.errors.length > 0 && (
                        <Grid item xs={12}>
                          <Typography variant="body2" color="error">
                            Errors: {result.errors.join(', ')}
                          </Typography>
                        </Grid>
                      )}
                      {result.warnings && result.warnings.length > 0 && (
                        <Grid item xs={12}>
                          <Typography variant="body2" color="warning.main">
                            Warnings: {result.warnings.join(', ')}
                          </Typography>
                        </Grid>
                      )}
                    </Grid>
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <Tooltip title="Download Results">
                  <IconButton edge="end">
                    <DownloadIcon />
                  </IconButton>
                </Tooltip>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
}; 