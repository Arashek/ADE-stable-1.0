import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Chip,
  Divider,
  Badge,
  Tooltip,
  IconButton,
  CircularProgress,
  LinearProgress,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Psychology as AIIcon,
  Build as DevIcon,
  Palette as DesignIcon,
  Insights as AdvisorIcon,
  Memory as ArchitectIcon,
  Storage as DataIcon,
  Terminal as TerminalIcon,
  Info as InfoIcon,
  Refresh as RefreshIcon,
  MoreVert as MoreIcon,
} from '@mui/icons-material';
import errorLogger from '../../services/errorLogging';

// Styled components
const AgentStatusRoot = styled(Paper)(({ theme }) => ({
  height: '100%',
  overflow: 'hidden',
  display: 'flex',
  flexDirection: 'column',
  boxShadow: theme.shadows[2],
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.paper,
}));

const AgentStatusHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1.5, 2),
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

const AgentListContainer = styled(Box)(({ theme }) => ({
  overflowY: 'auto',
  flex: 1,
  paddingBottom: theme.spacing(1),
}));

const SystemStatsContainer = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1.5, 2),
  borderTop: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.default,
}));

const ResourceLabel = styled(Typography)(({ theme }) => ({
  fontSize: '0.75rem',
  color: theme.palette.text.secondary,
  marginRight: theme.spacing(1),
  minWidth: 75,
}));

// Types
interface Agent {
  id: string;
  name: string;
  type: 'assistant' | 'developer' | 'designer' | 'advisor' | 'architect' | 'data' | 'terminal';
  status: 'active' | 'idle' | 'processing' | 'error' | 'ready' | 'paused';
  lastActivity: string;
  currentTask?: string;
  cpuUsage?: number;
  memoryUsage?: number;
  errorCount?: number;
  lastError?: {
    timestamp: string;
    message: string;
    code: string;
    details: string;
  };
}

interface SystemResources {
  cpuUsage: number;
  memoryUsage: number;
  networkLatency: number;
}

interface AgentStatusPanelProps {
  onAgentSelect?: (agentId: string) => void;
}

const AgentStatusPanel: React.FC<AgentStatusPanelProps> = ({ onAgentSelect }) => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [systemResources, setSystemResources] = useState<SystemResources>({
    cpuUsage: 0,
    memoryUsage: 0,
    networkLatency: 0,
  });
  const [isLoading, setIsLoading] = useState(false);
  const [isResetting, setIsResetting] = useState({});
  const [statusMessage, setStatusMessage] = useState({
    type: '',
    text: '',
  });

  // Simulate fetching agent statuses
  useEffect(() => {
    fetchAgentStatuses();
    const interval = setInterval(fetchAgentStatuses, 10000); // Refresh every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchAgentStatuses = () => {
    setIsLoading(true);
    // Simulate API call
    setTimeout(() => {
      const mockAgents: Agent[] = [
        {
          id: 'assistant-1',
          name: 'Assistant',
          type: 'assistant',
          status: 'active',
          lastActivity: new Date().toISOString(),
          currentTask: 'Coordinating development workflow',
          cpuUsage: 25,
          memoryUsage: 30,
        },
        {
          id: 'developer-1',
          name: 'Developer',
          type: 'developer',
          status: 'processing',
          lastActivity: new Date(Date.now() - 120000).toISOString(), // 2 minutes ago
          currentTask: 'Implementing LiveChat component',
          cpuUsage: 78,
          memoryUsage: 65,
        },
        {
          id: 'designer-1',
          name: 'Designer',
          type: 'designer',
          status: 'idle',
          lastActivity: new Date(Date.now() - 600000).toISOString(), // 10 minutes ago
          cpuUsage: 12,
          memoryUsage: 18,
        },
        {
          id: 'advisor-1',
          name: 'Advisor',
          type: 'advisor',
          status: 'idle',
          lastActivity: new Date(Date.now() - 900000).toISOString(), // 15 minutes ago
          cpuUsage: 8,
          memoryUsage: 15,
        },
        {
          id: 'architect-1',
          name: 'Architect',
          type: 'architect',
          status: 'error',
          lastActivity: new Date(Date.now() - 1800000).toISOString(), // 30 minutes ago
          currentTask: 'Optimizing database schema',
          cpuUsage: 0,
          memoryUsage: 5,
        },
      ];

      const mockSystemResources: SystemResources = {
        cpuUsage: Math.floor(Math.random() * 30) + 40, // 40-70%
        memoryUsage: Math.floor(Math.random() * 20) + 50, // 50-70%
        networkLatency: Math.floor(Math.random() * 100) + 50, // 50-150ms
      };

      setAgents(mockAgents);
      setSystemResources(mockSystemResources);
      setIsLoading(false);
    }, 800);
  };

  const handleRefresh = () => {
    fetchAgentStatuses();
  };

  const getAgentIcon = (type: Agent['type']) => {
    switch (type) {
      case 'assistant':
        return <AIIcon />;
      case 'developer':
        return <DevIcon />;
      case 'designer':
        return <DesignIcon />;
      case 'advisor':
        return <AdvisorIcon />;
      case 'architect':
        return <ArchitectIcon />;
      case 'data':
        return <DataIcon />;
      case 'terminal':
        return <TerminalIcon />;
      default:
        return <AIIcon />;
    }
  };

  const getAgentColor = (type: Agent['type']) => {
    switch (type) {
      case 'assistant':
        return '#9c27b0'; // purple
      case 'developer':
        return '#2196f3'; // blue
      case 'designer':
        return '#ff9800'; // orange
      case 'advisor': 
        return '#4caf50'; // green
      case 'architect':
        return '#f44336'; // red
      case 'data':
        return '#00bcd4'; // cyan
      case 'terminal':
        return '#607d8b'; // blue-gray
      default:
        return '#757575'; // gray
    }
  };

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'active':
        return '#4caf50'; // green
      case 'idle':
        return '#ffc107'; // amber
      case 'processing':
        return '#2196f3'; // blue
      case 'error':
        return '#f44336'; // red
      case 'ready':
        return '#4caf50'; // green
      case 'paused':
        return '#ff9800'; // orange
      default:
        return '#757575'; // gray
    }
  };

  const handleResetAgent = (agent: Agent) => {
    setIsResetting(prev => ({ ...prev, [agent.id]: true }));
    
    errorLogger.logAgentError(
      `Manual reset initiated for ${agent.name} agent`,
      'INFO',
      'AgentStatusPanel',
      { agentId: agent.id, agentType: agent.type }
    );
    
    setTimeout(() => {
      setAgents(prev => 
        prev.map(a => {
          if (a.id === agent.id) {
            return {
              ...a, 
              status: 'ready' as const,
              errorCount: 0,
              memoryUsage: Math.floor(Math.random() * 20) + 10,
              cpuUsage: Math.floor(Math.random() * 15) + 5,
              lastActivity: new Date().toISOString()
            };
          }
          return a;
        })
      );
      setIsResetting(prev => ({ ...prev, [agent.id]: false }));
      
      setStatusMessage({
        type: 'success',
        text: `${agent.name} agent has been reset successfully.`
      });
    }, 2000);
  };

  const handleToggleAgentStatus = (agent: Agent) => {
    setAgents(prev => 
      prev.map(a => {
        if (a.id === agent.id) {
          return {
            ...a, 
            status: a.status === 'ready' ? 'paused' as const : 'ready' as const,
            lastActivity: new Date().toISOString()
          };
        }
        return a;
      })
    );
    
    const newStatus = agent.status === 'ready' ? 'paused' : 'ready';
    
    errorLogger.logAgentError(
      `Agent ${agent.name} ${newStatus === 'paused' ? 'paused' : 'resumed'}`,
      'INFO',
      'AgentStatusPanel',
      { agentId: agent.id, agentType: agent.type, newStatus }
    );
    
    setStatusMessage({
      type: 'info',
      text: `${agent.name} agent has been ${newStatus === 'paused' ? 'paused' : 'resumed'}.`
    });
  };

  const simulateAgentError = (agent: Agent) => {
    setAgents(prev => 
      prev.map(a => {
        if (a.id === agent.id) {
          return {
            ...a, 
            status: 'error' as const,
            errorCount: (a.errorCount || 0) + 1,
            lastActivity: new Date().toISOString(),
            lastError: {
              timestamp: new Date().toISOString(),
              message: `Simulated error #${(a.errorCount || 0) + 1} in ${a.name} agent`,
              code: `ERR_AGENT_${agent.type.toUpperCase()}_${Math.floor(Math.random() * 1000)}`,
              details: `This is a simulated error for testing the error handling system. Random error ID: ${Math.random().toString(36).substring(2, 10)}`
            }
          };
        }
        return a;
      })
    );
    
    errorLogger.logAgentError(
      `Error in ${agent.name} agent: Simulated error test`,
      'ERROR',
      'AgentStatusPanel',
      { 
        agentId: agent.id, 
        agentType: agent.type,
        errorCode: `ERR_AGENT_${agent.type.toUpperCase()}_${Math.floor(Math.random() * 1000)}`,
      }
    );
    
    setStatusMessage({
      type: 'error',
      text: `Error detected in ${agent.name} agent. Check error logs for details.`
    });
  };

  const formatTimeSince = (date: string) => {
    const now = new Date();
    const diffMs = now.getTime() - new Date(date).getTime();
    const diffSec = Math.round(diffMs / 1000);
    
    if (diffSec < 60) return `${diffSec}s ago`;
    
    const diffMin = Math.round(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    
    const diffHr = Math.round(diffMin / 60);
    if (diffHr < 24) return `${diffHr}h ago`;
    
    const diffDays = Math.round(diffHr / 24);
    return `${diffDays}d ago`;
  };

  return (
    <AgentStatusRoot>
      <AgentStatusHeader>
        <Typography variant="h6" component="h2">
          Agent Status
        </Typography>
        <Box>
          <Tooltip title="Refresh agent statuses">
            <IconButton onClick={handleRefresh} disabled={isLoading}>
              {isLoading ? <CircularProgress size={24} /> : <RefreshIcon />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Simulate random agent error (for testing)">
            <IconButton onClick={() => simulateAgentError(agents[0])} disabled={isLoading}>
              <InfoIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </AgentStatusHeader>

      <AgentListContainer>
        <List disablePadding>
          {agents.map((agent) => (
            <React.Fragment key={agent.id}>
              <ListItem 
                button
                onClick={() => onAgentSelect && onAgentSelect(agent.id)}
                sx={{
                  '&:hover': {
                    backgroundColor: 'rgba(0, 0, 0, 0.04)',
                  },
                  cursor: 'pointer'
                }}
              >
                <ListItemAvatar>
                  <Badge
                    overlap="circular"
                    anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                    badgeContent={
                      <Box
                        sx={{
                          width: 10,
                          height: 10,
                          borderRadius: '50%',
                          backgroundColor: getStatusColor(agent.status),
                          border: '1px solid white',
                        }}
                      />
                    }
                  >
                    <Avatar
                      sx={{
                        bgcolor: getAgentColor(agent.type),
                      }}
                    >
                      {getAgentIcon(agent.type)}
                    </Avatar>
                  </Badge>
                </ListItemAvatar>
                <ListItemText
                  primary={agent.name}
                  secondary={
                    <React.Fragment>
                      <Typography
                        component="span"
                        variant="body2"
                        color="text.primary"
                        sx={{ display: 'block' }}
                      >
                        {agent.status === 'error' ? (
                          <Box sx={{ display: 'flex', alignItems: 'center' }}>
                            <Typography color="error" variant="body2" sx={{ mr: 1 }}>
                              {agent.lastError.message}
                            </Typography>
                            <Tooltip title="Reset agent">
                              <IconButton 
                                size="small" 
                                onClick={(e) => {
                                  e.stopPropagation();
                                  handleResetAgent(agent);
                                }}
                              >
                                <RefreshIcon fontSize="small" />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        ) : (
                          agent.currentTask || 'No active task'
                        )}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                        <ResourceLabel>CPU: {agent.cpuUsage || 0}%</ResourceLabel>
                        <LinearProgress
                          variant="determinate"
                          value={agent.cpuUsage || 0}
                          sx={{ 
                            flexGrow: 1, 
                            height: 6, 
                            borderRadius: 1,
                            backgroundColor: 'rgba(0,0,0,0.09)',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: agent.cpuUsage && agent.cpuUsage > 80 ? '#f44336' : undefined
                            }
                          }}
                        />
                      </Box>
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
                        <ResourceLabel>Memory: {agent.memoryUsage || 0}%</ResourceLabel>
                        <LinearProgress
                          variant="determinate"
                          value={agent.memoryUsage || 0}
                          sx={{ 
                            flexGrow: 1, 
                            height: 6, 
                            borderRadius: 1,
                            backgroundColor: 'rgba(0,0,0,0.09)',
                            '& .MuiLinearProgress-bar': {
                              backgroundColor: agent.memoryUsage && agent.memoryUsage > 80 ? '#f44336' : undefined
                            }
                          }}
                        />
                      </Box>
                      <Typography 
                        variant="caption" 
                        color="text.secondary" 
                        sx={{ display: 'block', mt: 0.5 }}
                      >
                        Last activity: {formatTimeSince(agent.lastActivity)}
                      </Typography>
                    </React.Fragment>
                  }
                />
                <Chip
                  label={agent.status.charAt(0).toUpperCase() + agent.status.slice(1)}
                  size="small"
                  sx={{
                    backgroundColor: `${getStatusColor(agent.status)}20`,
                    color: getStatusColor(agent.status),
                    fontWeight: 500,
                  }}
                />
                {agent.status === 'ready' || agent.status === 'paused' ? (
                  <Tooltip title={agent.status === 'ready' ? 'Pause agent' : 'Resume agent'}>
                    <IconButton 
                      size="small" 
                      onClick={(e) => {
                        e.stopPropagation();
                        handleToggleAgentStatus(agent);
                      }}
                    >
                      {agent.status === 'ready' ? <MoreIcon fontSize="small" /> : <RefreshIcon fontSize="small" />}
                    </IconButton>
                  </Tooltip>
                ) : null}
              </ListItem>
              <Divider component="li" />
            </React.Fragment>
          ))}
        </List>
      </AgentListContainer>

      <SystemStatsContainer>
        <Typography variant="subtitle2" gutterBottom>
          System Resources
        </Typography>
        <Box sx={{ mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">
              CPU Utilization
            </Typography>
            <Typography variant="caption" fontWeight="bold">
              {systemResources.cpuUsage}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={systemResources.cpuUsage}
            sx={{ 
              height: 8, 
              borderRadius: 1,
              backgroundColor: 'rgba(0,0,0,0.09)',
              '& .MuiLinearProgress-bar': {
                backgroundColor: systemResources.cpuUsage > 80 ? '#f44336' : undefined
              }
            }}
          />
        </Box>
        <Box sx={{ mb: 1 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">
              Memory Usage
            </Typography>
            <Typography variant="caption" fontWeight="bold">
              {systemResources.memoryUsage}%
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={systemResources.memoryUsage}
            sx={{ 
              height: 8, 
              borderRadius: 1,
              backgroundColor: 'rgba(0,0,0,0.09)',
              '& .MuiLinearProgress-bar': {
                backgroundColor: systemResources.memoryUsage > 80 ? '#f44336' : undefined
              }
            }}
          />
        </Box>
        <Box>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
            <Typography variant="caption" color="text.secondary">
              Network Latency
            </Typography>
            <Typography variant="caption" fontWeight="bold">
              {systemResources.networkLatency} ms
            </Typography>
          </Box>
          <LinearProgress
            variant="determinate"
            value={(systemResources.networkLatency / 200) * 100} // Scale to percentage (200ms = 100%)
            sx={{ 
              height: 8, 
              borderRadius: 1,
              backgroundColor: 'rgba(0,0,0,0.09)',
              '& .MuiLinearProgress-bar': {
                backgroundColor: systemResources.networkLatency > 150 ? '#f44336' : undefined
              }
            }}
          />
        </Box>
      </SystemStatsContainer>
      {statusMessage.text && (
        <Box sx={{ p: 2, backgroundColor: statusMessage.type === 'error' ? '#f44336' : statusMessage.type === 'success' ? '#4caf50' : '#ff9800', color: 'white' }}>
          {statusMessage.text}
        </Box>
      )}
    </AgentStatusRoot>
  );
};

export default AgentStatusPanel;
