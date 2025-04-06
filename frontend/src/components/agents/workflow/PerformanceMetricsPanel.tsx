import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Divider,
  FormControl,
  Select,
  MenuItem,
  InputLabel,
  useTheme,
  LinearProgress,
  Paper,
  Button,
  IconButton,
  Tooltip,
  Tab,
  Tabs
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Download as DownloadIcon,
  Timeline as TimelineIcon,
  BarChart as BarChartIcon,
  PieChart as PieChartIcon,
  FilterList as FilterListIcon
} from '@mui/icons-material';
import { Agent } from '../AgentListPanel';

interface PerformanceMetricsPanelProps {
  agents: Agent[];
  selectedAgentId?: string;
}

// Mock data for performance metrics
interface PerformanceMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  change: number; // percentage change
  target?: number;
  threshold?: {
    warning: number;
    critical: number;
  };
}

interface PerformanceCategory {
  id: string;
  name: string;
  metrics: PerformanceMetric[];
}

const generateMockPerformanceData = (): PerformanceCategory[] => {
  return [
    {
      id: 'response-time',
      name: 'Response Time',
      metrics: [
        {
          id: 'avg-response-time',
          name: 'Average Response Time',
          value: 235,
          unit: 'ms',
          change: -5.2,
          target: 200,
          threshold: {
            warning: 300,
            critical: 500
          }
        },
        {
          id: 'p95-response-time',
          name: 'P95 Response Time',
          value: 450,
          unit: 'ms',
          change: 2.1,
          target: 400,
          threshold: {
            warning: 600,
            critical: 1000
          }
        },
        {
          id: 'p99-response-time',
          name: 'P99 Response Time',
          value: 780,
          unit: 'ms',
          change: -1.3,
          target: 750,
          threshold: {
            warning: 1000,
            critical: 1500
          }
        }
      ]
    },
    {
      id: 'resource-usage',
      name: 'Resource Usage',
      metrics: [
        {
          id: 'cpu-usage',
          name: 'CPU Usage',
          value: 42,
          unit: '%',
          change: 8.5,
          target: 60,
          threshold: {
            warning: 75,
            critical: 90
          }
        },
        {
          id: 'memory-usage',
          name: 'Memory Usage',
          value: 3.2,
          unit: 'GB',
          change: 15.3,
          target: 4,
          threshold: {
            warning: 5,
            critical: 7
          }
        },
        {
          id: 'disk-io',
          name: 'Disk I/O',
          value: 120,
          unit: 'MB/s',
          change: -2.8,
          threshold: {
            warning: 200,
            critical: 300
          }
        }
      ]
    },
    {
      id: 'throughput',
      name: 'Throughput',
      metrics: [
        {
          id: 'requests-per-second',
          name: 'Requests Per Second',
          value: 320,
          unit: 'req/s',
          change: 12.7,
          target: 400
        },
        {
          id: 'tasks-completed',
          name: 'Tasks Completed',
          value: 1245,
          unit: 'tasks/hr',
          change: 5.4,
          target: 1500
        }
      ]
    }
  ];
};

const PerformanceMetricsPanel: React.FC<PerformanceMetricsPanelProps> = ({
  agents,
  selectedAgentId
}) => {
  const theme = useTheme();
  const [timeRange, setTimeRange] = useState('24h');
  const [chartType, setChartType] = useState(0);
  const [performanceData] = useState<PerformanceCategory[]>(generateMockPerformanceData());

  const handleTimeRangeChange = (event: any) => {
    setTimeRange(event.target.value);
  };

  const handleChartTypeChange = (event: React.SyntheticEvent, newValue: number) => {
    setChartType(newValue);
  };

  const getColorForMetric = (metric: PerformanceMetric) => {
    if (!metric.threshold) return theme.palette.info.main;
    
    if (metric.value >= metric.threshold.critical) {
      return theme.palette.error.main;
    } else if (metric.value >= metric.threshold.warning) {
      return theme.palette.warning.main;
    } else {
      return theme.palette.success.main;
    }
  };

  const getProgressValue = (metric: PerformanceMetric) => {
    if (!metric.target) return 100;
    return Math.min(100, (metric.value / metric.target) * 100);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Performance Metrics</Typography>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <FormControl variant="outlined" size="small" sx={{ minWidth: 120 }}>
            <InputLabel id="time-range-label">Time Range</InputLabel>
            <Select
              labelId="time-range-label"
              id="time-range"
              value={timeRange}
              onChange={handleTimeRangeChange}
              label="Time Range"
            >
              <MenuItem value="1h">Last Hour</MenuItem>
              <MenuItem value="6h">Last 6 Hours</MenuItem>
              <MenuItem value="24h">Last 24 Hours</MenuItem>
              <MenuItem value="7d">Last 7 Days</MenuItem>
              <MenuItem value="30d">Last 30 Days</MenuItem>
            </Select>
          </FormControl>
          
          <Tooltip title="Refresh Data">
            <IconButton>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          
          <Tooltip title="Download Report">
            <IconButton>
              <DownloadIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      
      <Paper sx={{ p: 1, mb: 2 }}>
        <Tabs
          value={chartType}
          onChange={handleChartTypeChange}
          variant="fullWidth"
        >
          <Tab icon={<TimelineIcon />} label="Line" />
          <Tab icon={<BarChartIcon />} label="Bar" />
          <Tab icon={<PieChartIcon />} label="Distribution" />
        </Tabs>
      </Paper>
      
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <Grid container spacing={2}>
          {performanceData.map((category) => (
            <Grid item xs={12} key={category.id}>
              <Card variant="outlined">
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    {category.name}
                  </Typography>
                  <Divider sx={{ mb: 2 }} />
                  
                  <Grid container spacing={3}>
                    {category.metrics.map((metric) => (
                      <Grid item xs={12} md={6} lg={4} key={metric.id}>
                        <Box sx={{ mb: 2 }}>
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                            <Typography variant="body2" color="textSecondary">
                              {metric.name}
                            </Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              <Typography 
                                variant="body2" 
                                color={metric.change < 0 ? 'success.main' : metric.change > 0 ? 'error.main' : 'textSecondary'}
                              >
                                {metric.change > 0 ? '+' : ''}{metric.change}%
                              </Typography>
                            </Box>
                          </Box>
                          
                          <Box sx={{ position: 'relative', pt: 0.5 }}>
                            <LinearProgress
                              variant="determinate"
                              value={getProgressValue(metric)}
                              sx={{ 
                                height: 8, 
                                borderRadius: 1,
                                bgcolor: theme.palette.background.paper,
                                '& .MuiLinearProgress-bar': {
                                  bgcolor: getColorForMetric(metric)
                                }
                              }}
                            />
                          </Box>
                          
                          <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 0.5 }}>
                            <Typography variant="h6">
                              {metric.value} <Typography component="span" variant="caption">{metric.unit}</Typography>
                            </Typography>
                            {metric.target && (
                              <Typography variant="body2" color="textSecondary">
                                Target: {metric.target} {metric.unit}
                              </Typography>
                            )}
                          </Box>
                        </Box>
                      </Grid>
                    ))}
                  </Grid>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Box>
    </Box>
  );
};

export default PerformanceMetricsPanel;
