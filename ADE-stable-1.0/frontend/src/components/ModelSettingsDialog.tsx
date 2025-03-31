import React, { useState, useEffect } from 'react';
import {
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Typography,
  Slider,
  Box,
  Chip,
  IconButton,
  Tooltip,
  Alert
} from '@mui/material';
import {
  Add as AddIcon,
  Remove as RemoveIcon,
  Info as InfoIcon
} from '@mui/icons-material';

interface ModelSettings {
  name: string;
  provider: string;
  quality: string;
  capabilities: string[];
  max_retries: number;
  timeout: number;
  temperature: number;
  top_p: number;
  frequency_penalty: number;
  presence_penalty: number;
  stop_sequences: string[];
  system_prompt: string;
  resource_requirements: {
    gpu_memory: number;
    cpu_cores: number;
    ram: number;
  };
}

interface ModelSettingsDialogProps {
  open: boolean;
  onClose: () => void;
  onSave: (settings: ModelSettings) => void;
  modelName?: string;
}

const ModelSettingsDialog: React.FC<ModelSettingsDialogProps> = ({
  open,
  onClose,
  onSave,
  modelName
}) => {
  const [settings, setSettings] = useState<ModelSettings>({
    name: '',
    provider: '',
    quality: '',
    capabilities: [],
    max_retries: 3,
    timeout: 30,
    temperature: 0.7,
    top_p: 0.9,
    frequency_penalty: 0,
    presence_penalty: 0,
    stop_sequences: [''],
    system_prompt: '',
    resource_requirements: {
      gpu_memory: 0,
      cpu_cores: 1,
      ram: 0
    }
  });

  const [providers, setProviders] = useState<Array<{ name: string; description: string }>>([]);
  const [qualityLevels, setQualityLevels] = useState<Array<{ name: string; description: string }>>([]);
  const [capabilities, setCapabilities] = useState<Array<{ name: string; description: string }>>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (open) {
      fetchOptions();
      if (modelName) {
        fetchModelSettings(modelName);
      }
    }
  }, [open, modelName]);

  const fetchOptions = async () => {
    try {
      const [providersRes, qualityRes, capabilitiesRes] = await Promise.all([
        fetch('/api/models/providers'),
        fetch('/api/models/quality-levels'),
        fetch('/api/models/capabilities')
      ]);

      const [providersData, qualityData, capabilitiesData] = await Promise.all([
        providersRes.json(),
        qualityRes.json(),
        capabilitiesRes.json()
      ]);

      setProviders(providersData.providers);
      setQualityLevels(qualityData.quality_levels);
      setCapabilities(capabilitiesData.capabilities);
    } catch (err) {
      setError('Failed to fetch options');
    }
  };

  const fetchModelSettings = async (name: string) => {
    try {
      const response = await fetch(`/api/models/${name}`);
      const data = await response.json();
      setSettings(data);
    } catch (err) {
      setError('Failed to fetch model settings');
    }
  };

  const handleChange = (field: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleResourceChange = (field: string, value: number) => {
    setSettings(prev => ({
      ...prev,
      resource_requirements: {
        ...prev.resource_requirements,
        [field]: value
      }
    }));
  };

  const handleStopSequenceChange = (index: number, value: string) => {
    setSettings(prev => ({
      ...prev,
      stop_sequences: prev.stop_sequences.map((seq, i) => i === index ? value : seq)
    }));
  };

  const addStopSequence = () => {
    setSettings(prev => ({
      ...prev,
      stop_sequences: [...prev.stop_sequences, '']
    }));
  };

  const removeStopSequence = (index: number) => {
    setSettings(prev => ({
      ...prev,
      stop_sequences: prev.stop_sequences.filter((_, i) => i !== index)
    }));
  };

  const handleSave = () => {
    onSave(settings);
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="md" fullWidth>
      <DialogTitle>
        {modelName ? `Edit Model: ${modelName}` : 'Create New Model'}
      </DialogTitle>
      <DialogContent>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}

        <Grid container spacing={3}>
          {/* Basic Settings */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Basic Settings
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              label="Model Name"
              value={settings.name}
              onChange={(e) => handleChange('name', e.target.value)}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Provider</InputLabel>
              <Select
                value={settings.provider}
                onChange={(e) => handleChange('provider', e.target.value)}
                label="Provider"
              >
                {providers.map((provider) => (
                  <MenuItem key={provider.name} value={provider.name}>
                    {provider.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Quality Level</InputLabel>
              <Select
                value={settings.quality}
                onChange={(e) => handleChange('quality', e.target.value)}
                label="Quality Level"
              >
                {qualityLevels.map((level) => (
                  <MenuItem key={level.name} value={level.name}>
                    {level.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>
          <Grid item xs={12} md={6}>
            <FormControl fullWidth>
              <InputLabel>Capabilities</InputLabel>
              <Select
                multiple
                value={settings.capabilities}
                onChange={(e) => handleChange('capabilities', e.target.value)}
                label="Capabilities"
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {(selected as string[]).map((value) => (
                      <Chip key={value} label={value} />
                    ))}
                  </Box>
                )}
              >
                {capabilities.map((capability) => (
                  <MenuItem key={capability.name} value={capability.name}>
                    {capability.name}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Model Parameters */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Model Parameters
            </Typography>
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Max Retries"
              value={settings.max_retries}
              onChange={(e) => handleChange('max_retries', parseInt(e.target.value))}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Timeout (seconds)"
              value={settings.timeout}
              onChange={(e) => handleChange('timeout', parseFloat(e.target.value))}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography gutterBottom>Temperature</Typography>
            <Slider
              value={settings.temperature}
              onChange={(_, value) => handleChange('temperature', value)}
              min={0}
              max={2}
              step={0.1}
              marks
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <Typography gutterBottom>Top P</Typography>
            <Slider
              value={settings.top_p}
              onChange={(_, value) => handleChange('top_p', value)}
              min={0}
              max={1}
              step={0.1}
              marks
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Frequency Penalty"
              value={settings.frequency_penalty}
              onChange={(e) => handleChange('frequency_penalty', parseFloat(e.target.value))}
            />
          </Grid>
          <Grid item xs={12} md={6}>
            <TextField
              fullWidth
              type="number"
              label="Presence Penalty"
              value={settings.presence_penalty}
              onChange={(e) => handleChange('presence_penalty', parseFloat(e.target.value))}
            />
          </Grid>

          {/* Stop Sequences */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Stop Sequences
            </Typography>
            {settings.stop_sequences.map((sequence, index) => (
              <Box key={index} sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <TextField
                  fullWidth
                  label={`Stop Sequence ${index + 1}`}
                  value={sequence}
                  onChange={(e) => handleStopSequenceChange(index, e.target.value)}
                />
                <IconButton
                  onClick={() => removeStopSequence(index)}
                  disabled={settings.stop_sequences.length === 1}
                >
                  <RemoveIcon />
                </IconButton>
              </Box>
            ))}
            <Button
              startIcon={<AddIcon />}
              onClick={addStopSequence}
              sx={{ mt: 1 }}
            >
              Add Stop Sequence
            </Button>
          </Grid>

          {/* System Prompt */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              System Prompt
            </Typography>
            <TextField
              fullWidth
              multiline
              rows={4}
              label="System Prompt"
              value={settings.system_prompt}
              onChange={(e) => handleChange('system_prompt', e.target.value)}
            />
          </Grid>

          {/* Resource Requirements */}
          <Grid item xs={12}>
            <Typography variant="h6" gutterBottom>
              Resource Requirements
            </Typography>
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              type="number"
              label="GPU Memory (GB)"
              value={settings.resource_requirements.gpu_memory}
              onChange={(e) => handleResourceChange('gpu_memory', parseFloat(e.target.value))}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              type="number"
              label="CPU Cores"
              value={settings.resource_requirements.cpu_cores}
              onChange={(e) => handleResourceChange('cpu_cores', parseInt(e.target.value))}
            />
          </Grid>
          <Grid item xs={12} md={4}>
            <TextField
              fullWidth
              type="number"
              label="RAM (GB)"
              value={settings.resource_requirements.ram}
              onChange={(e) => handleResourceChange('ram', parseFloat(e.target.value))}
            />
          </Grid>
        </Grid>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSave} variant="contained" color="primary">
          Save
        </Button>
      </DialogActions>
    </Dialog>
  );
};

export default ModelSettingsDialog; 