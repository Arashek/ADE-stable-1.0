import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemSecondaryAction,
  Switch,
  IconButton,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  Code as CodeIcon,
  BugReport as BugIcon,
  Description as DocIcon,
  Psychology as PsychologyIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

interface AgentControlPanelProps {
  onAgentConfigChange: (agentId: string, config: any) => void;
}

interface Agent {
  id: string;
  name: string;
  type: 'code_generator' | 'error_handler' | 'documentation' | 'task_planner';
  status: 'active' | 'inactive';
  performance: {
    successRate: number;
    avgResponseTime: number;
  };
}

export const AgentControlPanel: React.FC<AgentControlPanelProps> = ({ onAgentConfigChange }) => {
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: 'code-gen',
      name: 'Code Generator',
      type: 'code_generator',
      status: 'active',
      performance: {
        successRate: 95,
        avgResponseTime: 2.5,
      },
    },
    {
      id: 'error-handler',
      name: 'Error Handler',
      type: 'error_handler',
      status: 'active',
      performance: {
        successRate: 90,
        avgResponseTime: 1.8,
      },
    },
    {
      id: 'doc-gen',
      name: 'Documentation Generator',
      type: 'documentation',
      status: 'inactive',
      performance: {
        successRate: 85,
        avgResponseTime: 3.2,
      },
    },
    {
      id: 'task-planner',
      name: 'Task Planner',
      type: 'task_planner',
      status: 'active',
      performance: {
        successRate: 92,
        avgResponseTime: 2.1,
      },
    },
  ]);

  const handleStatusToggle = (agentId: string) => {
    setAgents(prev =>
      prev.map(agent =>
        agent.id === agentId
          ? { ...agent, status: agent.status === 'active' ? 'inactive' : 'active' }
          : agent
      )
    );
  };

  const getAgentIcon = (type: Agent['type']) => {
    switch (type) {
      case 'code_generator':
        return <CodeIcon />;
      case 'error_handler':
        return <BugIcon />;
      case 'documentation':
        return <DocIcon />;
      case 'task_planner':
        return <PsychologyIcon />;
      default:
        return <SettingsIcon />;
    }
  };

  return (
    <Card>
      <CardContent>
        <Typography variant="h6" gutterBottom>
          Agent Control Panel
        </Typography>
        <List>
          {agents.map((agent) => (
            <ListItem key={agent.id}>
              <ListItemIcon>{getAgentIcon(agent.type)}</ListItemIcon>
              <ListItemText
                primary={agent.name}
                secondary={
                  <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
                    <Chip
                      label={`${agent.performance.successRate}% Success`}
                      size="small"
                      color={agent.performance.successRate >= 90 ? 'success' : 'warning'}
                    />
                    <Chip
                      label={`${agent.performance.avgResponseTime}s Avg Response`}
                      size="small"
                      variant="outlined"
                    />
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <Tooltip title={agent.status === 'active' ? 'Deactivate Agent' : 'Activate Agent'}>
                  <Switch
                    edge="end"
                    checked={agent.status === 'active'}
                    onChange={() => handleStatusToggle(agent.id)}
                  />
                </Tooltip>
                <Tooltip title="Configure Agent">
                  <IconButton edge="end" onClick={() => onAgentConfigChange(agent.id, {})}>
                    <SettingsIcon />
                  </IconButton>
                </Tooltip>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );
}; 