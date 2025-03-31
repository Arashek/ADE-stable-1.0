import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  TextField,
  Button,
  Grid,
  Chip,
  FormControlLabel,
  Switch,
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
} from '@mui/icons-material';

interface TaskConfigurationPanelProps {
  onTaskConfigChange: (config: TaskConfig) => void;
}

interface TaskConfig {
  priority: 'low' | 'medium' | 'high';
  maxDuration: number;
  resourceLimits: {
    cpu: number;
    memory: number;
  };
  dependencies: string[];
  retryPolicy: {
    enabled: boolean;
    maxAttempts: number;
    backoffDelay: number;
  };
}

export const TaskConfigurationPanel: React.FC<TaskConfigurationPanelProps> = ({
  onTaskConfigChange,
}) => {
  const [config, setConfig] = useState<TaskConfig>({
    priority: 'medium',
    maxDuration: 3600,
    resourceLimits: {
      cpu: 80,
      memory: 1024,
    },
    dependencies: [],
    retryPolicy: {
      enabled: true,
      maxAttempts: 3,
      backoffDelay: 5,
    },
  });

  const handleChange = (field: keyof TaskConfig, value: any) => {
    const newConfig = { ...config, [field]: value };
    setConfig(newConfig);
    onTaskConfigChange(newConfig);
  };

  const handleResourceChange = (resource: 'cpu' | 'memory', value: number) => {
    const newConfig = {
      ...config,
      resourceLimits: {
        ...config.resourceLimits,
        [resource]: value,
      },
    };
    setConfig(newConfig);
    onTaskConfigChange(newConfig);
  };

  const handleRetryPolicyChange = (field: keyof TaskConfig['retryPolicy'], value: any) => {
    const newConfig = {
      ...config,
      retryPolicy: {
        ...config.retryPolicy,
        [field]: value,
      },
    };
    setConfig(newConfig);
    onTaskConfigChange(newConfig);
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Task Configuration
        </Typography>

        <Grid container spacing={3}>
          {/* Priority Selection */}
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Priority</InputLabel>
              <Select
                value={config.priority}
                label="Priority"
                onChange={(e) => handleChange('priority', e.target.value)}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Max Duration */}
          <Grid item xs={12}>
            <TextField
              fullWidth
              label="Max Duration (seconds)"
              type="number"
              value={config.maxDuration}
              onChange={(e) => handleChange('maxDuration', parseInt(e.target.value))}
            />
          </Grid>

          {/* Resource Limits */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Resource Limits
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="CPU Limit (%)"
                  type="number"
                  value={config.resourceLimits.cpu}
                  onChange={(e) => handleResourceChange('cpu', parseInt(e.target.value))}
                />
              </Grid>
              <Grid item xs={6}>
                <TextField
                  fullWidth
                  label="Memory Limit (MB)"
                  type="number"
                  value={config.resourceLimits.memory}
                  onChange={(e) => handleResourceChange('memory', parseInt(e.target.value))}
                />
              </Grid>
            </Grid>
          </Grid>

          {/* Retry Policy */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Retry Policy
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={config.retryPolicy.enabled}
                  onChange={(e) => handleRetryPolicyChange('enabled', e.target.checked)}
                />
              }
              label="Enable Retry"
            />
            {config.retryPolicy.enabled && (
              <Grid container spacing={2} sx={{ mt: 1 }}>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Max Attempts"
                    type="number"
                    value={config.retryPolicy.maxAttempts}
                    onChange={(e) =>
                      handleRetryPolicyChange('maxAttempts', parseInt(e.target.value))
                    }
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    fullWidth
                    label="Backoff Delay (s)"
                    type="number"
                    value={config.retryPolicy.backoffDelay}
                    onChange={(e) =>
                      handleRetryPolicyChange('backoffDelay', parseInt(e.target.value))
                    }
                  />
                </Grid>
              </Grid>
            )}
          </Grid>

          {/* Dependencies */}
          <Grid item xs={12}>
            <Typography variant="subtitle1" gutterBottom>
              Dependencies
            </Typography>
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
              {config.dependencies.map((dep) => (
                <Chip
                  key={dep}
                  label={dep}
                  onDelete={() =>
                    handleChange(
                      'dependencies',
                      config.dependencies.filter((d) => d !== dep)
                    )
                  }
                />
              ))}
            </Box>
            <Button
              variant="outlined"
              size="small"
              sx={{ mt: 1 }}
              onClick={() => {
                const newDep = prompt('Enter dependency name:');
                if (newDep) {
                  handleChange('dependencies', [...config.dependencies, newDep]);
                }
              }}
            >
              Add Dependency
            </Button>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}; 