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
  Chip,
  LinearProgress
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon
} from '@mui/icons-material';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer,
  Legend
} from 'recharts';

interface Model {
  name: string;
  provider: string;
}

interface ModelComparisonProps {
  models: Model[];
  selectedModel: string | null;
}

interface ComparisonMetrics {
  [key: string]: {
    performance: number;
    cost: number;
    reliability: number;
    scalability: number;
    security: number;
    compliance: number;
  };
}

const ModelComparison: React.FC<ModelComparisonProps> = ({
  models,
  selectedModel
}) => {
  const [selectedModels, setSelectedModels] = useState<string[]>([]);
  const [metrics, setMetrics] = useState<ComparisonMetrics>({});
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (selectedModels.length > 0) {
      fetchComparisonMetrics();
    }
  }, [selectedModels]);

  const fetchComparisonMetrics = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/models/comparison', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ models: selectedModels }),
      });
      const data = await response.json();
      setMetrics(data.metrics);
    } catch (err) {
      setError('Failed to fetch comparison metrics');
    } finally {
      setLoading(false);
    }
  };

  const handleModelSelect = (modelName: string) => {
    if (selectedModels.includes(modelName)) {
      setSelectedModels(selectedModels.filter(m => m !== modelName));
    } else if (selectedModels.length < 3) {
      setSelectedModels([...selectedModels, modelName]);
    }
  };

  const getTrendIcon = (value: number, average: number) => {
    if (value > average) {
      return <TrendingUpIcon color="success" />;
    } else if (value < average) {
      return <TrendingDownIcon color="error" />;
    }
    return null;
  };

  const getRadarData = () => {
    return Object.entries(metrics).map(([model, modelMetrics]) => ({
      model,
      ...modelMetrics
    }));
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
            <Typography variant="h4">Model Comparison</Typography>
            <Box>
              <Tooltip title="Refresh Comparison">
                <IconButton onClick={fetchComparisonMetrics}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
            </Box>
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

        {/* Model Selection */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Select Models to Compare (Max 3)
            </Typography>
            <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
              {models.map((model) => (
                <Chip
                  key={model.name}
                  label={`${model.name} (${model.provider})`}
                  color={selectedModels.includes(model.name) ? 'primary' : 'default'}
                  onClick={() => handleModelSelect(model.name)}
                  disabled={!selectedModels.includes(model.name) && selectedModels.length >= 3}
                />
              ))}
            </Box>
          </Paper>
        </Grid>

        {/* Comparison Visualization */}
        {selectedModels.length > 0 && (
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Typography variant="h6" gutterBottom>
                Performance Comparison
              </Typography>
              <Box sx={{ height: 400 }}>
                <ResponsiveContainer width="100%" height="100%">
                  <RadarChart data={getRadarData()}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="model" />
                    <PolarRadiusAxis domain={[0, 100]} />
                    <Radar
                      name="Performance"
                      dataKey="performance"
                      stroke="#8884d8"
                      fill="#8884d8"
                      fillOpacity={0.6}
                    />
                    <Radar
                      name="Cost"
                      dataKey="cost"
                      stroke="#82ca9d"
                      fill="#82ca9d"
                      fillOpacity={0.6}
                    />
                    <Radar
                      name="Reliability"
                      dataKey="reliability"
                      stroke="#ffc658"
                      fill="#ffc658"
                      fillOpacity={0.6}
                    />
                    <Radar
                      name="Scalability"
                      dataKey="scalability"
                      stroke="#ff8042"
                      fill="#ff8042"
                      fillOpacity={0.6}
                    />
                    <Radar
                      name="Security"
                      dataKey="security"
                      stroke="#ffbb28"
                      fill="#ffbb28"
                      fillOpacity={0.6}
                    />
                    <Radar
                      name="Compliance"
                      dataKey="compliance"
                      stroke="#00C49F"
                      fill="#00C49F"
                      fillOpacity={0.6}
                    />
                    <Legend />
                  </RadarChart>
                </ResponsiveContainer>
              </Box>
            </Paper>
          </Grid>
        )}

        {/* Detailed Metrics Table */}
        {selectedModels.length > 0 && (
          <Grid item xs={12}>
            <Paper>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Metric</TableCell>
                      {selectedModels.map((model) => (
                        <TableCell key={model} align="right">
                          {model}
                        </TableCell>
                      ))}
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {['performance', 'cost', 'reliability', 'scalability', 'security', 'compliance'].map((metric) => (
                      <TableRow key={metric}>
                        <TableCell component="th" scope="row">
                          {metric.charAt(0).toUpperCase() + metric.slice(1)}
                        </TableCell>
                        {selectedModels.map((model) => {
                          const value = metrics[model]?.[metric] || 0;
                          const average = Object.values(metrics).reduce((acc, curr) => acc + curr[metric], 0) / selectedModels.length;
                          return (
                            <TableCell key={model} align="right">
                              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 1 }}>
                                {value.toFixed(1)}
                                {getTrendIcon(value, average)}
                              </Box>
                            </TableCell>
                          );
                        })}
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

export default ModelComparison; 