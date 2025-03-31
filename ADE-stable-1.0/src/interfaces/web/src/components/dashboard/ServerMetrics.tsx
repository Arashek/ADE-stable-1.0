import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Box,
  Chip,
} from '@mui/material';
import {
  Timeline,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  TimelineItem,
  TimelineSeparator,
} from '@mui/lab';
import {
  Speed as SpeedIcon,
  People as PeopleIcon,
  Message as MessageIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';

interface Metrics {
  connections: {
    total: number;
    active: number;
    peak: number;
  };
  messages: {
    sent: number;
    received: number;
    errors: number;
    compressed: number;
  };
  performance: {
    avgMessageSize: number;
    avgProcessingTime: number;
  };
  rateLimit: {
    blocked: number;
    warnings: number;
  };
}

const MetricCard: React.FC<{
  title: string;
  value: number | string;
  icon: React.ReactNode;
  color?: string;
  subtitle?: string;
}> = ({ title, value, icon, color = 'primary', subtitle }) => (
  <Card sx={{ height: '100%' }}>
    <CardContent>
      <Box display="flex" alignItems="center" mb={2}>
        <Box mr={2}>{icon}</Box>
        <Typography variant="h6" component="div">
          {title}
        </Typography>
      </Box>
      <Typography variant="h4" component="div" color={color}>
        {value}
      </Typography>
      {subtitle && (
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
      )}
    </CardContent>
  </Card>
);

const ServerMetrics: React.FC = () => {
  const { data: metrics, isLoading, error } = useQuery<Metrics>({
    queryKey: ['serverMetrics'],
    queryFn: async () => {
      const response = await fetch('/api/metrics');
      if (!response.ok) {
        throw new Error('Failed to fetch metrics');
      }
      return response.json();
    },
    refetchInterval: 5000, // Refresh every 5 seconds
  });

  if (isLoading) {
    return <LinearProgress />;
  }

  if (error || !metrics) {
    return (
      <Typography color="error">
        Error loading metrics: {error?.message || 'Unknown error'}
      </Typography>
    );
  }

  const formatNumber = (num: number) => {
    return new Intl.NumberFormat().format(num);
  };

  const formatBytes = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  const formatTime = (ms: number) => {
    if (ms < 1) return `${(ms * 1000).toFixed(2)} μs`;
    if (ms < 1000) return `${ms.toFixed(2)} ms`;
    return `${(ms / 1000).toFixed(2)} s`;
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h5" gutterBottom>
        Server Metrics
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Active Connections"
            value={formatNumber(metrics.connections.active)}
            icon={<PeopleIcon color="primary" />}
            subtitle={`Peak: ${formatNumber(metrics.connections.peak)}`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Messages Today"
            value={formatNumber(metrics.messages.received)}
            icon={<MessageIcon color="info" />}
            subtitle={`${formatNumber(metrics.messages.compressed)} compressed`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Avg Processing Time"
            value={formatTime(metrics.performance.avgProcessingTime)}
            icon={<SpeedIcon color="success" />}
            subtitle={`Avg size: ${formatBytes(metrics.performance.avgMessageSize)}`}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <MetricCard
            title="Rate Limit Events"
            value={formatNumber(metrics.rateLimit.blocked)}
            icon={<WarningIcon color="warning" />}
            subtitle={`${formatNumber(metrics.rateLimit.warnings)} warnings`}
          />
        </Grid>
      </Grid>

      <Box mt={4}>
        <Typography variant="h6" gutterBottom>
          Message Flow
        </Typography>
        <Timeline position="alternate">
          <TimelineItem>
            <TimelineSeparator>
              <TimelineDot color="primary" />
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="h6">Messages Received</Typography>
              <Typography>{formatNumber(metrics.messages.received)}</Typography>
            </TimelineContent>
          </TimelineItem>
          <TimelineItem>
            <TimelineSeparator>
              <TimelineDot color="secondary" />
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="h6">Messages Sent</Typography>
              <Typography>{formatNumber(metrics.messages.sent)}</Typography>
            </TimelineContent>
          </TimelineItem>
          <TimelineItem>
            <TimelineSeparator>
              <TimelineDot color="warning" />
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="h6">Errors</Typography>
              <Typography>{formatNumber(metrics.messages.errors)}</Typography>
            </TimelineContent>
          </TimelineItem>
        </Timeline>
      </Box>

      <Box mt={4}>
        <Typography variant="h6" gutterBottom>
          System Status
        </Typography>
        <Box display="flex" gap={1}>
          <Chip
            label={`${metrics.connections.active} active connections`}
            color="primary"
            variant="outlined"
          />
          <Chip
            label={`${formatTime(metrics.performance.avgProcessingTime)} avg latency`}
            color="info"
            variant="outlined"
          />
          <Chip
            label={`${metrics.rateLimit.blocked} rate limits`}
            color="warning"
            variant="outlined"
          />
          <Chip
            label={`${formatBytes(metrics.performance.avgMessageSize)} avg msg size`}
            color="success"
            variant="outlined"
          />
        </Box>
      </Box>
    </Box>
  );
};

export default ServerMetrics; 