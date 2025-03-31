import React from 'react';
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  Box,
} from '@mui/material';
import {
  Code as CodeIcon,
  BugReport as BugIcon,
  Security as SecurityIcon,
  Speed as PerformanceIcon,
} from '@mui/icons-material';

// Sample data for demonstration
const agents = [
  {
    id: 1,
    name: 'Architect Agent',
    role: 'System Design',
    status: 'active',
    icon: <CodeIcon />,
    lastActivity: '2 minutes ago',
  },
  {
    id: 2,
    name: 'Security Agent',
    role: 'Security Analysis',
    status: 'active',
    icon: <SecurityIcon />,
    lastActivity: '5 minutes ago',
  },
  {
    id: 3,
    name: 'Performance Agent',
    role: 'Performance Optimization',
    status: 'inactive',
    icon: <PerformanceIcon />,
    lastActivity: '1 hour ago',
  },
  {
    id: 4,
    name: 'Debug Agent',
    role: 'Issue Resolution',
    status: 'active',
    icon: <BugIcon />,
    lastActivity: 'Just now',
  },
];

const AgentCollaboration: React.FC = () => {
  return (
    <Paper elevation={3} sx={{ p: 2 }}>
      <Typography variant="h6" gutterBottom>
        Agent Collaboration
      </Typography>
      <List>
        {agents.map((agent) => (
          <ListItem key={agent.id} divider>
            <ListItemAvatar>
              <Avatar sx={{ bgcolor: 'primary.main' }}>{agent.icon}</Avatar>
            </ListItemAvatar>
            <ListItemText
              primary={agent.name}
              secondary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    {agent.role}
                  </Typography>
                  <Chip
                    label={agent.status}
                    size="small"
                    color={agent.status === 'active' ? 'success' : 'default'}
                  />
                  <Typography variant="caption" color="text.secondary">
                    {agent.lastActivity}
                  </Typography>
                </Box>
              }
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

export default AgentCollaboration; 