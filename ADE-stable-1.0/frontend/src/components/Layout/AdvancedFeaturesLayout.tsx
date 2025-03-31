import React, { useState } from 'react';
import {
  Box,
  Grid,
  Paper,
  Tabs,
  Tab,
  IconButton,
  Tooltip,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Architecture,
  Timeline,
  AccountTree,
  Fullscreen,
  FullscreenExit,
} from '@mui/icons-material';
import { CodeDependencyGraph } from '../Visualization/CodeDependencyGraph';
import { PerformanceMonitor } from '../Performance/PerformanceMonitor';
import { ArchitectureSuggestions } from '../Architecture/ArchitectureSuggestions';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <Box
      role="tabpanel"
      hidden={value !== index}
      id={`vertical-tabpanel-${index}`}
      aria-labelledby={`vertical-tab-${index}`}
      sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}
      {...other}
    >
      {value === index && (
        <Box sx={{ flex: 1, display: 'flex' }}>
          {children}
        </Box>
      )}
    </Box>
  );
}

export const AdvancedFeaturesLayout: React.FC = () => {
  const [selectedTab, setSelectedTab] = useState(0);
  const [maximizedPanel, setMaximizedPanel] = useState<number | null>(null);
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setSelectedTab(newValue);
  };

  const handleMaximize = (index: number) => {
    setMaximizedPanel(maximizedPanel === index ? null : index);
  };

  const renderPanel = (index: number, component: React.ReactNode) => (
    <Box
      sx={{
        position: 'relative',
        height: '100%',
        width: '100%',
      }}
    >
      <Box
        sx={{
          position: 'absolute',
          top: theme.spacing(1),
          right: theme.spacing(1),
          zIndex: 1,
        }}
      >
        <Tooltip title={maximizedPanel === index ? 'Exit Fullscreen' : 'Fullscreen'}>
          <IconButton
            size="small"
            onClick={() => handleMaximize(index)}
            sx={{ bgcolor: 'background.paper' }}
          >
            {maximizedPanel === index ? <FullscreenExit /> : <Fullscreen />}
          </IconButton>
        </Tooltip>
      </Box>
      {component}
    </Box>
  );

  if (isMobile) {
    return (
      <Box sx={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Paper sx={{ borderRadius: 0 }}>
          <Tabs
            value={selectedTab}
            onChange={handleTabChange}
            variant="fullWidth"
            indicatorColor="primary"
            textColor="primary"
          >
            <Tab icon={<AccountTree />} label="Dependencies" />
            <Tab icon={<Timeline />} label="Performance" />
            <Tab icon={<Architecture />} label="Architecture" />
          </Tabs>
        </Paper>
        <Box sx={{ flex: 1, overflow: 'hidden' }}>
          <TabPanel value={selectedTab} index={0}>
            {renderPanel(0, <CodeDependencyGraph />)}
          </TabPanel>
          <TabPanel value={selectedTab} index={1}>
            {renderPanel(1, <PerformanceMonitor />)}
          </TabPanel>
          <TabPanel value={selectedTab} index={2}>
            {renderPanel(2, <ArchitectureSuggestions />)}
          </TabPanel>
        </Box>
      </Box>
    );
  }

  return (
    <Box sx={{ width: '100%', height: '100%', display: 'flex' }}>
      {maximizedPanel !== null ? (
        <Box sx={{ flex: 1, p: 2 }}>
          {maximizedPanel === 0 && renderPanel(0, <CodeDependencyGraph />)}
          {maximizedPanel === 1 && renderPanel(1, <PerformanceMonitor />)}
          {maximizedPanel === 2 && renderPanel(2, <ArchitectureSuggestions />)}
        </Box>
      ) : (
        <Grid container spacing={2} sx={{ flex: 1, p: 2 }}>
          <Grid item xs={12} md={6} lg={4} sx={{ height: '100%' }}>
            {renderPanel(0, <CodeDependencyGraph />)}
          </Grid>
          <Grid item xs={12} md={6} lg={4} sx={{ height: '100%' }}>
            {renderPanel(1, <PerformanceMonitor />)}
          </Grid>
          <Grid item xs={12} md={12} lg={4} sx={{ height: '100%' }}>
            {renderPanel(2, <ArchitectureSuggestions />)}
          </Grid>
        </Grid>
      )}
    </Box>
  );
}; 