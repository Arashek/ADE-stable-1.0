import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  CircularProgress,
  LinearProgress,
  Tooltip,
  IconButton,
} from '@mui/material';
import {
  Timeline,
  Memory,
  Speed,
  Warning,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { PerformanceService } from '../../services/performance/PerformanceService';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer } from 'recharts';

interface MetricCard {
  title: string;
  value: number;
  unit: string;
  icon: React.ReactNode;
  color: string;
  threshold?: number;
}

export const PerformanceMonitor: React.FC = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [timeSeriesData, setTimeSeriesData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const performanceService = PerformanceService.getInstance();
    let mounted = true;

    const fetchMetrics = async () => {
      try {
        const data = await performanceService.getCurrentMetrics();
        if (mounted) {
          setMetrics(data);
          setTimeSeriesData(prev => {
            const newData = [...prev, { ...data, timestamp: Date.now() }];
            return newData.slice(-20); // Keep last 20 data points
          });
        }
      } catch (error) {
        console.error('Error fetching metrics:', error);
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    };

    // Initial fetch
    fetchMetrics();

    // Set up real-time updates
    const interval = setInterval(fetchMetrics, 5000);

    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const handleRefresh = async () => {
    setLoading(true);
    const performanceService = PerformanceService.getInstance();
    try {
      const data = await performanceService.getCurrentMetrics();
      setMetrics(data);
    } finally {
      setLoading(false);
    }
  };

  if (!metrics && loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" height="100%">
        <CircularProgress />
      </Box>
    );
  }

  const metricCards: MetricCard[] = [
    {
      title: 'CPU Usage',
      value: metrics?.cpu || 0,
      unit: '%',
      icon: <Speed />,
      color: '#2196F3',
      threshold: 80,
    },
    {
      title: 'Memory Usage',
      value: metrics?.memory || 0,
      unit: '%',
      icon: <Memory />,
      color: '#4CAF50',
      threshold: 90,
    },
    {
      title: 'Response Time',
      value: metrics?.responseTime || 0,
      unit: 'ms',
      icon: <Timeline />,
      color: '#FF9800',
      threshold: 1000,
    },
    {
      title: 'Error Rate',
      value: metrics?.errorRate || 0,
      unit: '%',
      icon: <Warning />,
      color: '#f44336',
      threshold: 5,
    },
  ];

  return (
    <Paper elevation={3} sx={{ height: '100%', p: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
        <Typography variant="h6">Performance Monitoring</Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={handleRefresh} size="small">
            <RefreshIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Grid container spacing={2}>
        {metricCards.map((metric) => (
          <Grid item xs={12} sm={6} md={3} key={metric.title}>
            <Paper
              elevation={2}
              sx={{
                p: 2,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                position: 'relative',
                overflow: 'hidden',
              }}
            >
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  opacity: 0.1,
                  height: '100%',
                  bgcolor: metric.threshold && metric.value > metric.threshold
                    ? '#f44336'
                    : 'transparent',
                }}
              />
              <Box color={metric.color}>{metric.icon}</Box>
              <Typography variant="subtitle2" color="textSecondary">
                {metric.title}
              </Typography>
              <Typography variant="h6">
                {metric.value.toFixed(1)}{metric.unit}
              </Typography>
              <LinearProgress
                variant="determinate"
                value={Math.min((metric.value / (metric.threshold || 100)) * 100, 100)}
                sx={{
                  width: '100%',
                  mt: 1,
                  backgroundColor: `${metric.color}22`,
                  '& .MuiLinearProgress-bar': {
                    backgroundColor: metric.color,
                  },
                }}
              />
            </Paper>
          </Grid>
        ))}
      </Grid>

      <Box mt={4} height={300}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={timeSeriesData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis />
            <Line
              type="monotone"
              dataKey="cpu"
              stroke="#2196F3"
              name="CPU Usage"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="memory"
              stroke="#4CAF50"
              name="Memory Usage"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="responseTime"
              stroke="#FF9800"
              name="Response Time"
              dot={false}
            />
            <Line
              type="monotone"
              dataKey="errorRate"
              stroke="#f44336"
              name="Error Rate"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </Box>
    </Paper>
  );
}; 