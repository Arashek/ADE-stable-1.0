import React, { useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  LinearProgress,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  Timeline,
  Download,
  Share,
  Refresh,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  AreaChart,
  Area,
} from 'recharts';
import { MonitoringService } from '../../services/monitoring.service';

interface LoadTestResults {
  success: boolean;
  requests: number;
  rps: number;
  latency: {
    p50: number;
    p90: number;
    p99: number;
  };
  errors: number;
  timeline: Array<{
    timestamp: number;
    rps: number;
    latency: number;
    errors: number;
  }>;
}

interface LoadTestVisualizerProps {
  results: LoadTestResults;
}

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  height: '100%',
}));

const MetricBox = styled(Box)(({ theme }) => ({
  textAlign: 'center',
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.default,
}));

const getLatencyColor = (value: number): string => {
  if (value < 100) return '#4caf50';
  if (value < 300) return '#ff9800';
  return '#f44336';
};

const formatDuration = (ms: number): string => {
  if (ms < 1000) return `${ms}ms`;
  return `${(ms / 1000).toFixed(2)}s`;
};

export const LoadTestVisualizer: React.FC<LoadTestVisualizerProps> = ({ results }) => {
  const monitoring = MonitoringService.getInstance();

  useEffect(() => {
    monitoring.recordMetric({
      category: 'load_test',
      name: 'visualization_rendered',
      value: 1,
      tags: {
        success: results.success,
        total_requests: results.requests
      }
    });
  }, [results]);

  const handleExport = () => {
    try {
      const data = JSON.stringify(results, null, 2);
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `load-test-results-${Date.now()}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      monitoring.recordMetric({
        category: 'load_test',
        name: 'results_exported',
        value: 1
      });
    } catch (error) {
      monitoring.recordError('export_results_failed', error);
    }
  };

  const handleShare = () => {
    // Implement sharing functionality
    monitoring.recordMetric({
      category: 'load_test',
      name: 'results_shared',
      value: 1
    });
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
        <Typography variant="h6">Load Test Results</Typography>
        <Box>
          <Tooltip title="Export Results">
            <IconButton onClick={handleExport}>
              <Download />
            </IconButton>
          </Tooltip>
          <Tooltip title="Share Results">
            <IconButton onClick={handleShare}>
              <Share />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Summary Metrics */}
        <Grid item xs={12} md={3}>
          <StyledPaper>
            <MetricBox>
              <Typography variant="h4" color="primary">
                {results.requests.toLocaleString()}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Total Requests
              </Typography>
            </MetricBox>
          </StyledPaper>
        </Grid>
        <Grid item xs={12} md={3}>
          <StyledPaper>
            <MetricBox>
              <Typography 
                variant="h4"
                sx={{ color: getLatencyColor(results.latency.p90) }}
              >
                {formatDuration(results.latency.p90)}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                90th Percentile Latency
              </Typography>
            </MetricBox>
          </StyledPaper>
        </Grid>
        <Grid item xs={12} md={3}>
          <StyledPaper>
            <MetricBox>
              <Typography variant="h4" color="primary">
                {results.rps}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Requests per Second
              </Typography>
            </MetricBox>
          </StyledPaper>
        </Grid>
        <Grid item xs={12} md={3}>
          <StyledPaper>
            <MetricBox>
              <Typography 
                variant="h4"
                color={results.errors > 0 ? 'error' : 'success'}
              >
                {results.errors}
              </Typography>
              <Typography variant="body2" color="textSecondary">
                Total Errors
              </Typography>
            </MetricBox>
          </StyledPaper>
        </Grid>

        {/* Latency Distribution */}
        <Grid item xs={12} md={6}>
          <StyledPaper>
            <Typography variant="subtitle1" gutterBottom>
              Latency Distribution
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2">
                P50 Latency: {formatDuration(results.latency.p50)}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(results.latency.p50 / results.latency.p99) * 100}
                sx={{ 
                  height: 8,
                  backgroundColor: '#e0e0e0',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getLatencyColor(results.latency.p50)
                  }
                }}
              />
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2">
                P90 Latency: {formatDuration(results.latency.p90)}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(results.latency.p90 / results.latency.p99) * 100}
                sx={{
                  height: 8,
                  backgroundColor: '#e0e0e0',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getLatencyColor(results.latency.p90)
                  }
                }}
              />
            </Box>
            <Box>
              <Typography variant="body2">
                P99 Latency: {formatDuration(results.latency.p99)}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={100}
                sx={{
                  height: 8,
                  backgroundColor: '#e0e0e0',
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: getLatencyColor(results.latency.p99)
                  }
                }}
              />
            </Box>
          </StyledPaper>
        </Grid>

        {/* RPS Timeline */}
        <Grid item xs={12} md={6}>
          <StyledPaper>
            <Typography variant="subtitle1" gutterBottom>
              Requests per Second
            </Typography>
            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={results.timeline}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                />
                <YAxis />
                <RechartsTooltip
                  formatter={(value: number) => `${value} req/s`}
                  labelFormatter={(label: number) => new Date(label).toLocaleString()}
                />
                <Area
                  type="monotone"
                  dataKey="rps"
                  stroke="#2196f3"
                  fill="#2196f3"
                  fillOpacity={0.2}
                />
              </AreaChart>
            </ResponsiveContainer>
          </StyledPaper>
        </Grid>

        {/* Response Time Timeline */}
        <Grid item xs={12}>
          <StyledPaper>
            <Typography variant="subtitle1" gutterBottom>
              Response Time & Errors
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={results.timeline}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="timestamp"
                  tickFormatter={(value) => new Date(value).toLocaleTimeString()}
                />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <RechartsTooltip
                  formatter={(value: number, name: string) => [
                    name === 'latency' ? formatDuration(value) : value,
                    name === 'latency' ? 'Response Time' : 'Errors'
                  ]}
                  labelFormatter={(label: number) => new Date(label).toLocaleString()}
                />
                <Legend />
                <Line
                  yAxisId="left"
                  type="monotone"
                  dataKey="latency"
                  stroke="#2196f3"
                  name="Response Time"
                  dot={false}
                />
                <Line
                  yAxisId="right"
                  type="monotone"
                  dataKey="errors"
                  stroke="#f44336"
                  name="Errors"
                  dot={false}
                />
              </LineChart>
            </ResponsiveContainer>
          </StyledPaper>
        </Grid>
      </Grid>
    </Box>
  );
};
