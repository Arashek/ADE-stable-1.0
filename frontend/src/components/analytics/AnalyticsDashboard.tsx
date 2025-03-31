import React, { useEffect, useState, useMemo } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  useTheme,
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { analyticsService } from '../../services/analytics.service';
import { performanceMonitor } from '../../services/performance';

interface TimeRange {
  label: string;
  value: number;
}

const TIME_RANGES: TimeRange[] = [
  { label: 'Last Hour', value: 60 * 60 * 1000 },
  { label: 'Last 24 Hours', value: 24 * 60 * 60 * 1000 },
  { label: 'Last 7 Days', value: 7 * 24 * 60 * 60 * 1000 },
  { label: 'Last 30 Days', value: 30 * 24 * 60 * 60 * 1000 },
];

const METRICS = [
  { name: 'api-latency', label: 'API Latency' },
  { name: 'error-rate', label: 'Error Rate' },
  { name: 'user-actions', label: 'User Actions' },
  { name: 'memory-usage', label: 'Memory Usage' },
];

export const AnalyticsDashboard: React.FC = () => {
  const theme = useTheme();
  const [timeRange, setTimeRange] = useState<TimeRange>(TIME_RANGES[0]);
  const [data, setData] = useState<Record<string, any[]>>({});
  const [loading, setLoading] = useState(true);

  // Fetch data for all metrics
  useEffect(() => {
    const fetchData = async () => {
      const startTime = performance.now();
      setLoading(true);

      try {
        const newData: Record<string, any[]> = {};
        for (const metric of METRICS) {
          const timeSeriesData = analyticsService.getTimeSeriesData(
            metric.name,
            timeRange.value
          );
          newData[metric.name] = timeSeriesData;
        }
        setData(newData);
        performanceMonitor.recordMetric(
          'analytics-dashboard-data-fetch',
          performance.now() - startTime
        );
      } catch (error) {
        console.error('Error fetching analytics data:', error);
        performanceMonitor.recordMetric('analytics-dashboard-error', 1);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
    const interval = setInterval(fetchData, 60000); // Refresh every minute

    return () => clearInterval(interval);
  }, [timeRange]);

  // Calculate aggregated metrics
  const aggregatedMetrics = useMemo(() => {
    return METRICS.map(metric => ({
      ...metric,
      current: analyticsService.getAggregatedMetric(
        metric.name,
        'avg',
        timeRange.value
      ),
      total: analyticsService.getAggregatedMetric(
        metric.name,
        'sum',
        timeRange.value
      ),
    }));
  }, [timeRange, data]);

  const renderMetricCard = (metric: typeof METRICS[0]) => {
    const aggregated = aggregatedMetrics.find(m => m.name === metric.name);
    if (!aggregated) return null;

    return (
      <Grid item xs={12} sm={6} md={3}>
        <Paper
          sx={{
            p: 2,
            height: '100%',
            display: 'flex',
            flexDirection: 'column',
            bgcolor: theme.palette.background.paper,
          }}
        >
          <Typography variant="h6" gutterBottom>
            {metric.label}
          </Typography>
          <Typography variant="h4" component="div">
            {aggregated.current.toFixed(2)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Total: {aggregated.total.toFixed(2)}
          </Typography>
        </Paper>
      </Grid>
    );
  };

  const renderLineChart = (metric: typeof METRICS[0]) => {
    const chartData = data[metric.name] || [];

    return (
      <Grid item xs={12} md={6}>
        <Paper
          sx={{
            p: 2,
            height: 300,
            bgcolor: theme.palette.background.paper,
          }}
        >
          <Typography variant="h6" gutterBottom>
            {metric.label} Over Time
          </Typography>
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={(timestamp) =>
                  new Date(timestamp).toLocaleTimeString()
                }
              />
              <YAxis />
              <Tooltip
                labelFormatter={(timestamp) =>
                  new Date(timestamp).toLocaleString()
                }
              />
              <Legend />
              <Line
                type="monotone"
                dataKey="value"
                stroke={theme.palette.primary.main}
                dot={false}
              />
            </LineChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>
    );
  };

  const renderAreaChart = (metric: typeof METRICS[0]) => {
    const chartData = data[metric.name] || [];

    return (
      <Grid item xs={12} md={6}>
        <Paper
          sx={{
            p: 2,
            height: 300,
            bgcolor: theme.palette.background.paper,
          }}
        >
          <Typography variant="h6" gutterBottom>
            {metric.label} Distribution
          </Typography>
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="timestamp"
                tickFormatter={(timestamp) =>
                  new Date(timestamp).toLocaleTimeString()
                }
              />
              <YAxis />
              <Tooltip
                labelFormatter={(timestamp) =>
                  new Date(timestamp).toLocaleString()
                }
              />
              <Area
                type="monotone"
                dataKey="value"
                stroke={theme.palette.secondary.main}
                fill={theme.palette.secondary.light}
              />
            </AreaChart>
          </ResponsiveContainer>
        </Paper>
      </Grid>
    );
  };

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 3, display: 'flex', justifyContent: 'space-between' }}>
        <Typography variant="h4">Analytics Dashboard</Typography>
        <FormControl sx={{ minWidth: 200 }}>
          <InputLabel>Time Range</InputLabel>
          <Select
            value={timeRange.value}
            label="Time Range"
            onChange={(e) =>
              setTimeRange(
                TIME_RANGES.find((r) => r.value === e.target.value) ||
                  TIME_RANGES[0]
              )
            }
          >
            {TIME_RANGES.map((range) => (
              <MenuItem key={range.value} value={range.value}>
                {range.label}
              </MenuItem>
            ))}
          </Select>
        </FormControl>
      </Box>

      <Grid container spacing={3}>
        {/* Metric Cards */}
        {METRICS.map((metric) => renderMetricCard(metric))}

        {/* Charts */}
        {METRICS.slice(0, 2).map((metric) => renderLineChart(metric))}
        {METRICS.slice(2).map((metric) => renderAreaChart(metric))}
      </Grid>
    </Box>
  );
}; 