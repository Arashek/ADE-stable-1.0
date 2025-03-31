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
  IconButton,
  Tooltip,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  LinearProgress,
  Chip
} from '@mui/material';
import {
  Info as InfoIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon
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
  BarChart,
  Bar
} from 'recharts';

interface PerformanceMetrics {
  response_time: {
    average: number;
    min: number;
    max: number;
    p95: number;
    p99: number;
  };
  success_rate: number;
  error_rate: number;
  cost_per_request: number;
  resource_usage: {
    cpu: number;
    memory: number;
    gpu: number;
  };
  quality_metrics: {
    code_quality: number;
    test_coverage: number;
    documentation: number;
  };
  compliance_metrics: {
    security: number;
    privacy: number;
    ethics: number;
  };
}

interface ModelPerformanceMetricsProps {
  modelName?: string;
  timeRange?: string;
}

const ModelPerformanceMetrics: React.FC<ModelPerformanceMetricsProps> = ({
  modelName,
  timeRange = '24h'
}) => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [historicalData, setHistoricalData] = useState<any[]>([]);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchMetrics();
  }, [modelName, timeRange]);

  const fetchMetrics = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/models/metrics?model=${modelName}&time_range=${timeRange}`);
      const data = await response.json();
      setMetrics(data.metrics);
      setHistoricalData(data.historical_data);
    } catch (err) {
      setError('Failed to fetch performance metrics');
    } finally {
      setLoading(false);
    }
  };

  const getTrendIcon = (current: number, previous: number) => {
    if (current > previous) {
      return <TrendingUpIcon color="success" />;
    } else if (current < previous) {
      return <TrendingDownIcon color="error" />;
    }
    return null;
  };

  const formatValue = (value: number, type: string) => {
    switch (type) {
      case 'time':
        return `${value.toFixed(2)}ms`;
      case 'percentage':
        return `${(value * 100).toFixed(1)}%`;
      case 'cost':
        return `$${value.toFixed(4)}`;
      default:
        return value.toFixed(2);
    }
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">Performance Metrics</Typography>
            <Tooltip title="Refresh Metrics">
              <IconButton onClick={fetchMetrics}>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Grid>

        {/* Error Alert */}
        {error && (
          <Grid item xs={12}>
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          </Grid>
        )}

        {/* Response Time Metrics */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Response Time
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={historicalData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <ChartTooltip />
                  <Legend />
                  <Line
                    type="monotone"
                    dataKey="response_time"
                    stroke="#8884d8"
                    name="Response Time (ms)"
                  />
                </LineChart>
              </ResponsiveContainer>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell>Average</TableCell>
                    <TableCell align="right">
                      {formatValue(metrics?.response_time.average || 0, 'time')}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>P95</TableCell>
                    <TableCell align="right">
                      {formatValue(metrics?.response_time.p95 || 0, 'time')}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>P99</TableCell>
                    <TableCell align="right">
                      {formatValue(metrics?.response_time.p99 || 0, 'time')}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* Success/Error Rates */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Success/Error Rates
            </Typography>
            <Box sx={{ height: 300 }}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={historicalData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="timestamp" />
                  <YAxis />
                  <ChartTooltip />
                  <Legend />
                  <Bar
                    dataKey="success_rate"
                    fill="#4caf50"
                    name="Success Rate"
                  />
                  <Bar
                    dataKey="error_rate"
                    fill="#f44336"
                    name="Error Rate"
                  />
                </BarChart>
              </ResponsiveContainer>
            </Box>
            <TableContainer>
              <Table size="small">
                <TableBody>
                  <TableRow>
                    <TableCell>Success Rate</TableCell>
                    <TableCell align="right">
                      {formatValue(metrics?.success_rate || 0, 'percentage')}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Error Rate</TableCell>
                    <TableCell align="right">
                      {formatValue(metrics?.error_rate || 0, 'percentage')}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* Resource Usage */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Resource Usage
            </Typography>
            <TableContainer>
              <Table>
                <TableBody>
                  <TableRow>
                    <TableCell>CPU Usage</TableCell>
                    <TableCell align="right">
                      {formatValue(metrics?.resource_usage.cpu || 0, 'percentage')}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Memory Usage</TableCell>
                    <TableCell align="right">
                      {formatValue(metrics?.resource_usage.memory || 0, 'percentage')}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>GPU Usage</TableCell>
                    <TableCell align="right">
                      {formatValue(metrics?.resource_usage.gpu || 0, 'percentage')}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* Quality Metrics */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Quality Metrics
            </Typography>
            <TableContainer>
              <Table>
                <TableBody>
                  <TableRow>
                    <TableCell>Code Quality</TableCell>
                    <TableCell align="right">
                      {formatValue(metrics?.quality_metrics.code_quality || 0, 'percentage')}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Test Coverage</TableCell>
                    <TableCell align="right">
                      {formatValue(metrics?.quality_metrics.test_coverage || 0, 'percentage')}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Documentation</TableCell>
                    <TableCell align="right">
                      {formatValue(metrics?.quality_metrics.documentation || 0, 'percentage')}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* Compliance Metrics */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Compliance Metrics
            </Typography>
            <TableContainer>
              <Table>
                <TableBody>
                  <TableRow>
                    <TableCell>Security</TableCell>
                    <TableCell align="right">
                      {formatValue(metrics?.compliance_metrics.security || 0, 'percentage')}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Privacy</TableCell>
                    <TableCell align="right">
                      {formatValue(metrics?.compliance_metrics.privacy || 0, 'percentage')}
                    </TableCell>
                  </TableRow>
                  <TableRow>
                    <TableCell>Ethics</TableCell>
                    <TableCell align="right">
                      {formatValue(metrics?.compliance_metrics.ethics || 0, 'percentage')}
                    </TableCell>
                  </TableRow>
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ModelPerformanceMetrics; 