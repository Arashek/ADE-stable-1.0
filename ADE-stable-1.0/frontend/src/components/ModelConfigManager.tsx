import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button,
  IconButton,
  Tooltip,
  Alert,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  Switch,
  FormControlLabel,
  Slider,
  Divider
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Info as InfoIcon
} from '@mui/icons-material';

interface ModelConfig {
  name: string;
  provider: string;
  model_id: string;
  quality: string;
  capabilities: string[];
  max_retries: number;
  timeout: number;
  temperature: number;
  top_p: number;
  stop_sequences: string[];
  resource_requirements: {
    gpu_memory: number;
    cpu_cores: number;
    ram: number;
  };
  compliance_config: {
    security: boolean;
    privacy: boolean;
    ethics: boolean;
  };
  security_config: {
    encryption: boolean;
    authentication: boolean;
    audit_logging: boolean;
  };
  privacy_config: {
    data_retention: number;
    data_anonymization: boolean;
    access_control: boolean;
  };
  ethics_config: {
    bias_detection: boolean;
    fairness_metrics: boolean;
    transparency: boolean;
  };
}

interface ModelConfigManagerProps {
  onConfigChange?: (config: ModelConfig) => void;
}

const ModelConfigManager: React.FC<ModelConfigManagerProps> = ({
  onConfigChange
}) => {
  const [configs, setConfigs] = useState<ModelConfig[]>([]);
  const [selectedConfig, setSelectedConfig] = useState<ModelConfig | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [providers, setProviders] = useState<string[]>([]);
  const [capabilities, setCapabilities] = useState<string[]>([]);
  const [qualityLevels, setQualityLevels] = useState<string[]>([]);

  useEffect(() => {
    fetchConfigs();
    fetchOptions();
  }, []);

  const fetchConfigs = async () => {
    try {
      const response = await fetch('/api/models/configs');
      const data = await response.json();
      setConfigs(data.configs);
    } catch (err) {
      setError('Failed to fetch model configurations');
    }
  };

  const fetchOptions = async () => {
    try {
      const [providersRes, capabilitiesRes, qualityRes] = await Promise.all([
        fetch('/api/models/providers'),
        fetch('/api/models/capabilities'),
        fetch('/api/models/quality-levels')
      ]);
      const [providersData, capabilitiesData, qualityData] = await Promise.all([
        providersRes.json(),
        capabilitiesRes.json(),
        qualityRes.json()
      ]);
      setProviders(providersData.providers);
      setCapabilities(capabilitiesData.capabilities);
      setQualityLevels(qualityData.quality_levels);
    } catch (err) {
      setError('Failed to fetch configuration options');
    }
  };

  const handleOpenDialog = (config?: ModelConfig) => {
    setSelectedConfig(config || {
      name: '',
      provider: '',
      model_id: '',
      quality: '',
      capabilities: [],
      max_retries: 3,
      timeout: 30,
      temperature: 0.7,
      top_p: 1,
      stop_sequences: [],
      resource_requirements: {
        gpu_memory: 8,
        cpu_cores: 2,
        ram: 16
      },
      compliance_config: {
        security: true,
        privacy: true,
        ethics: true
      },
      security_config: {
        encryption: true,
        authentication: true,
        audit_logging: true
      },
      privacy_config: {
        data_retention: 30,
        data_anonymization: true,
        access_control: true
      },
      ethics_config: {
        bias_detection: true,
        fairness_metrics: true,
        transparency: true
      }
    });
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedConfig(null);
  };

  const handleSaveConfig = async () => {
    if (!selectedConfig) return;

    try {
      const response = await fetch('/api/models/configs', {
        method: selectedConfig.name ? 'PUT' : 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(selectedConfig),
      });

      if (!response.ok) {
        throw new Error('Failed to save configuration');
      }

      fetchConfigs();
      handleCloseDialog();
      onConfigChange?.(selectedConfig);
    } catch (err) {
      setError('Failed to save model configuration');
    }
  };

  const handleDeleteConfig = async (name: string) => {
    try {
      const response = await fetch(`/api/models/configs/${name}`, {
        method: 'DELETE',
      });

      if (!response.ok) {
        throw new Error('Failed to delete configuration');
      }

      fetchConfigs();
    } catch (err) {
      setError('Failed to delete model configuration');
    }
  };

  const handleConfigChange = (field: string, value: any) => {
    if (!selectedConfig) return;

    setSelectedConfig({
      ...selectedConfig,
      [field]: value
    });
  };

  const handleNestedConfigChange = (parent: string, field: string, value: any) => {
    if (!selectedConfig) return;

    setSelectedConfig({
      ...selectedConfig,
      [parent]: {
        ...selectedConfig[parent as keyof ModelConfig],
        [field]: value
      }
    });
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">Model Configurations</Typography>
            <Box>
              <Tooltip title="Refresh Configurations">
                <IconButton onClick={fetchConfigs}>
                  <RefreshIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Add Configuration">
                <IconButton onClick={() => handleOpenDialog()}>
                  <AddIcon />
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

        {/* Configurations Table */}
        <Grid item xs={12}>
          <Paper>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Name</TableCell>
                    <TableCell>Provider</TableCell>
                    <TableCell>Model ID</TableCell>
                    <TableCell>Quality</TableCell>
                    <TableCell>Capabilities</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {configs.map((config) => (
                    <TableRow key={config.name}>
                      <TableCell>{config.name}</TableCell>
                      <TableCell>{config.provider}</TableCell>
                      <TableCell>{config.model_id}</TableCell>
                      <TableCell>{config.quality}</TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                          {config.capabilities.map((capability) => (
                            <Chip
                              key={capability}
                              label={capability}
                              size="small"
                            />
                          ))}
                        </Box>
                      </TableCell>
                      <TableCell>
                        <Tooltip title="Edit">
                          <IconButton onClick={() => handleOpenDialog(config)}>
                            <EditIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete">
                          <IconButton onClick={() => handleDeleteConfig(config.name)}>
                            <DeleteIcon />
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

      {/* Configuration Dialog */}
      <Dialog
        open={openDialog}
        onClose={handleCloseDialog}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedConfig?.name ? 'Edit Configuration' : 'New Configuration'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="h6">Basic Information</Typography>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Name"
                value={selectedConfig?.name || ''}
                onChange={(e) => handleConfigChange('name', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Provider</InputLabel>
                <Select
                  value={selectedConfig?.provider || ''}
                  onChange={(e) => handleConfigChange('provider', e.target.value)}
                  label="Provider"
                >
                  {providers.map((provider) => (
                    <MenuItem key={provider} value={provider}>
                      {provider}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <TextField
                fullWidth
                label="Model ID"
                value={selectedConfig?.model_id || ''}
                onChange={(e) => handleConfigChange('model_id', e.target.value)}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Quality</InputLabel>
                <Select
                  value={selectedConfig?.quality || ''}
                  onChange={(e) => handleConfigChange('quality', e.target.value)}
                  label="Quality"
                >
                  {qualityLevels.map((level) => (
                    <MenuItem key={level} value={level}>
                      {level}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Capabilities */}
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mt: 2 }}>Capabilities</Typography>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Select Capabilities</InputLabel>
                <Select
                  multiple
                  value={selectedConfig?.capabilities || []}
                  onChange={(e) => handleConfigChange('capabilities', e.target.value)}
                  label="Select Capabilities"
                  renderValue={(selected) => (
                    <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                      {(selected as string[]).map((value) => (
                        <Chip key={value} label={value} />
                      ))}
                    </Box>
                  )}
                >
                  {capabilities.map((capability) => (
                    <MenuItem key={capability} value={capability}>
                      {capability}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            {/* Model Parameters */}
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mt: 2 }}>Model Parameters</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="Max Retries"
                value={selectedConfig?.max_retries || 3}
                onChange={(e) => handleConfigChange('max_retries', parseInt(e.target.value))}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="Timeout (seconds)"
                value={selectedConfig?.timeout || 30}
                onChange={(e) => handleConfigChange('timeout', parseInt(e.target.value))}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="Temperature"
                value={selectedConfig?.temperature || 0.7}
                onChange={(e) => handleConfigChange('temperature', parseFloat(e.target.value))}
              />
            </Grid>

            {/* Resource Requirements */}
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mt: 2 }}>Resource Requirements</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="GPU Memory (GB)"
                value={selectedConfig?.resource_requirements.gpu_memory || 8}
                onChange={(e) => handleNestedConfigChange('resource_requirements', 'gpu_memory', parseInt(e.target.value))}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="CPU Cores"
                value={selectedConfig?.resource_requirements.cpu_cores || 2}
                onChange={(e) => handleNestedConfigChange('resource_requirements', 'cpu_cores', parseInt(e.target.value))}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="RAM (GB)"
                value={selectedConfig?.resource_requirements.ram || 16}
                onChange={(e) => handleNestedConfigChange('resource_requirements', 'ram', parseInt(e.target.value))}
              />
            </Grid>

            {/* Compliance Configuration */}
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mt: 2 }}>Compliance Configuration</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={selectedConfig?.compliance_config.security || false}
                    onChange={(e) => handleNestedConfigChange('compliance_config', 'security', e.target.checked)}
                  />
                }
                label="Security"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={selectedConfig?.compliance_config.privacy || false}
                    onChange={(e) => handleNestedConfigChange('compliance_config', 'privacy', e.target.checked)}
                  />
                }
                label="Privacy"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={selectedConfig?.compliance_config.ethics || false}
                    onChange={(e) => handleNestedConfigChange('compliance_config', 'ethics', e.target.checked)}
                  />
                }
                label="Ethics"
              />
            </Grid>

            {/* Security Configuration */}
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mt: 2 }}>Security Configuration</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={selectedConfig?.security_config.encryption || false}
                    onChange={(e) => handleNestedConfigChange('security_config', 'encryption', e.target.checked)}
                  />
                }
                label="Encryption"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={selectedConfig?.security_config.authentication || false}
                    onChange={(e) => handleNestedConfigChange('security_config', 'authentication', e.target.checked)}
                  />
                }
                label="Authentication"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={selectedConfig?.security_config.audit_logging || false}
                    onChange={(e) => handleNestedConfigChange('security_config', 'audit_logging', e.target.checked)}
                  />
                }
                label="Audit Logging"
              />
            </Grid>

            {/* Privacy Configuration */}
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mt: 2 }}>Privacy Configuration</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <TextField
                fullWidth
                type="number"
                label="Data Retention (days)"
                value={selectedConfig?.privacy_config.data_retention || 30}
                onChange={(e) => handleNestedConfigChange('privacy_config', 'data_retention', parseInt(e.target.value))}
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={selectedConfig?.privacy_config.data_anonymization || false}
                    onChange={(e) => handleNestedConfigChange('privacy_config', 'data_anonymization', e.target.checked)}
                  />
                }
                label="Data Anonymization"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={selectedConfig?.privacy_config.access_control || false}
                    onChange={(e) => handleNestedConfigChange('privacy_config', 'access_control', e.target.checked)}
                  />
                }
                label="Access Control"
              />
            </Grid>

            {/* Ethics Configuration */}
            <Grid item xs={12}>
              <Typography variant="h6" sx={{ mt: 2 }}>Ethics Configuration</Typography>
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={selectedConfig?.ethics_config.bias_detection || false}
                    onChange={(e) => handleNestedConfigChange('ethics_config', 'bias_detection', e.target.checked)}
                  />
                }
                label="Bias Detection"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={selectedConfig?.ethics_config.fairness_metrics || false}
                    onChange={(e) => handleNestedConfigChange('ethics_config', 'fairness_metrics', e.target.checked)}
                  />
                }
                label="Fairness Metrics"
              />
            </Grid>
            <Grid item xs={12} md={4}>
              <FormControlLabel
                control={
                  <Switch
                    checked={selectedConfig?.ethics_config.transparency || false}
                    onChange={(e) => handleNestedConfigChange('ethics_config', 'transparency', e.target.checked)}
                  />
                }
                label="Transparency"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button
            onClick={handleSaveConfig}
            variant="contained"
            startIcon={<SaveIcon />}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ModelConfigManager; 