import React from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  ListItemSecondaryAction,
  Avatar,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  SmartToy as AgentIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import Card from '../common/Card';
import { dashboardService } from '../../services/dashboardService';
import { useWebSocket } from '../../hooks/useWebSocket';

export interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'online' | 'offline' | 'busy';
  currentTask?: string;
  lastActive: string;
  performance: number;
}

const mockAgents: Agent[] = [
  {
    id: '1',
    name: 'Code Review Agent',
    type: 'reviewer',
    status: 'online',
    currentTask: 'Reviewing PR #123',
    lastActive: '2024-03-20T10:30:00Z',
    performance: 95,
  },
  {
    id: '2',
    name: 'Test Generator',
    type: 'tester',
    status: 'busy',
    currentTask: 'Generating test cases',
    lastActive: '2024-03-20T10:25:00Z',
    performance: 88,
  },
  {
    id: '3',
    name: 'Documentation Bot',
    type: 'documenter',
    status: 'offline',
    lastActive: '2024-03-20T09:00:00Z',
    performance: 92,
  },
];

const getStatusColor = (status: Agent['status']) => {
  switch (status) {
    case 'online':
      return 'success';
    case 'busy':
      return 'warning';
    case 'offline':
      return 'error';
    default:
      return 'default';
  }
};

const AgentStatusCard: React.FC = () => {
  const queryClient = useQueryClient();
  
  // Add WebSocket subscription
  useWebSocket('agent');

  const handleAgentAction = async (agentId: string, action: 'start' | 'stop' | 'restart') => {
    try {
      await dashboardService.updateAgentStatus(agentId, action);
      // Remove manual query invalidation as WebSocket will handle updates
    } catch (error) {
      console.error(`Failed to ${action} agent:`, error);
    }
  };

  const getStatusAction = (agent: Agent) => {
    switch (agent.status) {
      case 'online':
        return (
          <Tooltip title="Stop agent">
            <IconButton
              size="small"
              color="error"
              onClick={() => handleAgentAction(agent.id, 'stop')}
            >
              <StopIcon />
            </IconButton>
          </Tooltip>
        );
      case 'offline':
        return (
          <Tooltip title="Start agent">
            <IconButton
              size="small"
              color="success"
              onClick={() => handleAgentAction(agent.id, 'start')}
            >
              <StartIcon />
            </IconButton>
          </Tooltip>
        );
      case 'busy':
        return (
          <Tooltip title="Restart agent">
            <IconButton
              size="small"
              color="warning"
              onClick={() => handleAgentAction(agent.id, 'restart')}
            >
              <RefreshIcon />
            </IconButton>
          </Tooltip>
        );
      default:
        return null;
    }
  };

  const { data: agents, isLoading, error } = useQuery<Agent[]>({
    queryKey: ['agents'],
    queryFn: dashboardService.getAgents,
    // Remove refetchInterval as we'll use WebSocket for updates
  });

  if (isLoading) {
    return (
      <Card title="Agent Status">
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Agent Status">
        <Alert severity="error">Failed to load agents</Alert>
      </Card>
    );
  }

  const onlineCount = agents?.filter((a) => a.status === 'online').length || 0;
  const totalCount = agents?.length || 0;

  return (
    <Card
      title="Agent Status"
      subtitle={`${onlineCount} of ${totalCount} agents online`}
    >
      <List>
        {agents?.map((agent) => (
          <ListItem
            key={agent.id}
            sx={{
              borderRadius: 1,
              mb: 1,
              '&:hover': {
                backgroundColor: 'action.hover',
              },
            }}
          >
            <ListItemAvatar>
              <Avatar
                sx={{
                  bgcolor: `${getStatusColor(agent.status)}.main`,
                }}
              >
                <AgentIcon />
              </Avatar>
            </ListItemAvatar>
            <ListItemText
              primary={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography variant="subtitle2">{agent.name}</Typography>
                  <Chip
                    size="small"
                    label={agent.status}
                    color={getStatusColor(agent.status)}
                  />
                </Box>
              }
              secondary={
                <>
                  <Typography variant="body2" color="text.secondary">
                    {agent.currentTask || 'No active task'}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    Performance: {agent.performance}%
                  </Typography>
                </>
              }
            />
            <ListItemSecondaryAction>
              {getStatusAction(agent)}
            </ListItemSecondaryAction>
          </ListItem>
        ))}
      </List>
    </Card>
  );
};

export default AgentStatusCard; 