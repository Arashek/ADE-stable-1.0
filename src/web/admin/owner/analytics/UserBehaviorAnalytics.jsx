import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  ButtonGroup,
  ToggleButton,
  ToggleButtonGroup,
  Tooltip,
  IconButton,
  Alert,
  Snackbar,
} from '@mui/material';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  AreaChart,
  Area,
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
  TrendingUp as TrendingUpIcon,
  Timeline as TimelineIcon,
  Group as GroupIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';

// Mock data - Replace with actual API calls
const mockFeatureUsageData = [
  { name: 'Feature A', usage: 65, adoption: 45, retention: 80 },
  { name: 'Feature B', usage: 45, adoption: 30, retention: 70 },
  { name: 'Feature C', usage: 80, adoption: 60, retention: 85 },
  { name: 'Feature D', usage: 35, adoption: 25, retention: 65 },
  { name: 'Feature E', usage: 55, adoption: 40, retention: 75 },
];

const mockUserJourneyData = [
  { step: 'Landing', users: 1000 },
  { step: 'Sign Up', users: 800 },
  { step: 'Profile Setup', users: 600 },
  { step: 'Feature A', users: 400 },
  { step: 'Feature B', users: 300 },
  { step: 'Feature C', users: 200 },
];

const mockRetentionData = [
  { week: 'Week 1', cohort1: 100, cohort2: 95, cohort3: 90 },
  { week: 'Week 2', cohort1: 85, cohort2: 80, cohort3: 75 },
  { week: 'Week 3', cohort1: 70, cohort2: 65, cohort3: 60 },
  { week: 'Week 4', cohort1: 55, cohort2: 50, cohort3: 45 },
];

const mockFeatureAdoptionData = [
  { name: 'Feature A', value: 45 },
  { name: 'Feature B', value: 30 },
  { name: 'Feature C', value: 60 },
  { name: 'Feature D', value: 25 },
  { name: 'Feature E', value: 40 },
];

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

// Feature Usage Visualization Component
const FeatureUsageVisualization = () => {
  const [timeRange, setTimeRange] = useState('week');
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
          <TrendingUpIcon sx={{ mr: 1 }} />
          Feature Usage Analytics
        </Typography>
        <Box>
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="View detailed analytics">
            <InfoIcon color="action" />
          </Tooltip>
        </Box>
      </Box>
      <Box sx={{ mb: 2 }}>
        <ButtonGroup size="small" sx={{ mb: 2 }}>
          <Button
            variant={timeRange === 'day' ? 'contained' : 'outlined'}
            onClick={() => setTimeRange('day')}
          >
            Day
          </Button>
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
        </ButtonGroup>
      </Box>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={mockFeatureUsageData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <RechartsTooltip />
          <Legend />
          <Bar dataKey="usage" fill="#8884d8" name="Usage %" />
          <Bar dataKey="adoption" fill="#82ca9d" name="Adoption %" />
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

// User Journey Analysis Component
const UserJourneyAnalysis = () => {
  const [viewMode, setViewMode] = useState('funnel');
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
          <TimelineIcon sx={{ mr: 1 }} />
          User Journey Analysis
        </Typography>
        <Box>
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="View detailed analytics">
            <InfoIcon color="action" />
          </Tooltip>
        </Box>
      </Box>
      <Box sx={{ mb: 2 }}>
        <ToggleButtonGroup
          value={viewMode}
          exclusive
          onChange={(_, newMode) => newMode && setViewMode(newMode)}
          size="small"
        >
          <ToggleButton value="funnel">Funnel View</ToggleButton>
          <ToggleButton value="path">Path Analysis</ToggleButton>
        </ToggleButtonGroup>
      </Box>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={mockUserJourneyData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="step" />
          <YAxis />
          <RechartsTooltip />
          <Legend />
          <Bar dataKey="users" fill="#8884d8" name="Users" />
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

// Retention Metrics Component
const RetentionMetrics = () => {
  const [cohort, setCohort] = useState('all');
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
          <GroupIcon sx={{ mr: 1 }} />
          Retention Metrics
        </Typography>
        <Box>
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="View detailed analytics">
            <InfoIcon color="action" />
          </Tooltip>
        </Box>
      </Box>
      <FormControl fullWidth sx={{ mb: 2 }}>
        <InputLabel>Cohort</InputLabel>
        <Select
          value={cohort}
          label="Cohort"
          onChange={(e) => setCohort(e.target.value)}
        >
          <MenuItem value="all">All Cohorts</MenuItem>
          <MenuItem value="cohort1">Cohort 1</MenuItem>
          <MenuItem value="cohort2">Cohort 2</MenuItem>
          <MenuItem value="cohort3">Cohort 3</MenuItem>
        </Select>
      </FormControl>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={mockRetentionData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="week" />
          <YAxis />
          <RechartsTooltip />
          <Legend />
          <Area
            type="monotone"
            dataKey="cohort1"
            stackId="1"
            stroke="#8884d8"
            fill="#8884d8"
            fillOpacity={0.3}
            name="Cohort 1"
          />
          <Area
            type="monotone"
            dataKey="cohort2"
            stackId="2"
            stroke="#82ca9d"
            fill="#82ca9d"
            fillOpacity={0.3}
            name="Cohort 2"
          />
          <Area
            type="monotone"
            dataKey="cohort3"
            stackId="3"
            stroke="#ffc658"
            fill="#ffc658"
            fillOpacity={0.3}
            name="Cohort 3"
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

// Feature Adoption Tracking Component
const FeatureAdoptionTracking = () => {
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
          <AssessmentIcon sx={{ mr: 1 }} />
          Feature Adoption Tracking
        </Typography>
        <Box>
          <Tooltip title="Refresh data">
            <IconButton onClick={handleRefresh} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="View detailed analytics">
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
            data={mockFeatureAdoptionData}
            cx="50%"
            cy="50%"
            labelLine={false}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
            label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
          >
            {mockFeatureAdoptionData.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <RechartsTooltip />
          <Legend />
        </PieChart>
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

const UserBehaviorAnalytics = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        User Behavior Analytics
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <FeatureUsageVisualization />
        </Grid>
        <Grid item xs={12} md={6}>
          <UserJourneyAnalysis />
        </Grid>
        <Grid item xs={12} md={6}>
          <RetentionMetrics />
        </Grid>
        <Grid item xs={12} md={6}>
          <FeatureAdoptionTracking />
        </Grid>
      </Grid>
    </Box>
  );
};

export default UserBehaviorAnalytics; 