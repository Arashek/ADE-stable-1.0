import React, { useState, useEffect } from 'react';
import {
  Box,
  Drawer,
  IconButton,
  Typography,
  Divider,
  useTheme,
  useMediaQuery,
  Tab,
  Tabs,
  Badge,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  Chat as ChatIcon,
  Timeline as TimelineIcon,
  Group as GroupIcon,
  Assignment as AssignmentIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon
} from '@mui/icons-material';
import AgentActivityStream from './agent/AgentActivityStream';
import AgentChat from './agent/AgentChat';
import AgentDirectory from './agent/AgentDirectory';
import AgentVisualization from './agent/AgentVisualization';
import AgentControls from './agent/AgentControls';
import AgentSettings from './agent/AgentSettings';
import { useAgentContext } from '../contexts/AgentContext';

interface AgentPanelProps {
  currentFile?: string;
  projectId: string;
}

const DRAWER_WIDTH = 400;

const AgentPanel: React.FC<AgentPanelProps> = ({ currentFile, projectId }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [isOpen, setIsOpen] = useState(!isMobile);
  const [activeTab, setActiveTab] = useState(0);
  const { state, actions } = useAgentContext();
  const [unreadMessages, setUnreadMessages] = useState(0);

  useEffect(() => {
    // Subscribe to agent messages
    const unsubscribe = actions.subscribeToMessages((message) => {
      if (!message.read) {
        setUnreadMessages(prev => prev + 1);
      }
    });

    return () => unsubscribe();
  }, [actions]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const renderTabContent = () => {
    switch (activeTab) {
      case 0:
        return <AgentActivityStream projectId={projectId} />;
      case 1:
        return <AgentChat projectId={projectId} currentFile={currentFile} />;
      case 2:
        return <AgentDirectory projectId={projectId} />;
      case 3:
        return <AgentVisualization projectId={projectId} />;
      case 4:
        return <AgentControls projectId={projectId} />;
      case 5:
        return <AgentSettings projectId={projectId} />;
      default:
        return null;
    }
  };

  return (
    <Drawer
      variant={isMobile ? 'temporary' : 'persistent'}
      anchor="right"
      open={isOpen}
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: DRAWER_WIDTH,
          boxSizing: 'border-box',
          display: 'flex',
          flexDirection: 'column'
        }
      }}
    >
      <Box sx={{ p: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
        <Typography variant="h6">Agent Panel</Typography>
        <IconButton onClick={() => setIsOpen(false)}>
          <ChevronRightIcon />
        </IconButton>
      </Box>
      <Divider />
      
      <Tabs
        value={activeTab}
        onChange={handleTabChange}
        variant="scrollable"
        scrollButtons="auto"
        sx={{ borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab
          icon={<TimelineIcon />}
          label="Activity"
          iconPosition="start"
        />
        <Tab
          icon={
            <Badge badgeContent={unreadMessages} color="error">
              <ChatIcon />
            </Badge>
          }
          label="Chat"
          iconPosition="start"
        />
        <Tab
          icon={<GroupIcon />}
          label="Directory"
          iconPosition="start"
        />
        <Tab
          icon={<AssignmentIcon />}
          label="Visualization"
          iconPosition="start"
        />
        <Tab
          icon={<SettingsIcon />}
          label="Controls"
          iconPosition="start"
        />
        <Tab
          icon={<NotificationsIcon />}
          label="Settings"
          iconPosition="start"
        />
      </Tabs>

      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        {renderTabContent()}
      </Box>

      {!isOpen && (
        <Tooltip title="Open Agent Panel">
          <IconButton
            onClick={() => setIsOpen(true)}
            sx={{
              position: 'fixed',
              right: 16,
              bottom: 16,
              bgcolor: 'background.paper',
              boxShadow: 3
            }}
          >
            <ChevronLeftIcon />
          </IconButton>
        </Tooltip>
      )}
    </Drawer>
  );
};

export default AgentPanel; 