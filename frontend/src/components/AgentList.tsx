import React from 'react';
import {
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Chip,
  Box,
  Typography,
  CircularProgress,
} from '@mui/material';
import {
  Architecture,
  Code,
  BugReport,
  RateReview,
  CloudUpload,
} from '@mui/icons-material';

interface Agent {
  id: string;
  type: 'architecture' | 'code_generator' | 'test_writer' | 'reviewer' | 'deployer';
  status: 'idle' | 'working' | 'completed' | 'error';
  currentTask?: string;
  model: string;
}

interface AgentListProps {
  agents: Agent[];
}

export const AgentList: React.FC<AgentListProps> = ({ agents }) => {
  const getAgentIcon = (type: Agent['type']) => {
    switch (type) {
      case 'architecture':
        return <Architecture />;
      case 'code_generator':
        return <Code />;
      case 'test_writer':
        return <BugReport />;
      case 'reviewer':
        return <RateReview />;
      case 'deployer':
        return <CloudUpload />;
    }
  };

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'idle':
        return 'default';
      case 'working':
        return 'primary';
      case 'completed':
        return 'success';
      case 'error':
        return 'error';
    }
  };

  const getAgentName = (type: Agent['type']) => {
    switch (type) {
      case 'architecture':
        return 'Architecture Designer';
      case 'code_generator':
        return 'Code Generator';
      case 'test_writer':
        return 'Test Writer';
      case 'reviewer':
        return 'Code Reviewer';
      case 'deployer':
        return 'Deployer';
    }
  };

  return (
    <List>
      {agents.map((agent) => (
        <ListItem
          key={agent.id}
          sx={{
            mb: 1,
            bgcolor: 'background.paper',
            borderRadius: 1,
            boxShadow: 1,
          }}
        >
          <ListItemIcon>{getAgentIcon(agent.type)}</ListItemIcon>
          <ListItemText
            primary={
              <Box display="flex" alignItems="center" gap={1}>
                <Typography variant="subtitle1">
                  {getAgentName(agent.type)}
                </Typography>
                <Chip
                  size="small"
                  label={agent.status}
                  color={getStatusColor(agent.status)}
                />
              </Box>
            }
            secondary={
              <Box>
                <Typography variant="caption" display="block">
                  Model: {agent.model}
                </Typography>
                {agent.currentTask && (
                  <Box display="flex" alignItems="center" gap={1}>
                    <CircularProgress size={12} />
                    <Typography variant="caption">
                      {agent.currentTask}
                    </Typography>
                  </Box>
                )}
              </Box>
            }
          />
        </ListItem>
      ))}
    </List>
  );
};
