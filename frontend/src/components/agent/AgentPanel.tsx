import React, { useState } from 'react';
import { Box, IconButton, Drawer, useTheme, useMediaQuery, Tabs, Tab, Chip } from '@mui/material';
import { ChevronLeft, ChevronRight } from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import AgentActivityStream from './AgentActivityStream';
import AgentChat from './AgentChat';
import AgentVisualization from './AgentVisualization';
import AgentDirectory from './AgentDirectory';
import AgentControls from './AgentControls';
import AgentSettings from './AgentSettings';
import { useAgentContext } from './AgentContext';

const DRAWER_WIDTH = 400;

const Main = styled('main', { shouldForwardProp: (prop) => prop !== 'open' })<{
  open?: boolean;
}>(({ theme, open }) => ({
  flexGrow: 1,
  padding: theme.spacing(3),
  transition: theme.transitions.create('margin', {
    easing: theme.transitions.easing.sharp,
    duration: theme.transitions.duration.leavingScreen,
  }),
  marginRight: -DRAWER_WIDTH,
  ...(open && {
    transition: theme.transitions.create('margin', {
      easing: theme.transitions.easing.easeOut,
      duration: theme.transitions.duration.enteringScreen,
    }),
    marginRight: 0,
  }),
}));

const DrawerHeader = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0, 1),
  ...theme.mixins.toolbar,
  justifyContent: 'flex-start',
}));

interface AgentPanelProps {
  projectId: string;
}

const AgentPanel: React.FC<AgentPanelProps> = ({ projectId }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [open, setOpen] = useState(!isMobile);
  const [activeTab, setActiveTab] = useState(0);
  const { agents, tasks } = useAgentContext();

  const handleDrawerToggle = () => {
    setOpen(!open);
  };

  const tabs = [
    { label: 'Activity', component: <AgentActivityStream projectId={projectId} /> },
    { label: 'Chat', component: <AgentChat projectId={projectId} /> },
    { label: 'Visualization', component: <AgentVisualization projectId={projectId} /> },
    { label: 'Directory', component: <AgentDirectory projectId={projectId} /> },
    { label: 'Controls', component: <AgentControls projectId={projectId} /> },
    { label: 'Settings', component: <AgentSettings projectId={projectId} /> },
  ];

  return (
    <>
      <IconButton
        color="inherit"
        aria-label="open drawer"
        edge="end"
        onClick={handleDrawerToggle}
        sx={{
          position: 'fixed',
          right: open ? DRAWER_WIDTH + 16 : 16,
          top: 16,
          zIndex: theme.zIndex.drawer + 1,
          backgroundColor: theme.palette.background.paper,
          '&:hover': {
            backgroundColor: theme.palette.action.hover,
          },
        }}
      >
        {open ? <ChevronRight /> : <ChevronLeft />}
      </IconButton>

      <Drawer
        sx={{
          width: DRAWER_WIDTH,
          flexShrink: 0,
          '& .MuiDrawer-paper': {
            width: DRAWER_WIDTH,
            boxSizing: 'border-box',
            backgroundColor: theme.palette.background.default,
          },
        }}
        variant={isMobile ? 'temporary' : 'persistent'}
        anchor="right"
        open={open}
        onClose={handleDrawerToggle}
      >
        <DrawerHeader>
          <Box sx={{ width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Box
                component="img"
                src="/agent-icon.png"
                alt="Agent"
                sx={{ width: 24, height: 24 }}
              />
              <Box sx={{ typography: 'h6' }}>Agent Panel</Box>
            </Box>
            <Box sx={{ display: 'flex', gap: 1 }}>
              {agents.filter(a => a.status === 'active').length} active
            </Box>
          </Box>
        </DrawerHeader>

        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs
            value={activeTab}
            onChange={(_, newValue) => setActiveTab(newValue)}
            variant="scrollable"
            scrollButtons="auto"
            sx={{
              '& .MuiTab-root': {
                minWidth: 'auto',
                px: 2,
              },
            }}
          >
            {tabs.map((tab, index) => (
              <Tab
                key={index}
                label={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    {tab.label}
                    {tab.label === 'Activity' && tasks.length > 0 && (
                      <Chip
                        size="small"
                        label={tasks.length}
                        color="primary"
                        sx={{ height: 20 }}
                      />
                    )}
                  </Box>
                }
                value={index}
              />
            ))}
          </Tabs>
        </Box>

        <Box sx={{ p: 2, height: 'calc(100vh - 120px)', overflow: 'auto' }}>
          {tabs[activeTab].component}
        </Box>
      </Drawer>

      <Main open={open}>
        {/* Main content */}
      </Main>
    </>
  );
};

export default AgentPanel; 