import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Slider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow
} from '@mui/material';
import {
  Info as InfoIcon,
  Refresh as RefreshIcon,
  Save as SaveIcon
} from '@mui/icons-material';
import {
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  ResponsiveContainer
} from 'recharts';

interface Strategy {
  name: string;
  description: string;
  weights: Record<string, number>;
}

interface ModelSelectionStrategyProps {
  onStrategyChange?: (strategy: Strategy) => void;
}

const ModelSelectionStrategy: React.FC<ModelSelectionStrategyProps> = ({
  onStrategyChange
}) => {
  const [strategies, setStrategies] = useState<Strategy[]>([]);
  const [selectedStrategy, setSelectedStrategy] = useState<string>('');
  const [customWeights, setCustomWeights] = useState<Record<string, number>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchStrategies();
  }, []);

  const fetchStrategies = async () => {
    try {
      const response = await fetch('/api/models/selection-strategies');
      const data = await response.json();
      setStrategies(data.strategies);
      if (data.strategies.length > 0) {
        setSelectedStrategy(data.strategies[0].name);
        setCustomWeights(data.strategies[0].weights);
      }
    } catch (err) {
      setError('Failed to fetch selection strategies');
    }
  };

  const handleStrategyChange = (strategyName: string) => {
    setSelectedStrategy(strategyName);
    const strategy = strategies.find(s => s.name === strategyName);
    if (strategy) {
      setCustomWeights(strategy.weights);
      onStrategyChange?.(strategy);
    }
  };

  const handleWeightChange = (metric: string, value: number) => {
    setCustomWeights(prev => ({
      ...prev,
      [metric]: value
    }));
  };

  const handleSave = async () => {
    try {
      const response = await fetch('/api/models/selection-strategies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          name: selectedStrategy,
          weights: customWeights
        }),
      });
      if (!response.ok) {
        throw new Error('Failed to save strategy');
      }
      fetchStrategies();
    } catch (err) {
      setError('Failed to save selection strategy');
    }
  };

  const getStrategyData = () => {
    return Object.entries(customWeights).map(([metric, value]) => ({
      metric: metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()),
      value: value * 100
    }));
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">Model Selection Strategy</Typography>
            <Box>
              <Tooltip title="Refresh Strategies">
                <IconButton onClick={fetchStrategies}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Save Strategy">
                <IconButton onClick={handleSave}>
                  <SaveIcon />
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

        {/* Strategy Selection */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <FormControl fullWidth>
              <InputLabel>Selection Strategy</InputLabel>
              <Select
                value={selectedStrategy}
                onChange={(e) => handleStrategyChange(e.target.value as string)}
                label="Selection Strategy"
              >
                {strategies.map((strategy) => (
                  <MenuItem key={strategy.name} value={strategy.name}>
                    {strategy.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
            {selectedStrategy && (
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {strategies.find(s => s.name === selectedStrategy)?.description}
              </Typography>
            )}
          </Paper>
        </Grid>

        {/* Strategy Visualization */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Strategy Visualization
            </Typography>
            <Box sx={{ height: 400 }}>
              <ResponsiveContainer width="100%" height="100%">
                <RadarChart data={getStrategyData()}>
                  <PolarGrid />
                  <PolarAngleAxis dataKey="metric" />
                  <PolarRadiusAxis domain={[0, 100]} />
                  <Radar
                    name="Weights"
                    dataKey="value"
                    stroke="#8884d8"
                    fill="#8884d8"
                    fillOpacity={0.6}
                  />
                </RadarChart>
              </ResponsiveContainer>
            </Box>
          </Paper>
        </Grid>

        {/* Weight Configuration */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Weight Configuration
            </Typography>
            <Grid container spacing={2}>
              {Object.entries(customWeights).map(([metric, value]) => (
                <Grid item xs={12} md={6} key={metric}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography sx={{ minWidth: 200 }}>
                      {metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </Typography>
                    <Slider
                      value={value * 100}
                      onChange={(_, newValue) => handleWeightChange(metric, newValue as number / 100)}
                      min={0}
                      max={100}
                      step={1}
                      marks
                      valueLabelDisplay="auto"
                      valueLabelFormat={(value) => `${value}%`}
                    />
                    <Typography sx={{ minWidth: 60 }}>
                      {Math.round(value * 100)}%
                    </Typography>
                  </Box>
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>

        {/* Strategy Details */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Strategy Details
            </Typography>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Metric</TableCell>
                    <TableCell>Weight</TableCell>
                    <TableCell>Description</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(customWeights).map(([metric, weight]) => (
                    <TableRow key={metric}>
                      <TableCell>
                        {metric.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </TableCell>
                      <TableCell>{Math.round(weight * 100)}%</TableCell>
                      <TableCell>
                        <Tooltip title="Get more information about this metric">
                          <IconButton size="small">
                            <InfoIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ModelSelectionStrategy; 