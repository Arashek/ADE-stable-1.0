import React, { useState, useEffect } from 'react';
import {
  Box,
  Tabs,
  Tab,
  Badge,
  IconButton,
  Tooltip,
  Paper,
  Typography,
  Fade,
} from '@mui/material';
import {
  Palette as DesignIcon,
  Code as CodeIcon,
  Architecture as ArchitectureIcon,
  BugReport as BugReportIcon,
  Description as DescriptionIcon,
  Group as GroupIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { AgentChat } from './AgentChat';

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
      id={`agent-tabpanel-${index}`}
      aria-labelledby={`agent-tab-${index}`}
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

interface AgentChatTabsProps {
  projectId: string;
  onTabChange?: (tabIndex: number) => void;
}

interface TabState {
  id: string;
  label: string;
  icon: React.ReactNode;
  agentType: string;
  hasUpdates: boolean;
  isActive: boolean;
  lastMessage?: string;
  lastMessageTime?: Date;
}

export const AgentChatTabs: React.FC<AgentChatTabsProps> = ({ projectId, onTabChange }) => {
  const [value, setValue] = useState(0);
  const [tabs, setTabs] = useState<TabState[]>([
    {
      id: 'ui-ux',
      label: 'UI/UX Design',
      icon: <DesignIcon />,
      agentType: 'designer',
      hasUpdates: false,
      isActive: true,
    },
    {
      id: 'code',
      label: 'Code Implementation',
      icon: <CodeIcon />,
      agentType: 'code-implementer',
      hasUpdates: false,
      isActive: true,
    },
    {
      id: 'architecture',
      label: 'Architecture',
      icon: <ArchitectureIcon />,
      agentType: 'architect',
      hasUpdates: false,
      isActive: true,
    },
    {
      id: 'testing',
      label: 'Testing',
      icon: <BugReportIcon />,
      agentType: 'tester',
      hasUpdates: false,
      isActive: true,
    },
    {
      id: 'documentation',
      label: 'Documentation',
      icon: <DescriptionIcon />,
      agentType: 'documentation',
      hasUpdates: false,
      isActive: true,
    },
    {
      id: 'collaboration',
      label: 'Collaboration',
      icon: <GroupIcon />,
      agentType: 'collaboration',
      hasUpdates: false,
      isActive: true,
    },
    {
      id: 'settings',
      label: 'Settings',
      icon: <SettingsIcon />,
      agentType: 'settings',
      hasUpdates: false,
      isActive: true,
    },
  ]);

  useEffect(() => {
    // Listen for agent updates
    const handleAgentUpdate = (data: any) => {
      setTabs(prevTabs => 
        prevTabs.map(tab => 
          tab.agentType === data.agentType
            ? { ...tab, hasUpdates: true, lastMessage: data.message, lastMessageTime: new Date() }
            : tab
        )
      );
    };

    // Subscribe to agent updates
    window.addEventListener('agent:update', handleAgentUpdate);

    return () => {
      window.removeEventListener('agent:update', handleAgentUpdate);
    };
  }, []);

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
    onTabChange?.(newValue);

    // Clear update flag when tab is selected
    setTabs(prevTabs =>
      prevTabs.map((tab, index) =>
        index === newValue ? { ...tab, hasUpdates: false } : tab
      )
    );
  };

  return (
    <Paper sx={{ width: '100%', height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs
          value={value}
          onChange={handleChange}
          variant="scrollable"
          scrollButtons="auto"
          aria-label="agent chat tabs"
        >
          {tabs.map((tab, index) => (
            <Tab
              key={tab.id}
              icon={
                <Badge
                  color="error"
                  variant="dot"
                  invisible={!tab.hasUpdates}
                >
                  {tab.icon}
                </Badge>
              }
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2">{tab.label}</Typography>
                  {tab.hasUpdates && (
                    <Fade in timeout={500}>
                      <Typography
                        variant="caption"
                        color="error"
                        sx={{ ml: 1 }}
                      >
                        New
                      </Typography>
                    </Fade>
                  )}
                </Box>
              }
              {...a11yProps(index)}
            />
          ))}
        </Tabs>
      </Box>

      {tabs.map((tab, index) => (
        <TabPanel key={tab.id} value={value} index={index}>
          <AgentChat
            projectId={projectId}
            agentType={tab.agentType}
            onClose={() => {
              // Handle tab close if needed
            }}
          />
        </TabPanel>
      ))}
    </Paper>
  );
};

function a11yProps(index: number) {
  return {
    id: `agent-tab-${index}`,
    'aria-controls': `agent-tabpanel-${index}`,
  };
} 