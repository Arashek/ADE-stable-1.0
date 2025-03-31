import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  FormControlLabel,
  Switch,
  Button,
  IconButton,
  Tooltip,
  Divider,
  TextField,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  OpenInNew as OpenInNewIcon,
  Devices as DevicesIcon,
  ZoomIn as ZoomInIcon,
  ZoomOut as ZoomOutIcon,
  Fullscreen as FullscreenIcon,
  FullscreenExit as FullscreenExitIcon,
  Settings as SettingsIcon,
  PhoneAndroid,
  Laptop,
  TabletMac,
  Code,
  ViewQuilt,
  Terminal,
  NetworkCheck,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';

const PreviewContainer = styled(Box)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.background.paper,
}));

const PreviewFrame = styled('iframe')({
  border: 'none',
  width: '100%',
  height: '100%',
  backgroundColor: 'white',
});

const ToolbarContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1),
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

const ViewportSizes = {
  mobile: { width: '375px', height: '667px' },
  tablet: { width: '768px', height: '1024px' },
  desktop: { width: '100%', height: '100%' },
};

interface PreviewPanelProps {
  projectUrl: string;
  projectType: string;
  onRefresh?: () => void;
}

const PreviewPanel: React.FC<PreviewPanelProps> = ({
  projectUrl,
  projectType,
  onRefresh
}) => {
  const [viewport, setViewport] = useState<'mobile' | 'tablet' | 'desktop'>('desktop');
  const [activeTab, setActiveTab] = useState(0);
  const [showConsole, setShowConsole] = useState(false);
  const [showNetwork, setShowNetwork] = useState(false);
  const [componentView, setComponentView] = useState(false);
  const iframeRef = useRef<HTMLIFrameElement>(null);
  const [previewError, setPreviewError] = useState<string | null>(null);

  useEffect(() => {
    // Load Boundaries preview configuration
    const loadBoundariesConfig = async () => {
      try {
        const response = await fetch('/.boundaries/preview.json');
        const config = await response.json();
        // Apply preview configuration
        if (config.previewConfig) {
          // Enable hot reload if supported
          if (config.previewConfig.enableHotReload) {
            setupHotReload();
          }
        }
      } catch (error) {
        console.error('Failed to load preview configuration:', error);
      }
    };

    loadBoundariesConfig();
  }, []);

  const setupHotReload = () => {
    // Set up WebSocket connection for hot reload
    const ws = new WebSocket('ws://localhost:8000/preview/ws');
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'reload') {
        refreshPreview();
      }
    };
  };

  const refreshPreview = () => {
    if (iframeRef.current) {
      iframeRef.current.src = iframeRef.current.src;
    }
    onRefresh?.();
  };

  const handleViewportChange = (newViewport: 'mobile' | 'tablet' | 'desktop') => {
    setViewport(newViewport);
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const toggleConsole = () => {
    setShowConsole(!showConsole);
  };

  const toggleNetwork = () => {
    setShowNetwork(!showNetwork);
  };

  const toggleComponentView = () => {
    setComponentView(!componentView);
  };

  return (
    <PreviewContainer>
      <ToolbarContainer>
        <Box display="flex" alignItems="center" gap={1}>
          <Tooltip title="Mobile View">
            <IconButton
              size="small"
              onClick={() => handleViewportChange('mobile')}
              color={viewport === 'mobile' ? 'primary' : 'default'}
            >
              <PhoneAndroid />
            </IconButton>
          </Tooltip>
          <Tooltip title="Tablet View">
            <IconButton
              size="small"
              onClick={() => handleViewportChange('tablet')}
              color={viewport === 'tablet' ? 'primary' : 'default'}
            >
              <TabletMac />
            </IconButton>
          </Tooltip>
          <Tooltip title="Desktop View">
            <IconButton
              size="small"
              onClick={() => handleViewportChange('desktop')}
              color={viewport === 'desktop' ? 'primary' : 'default'}
            >
              <Laptop />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh Preview">
            <IconButton size="small" onClick={refreshPreview}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        </Box>
        <Box display="flex" alignItems="center" gap={1}>
          <Tooltip title="Toggle Console">
            <IconButton
              size="small"
              onClick={toggleConsole}
              color={showConsole ? 'primary' : 'default'}
            >
              <Terminal />
            </IconButton>
          </Tooltip>
          <Tooltip title="Network Inspector">
            <IconButton
              size="small"
              onClick={toggleNetwork}
              color={showNetwork ? 'primary' : 'default'}
            >
              <NetworkCheck />
            </IconButton>
          </Tooltip>
          <Tooltip title="Component View">
            <IconButton
              size="small"
              onClick={toggleComponentView}
              color={componentView ? 'primary' : 'default'}
            >
              <ViewQuilt />
            </IconButton>
          </Tooltip>
          <Tooltip title="View Source">
            <IconButton size="small" onClick={() => setActiveTab(1)}>
              <Code />
            </IconButton>
          </Tooltip>
        </Box>
      </ToolbarContainer>

      <Tabs value={activeTab} onChange={handleTabChange}>
        <Tab label="Preview" />
        <Tab label="Source" />
        {showConsole && <Tab label="Console" />}
        {showNetwork && <Tab label="Network" />}
      </Tabs>

      <Box flex={1} position="relative">
        {activeTab === 0 && (
          <Box
            sx={{
              width: ViewportSizes[viewport].width,
              height: ViewportSizes[viewport].height,
              margin: viewport === 'desktop' ? 0 : 'auto',
              border: viewport !== 'desktop' ? '1px solid #ccc' : 'none',
              borderRadius: viewport !== 'desktop' ? '8px' : 0,
              overflow: 'hidden',
            }}
          >
            {previewError ? (
              <Paper sx={{ p: 2, m: 2 }}>
                <Typography color="error">
                  Preview Error: {previewError}
                </Typography>
              </Paper>
            ) : (
              <PreviewFrame
                ref={iframeRef}
                src={projectUrl}
                onError={() => setPreviewError('Failed to load preview')}
              />
            )}
          </Box>
        )}
        {activeTab === 1 && (
          <Box p={2}>
            <Typography variant="body2" component="pre">
              {/* Source code view */}
            </Typography>
          </Box>
        )}
        {activeTab === 2 && showConsole && (
          <Box p={2}>
            {/* Console output */}
          </Box>
        )}
        {activeTab === 3 && showNetwork && (
          <Box p={2}>
            {/* Network inspector */}
          </Box>
        )}
      </Box>
    </PreviewContainer>
  );
};

export default PreviewPanel; 