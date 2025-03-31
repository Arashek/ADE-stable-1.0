import React, { useState } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Typography,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Group as GroupIcon,
  Chat as ChatIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import TeamManagement from './TeamManagement';
import TeamCollaboration from './TeamCollaboration';
import TeamAnalytics from './TeamAnalytics';
import TeamSettings from './TeamSettings';

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
      id={`team-tabpanel-${index}`}
      aria-labelledby={`team-tab-${index}`}
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

const TeamDashboard: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  return (
    <Box sx={{ width: '100%' }}>
      <Paper sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="team dashboard tabs"
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab
            icon={<GroupIcon />}
            label="Team Management"
            iconPosition="start"
          />
          <Tab
            icon={<ChatIcon />}
            label="Collaboration"
            iconPosition="start"
          />
          <Tab
            icon={<AssessmentIcon />}
            label="Analytics"
            iconPosition="start"
          />
          <Tab
            icon={<SettingsIcon />}
            label="Settings"
            iconPosition="start"
          />
        </Tabs>
      </Paper>

      <TabPanel value={activeTab} index={0}>
        <TeamManagement />
      </TabPanel>
      <TabPanel value={activeTab} index={1}>
        <TeamCollaboration />
      </TabPanel>
      <TabPanel value={activeTab} index={2}>
        <TeamAnalytics />
      </TabPanel>
      <TabPanel value={activeTab} index={3}>
        <TeamSettings />
      </TabPanel>
    </Box>
  );
};

export default TeamDashboard; 