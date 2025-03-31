import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  ButtonGroup,
  Tooltip,
  IconButton,
  Alert,
  Snackbar,
  LinearProgress,
  Card,
  CardContent,
} from '@mui/material';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';
import {
  Refresh as RefreshIcon,
  Info as InfoIcon,
  Memory as MemoryIcon,
  Speed as SpeedIcon,
  Error as ErrorIcon,
  MonetizationOn as MonetizationOnIcon,
} from '@mui/icons-material';

// Mock data - Replace with actual API calls
const mockResourceData = [
  { time: '00:00', cpu: 45, memory: 60, disk: 30 },
  { time: '04:00', cpu: 55, memory: 65, disk: 35 },
  { time: '08:00', cpu: 75, memory: 80, disk: 45 },
  { time: '12:00', cpu: 65, memory: 70, disk: 40 },
  { time: '16:00', cpu: 85, memory: 85, disk: 50 },
  { time: '20:00', cpu: 60, memory: 65, disk: 35 },
];

const mockResponseTimeData = [
  { endpoint: '/api/users', avg: 120, p95: 250, p99: 500 },
  { endpoint: '/api/auth', avg: 80, p95: 150, p99: 300 },
  { endpoint: '/api/analytics', avg: 200, p95: 400, p99: 800 },
  { endpoint: '/api/search', avg: 150, p95: 300, p99: 600 },
];

const mockErrorData = [
  { type: 'Validation', count: 150, rate: 2.5 },
  { type: 'Authentication', count: 80, rate: 1.3 },
  { type: 'Database', count: 45, rate: 0.8 },
  { type: 'Network', count: 30, rate: 0.5 },
];

const mockCostData = [
  { service: 'Compute', cost: 1200, efficiency: 85 },
  { service: 'Storage', cost: 800, efficiency: 90 },
  { service: 'Network', cost: 600, efficiency: 88 },
  { service: 'Database', cost: 1000, efficiency: 82 },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042'];

// Resource Utilization Component
const ResourceUtilization = () => {
  const [timeRange, setTimeRange] = useState('24h');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  const handleRefresh = () => {
    // Implement refresh logic
    setNotification({
      open: true,
      message: 'Data refreshed successfully',
      severity: 'success',
    });
  };

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <MemoryIcon sx={{ mr: 1 }} />
          Resource Utilization
        </Typography>
        <Box>
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="View detailed metrics">
            <InfoIcon color="action" />
          </Tooltip>
        </Box>
      </Box>
      <Box sx={{ mb: 2 }}>
        <ButtonGroup size="small" sx={{ mb: 2 }}>
          <Button
            variant={timeRange === '1h' ? 'contained' : 'outlined'}
            onClick={() => setTimeRange('1h')}
          >
            1H
          </Button>
          <Button
            variant={timeRange === '24h' ? 'contained' : 'outlined'}
            onClick={() => setTimeRange('24h')}
          >
            24H
          </Button>
          <Button
            variant={timeRange === '7d' ? 'contained' : 'outlined'}
            onClick={() => setTimeRange('7d')}
          >
            7D
          </Button>
        </ButtonGroup>
      </Box>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={mockResourceData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="time" />
          <YAxis />
          <RechartsTooltip />
          <Legend />
          <Area
            type="monotone"
            dataKey="cpu"
            stackId="1"
            stroke="#8884d8"
            fill="#8884d8"
            fillOpacity={0.3}
            name="CPU %"
          />
          <Area
            type="monotone"
            dataKey="memory"
            stackId="2"
            stroke="#82ca9d"
            fill="#82ca9d"
            fillOpacity={0.3}
            name="Memory %"
          />
          <Area
            type="monotone"
            dataKey="disk"
            stackId="3"
            stroke="#ffc658"
            fill="#ffc658"
            fillOpacity={0.3}
            name="Disk %"
          />
        </AreaChart>
      </ResponsiveContainer>
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

// Response Time Monitoring Component
const ResponseTimeMonitoring = () => {
  const [timeRange, setTimeRange] = useState('24h');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  const handleRefresh = () => {
    // Implement refresh logic
    setNotification({
      open: true,
      message: 'Data refreshed successfully',
      severity: 'success',
    });
  };

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <SpeedIcon sx={{ mr: 1 }} />
          Response Time Monitoring
        </Typography>
        <Box>
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="View detailed metrics">
            <InfoIcon color="action" />
          </Tooltip>
        </Box>
      </Box>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={mockResponseTimeData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="endpoint" />
          <YAxis />
          <RechartsTooltip />
          <Legend />
          <Bar dataKey="avg" fill="#8884d8" name="Average (ms)" />
          <Bar dataKey="p95" fill="#82ca9d" name="P95 (ms)" />
          <Bar dataKey="p99" fill="#ffc658" name="P99 (ms)" />
        </BarChart>
      </ResponsiveContainer>
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

// Error Rate Visualization Component
const ErrorRateVisualization = () => {
  const [errorType, setErrorType] = useState('all');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  const handleRefresh = () => {
    // Implement refresh logic
    setNotification({
      open: true,
      message: 'Data refreshed successfully',
      severity: 'success',
    });
  };

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <ErrorIcon sx={{ mr: 1 }} />
          Error Rate Analysis
        </Typography>
        <Box>
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="View detailed metrics">
            <InfoIcon color="action" />
          </Tooltip>
        </Box>
      </Box>
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Error Type</InputLabel>
        <Select
          value={errorType}
          label="Error Type"
          onChange={(e) => setErrorType(e.target.value)}
        >
          <MenuItem value="all">All Types</MenuItem>
          <MenuItem value="validation">Validation</MenuItem>
          <MenuItem value="auth">Authentication</MenuItem>
          <MenuItem value="database">Database</MenuItem>
          <MenuItem value="network">Network</MenuItem>
        </Select>
      </FormControl>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={mockErrorData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="type" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <RechartsTooltip />
          <Legend />
          <Bar
            yAxisId="left"
            dataKey="count"
            fill="#8884d8"
            name="Error Count"
          />
          <Bar
            yAxisId="right"
            dataKey="rate"
            fill="#82ca9d"
            name="Error Rate %"
          />
        </BarChart>
      </ResponsiveContainer>
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

// Cost Efficiency Metrics Component
const CostEfficiencyMetrics = () => {
  const [timeRange, setTimeRange] = useState('month');
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  const handleRefresh = () => {
    // Implement refresh logic
    setNotification({
      open: true,
      message: 'Data refreshed successfully',
      severity: 'success',
    });
  };

  return (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <MonetizationOnIcon sx={{ mr: 1 }} />
          Cost Efficiency Metrics
        </Typography>
        <Box>
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="View detailed metrics">
            <InfoIcon color="action" />
          </Tooltip>
        </Box>
      </Box>
      <Box sx={{ mb: 2 }}>
        <ButtonGroup size="small" sx={{ mb: 2 }}>
          <Button
            variant={timeRange === 'week' ? 'contained' : 'outlined'}
            onClick={() => setTimeRange('week')}
          >
            Week
          </Button>
          <Button
            variant={timeRange === 'month' ? 'contained' : 'outlined'}
            onClick={() => setTimeRange('month')}
          >
            Month
          </Button>
          <Button
            variant={timeRange === 'quarter' ? 'contained' : 'outlined'}
            onClick={() => setTimeRange('quarter')}
          >
            Quarter
          </Button>
        </ButtonGroup>
      </Box>
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={mockCostData}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="cost"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          >
            {mockCostData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <RechartsTooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>
      <Box sx={{ mt: 2 }}>
        {mockCostData.map((service) => (
          <Box key={service.service} sx={{ mb: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="body2">{service.service}</Typography>
              <Typography variant="body2">{service.efficiency}% Efficiency</Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={service.efficiency}
              sx={{ height: 8, borderRadius: 4 }}
            />
          </Box>
        ))}
      </Box>
      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

const SystemPerformanceAnalytics = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        System Performance Analytics
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <ResourceUtilization />
        </Grid>
        <Grid item xs={12} md={6}>
          <ResponseTimeMonitoring />
        </Grid>
        <Grid item xs={12} md={6}>
          <ErrorRateVisualization />
        </Grid>
        <Grid item xs={12} md={6}>
          <CostEfficiencyMetrics />
        </Grid>
      </Grid>
    </Box>
  );
};

export default SystemPerformanceAnalytics; 