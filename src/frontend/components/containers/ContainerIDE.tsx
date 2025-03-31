import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Code,
  BugReport,
  Terminal,
  Settings,
  Refresh,
  PlayArrow,
  Stop,
  Pause,
} from '@mui/icons-material';
import { ContainerService } from '../../services/ContainerService';
import { ContainerTerminal } from './ContainerTerminal';
import { ContainerFileBrowser } from './ContainerFileBrowser';

interface ContainerIDEProps {
  containerId: string;
  containerName: string;
}

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
      id={`container-tabpanel-${index}`}
      aria-labelledby={`container-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export const ContainerIDE: React.FC<ContainerIDEProps> = ({
  containerId,
  containerName,
}) => {
  const [tabValue, setTabValue] = useState(0);
  const [containerStatus, setContainerStatus] = useState<'running' | 'stopped' | 'paused'>('stopped');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const containerService = new ContainerService();

  useEffect(() => {
    loadContainerStatus();
  }, [containerId]);

  const loadContainerStatus = async () => {
    try {
      setLoading(true);
      const status = await containerService.getContainerStatus(containerId);
      setContainerStatus(status);
    } catch (error) {
      setError('Failed to load container status');
      console.error('Failed to load container status:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleContainerAction = async (action: 'start' | 'stop' | 'pause' | 'resume') => {
    try {
      setLoading(true);
      setError(null);
      switch (action) {
        case 'start':
          await containerService.startContainer(containerId);
          break;
        case 'stop':
          await containerService.stopContainer(containerId);
          break;
        case 'pause':
          await containerService.pauseContainer(containerId);
          break;
        case 'resume':
          await containerService.resumeContainer(containerId);
          break;
      }
      await loadContainerStatus();
    } catch (error) {
      setError(`Failed to ${action} container`);
      console.error(`Failed to ${action} container:`, error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">
            IDE - {containerName}
          </Typography>
          <Box sx={{ display: 'flex', gap: 1 }}>
            <Tooltip title="Start Container">
              <IconButton
                onClick={() => handleContainerAction('start')}
                disabled={loading || containerStatus === 'running'}
                color="primary"
              >
                <PlayArrow />
              </IconButton>
            </Tooltip>
            <Tooltip title="Stop Container">
              <IconButton
                onClick={() => handleContainerAction('stop')}
                disabled={loading || containerStatus === 'stopped'}
                color="error"
              >
                <Stop />
              </IconButton>
            </Tooltip>
            <Tooltip title="Pause Container">
              <IconButton
                onClick={() => handleContainerAction('pause')}
                disabled={loading || containerStatus === 'paused'}
                color="warning"
              >
                <Pause />
              </IconButton>
            </Tooltip>
            <Tooltip title="Refresh">
              <IconButton
                onClick={loadContainerStatus}
                disabled={loading}
              >
                <Refresh />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        {error && (
          <Alert severity="error" sx={{ mb: 2 }}>
            {error}
          </Alert>
        )}
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', mb: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
      </Box>

      <Box sx={{ flexGrow: 1, overflow: 'hidden' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="container tabs"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          <Tab
            icon={<Code />}
            label="Editor"
            id="container-tab-0"
            aria-controls="container-tabpanel-0"
          />
          <Tab
            icon={<Terminal />}
            label="Terminal"
            id="container-tab-1"
            aria-controls="container-tabpanel-1"
          />
          <Tab
            icon={<BugReport />}
            label="Debug"
            id="container-tab-2"
            aria-controls="container-tabpanel-2"
          />
          <Tab
            icon={<Settings />}
            label="Settings"
            id="container-tab-3"
            aria-controls="container-tabpanel-3"
          />
        </Tabs>

        <TabPanel value={tabValue} index={0}>
          <ContainerFileBrowser
            containerId={containerId}
            containerName={containerName}
          />
        </TabPanel>
        <TabPanel value={tabValue} index={1}>
          <ContainerTerminal
            containerId={containerId}
            containerName={containerName}
          />
        </TabPanel>
        <TabPanel value={tabValue} index={2}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Debug Configuration
            </Typography>
            {/* Debug configuration UI will be implemented here */}
            <Typography color="text.secondary">
              Debug features coming soon...
            </Typography>
          </Paper>
        </TabPanel>
        <TabPanel value={tabValue} index={3}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Container Settings
            </Typography>
            {/* Container settings UI will be implemented here */}
            <Typography color="text.secondary">
              Container settings coming soon...
            </Typography>
          </Paper>
        </TabPanel>
      </Box>
    </Box>
  );
}; 