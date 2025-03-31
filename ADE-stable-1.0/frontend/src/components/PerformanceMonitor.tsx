import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  Speed as SpeedIcon,
  Memory as MemoryIcon,
  BugReport as BugIcon,
  Code as CodeIcon,
  Assessment as AssessmentIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as ChartTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface PerformanceMetrics {
  model: {
    responseTime: number;
    successRate: number;
    errorRate: number;
    tokenUsage: number;
    costPerRequest: number;
    historicalData: Array<{
      timestamp: string;
      responseTime: number;
      successRate: number;
      errorRate: number;
      tokenUsage: number;
      costPerRequest: number;
    }>;
  };
  agent: {
    taskCompletionRate: number;
    errorRecoveryRate: number;
    coordinationEfficiency: number;
    resourceUsage: number;
    historicalData: Array<{
      timestamp: string;
      taskCompletionRate: number;
      errorRecoveryRate: number;
      coordinationEfficiency: number;
      resourceUsage: number;
    }>;
  };
  system: {
    apiLatency: number;
    queueLength: number;
    resourceUtilization: number;
    costTracking: number;
    historicalData: Array<{
      timestamp: string;
      apiLatency: number;
      queueLength: number;
      resourceUtilization: number;
      costTracking: number;
    }>;
  };
  quality: {
    codeQualityScore: number;
    testCoverage: number;
    documentationCompleteness: number;
    errorPreventionRate: number;
    historicalData: Array<{
      timestamp: string;
      codeQualityScore: number;
      testCoverage: number;
      documentationCompleteness: number;
      errorPreventionRate: number;
    }>;
  };
}

interface PerformanceMonitorProps {
  projectId: string;
}

const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({ projectId }) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [timeRange, setTimeRange] = useState<'1h' | '24h' | '7d' | '30d'>('24h');
  const [selectedMetric, setSelectedMetric] = useState<string>('model');
  const [openDetailsDialog, setOpenDetailsDialog] = useState(false);

  useEffect(() => {
    fetchMetrics();
  }, [projectId, timeRange]);

  const fetchMetrics = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/performance/metrics?projectId=${projectId}&timeRange=${timeRange}`);
      if (!response.ok) {
        throw new Error('Failed to fetch performance metrics');
      }
      const data = await response.json();
      setMetrics(data);
    } catch (err) {
      setError('Failed to fetch performance metrics');
      console.error('Error fetching metrics:', err);
    } finally {
      setLoading(false);
    }
  };

  const getMetricColor = (value: number, threshold: number) => {
    return value >= threshold ? 'success' : value >= threshold * 0.7 ? 'warning' : 'error';
  };

  const renderMetricCard = (title: string, value: number, unit: string, threshold: number, icon: React.ReactNode) => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
          {icon}
          <Typography variant="h6" sx={{ ml: 1 }}>
            {title}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
          <Typography variant="h4" component="div">
            {value.toFixed(2)}
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ ml: 1 }}>
            {unit}
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={Math.min((value / threshold) * 100, 100)}
          color={getMetricColor(value, threshold)}
          sx={{ height: 8, borderRadius: 4 }}
        />
      </CardContent>
    </Card>
  );

  const renderHistoricalChart = (data: any[], metric: string) => (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="timestamp" />
        <YAxis />
        <ChartTooltip />
        <Legend />
        <Line type="monotone" dataKey={metric} stroke="#8884d8" />
      </LineChart>
    </ResponsiveContainer>
  );

  if (loading) {
    return <LinearProgress />;
  }

  if (error || !metrics) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="error">{error || 'No metrics available'}</Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">Performance Monitor</Typography>
            <Box>
              <FormControl sx={{ minWidth: 120, mr: 2 }}>
                <InputLabel>Time Range</InputLabel>
                <Select
                  value={timeRange}
                  label="Time Range"
                  onChange={(e) => setTimeRange(e.target.value as '1h' | '24h' | '7d' | '30d')}
                >
                  <MenuItem value="1h">Last Hour</MenuItem>
                  <MenuItem value="24h">Last 24 Hours</MenuItem>
                  <MenuItem value="7d">Last 7 Days</MenuItem>
                  <MenuItem value="30d">Last 30 Days</MenuItem>
                </Select>
              </FormControl>
              <IconButton onClick={fetchMetrics}>
                <RefreshIcon />
              </IconButton>
            </Box>
          </Box>
        </Grid>

        {/* Model Performance */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Model Performance
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Response Time',
                metrics.model.responseTime,
                'ms',
                1000,
                <SpeedIcon color="primary" />
              )}
            </Grid>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Success Rate',
                metrics.model.successRate,
                '%',
                95,
                <TrendingUpIcon color="primary" />
              )}
            </Grid>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Error Rate',
                metrics.model.errorRate,
                '%',
                5,
                <TrendingDownIcon color="primary" />
              )}
            </Grid>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Token Usage',
                metrics.model.tokenUsage,
                'tokens',
                1000,
                <MemoryIcon color="primary" />
              )}
            </Grid>
          </Grid>
        </Grid>

        {/* Agent Performance */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Agent Performance
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Task Completion',
                metrics.agent.taskCompletionRate,
                '%',
                90,
                <TimelineIcon color="primary" />
              )}
            </Grid>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Error Recovery',
                metrics.agent.errorRecoveryRate,
                '%',
                85,
                <BugIcon color="primary" />
              )}
            </Grid>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Coordination',
                metrics.agent.coordinationEfficiency,
                '%',
                80,
                <AssessmentIcon color="primary" />
              )}
            </Grid>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Resource Usage',
                metrics.agent.resourceUsage,
                '%',
                70,
                <MemoryIcon color="primary" />
              )}
            </Grid>
          </Grid>
        </Grid>

        {/* System Performance */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            System Performance
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'API Latency',
                metrics.system.apiLatency,
                'ms',
                500,
                <SpeedIcon color="primary" />
              )}
            </Grid>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Queue Length',
                metrics.system.queueLength,
                'tasks',
                100,
                <TimelineIcon color="primary" />
              )}
            </Grid>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Resource Usage',
                metrics.system.resourceUtilization,
                '%',
                80,
                <MemoryIcon color="primary" />
              )}
            </Grid>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Cost Tracking',
                metrics.system.costTracking,
                '$',
                100,
                <AssessmentIcon color="primary" />
              )}
            </Grid>
          </Grid>
        </Grid>

        {/* Quality Metrics */}
        <Grid item xs={12}>
          <Typography variant="h6" gutterBottom>
            Quality Metrics
          </Typography>
          <Grid container spacing={2}>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Code Quality',
                metrics.quality.codeQualityScore,
                '%',
                85,
                <CodeIcon color="primary" />
              )}
            </Grid>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Test Coverage',
                metrics.quality.testCoverage,
                '%',
                80,
                <AssessmentIcon color="primary" />
              )}
            </Grid>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Documentation',
                metrics.quality.documentationCompleteness,
                '%',
                90,
                <CodeIcon color="primary" />
              )}
            </Grid>
            <Grid item xs={12} md={3}>
              {renderMetricCard(
                'Error Prevention',
                metrics.quality.errorPreventionRate,
                '%',
                85,
                <BugIcon color="primary" />
              )}
            </Grid>
          </Grid>
        </Grid>

        {/* Historical Data Chart */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Historical Performance
            </Typography>
            <FormControl sx={{ minWidth: 200, mb: 2 }}>
              <InputLabel>Metric</InputLabel>
              <Select
                value={selectedMetric}
                label="Metric"
                onChange={(e) => setSelectedMetric(e.target.value)}
              >
                <MenuItem value="model">Model Performance</MenuItem>
                <MenuItem value="agent">Agent Performance</MenuItem>
                <MenuItem value="system">System Performance</MenuItem>
                <MenuItem value="quality">Quality Metrics</MenuItem>
              </Select>
            </FormControl>
            {renderHistoricalChart(
              metrics[selectedMetric as keyof PerformanceMetrics].historicalData,
              Object.keys(metrics[selectedMetric as keyof PerformanceMetrics].historicalData[0])[1]
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Details Dialog */}
      <Dialog
        open={openDetailsDialog}
        onClose={() => setOpenDetailsDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Performance Details</DialogTitle>
        <DialogContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Metric</TableCell>
                  <TableCell>Current Value</TableCell>
                  <TableCell>Threshold</TableCell>
                  <TableCell>Status</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {/* Add detailed metrics table here */}
              </TableBody>
            </Table>
          </TableContainer>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDetailsDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default PerformanceMonitor; 