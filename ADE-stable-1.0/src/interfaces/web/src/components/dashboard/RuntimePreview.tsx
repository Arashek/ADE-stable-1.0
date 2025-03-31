import React, { useState } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  Typography,
} from '@mui/material';
import {
  Refresh as RefreshIcon,
  OpenInNew as OpenInNewIcon,
  Fullscreen as FullscreenIcon,
  PhoneAndroid as MobileIcon,
  DesktopWindows as DesktopIcon,
  Web as BrowserIcon,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  value: number;
  index: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <div
    role="tabpanel"
    hidden={value !== index}
    id={`preview-tabpanel-${index}`}
    aria-labelledby={`preview-tab-${index}`}
  >
    {value === index && <Box sx={{ p: 2 }}>{children}</Box>}
  </div>
);

const RuntimePreview: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Tabs value={currentTab} onChange={handleTabChange}>
            <Tab icon={<BrowserIcon />} label="Browser" />
            <Tab icon={<MobileIcon />} label="Mobile" />
            <Tab icon={<DesktopIcon />} label="Desktop" />
          </Tabs>
          <Box>
            <Tooltip title="Refresh">
              <IconButton>
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Open in New Window">
              <IconButton>
                <OpenInNewIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Fullscreen">
              <IconButton>
                <FullscreenIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </Box>

      <TabPanel value={currentTab} index={0}>
        <Paper
          sx={{
            height: 'calc(100vh - 300px)',
            backgroundColor: 'background.paper',
            overflow: 'hidden',
          }}
        >
          <Box
            component="iframe"
            src="about:blank"
            title="Runtime Preview"
            sx={{
              width: '100%',
              height: '100%',
              border: 'none',
            }}
          />
        </Paper>
      </TabPanel>

      <TabPanel value={currentTab} index={1}>
        <Paper
          sx={{
            height: 'calc(100vh - 300px)',
            width: '375px',
            mx: 'auto',
            backgroundColor: 'background.paper',
            overflow: 'hidden',
            borderRadius: '20px',
            position: 'relative',
          }}
        >
          <Box
            component="iframe"
            src="about:blank"
            title="Mobile Preview"
            sx={{
              width: '100%',
              height: '100%',
              border: 'none',
            }}
          />
        </Paper>
      </TabPanel>

      <TabPanel value={currentTab} index={2}>
        <Paper
          sx={{
            height: 'calc(100vh - 300px)',
            backgroundColor: 'background.paper',
            overflow: 'hidden',
            borderRadius: '8px',
          }}
        >
          <Box
            component="iframe"
            src="about:blank"
            title="Desktop Preview"
            sx={{
              width: '100%',
              height: '100%',
              border: 'none',
            }}
          />
        </Paper>
      </TabPanel>
    </Box>
  );
};

export default RuntimePreview; 