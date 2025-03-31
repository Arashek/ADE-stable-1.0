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
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
} from 'recharts';
import {
  Refresh as RefreshIcon,
  Info as InfoIcon,
  TrendingUp as TrendingUpIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Psychology as PsychologyIcon,
} from '@mui/icons-material';

// Mock data - Replace with actual API calls
const mockModelPerformanceData = [
  { date: '2024-01', accuracy: 85, precision: 82, recall: 88, f1: 85 },
  { date: '2024-02', accuracy: 87, precision: 84, recall: 90, f1: 87 },
  { date: '2024-03', accuracy: 89, precision: 86, recall: 92, f1: 89 },
  { date: '2024-04', accuracy: 91, precision: 88, recall: 94, f1: 91 },
];

const mockErrorReductionData = [
  { type: 'Validation', before: 15, after: 5, reduction: 67 },
  { type: 'Classification', before: 25, after: 10, reduction: 60 },
  { type: 'Prediction', before: 20, after: 8, reduction: 60 },
  { type: 'Processing', before: 18, after: 6, reduction: 67 },
];

const mockKnowledgeDomainData = [
  { domain: 'Natural Language', coverage: 85, confidence: 90 },
  { domain: 'Computer Vision', coverage: 75, confidence: 85 },
  { domain: 'Speech Recognition', coverage: 80, confidence: 88 },
  { domain: 'Recommendation', coverage: 90, confidence: 92 },
  { domain: 'Anomaly Detection', coverage: 70, confidence: 82 },
  { domain: 'Time Series', coverage: 65, confidence: 78 },
];

// Model Performance Tracking Component
const ModelPerformanceTracking = () => {
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
          <TrendingUpIcon sx={{ mr: 1 }} />
          Model Performance Tracking
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
        <LineChart data={mockModelPerformanceData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" />
          <YAxis />
          <RechartsTooltip />
          <Legend />
          <Line
            type="monotone"
            dataKey="accuracy"
            stroke="#8884d8"
            name="Accuracy %"
          />
          <Line
            type="monotone"
            dataKey="precision"
            stroke="#82ca9d"
            name="Precision %"
          />
          <Line
            type="monotone"
            dataKey="recall"
            stroke="#ffc658"
            name="Recall %"
          />
          <Line
            type="monotone"
            dataKey="f1"
            stroke="#ff7300"
            name="F1 Score %"
          />
        </LineChart>
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

// Error Reduction Trends Component
const ErrorReductionTrends = () => {
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
          <TimelineIcon sx={{ mr: 1 }} />
          Error Reduction Trends
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
        <BarChart data={mockErrorReductionData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="type" />
          <YAxis yAxisId="left" />
          <YAxis yAxisId="right" orientation="right" />
          <RechartsTooltip />
          <Legend />
          <Bar
            yAxisId="left"
            dataKey="before"
            fill="#8884d8"
            name="Before %"
          />
          <Bar
            yAxisId="left"
            dataKey="after"
            fill="#82ca9d"
            name="After %"
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="reduction"
            stroke="#ff7300"
            name="Reduction %"
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

// Knowledge Domain Coverage Component
const KnowledgeDomainCoverage = () => {
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
          <PsychologyIcon sx={{ mr: 1 }} />
          Knowledge Domain Coverage
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
        <RadarChart data={mockKnowledgeDomainData}>
          <PolarGrid />
          <PolarAngleAxis dataKey="domain" />
          <PolarRadiusAxis />
          <Radar
            name="Coverage"
            dataKey="coverage"
            stroke="#8884d8"
            fill="#8884d8"
            fillOpacity={0.6}
          />
          <Radar
            name="Confidence"
            dataKey="confidence"
            stroke="#82ca9d"
            fill="#82ca9d"
            fillOpacity={0.6}
          />
          <Legend />
        </RadarChart>
      </ResponsiveContainer>
      <Box sx={{ mt: 2 }}>
        {mockKnowledgeDomainData.map((domain) => (
          <Box key={domain.domain} sx={{ mb: 1 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
              <Typography variant="body2">{domain.domain}</Typography>
              <Typography variant="body2">
                {domain.coverage}% Coverage | {domain.confidence}% Confidence
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={domain.coverage}
              sx={{ height: 8, borderRadius: 4, mb: 0.5 }}
            />
            <LinearProgress
              variant="determinate"
              value={domain.confidence}
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

const LearningAnalytics = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Learning Analytics
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <ModelPerformanceTracking />
        </Grid>
        <Grid item xs={12} md={6}>
          <ErrorReductionTrends />
        </Grid>
        <Grid item xs={12}>
          <KnowledgeDomainCoverage />
        </Grid>
      </Grid>
    </Box>
  );
};

export default LearningAnalytics; 