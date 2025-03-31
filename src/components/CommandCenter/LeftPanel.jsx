import React, { useState } from 'react';
import { useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemIcon from '@mui/material/ListItemIcon';
import ListItemText from '@mui/material/ListItemText';
import ListItemButton from '@mui/material/ListItemButton';
import Divider from '@mui/material/Divider';
import Typography from '@mui/material/Typography';
import { styled } from '@mui/material/styles';
import CodeIcon from '@mui/icons-material/Code';
import BugReportIcon from '@mui/icons-material/BugReport';
import MemoryIcon from '@mui/icons-material/Memory';
import AssignmentIcon from '@mui/icons-material/Assignment';
import SettingsIcon from '@mui/icons-material/Settings';

const PanelContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
  overflow: 'hidden',
}));

const PanelHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

const AgentList = styled(List)(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(1),
}));

const AgentStatus = styled(Box)(({ theme, status }) => ({
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

const LeftPanel = ({ 
  activeAgent,
  onAgentSelect,
  agentStatus,
  notifications,
}) => {
  const theme = useTheme();
  const [selectedIndex, setSelectedIndex] = useState(0);

  const handleListItemClick = (index, agent) => {
    setSelectedIndex(index);
    onAgentSelect(agent);
  };

  const agents = [
    { id: 'codeAnalysis', name: 'Code Analysis', icon: <CodeIcon /> },
    { id: 'errorHandling', name: 'Error Handling', icon: <BugReportIcon /> },
    { id: 'resourceManagement', name: 'Resource Management', icon: <MemoryIcon /> },
    { id: 'taskPlanning', name: 'Task Planning', icon: <AssignmentIcon /> },
  ];

  return (
    <PanelContainer>
      <PanelHeader>
        <Typography variant="h6">Agents</Typography>
      </PanelHeader>
      <Divider />
      <AgentList>
        {agents.map((agent, index) => (
          <ListItem key={agent.id} disablePadding>
            <ListItemButton
              selected={selectedIndex === index}
              onClick={() => handleListItemClick(index, agent.id)}
            >
              <ListItemIcon>
                {agent.icon}
                <AgentStatus status={agentStatus[agent.id]} />
              </ListItemIcon>
              <ListItemText 
                primary={agent.name}
                secondary={
                  notifications.filter(n => n.agent === agent.id).length > 0
                    ? `${notifications.filter(n => n.agent === agent.id).length} notifications`
                    : null
                }
              />
            </ListItemButton>
          </ListItem>
        ))}
      </AgentList>
      <Divider />
      <ListItem disablePadding>
        <ListItemButton>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Settings" />
        </ListItemButton>
      </ListItem>
    </PanelContainer>
  );
};

export default LeftPanel; 