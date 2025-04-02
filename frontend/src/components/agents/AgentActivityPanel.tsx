import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Chip,
  Divider,
  IconButton,
  Tooltip,
  CircularProgress,
  Button,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Psychology as AIIcon,
  Build as DevIcon,
  Palette as DesignIcon,
  Insights as AdvisorIcon,
  Memory as ArchitectIcon,
  Storage as DataIcon,
  Code as CodeIcon,
  Terminal as TerminalIcon,
  CheckCircleOutline as SuccessIcon,
  ErrorOutline as ErrorIcon,
  Refresh as RefreshIcon,
  AccessTime as TimeIcon,
  Clear as ClearIcon,
} from '@mui/icons-material';
import errorLogger from '../../services/errorLogging';

// Styled components
const ActivityPanelRoot = styled(Paper)(({ theme }) => ({
  height: '100%',
  overflow: 'hidden',
  display: 'flex',
  flexDirection: 'column',
  border: `1px solid ${theme.palette.divider}`,
}));

const ActivityHeader = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(2),
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

const ActivityListContainer = styled(Box)(({ theme }) => ({
  flexGrow: 1,
  overflow: 'auto',
  padding: theme.spacing(0),
}));

const ActivityFooter = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1, 2),
  borderTop: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.default,
}));

const AgentActivityItem = styled(ListItem, {
  shouldForwardProp: (prop) => prop !== 'status',
})<{ status?: AgentActivity['status'] }>(({ theme, status }) => ({
  transition: 'background-color 0.2s ease',
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
  ...(status === 'error' && {
    borderLeft: `4px solid ${theme.palette.error.main}`,
  }),
  ...(status === 'success' && {
    borderLeft: `4px solid ${theme.palette.success.main}`,
  }),
  ...(status === 'inProgress' && {
    borderLeft: `4px solid ${theme.palette.primary.main}`,
  }),
}));

// Types
type AgentType = 'assistant' | 'developer' | 'designer' | 'advisor' | 'architect' | 'data' | 'terminal';

interface AgentActivity {
  id: string;
  agentType: AgentType;
  agentName: string;
  action: string;
  details?: string;
  timestamp: Date;
  duration?: number; // in milliseconds
  status: 'success' | 'error' | 'inProgress' | 'pending';
  relatedComponents?: string[];
  resourceConsumption?: {
    cpu: number;
    memory: number;
  };
}

interface AgentActivityPanelProps {
  projectId?: string;
  maxActivities?: number;
  onActivitySelect?: (activity: AgentActivity) => void;
}

const AgentActivityPanel: React.FC<AgentActivityPanelProps> = ({ 
  projectId,
  maxActivities = 15,
  onActivitySelect
}) => {
  const [activities, setActivities] = useState<AgentActivity[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [refreshCount, setRefreshCount] = useState(0);
  const activityListRef = useRef<HTMLDivElement>(null);

  // Simulate fetching agent activities
  useEffect(() => {
    fetchActivities();
    // Auto-refresh every minute
    const interval = setInterval(() => {
      fetchActivities();
    }, 60000);
    
    return () => clearInterval(interval);
  }, [projectId, refreshCount]);

  // Generate a random agent activity for simulation
  const generateRandomActivity = (): AgentActivity => {
    const agentTypes: AgentType[] = ['assistant', 'developer', 'designer', 'advisor', 'architect', 'data', 'terminal'];
    const actions = [
      'Created component',
      'Fixed bug',
      'Optimized code',
      'Generated UI',
      'Analyzed performance',
      'Integrated API',
      'Refactored module',
      'Tested functionality',
      'Updated schema',
      'Deployed changes'
    ];
    const statuses: AgentActivity['status'][] = ['success', 'error', 'inProgress', 'pending'];
    const components = ['Dashboard', 'CommandHub', 'LiveChat', 'AgentStatusPanel', 'Navigation', 'CodeEditor', 'ProjectManager'];
    
    const randomAgentType = agentTypes[Math.floor(Math.random() * agentTypes.length)];
    const randomAction = actions[Math.floor(Math.random() * actions.length)];
    const randomStatus = Math.random() > 0.7 
      ? 'inProgress' 
      : Math.random() > 0.1 
        ? 'success' 
        : Math.random() > 0.5 
          ? 'error' 
          : 'pending';
    
    const timestamp = new Date();
    timestamp.setMinutes(timestamp.getMinutes() - Math.floor(Math.random() * 60));
    
    const duration = randomStatus === 'inProgress' 
      ? undefined 
      : Math.floor(Math.random() * 120000);
    
    const relatedComponents = [];
    const numComponents = Math.floor(Math.random() * 3) + 1;
    for (let i = 0; i < numComponents; i++) {
      const component = components[Math.floor(Math.random() * components.length)];
      if (!relatedComponents.includes(component)) {
        relatedComponents.push(component);
      }
    }
    
    return {
      id: `activity-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      agentType: randomAgentType,
      agentName: randomAgentType.charAt(0).toUpperCase() + randomAgentType.slice(1),
      action: randomAction,
      details: Math.random() > 0.3 ? `${randomAction} for ${relatedComponents.join(', ')}` : undefined,
      timestamp,
      duration,
      status: randomStatus,
      relatedComponents,
      resourceConsumption: {
        cpu: Math.floor(Math.random() * 100),
        memory: Math.floor(Math.random() * 100)
      }
    };
  };

  const fetchActivities = () => {
    setIsLoading(true);
    
    // Simulate API call delay
    setTimeout(() => {
      // In a real implementation, this would fetch from an API
      // For now, we're generating mock data for demonstration
      
      // Generate new activities (1-3 new activities)
      const newActivitiesCount = Math.floor(Math.random() * 3) + 1;
      const newActivities: AgentActivity[] = [];
      
      for (let i = 0; i < newActivitiesCount; i++) {
        newActivities.push(generateRandomActivity());
      }
      
      // Sort by timestamp (newest first) and limit to maxActivities
      setActivities(prev => 
        [...newActivities, ...prev]
          .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
          .slice(0, maxActivities)
      );
      
      setIsLoading(false);
    }, 800);
  };

  const handleRefresh = () => {
    setRefreshCount(prev => prev + 1);
  };

  const handleClearActivities = () => {
    setActivities([]);
  };

  const getAgentIcon = (type: AgentType) => {
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

  const getAgentColor = (type: AgentType) => {
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

  const getStatusIcon = (status: AgentActivity['status']) => {
    switch (status) {
      case 'success':
        return <SuccessIcon color="success" />;
      case 'error':
        return <ErrorIcon color="error" />;
      case 'inProgress':
        return <CircularProgress size={18} />;
      case 'pending':
        return <TimeIcon color="disabled" />;
      default:
        return null;
    }
  };

  const formatDuration = (duration: number) => {
    const totalSeconds = Math.floor(duration / 1000);
    const minutes = Math.floor(totalSeconds / 60);
    const seconds = totalSeconds % 60;
    
    if (minutes > 0) {
      return `${minutes}m ${seconds}s`;
    }
    
    return `${seconds}s`;
  };

  const formatTimeAgo = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSec = Math.round(diffMs / 1000);
    
    if (diffSec < 60) return `${diffSec}s ago`;
    
    const diffMin = Math.round(diffSec / 60);
    if (diffMin < 60) return `${diffMin}m ago`;
    
    const diffHr = Math.round(diffMin / 60);
    if (diffHr < 24) return `${diffHr}h ago`;
    
    const diffDays = Math.round(diffHr / 24);
    return `${diffDays}d ago`;
  };

  // Function to log activity to the error logging system if it's an error
  const logActivityError = (activity: AgentActivity) => {
    if (activity.status !== 'error') return;
    
    // Log the error using our centralized error logging service
    errorLogger.logAgentError(
      `${activity.agentName} failed to ${activity.action}: ${activity.details || 'No details provided'}`,
      'ERROR',
      'AgentActivityPanel',
      {
        agentType: activity.agentType,
        action: activity.action,
        relatedComponents: activity.relatedComponents,
        resourceConsumption: activity.resourceConsumption,
        timestamp: activity.timestamp.toISOString()
      }
    );
  };

  // Log errors when activities are loaded or updated
  useEffect(() => {
    // Check for any error activities and log them
    activities
      .filter(activity => activity.status === 'error')
      .forEach(errorActivity => {
        logActivityError(errorActivity);
      });
  }, [activities]);

  return (
    <ActivityPanelRoot>
      <ActivityHeader>
        <Typography variant="h6" component="h2">
          Agent Activity
        </Typography>
        <Box>
          <Tooltip title="Refresh activities">
            <IconButton onClick={handleRefresh} disabled={isLoading}>
              {isLoading ? <CircularProgress size={24} /> : <RefreshIcon />}
            </IconButton>
          </Tooltip>
          <Tooltip title="Clear all activities">
            <IconButton onClick={handleClearActivities} disabled={isLoading}>
              <ClearIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </ActivityHeader>

      <ActivityListContainer ref={activityListRef}>
        {activities.length === 0 ? (
          <Box sx={{ p: 3, textAlign: 'center' }}>
            <Typography variant="body2" color="text.secondary">
              No recent agent activities
            </Typography>
            <Button 
              startIcon={<RefreshIcon />} 
              onClick={handleRefresh} 
              sx={{ mt: 1 }}
              size="small"
            >
              Refresh
            </Button>
          </Box>
        ) : (
          <List disablePadding>
            {activities.map((activity) => (
              <AgentActivityItem 
                key={activity.id} 
                status={activity.status}
                onClick={onActivitySelect ? () => onActivitySelect(activity) : undefined}
                sx={{
                  cursor: onActivitySelect ? 'pointer' : 'default',
                  opacity: activity.status === 'pending' ? 0.7 : 1,
                }}
              >
                <ListItemAvatar>
                  <Avatar sx={{ bgcolor: getAgentColor(activity.agentType) }}>
                    {getAgentIcon(activity.agentType)}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', alignItems: 'center' }}>
                      <Typography variant="body1" sx={{ fontWeight: 500, flexGrow: 1 }}>
                        {activity.action}
                      </Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', ml: 1 }}>
                        {getStatusIcon(activity.status)}
                      </Box>
                    </Box>
                  }
                  secondary={
                    <React.Fragment>
                      {activity.details && (
                        <Typography 
                          variant="body2" 
                          color="text.secondary" 
                          sx={{ 
                            display: 'block',
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap'
                          }}
                        >
                          {activity.details}
                        </Typography>
                      )}
                      <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5, flexWrap: 'wrap' }}>
                        <Typography 
                          variant="caption" 
                          color="text.secondary" 
                          sx={{ display: 'flex', alignItems: 'center', mr: 1.5 }}
                        >
                          {activity.agentName} Agent
                        </Typography>
                        {activity.duration && (
                          <Typography 
                            variant="caption" 
                            color="text.secondary" 
                            sx={{ display: 'flex', alignItems: 'center', mr: 1.5 }}
                          >
                            <TimeIcon fontSize="inherit" sx={{ mr: 0.5, opacity: 0.7 }} />
                            {formatDuration(activity.duration)}
                          </Typography>
                        )}
                        <Typography 
                          variant="caption" 
                          color="text.secondary" 
                          sx={{ display: 'flex', alignItems: 'center' }}
                        >
                          {formatTimeAgo(activity.timestamp)}
                        </Typography>
                      </Box>
                      {activity.relatedComponents && activity.relatedComponents.length > 0 && (
                        <Box sx={{ display: 'flex', flexWrap: 'wrap', mt: 0.5, gap: 0.5 }}>
                          {activity.relatedComponents.map((component, index) => (
                            <Chip
                              key={`${activity.id}-component-${index}`}
                              label={component}
                              size="small"
                              variant="outlined"
                              icon={<CodeIcon fontSize="small" />}
                              sx={{ height: 20, '& .MuiChip-label': { fontSize: '0.7rem', px: 1 } }}
                            />
                          ))}
                        </Box>
                      )}
                    </React.Fragment>
                  }
                />
              </AgentActivityItem>
            ))}
          </List>
        )}
      </ActivityListContainer>

      <ActivityFooter>
        <Typography variant="caption" color="text.secondary">
          Showing {activities.length} of {maxActivities} max activities
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Auto-refreshes every minute
        </Typography>
      </ActivityFooter>
    </ActivityPanelRoot>
  );
};

export default AgentActivityPanel;
