import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  Alert,
  Divider,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Button
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
  Assessment as AssessmentIcon,
  Extension as ExtensionIcon,
  Compare as CompareIcon
} from '@mui/icons-material';
import ModelPerformanceMetrics from './ModelPerformanceMetrics';
import ModelConfigManager from './ModelConfigManager';
import ModelSelectionStrategy from './ModelSelectionStrategy';
import ModelCapabilities from './ModelCapabilities';
import ModelComparison from './ModelComparison';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`model-tabpanel-${index}`}
      aria-labelledby={`model-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

function a11yProps(index: number) {
  return {
    id: `model-tab-${index}`,
    'aria-controls': `model-tabpanel-${index}`,
  };
}

const ModelDashboard: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [selectedModel, setSelectedModel] = useState<string | null>(null);
  const [models, setModels] = useState<Array<{ name: string; provider: string }>>([]);

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      const response = await fetch('/api/models');
      const data = await response.json();
      setModels(data.models);
    } catch (err) {
      setError('Failed to fetch models');
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleModelChange = (modelName: string) => {
    setSelectedModel(modelName);
  };

  const handleConfigChange = (config: any) => {
    // Handle configuration changes
    console.log('Config changed:', config);
  };

  const handleStrategyChange = (strategy: any) => {
    // Handle strategy changes
    console.log('Strategy changed:', strategy);
  };

  const handleCapabilityChange = (capability: any) => {
    // Handle capability changes
    console.log('Capability changed:', capability);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">Model Management Dashboard</Typography>
            <Box>
              <Tooltip title="Refresh Dashboard">
                <IconButton onClick={fetchModels}>
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
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Select Model</InputLabel>
            <Select
              value={selectedModel || ''}
              onChange={(e) => setSelectedModel(e.target.value as string)}
              label="Select Model"
            >
              {models.map((model) => (
                <MenuItem key={model.name} value={model.name}>
                  {model.name} ({model.provider})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>

        {/* Tabs */}
        <Grid item xs={12}>
          <Paper>
            <Tabs
              value={tabValue}
              onChange={handleTabChange}
              aria-label="model management tabs"
              sx={{ borderBottom: 1, borderColor: 'divider' }}
            >
              <Tab
                icon={<AssessmentIcon />}
                label="Performance"
                {...a11yProps(0)}
              />
              <Tab
                icon={<SettingsIcon />}
                label="Configuration"
                {...a11yProps(1)}
              />
              <Tab
                icon={<ExtensionIcon />}
                label="Capabilities"
                {...a11yProps(2)}
              />
              <Tab
                icon={<SettingsIcon />}
                label="Selection Strategy"
                {...a11yProps(3)}
              />
              <Tab
                icon={<CompareIcon />}
                label="Compare Models"
                {...a11yProps(4)}
              />
            </Tabs>

            {/* Tab Panels */}
            <TabPanel value={tabValue} index={0}>
              <ModelPerformanceMetrics
                modelName={selectedModel || undefined}
                timeRange="24h"
              />
            </TabPanel>
            <TabPanel value={tabValue} index={1}>
              <ModelConfigManager
                onConfigChange={handleConfigChange}
              />
            </TabPanel>
            <TabPanel value={tabValue} index={2}>
              <ModelCapabilities
                onCapabilityChange={handleCapabilityChange}
              />
            </TabPanel>
            <TabPanel value={tabValue} index={3}>
              <ModelSelectionStrategy
                onStrategyChange={handleStrategyChange}
              />
            </TabPanel>
            <TabPanel value={tabValue} index={4}>
              <ModelComparison
                models={models}
                selectedModel={selectedModel}
              />
            </TabPanel>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ModelDashboard; 