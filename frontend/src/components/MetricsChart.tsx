import React from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
  Tooltip,
} from '@mui/material';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
} from 'recharts';

interface Metric {
  name: string;
  value: number;
  target: number;
  unit: string;
}

interface MetricsChartProps {
  metrics: {
    codeQuality: Metric[];
    performance: Metric[];
    coverage: Metric[];
  };
}

export const MetricsChart: React.FC<MetricsChartProps> = ({ metrics }) => {
  const getProgressColor = (value: number, target: number) => {
    const ratio = value / target;
    if (ratio >= 1) return 'success';
    if (ratio >= 0.7) return 'warning';
    return 'error';
  };

  return (
    <Grid container spacing={3}>
      {/* Code Quality Metrics */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Code Quality
            </Typography>
            {metrics.codeQuality.map((metric) => (
              <Box key={metric.name} mb={2}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">{metric.name}</Typography>
                  <Typography variant="body2">
                    {metric.value}/{metric.target} {metric.unit}
                  </Typography>
                </Box>
                <Tooltip title={`Target: ${metric.target} ${metric.unit}`}>
                  <LinearProgress
                    variant="determinate"
                    value={(metric.value / metric.target) * 100}
                    color={getProgressColor(metric.value, metric.target)}
                  />
                </Tooltip>
              </Box>
            ))}
          </CardContent>
        </Card>
      </Grid>

      {/* Performance Metrics */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Performance
            </Typography>
            <Box height={200}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={metrics.performance}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis />
                  <RechartsTooltip />
                  <Bar
                    dataKey="value"
                    fill="#2196f3"
                    name="Current"
                  />
                  <Bar
                    dataKey="target"
                    fill="#4caf50"
                    name="Target"
                  />
                </BarChart>
              </ResponsiveContainer>
            </Box>
          </CardContent>
        </Card>
      </Grid>

      {/* Test Coverage */}
      <Grid item xs={12} md={4}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Test Coverage
            </Typography>
            {metrics.coverage.map((metric) => (
              <Box key={metric.name} mb={2}>
                <Box display="flex" justifyContent="space-between" mb={1}>
                  <Typography variant="body2">{metric.name}</Typography>
                  <Typography variant="body2">
                    {metric.value}% / {metric.target}%
                  </Typography>
                </Box>
                <Tooltip title={`Target: ${metric.target}%`}>
                  <LinearProgress
                    variant="determinate"
                    value={metric.value}
                    color={getProgressColor(metric.value, metric.target)}
                  />
                </Tooltip>
              </Box>
            ))}
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );
};
