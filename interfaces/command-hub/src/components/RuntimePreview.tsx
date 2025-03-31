import React, { useState } from 'react';
import {
  Paper,
  Box,
  Typography,
  IconButton,
  Tooltip,
  Tabs,
  Tab,
  Button,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Fullscreen as FullscreenIcon,
  Settings as SettingsIcon,
  BugReport as DebugIcon,
} from '@mui/icons-material';

interface RuntimeEnvironment {
  id: string;
  name: string;
  type: 'development' | 'staging' | 'production';
  url: string;
  status: 'running' | 'stopped' | 'error';
}

const RuntimePreview: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [selectedEnv, setSelectedEnv] = useState<string>('dev');
  const [isFullscreen, setIsFullscreen] = useState(false);

  // Mock data - replace with actual data from API
  const environments: RuntimeEnvironment[] = [
    {
      id: 'dev',
      name: 'Development',
      type: 'development',
      url: 'http://localhost:3000',
      status: 'running',
    },
    {
      id: 'staging',
      name: 'Staging',
      type: 'staging',
      url: 'https://staging.example.com',
      status: 'stopped',
    },
  ];

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleEnvironmentChange = (event: React.ChangeEvent<{ value: unknown }>) => {
    setSelectedEnv(event.target.value as string);
  };

  const toggleFullscreen = () => {
    setIsFullscreen(!isFullscreen);
    // TODO: Implement actual fullscreen toggle
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        mb: 2,
        backgroundColor: 'background.paper',
        height: '400px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Runtime Preview</Typography>
        <Box sx={{ ml: 'auto', display: 'flex', gap: 1 }}>
          <FormControl size="small" sx={{ minWidth: 120 }}>
            <InputLabel>Environment</InputLabel>
            <Select
              value={selectedEnv}
              label="Environment"
              onChange={handleEnvironmentChange}
            >
              {environments.map((env) => (
                <MenuItem key={env.id} value={env.id}>
                  {env.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Tooltip title="Start">
            <IconButton color="success">
              <PlayIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Stop">
            <IconButton color="error">
              <StopIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh">
            <IconButton>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Debug">
            <IconButton>
              <DebugIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Settings">
            <IconButton>
              <SettingsIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Fullscreen">
            <IconButton onClick={toggleFullscreen}>
              <FullscreenIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Tabs
        value={activeTab}
        onChange={handleTabChange}
        sx={{ borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab label="Preview" />
        <Tab label="Console" />
        <Tab label="Network" />
      </Tabs>

      <Box sx={{ flex: 1, mt: 2, position: 'relative' }}>
        {activeTab === 0 && (
          <Box
            sx={{
              width: '100%',
              height: '100%',
              backgroundColor: 'background.default',
              borderRadius: 1,
              overflow: 'hidden',
            }}
          >
            {/* TODO: Implement actual iframe or webview */}
            <Box
              sx={{
                width: '100%',
                height: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'text.secondary',
              }}
            >
              Preview Content
            </Box>
          </Box>
        )}
        {activeTab === 1 && (
          <Box
            sx={{
              width: '100%',
              height: '100%',
              backgroundColor: 'background.default',
              borderRadius: 1,
              p: 2,
              fontFamily: 'monospace',
              fontSize: '0.875rem',
              overflow: 'auto',
            }}
          >
            {/* TODO: Implement console output */}
            <Typography variant="body2" color="text.secondary">
              Console output will appear here...
            </Typography>
          </Box>
        )}
        {activeTab === 2 && (
          <Box
            sx={{
              width: '100%',
              height: '100%',
              backgroundColor: 'background.default',
              borderRadius: 1,
              p: 2,
              overflow: 'auto',
            }}
          >
            {/* TODO: Implement network requests list */}
            <Typography variant="body2" color="text.secondary">
              Network requests will appear here...
            </Typography>
          </Box>
        )}
      </Box>
    </Paper>
  );
};

export default RuntimePreview; 