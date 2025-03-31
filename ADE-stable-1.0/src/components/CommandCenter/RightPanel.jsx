import React, { useState } from 'react';
import { useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import Tabs from '@mui/material/Tabs';
import Tab from '@mui/material/Tab';
import { styled } from '@mui/material/styles';
import ChatIcon from '@mui/icons-material/Chat';
import AssignmentIcon from '@mui/icons-material/Assignment';
import TimelineIcon from '@mui/icons-material/Timeline';
import InfoIcon from '@mui/icons-material/Info';

const PanelContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
  overflow: 'hidden',
}));

const PanelHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: `1px solid ${theme.palette.divider}`,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
}));

const TabPanel = styled(Box)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
}));

const AgentInfo = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(2),
  marginBottom: theme.spacing(2),
}));

const StatusIndicator = styled(Box)(({ theme, status }) => ({
  display: 'inline-block',
  width: 8,
  height: 8,
  borderRadius: '50%',
  backgroundColor: status === 'active' 
    ? theme.palette.success.main 
    : status === 'error'
    ? theme.palette.error.main
    : theme.palette.grey[400],
  marginRight: theme.spacing(1),
}));

const RightPanel = ({ 
  activeAgent,
  agentStatus,
  conversations,
  tasks,
  metrics,
}) => {
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event, newValue) => {
    setTabValue(newValue);
  };

  const getAgentName = (id) => {
    const names = {
      codeAnalysis: 'Code Analysis Agent',
      errorHandling: 'Error Handling Agent',
      resourceManagement: 'Resource Management Agent',
      taskPlanning: 'Task Planning Agent',
    };
    return names[id] || id;
  };

  const getAgentDescription = (id) => {
    const descriptions = {
      codeAnalysis: 'Analyzes code quality, complexity, and dependencies',
      errorHandling: 'Manages error detection, analysis, and recovery',
      resourceManagement: 'Monitors and optimizes system resources',
      taskPlanning: 'Plans and coordinates development tasks',
    };
    return descriptions[id] || '';
  };

  return (
    <PanelContainer>
      <PanelHeader>
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <StatusIndicator status={agentStatus[activeAgent]} />
          <Typography variant="h6">
            {getAgentName(activeAgent)}
          </Typography>
        </Box>
      </PanelHeader>

      <Tabs
        value={tabValue}
        onChange={handleTabChange}
        variant="fullWidth"
        sx={{ borderBottom: 1, borderColor: 'divider' }}
      >
        <Tab icon={<ChatIcon />} label="Conversations" />
        <Tab icon={<AssignmentIcon />} label="Tasks" />
        <Tab icon={<TimelineIcon />} label="Metrics" />
        <Tab icon={<InfoIcon />} label="Info" />
      </Tabs>

      <TabPanel value={tabValue} index={0}>
        {/* Conversations content */}
        <Typography variant="body2" color="text.secondary">
          No conversations available
        </Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        {/* Tasks content */}
        <Typography variant="body2" color="text.secondary">
          No tasks available
        </Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        {/* Metrics content */}
        <Typography variant="body2" color="text.secondary">
          No metrics available
        </Typography>
      </TabPanel>

      <TabPanel value={tabValue} index={3}>
        <AgentInfo>
          <Typography variant="subtitle1" gutterBottom>
            Agent Information
          </Typography>
          <Typography variant="body2" paragraph>
            {getAgentDescription(activeAgent)}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            Status: {agentStatus[activeAgent]}
          </Typography>
        </AgentInfo>
      </TabPanel>
    </PanelContainer>
  );
};

export default RightPanel; 