import React, { useEffect, useState } from 'react';
import { Box, Paper, Typography, Grid, CircularProgress, Tooltip } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, ResponsiveContainer, Legend } from 'recharts';
import { performanceMonitor } from '../../services/performance';

interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
}

interface MetricChartData {
  timestamp: number;
  [key: string]: number;
}

const PerformancePanel: React.FC = () => {
  const [metrics, setMetrics] = useState<PerformanceMetric[]>([]);
  const [chartData, setChartData] = useState<MetricChartData[]>([]);

  useEffect(() => {
    const unsubscribe = performanceMonitor.subscribe((newMetrics) => {
      setMetrics(newMetrics);
      processChartData(newMetrics);
    });

    return () => {
      unsubscribe();
    };
  }, []);

  const processChartData = (metrics: PerformanceMetric[]) => {
    const timeWindow = 5 * 60 * 1000; // 5 minutes
    const now = Date.now();
    const recentMetrics = metrics.filter(m => now - m.timestamp <= timeWindow);

    const dataByTimestamp: { [key: number]: MetricChartData } = {};
    recentMetrics.forEach(metric => {
      const timestamp = metric.timestamp;
      if (!dataByTimestamp[timestamp]) {
        dataByTimestamp[timestamp] = { timestamp };
      }
      dataByTimestamp[timestamp][metric.name] = metric.value;
    });

    setChartData(Object.values(dataByTimestamp).sort((a, b) => a.timestamp - b.timestamp));
  };

  const getMetricAverage = (name: string): number => {
    return performanceMonitor.getAverageMetric(name);
  };

  const renderMetricCard = (name: string, description: string) => {
    const average = getMetricAverage(name);
    return (
      <Grid item xs={12} sm={6} md={4}>
        <Paper sx={{ p: 2, height: '100%' }}>
          <Typography variant="subtitle2" color="textSecondary">
            {description}
          </Typography>
          <Box display="flex" alignItems="center" mt={1}>
            <Typography variant="h6">
              {average.toFixed(2)} ms
            </Typography>
            <Tooltip title="Average over last minute">
              <CircularProgress
                variant="determinate"
                value={Math.min((average / 1000) * 100, 100)}
                size={24}
                sx={{ ml: 1 }}
              />
            </Tooltip>
          </Box>
        </Paper>
      </Grid>
    );
  };

  const renderPerformanceChart = () => {
    const metrics = ['ttfb', 'dom-load', 'page-load'];
    
    return (
      <Box height={400} mt={3}>
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              tickFormatter={(timestamp) => new Date(timestamp).toLocaleTimeString()}
            />
            <YAxis />
            <Legend />
            {metrics.map((metric, index) => (
              <Line
                key={metric}
                type="monotone"
                dataKey={metric}
                stroke={`hsl(${index * 120}, 70%, 50%)`}
                dot={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </Box>
    );
  };

  return (
    <Box p={3}>
      <Typography variant="h5" gutterBottom>
        Performance Metrics
      </Typography>
      
      <Grid container spacing={3}>
        {renderMetricCard('ttfb', 'Time to First Byte')}
        {renderMetricCard('dom-load', 'DOM Load Time')}
        {renderMetricCard('page-load', 'Page Load Time')}
      </Grid>

      {renderPerformanceChart()}

      <Grid container spacing={3} mt={3}>
        {renderMetricCard('heap-used', 'Heap Usage')}
        {renderMetricCard('long-task', 'Long Tasks Duration')}
        {renderMetricCard('connection-time', 'Connection Time')}
      </Grid>
    </Box>
  );
};

export default PerformancePanel; 