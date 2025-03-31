import React from 'react';
import {
  Box,
  Paper,
  Typography,
  LinearProgress,
  Grid,
  Tooltip
} from '@mui/material';
import {
  Memory as MemoryIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  Memory as CpuIcon
} from '@mui/icons-material';

export interface ResourceMetrics {
  cpu: {
    usage: number;
    cores: number;
    temperature?: number;
  };
  memory: {
    total: number;
    used: number;
    free: number;
  };
  disk: {
    total: number;
    used: number;
    free: number;
  };
  network: {
    bytesIn: number;
    bytesOut: number;
    connections: number;
  };
}

interface ResourceMonitorProps {
  resources: ResourceMetrics;
}

const formatBytes = (bytes: number): string => {
  const units = ['B', 'KB', 'MB', 'GB', 'TB'];
  let value = bytes;
  let unitIndex = 0;

  while (value >= 1024 && unitIndex < units.length - 1) {
    value /= 1024;
    unitIndex++;
  }

  return `${value.toFixed(1)} ${units[unitIndex]}`;
};

const formatSpeed = (bytesPerSecond: number): string => {
  return `${formatBytes(bytesPerSecond)}/s`;
};

export const ResourceMonitor: React.FC<ResourceMonitorProps> = ({ resources }) => {
  const {
    cpu,
    memory,
    disk,
    network
  } = resources;

  const memoryUsage = (memory.used / memory.total) * 100;
  const diskUsage = (disk.used / disk.total) * 100;

  return (
    <Paper sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Resource Usage
      </Typography>
      <Grid container spacing={2}>
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <CpuIcon sx={{ mr: 1 }} />
            <Typography variant="body2">CPU</Typography>
          </Box>
          <Tooltip title={`${cpu.usage.toFixed(1)}% (${cpu.cores} cores)`}>
            <LinearProgress
              variant="determinate"
              value={cpu.usage}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Tooltip>
        </Grid>

        <Grid item xs={12}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <MemoryIcon sx={{ mr: 1 }} />
            <Typography variant="body2">Memory</Typography>
          </Box>
          <Tooltip title={`${formatBytes(memory.used)} / ${formatBytes(memory.total)}`}>
            <LinearProgress
              variant="determinate"
              value={memoryUsage}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Tooltip>
        </Grid>

        <Grid item xs={12}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <StorageIcon sx={{ mr: 1 }} />
            <Typography variant="body2">Disk</Typography>
          </Box>
          <Tooltip title={`${formatBytes(disk.used)} / ${formatBytes(disk.total)}`}>
            <LinearProgress
              variant="determinate"
              value={diskUsage}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Tooltip>
        </Grid>

        <Grid item xs={12}>
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
            <SpeedIcon sx={{ mr: 1 }} />
            <Typography variant="body2">Network</Typography>
          </Box>
          <Box sx={{ display: 'flex', gap: 2 }}>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="textSecondary">
                Upload: {formatSpeed(network.bytesOut)}
              </Typography>
            </Box>
            <Box sx={{ flex: 1 }}>
              <Typography variant="caption" color="textSecondary">
                Download: {formatSpeed(network.bytesIn)}
              </Typography>
            </Box>
          </Box>
        </Grid>
      </Grid>
    </Paper>
  );
}; 