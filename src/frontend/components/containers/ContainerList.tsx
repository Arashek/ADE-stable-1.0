import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  IconButton,
  Chip,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  MenuItem,
  Grid,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Pause,
  Delete,
  Backup,
  Restore,
  Settings,
} from '@mui/icons-material';
import { ContainerService, ContainerInfo } from '../../services/ContainerService';
import { ContainerConfig } from '../../../core/models/project/ContainerLifecycleManager';
import { ResourceLimits, AutoScalingConfig } from '../../../core/models/project/ResourceManager';

const containerService = new ContainerService();

export const ContainerList: React.FC = () => {
  const [containers, setContainers] = useState<ContainerInfo[]>([]);
  const [selectedContainer, setSelectedContainer] = useState<ContainerInfo | null>(null);
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [settingsDialogOpen, setSettingsDialogOpen] = useState(false);
  const [newContainerConfig, setNewContainerConfig] = useState<Partial<ContainerConfig>>({});
  const [resourceLimits, setResourceLimits] = useState<ResourceLimits>({
    cpu: { shares: 1024, period: 100000, quota: 100000 },
    memory: { limit: '2g', swap: '4g', reservation: '1g' },
    storage: { size: '20g', iops: 1000 },
  });
  const [autoScalingConfig, setAutoScalingConfig] = useState<AutoScalingConfig>({
    enabled: false,
    minInstances: 1,
    maxInstances: 5,
    targetCPUUtilization: 70,
    targetMemoryUtilization: 80,
    scaleUpThreshold: 80,
    scaleDownThreshold: 20,
    cooldownPeriod: 300,
  });

  useEffect(() => {
    loadContainers();
  }, []);

  const loadContainers = async () => {
    try {
      const containerList = await containerService.listContainers();
      setContainers(containerList);
    } catch (error) {
      console.error('Failed to load containers:', error);
    }
  };

  const handleCreateContainer = async () => {
    try {
      await containerService.createContainer(newContainerConfig as ContainerConfig);
      setCreateDialogOpen(false);
      loadContainers();
    } catch (error) {
      console.error('Failed to create container:', error);
    }
  };

  const handleContainerAction = async (action: string, containerId: string) => {
    try {
      switch (action) {
        case 'start':
          await containerService.startContainer(containerId);
          break;
        case 'stop':
          await containerService.stopContainer(containerId);
          break;
        case 'pause':
          await containerService.pauseContainer(containerId);
          break;
        case 'resume':
          await containerService.resumeContainer(containerId);
          break;
        case 'delete':
          await containerService.deleteContainer(containerId);
          break;
        case 'backup':
          await containerService.createBackup(containerId);
          break;
      }
      loadContainers();
    } catch (error) {
      console.error(`Failed to ${action} container:`, error);
    }
  };

  const handleUpdateSettings = async () => {
    if (!selectedContainer) return;

    try {
      await containerService.setResourceLimits(selectedContainer.id, resourceLimits);
      await containerService.configureAutoScaling(selectedContainer.id, autoScalingConfig);
      setSettingsDialogOpen(false);
      loadContainers();
    } catch (error) {
      console.error('Failed to update container settings:', error);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'running':
        return 'success';
      case 'stopped':
        return 'error';
      case 'paused':
        return 'warning';
      case 'restarting':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h5">Containers</Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={() => setCreateDialogOpen(true)}
        >
          Create Container
        </Button>
      </Box>

      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Status</TableCell>
              <TableCell>Health</TableCell>
              <TableCell>Resources</TableCell>
              <TableCell>Started At</TableCell>
              <TableCell>Actions</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {containers.map((container) => (
              <TableRow key={container.id}>
                <TableCell>{container.name}</TableCell>
                <TableCell>
                  <Chip
                    label={container.status}
                    color={getStatusColor(container.status)}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Chip
                    label={container.health}
                    color={container.health === 'healthy' ? 'success' : 'error'}
                    size="small"
                  />
                </TableCell>
                <TableCell>
                  <Typography variant="body2">
                    CPU: {container.resources.cpu}%
                  </Typography>
                  <Typography variant="body2">
                    Memory: {container.resources.memory}
                  </Typography>
                  <Typography variant="body2">
                    Storage: {container.resources.storage}
                  </Typography>
                </TableCell>
                <TableCell>
                  {new Date(container.startedAt).toLocaleString()}
                </TableCell>
                <TableCell>
                  <IconButton
                    onClick={() => handleContainerAction('start', container.id)}
                    disabled={container.status === 'running'}
                  >
                    <PlayArrow />
                  </IconButton>
                  <IconButton
                    onClick={() => handleContainerAction('stop', container.id)}
                    disabled={container.status === 'stopped'}
                  >
                    <Stop />
                  </IconButton>
                  <IconButton
                    onClick={() => handleContainerAction('pause', container.id)}
                    disabled={container.status !== 'running'}
                  >
                    <Pause />
                  </IconButton>
                  <IconButton
                    onClick={() => handleContainerAction('resume', container.id)}
                    disabled={container.status !== 'paused'}
                  >
                    <PlayArrow />
                  </IconButton>
                  <IconButton
                    onClick={() => handleContainerAction('backup', container.id)}
                  >
                    <Backup />
                  </IconButton>
                  <IconButton
                    onClick={() => {
                      setSelectedContainer(container);
                      setSettingsDialogOpen(true);
                    }}
                  >
                    <Settings />
                  </IconButton>
                  <IconButton
                    onClick={() => handleContainerAction('delete', container.id)}
                    color="error"
                  >
                    <Delete />
                  </IconButton>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* Create Container Dialog */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)}>
        <DialogTitle>Create New Container</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                value={newContainerConfig.name || ''}
                onChange={(e) =>
                  setNewContainerConfig({ ...newContainerConfig, name: e.target.value })
                }
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Image"
                value={newContainerConfig.image || ''}
                onChange={(e) =>
                  setNewContainerConfig({ ...newContainerConfig, image: e.target.value })
                }
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Restart Policy"
                select
                value={newContainerConfig.restartPolicy || 'unless-stopped'}
                onChange={(e) =>
                  setNewContainerConfig({
                    ...newContainerConfig,
                    restartPolicy: e.target.value as ContainerConfig['restartPolicy'],
                  })
                }
              >
                <MenuItem value="no">No</MenuItem>
                <MenuItem value="always">Always</MenuItem>
                <MenuItem value="unless-stopped">Unless Stopped</MenuItem>
                <MenuItem value="on-failure">On Failure</MenuItem>
              </TextField>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleCreateContainer} variant="contained" color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Settings Dialog */}
      <Dialog open={settingsDialogOpen} onClose={() => setSettingsDialogOpen(false)}>
        <DialogTitle>Container Settings</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Typography variant="h6">Resource Limits</Typography>
            </Grid>
            <Grid item xs={4}>
              <TextField
                fullWidth
                label="CPU Shares"
                type="number"
                value={resourceLimits.cpu.shares}
                onChange={(e) =>
                  setResourceLimits({
                    ...resourceLimits,
                    cpu: { ...resourceLimits.cpu, shares: parseInt(e.target.value) },
                  })
                }
              />
            </Grid>
            <Grid item xs={4}>
              <TextField
                fullWidth
                label="Memory Limit"
                value={resourceLimits.memory.limit}
                onChange={(e) =>
                  setResourceLimits({
                    ...resourceLimits,
                    memory: { ...resourceLimits.memory, limit: e.target.value },
                  })
                }
              />
            </Grid>
            <Grid item xs={4}>
              <TextField
                fullWidth
                label="Storage Size"
                value={resourceLimits.storage.size}
                onChange={(e) =>
                  setResourceLimits({
                    ...resourceLimits,
                    storage: { ...resourceLimits.storage, size: e.target.value },
                  })
                }
              />
            </Grid>

            <Grid item xs={12}>
              <Typography variant="h6">Auto Scaling</Typography>
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Min Instances"
                type="number"
                value={autoScalingConfig.minInstances}
                onChange={(e) =>
                  setAutoScalingConfig({
                    ...autoScalingConfig,
                    minInstances: parseInt(e.target.value),
                  })
                }
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Max Instances"
                type="number"
                value={autoScalingConfig.maxInstances}
                onChange={(e) =>
                  setAutoScalingConfig({
                    ...autoScalingConfig,
                    maxInstances: parseInt(e.target.value),
                  })
                }
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Scale Up Threshold (%)"
                type="number"
                value={autoScalingConfig.scaleUpThreshold}
                onChange={(e) =>
                  setAutoScalingConfig({
                    ...autoScalingConfig,
                    scaleUpThreshold: parseInt(e.target.value),
                  })
                }
              />
            </Grid>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Scale Down Threshold (%)"
                type="number"
                value={autoScalingConfig.scaleDownThreshold}
                onChange={(e) =>
                  setAutoScalingConfig({
                    ...autoScalingConfig,
                    scaleDownThreshold: parseInt(e.target.value),
                  })
                }
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsDialogOpen(false)}>Cancel</Button>
          <Button onClick={handleUpdateSettings} variant="contained" color="primary">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}; 