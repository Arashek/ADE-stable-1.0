import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Slider,
  TextField,
  Grid,
  Chip,
} from '@mui/material';
import { Speed as SpeedIcon, Memory as MemoryIcon, AttachMoney as CostIcon } from '@mui/icons-material';

interface ModelSelectionPanelProps {
  onModelConfigChange: (config: ModelConfig) => void;
}

interface ModelConfig {
  quality: 'high' | 'medium' | 'low';
  responseTimeLimit: number;
  contextLength: number;
  costPreference: 'optimize' | 'balanced' | 'performance';
}

export const ModelSelectionPanel: React.FC<ModelSelectionPanelProps> = ({ onModelConfigChange }) => {
  const [config, setConfig] = useState<ModelConfig>({
    quality: 'balanced',
    responseTimeLimit: 5000,
    contextLength: 4096,
    costPreference: 'balanced',
  });

  const handleChange = (field: keyof ModelConfig, value: any) => {
    const newConfig = { ...config, [field]: value };
    setConfig(newConfig);
    onModelConfigChange(newConfig);
  };

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Model Configuration
        </Typography>
        
        <Grid container spacing={3}>
          {/* Quality Selection */}
          <Grid item xs={12}>
            <FormControl fullWidth>
              <InputLabel>Model Quality</InputLabel>
              <Select
                value={config.quality}
                label="Model Quality"
                onChange={(e) => handleChange('quality', e.target.value)}
              >
                <MenuItem value="high">High Quality (More Accurate)</MenuItem>
                <MenuItem value="medium">Balanced</MenuItem>
                <MenuItem value="low">Fast Processing</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Response Time Limit */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <SpeedIcon color="primary" />
              <Typography gutterBottom>Response Time Limit (ms)</Typography>
            </Box>
            <Slider
              value={config.responseTimeLimit}
              onChange={(_, value) => handleChange('responseTimeLimit', value)}
              min={1000}
              max={10000}
              step={500}
              marks
            />
            <Typography variant="body2" color="text.secondary">
              {config.responseTimeLimit}ms
            </Typography>
          </Grid>

          {/* Context Length */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <MemoryIcon color="primary" />
              <Typography gutterBottom>Context Length</Typography>
            </Box>
            <TextField
              fullWidth
              type="number"
              value={config.contextLength}
              onChange={(e) => handleChange('contextLength', parseInt(e.target.value))}
              inputProps={{ min: 1024, max: 8192, step: 1024 }}
            />
          </Grid>

          {/* Cost Preference */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <CostIcon color="primary" />
              <Typography gutterBottom>Cost Preference</Typography>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              <Chip
                label="Optimize Cost"
                onClick={() => handleChange('costPreference', 'optimize')}
                color={config.costPreference === 'optimize' ? 'primary' : 'default'}
              />
              <Chip
                label="Balanced"
                onClick={() => handleChange('costPreference', 'balanced')}
                color={config.costPreference === 'balanced' ? 'primary' : 'default'}
              />
              <Chip
                label="Max Performance"
                onClick={() => handleChange('costPreference', 'performance')}
                color={config.costPreference === 'performance' ? 'primary' : 'default'}
              />
            </Box>
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
}; 