import React, { useState } from 'react';
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
  TextField,
  InputAdornment,
  Badge,
  useTheme,
  alpha
} from '@mui/material';
import {
  AccessTime as AccessTimeIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
  Code as CodeIcon,
  Build as BuildIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  SettingsEthernet as SettingsEthernetIcon,
  ArrowDownward as ArrowDownwardIcon,
  ArrowUpward as ArrowUpwardIcon
} from '@mui/icons-material';
import { Agent, AgentType, AgentStatus } from './AgentListPanel';

// Define the activity types
export enum ActivityType {
  TASK_STARTED = 'TASK_STARTED',
  TASK_COMPLETED = 'TASK_COMPLETED',
  ERROR = 'ERROR',
  WARNING = 'WARNING',
  COMMUNICATION = 'COMMUNICATION',
  STATUS_CHANGE = 'STATUS_CHANGE',
  RESOURCE_USAGE = 'RESOURCE_USAGE'
}

// Define the activity interface
export interface AgentActivity {
  id: string;
  agentId: string;
  timestamp: Date;
  type: ActivityType;
  title: string;
  description: string;
  severity?: 'low' | 'medium' | 'high';
  relatedAgentIds?: string[];
  metadata?: Record<string, any>;
}

interface AgentActivityTimelineProps {
  agents: Agent[];
  selectedAgentId?: string;
  onActivitySelect?: (activity: AgentActivity) => void;
}

/**
 * Helper function to generate mock activities for development and testing
 */
export const generateMockActivities = (agents: Agent[], count: number = 20): AgentActivity[] => {
  const activities: AgentActivity[] = [];
  const activityTypes = Object.values(ActivityType);
  
  // Generate activities within the last 24 hours
  const now = new Date();
  const oneDayAgo = new Date(now.getTime() - 24 * 60 * 60 * 1000);
  
  for (let i = 0; i < count; i++) {
    const agent = agents[Math.floor(Math.random() * agents.length)];
    const type = activityTypes[Math.floor(Math.random() * activityTypes.length)];
    
    // Generate a random timestamp between now and oneDayAgo
    const timestamp = new Date(
      oneDayAgo.getTime() + Math.random() * (now.getTime() - oneDayAgo.getTime())
    );
    
    // Generate title and description based on activity type
    let title = '';
    let description = '';
    let severity: 'low' | 'medium' | 'high' | undefined;
    let relatedAgentIds: string[] | undefined;
    
    switch (type) {
      case ActivityType.TASK_STARTED:
        title = `Started ${['code analysis', 'requirements validation', 'security scan', 'performance optimization', 'architecture review'][Math.floor(Math.random() * 5)]}`;
        description = `${agent.name} initiated a new task`;
        break;
      case ActivityType.TASK_COMPLETED:
        title = `Completed ${['code review', 'requirements analysis', 'security check', 'performance analysis', 'design review'][Math.floor(Math.random() * 5)]}`;
        description = `${agent.name} successfully completed the task`;
        break;
      case ActivityType.ERROR:
        title = `Error: ${['Connection failed', 'API timeout', 'Resource not found', 'Access denied', 'Validation failed'][Math.floor(Math.random() * 5)]}`;
        description = `${agent.name} encountered an error while processing the request`;
        severity = ['medium', 'high'][Math.floor(Math.random() * 2)] as 'medium' | 'high';
        break;
      case ActivityType.WARNING:
        title = `Warning: ${['Resource usage high', 'Response time degraded', 'Rate limit approaching', 'Deprecated API', 'Configuration issue'][Math.floor(Math.random() * 5)]}`;
        description = `${agent.name} detected a potential issue`;
        severity = 'low';
        break;
      case ActivityType.COMMUNICATION:
        // Select a random agent to communicate with
        const targetAgent = agents.filter(a => a.id !== agent.id)[Math.floor(Math.random() * (agents.length - 1))];
        title = `Communication with ${targetAgent.name}`;
        description = `${agent.name} sent a message to ${targetAgent.name}`;
        relatedAgentIds = [targetAgent.id];
        break;
      case ActivityType.STATUS_CHANGE:
        const newStatus = Object.values(AgentStatus)[Math.floor(Math.random() * Object.values(AgentStatus).length)];
        title = `Status changed to ${newStatus}`;
        description = `${agent.name} changed status from ${agent.status} to ${newStatus}`;
        break;
      case ActivityType.RESOURCE_USAGE:
        const resource = ['CPU', 'Memory', 'Network', 'Storage', 'API calls'][Math.floor(Math.random() * 5)];
        const usage = Math.floor(Math.random() * 100);
        title = `${resource} usage at ${usage}%`;
        description = `${agent.name} is currently using ${usage}% of available ${resource}`;
        severity = usage > 80 ? 'high' : usage > 60 ? 'medium' : 'low';
        break;
      default:
        title = 'System activity';
        description = `${agent.name} performed a system action`;
    }
    
    activities.push({
      id: `activity-${i}`,
      agentId: agent.id,
      timestamp,
      type,
      title,
      description,
      severity,
      relatedAgentIds
    });
  }
  
  // Sort activities by timestamp, most recent first
  return activities.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime());
};

/**
 * AgentActivityTimeline Component - Displays a chronological timeline of agent activities
 */
const AgentActivityTimeline: React.FC<AgentActivityTimelineProps> = ({
  agents,
  selectedAgentId,
  onActivitySelect
}) => {
  const theme = useTheme();
  const [activities, setActivities] = useState<AgentActivity[]>(generateMockActivities(agents));
  const [searchTerm, setSearchTerm] = useState('');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc'); // Default newest first
  const [selectedTypes, setSelectedTypes] = useState<ActivityType[]>([]);

  // Format timestamp to readable string
  const formatTimestamp = (timestamp: Date): string => {
    const now = new Date();
    const diffMs = now.getTime() - timestamp.getTime();
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHour = Math.floor(diffMin / 60);
    
    if (diffHour > 0) {
      return `${diffHour}h ago`;
    } else if (diffMin > 0) {
      return `${diffMin}m ago`;
    } else {
      return `${diffSec}s ago`;
    }
  };

  // Filter activities based on search term, selected agent, and activity types
  const filteredActivities = activities
    .filter(activity => 
      // Filter by selected agent if any
      (selectedAgentId ? activity.agentId === selectedAgentId || (activity.relatedAgentIds?.includes(selectedAgentId)) : true) && 
      // Search term in title or description
      (searchTerm === '' || 
        activity.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
        activity.description.toLowerCase().includes(searchTerm.toLowerCase())) &&
      // Filter by selected types if any
      (selectedTypes.length === 0 || selectedTypes.includes(activity.type))
    )
    // Sort by timestamp
    .sort((a, b) => {
      if (sortDirection === 'asc') {
        return a.timestamp.getTime() - b.timestamp.getTime();
      } else {
        return b.timestamp.getTime() - a.timestamp.getTime();
      }
    });

  // Toggle sorting direction
  const toggleSortDirection = () => {
    setSortDirection(prevDirection => prevDirection === 'asc' ? 'desc' : 'asc');
  };

  // Toggle filter for activity type
  const toggleActivityTypeFilter = (type: ActivityType) => {
    setSelectedTypes(prevTypes => 
      prevTypes.includes(type) 
        ? prevTypes.filter(t => t !== type)
        : [...prevTypes, type]
    );
  };

  // Get icon for activity type
  const getActivityIcon = (type: ActivityType) => {
    switch (type) {
      case ActivityType.TASK_STARTED:
        return <BuildIcon />;
      case ActivityType.TASK_COMPLETED:
        return <CheckCircleIcon style={{ color: theme.palette.success.main }} />;
      case ActivityType.ERROR:
        return <ErrorIcon style={{ color: theme.palette.error.main }} />;
      case ActivityType.WARNING:
        return <WarningIcon style={{ color: theme.palette.warning.main }} />;
      case ActivityType.COMMUNICATION:
        return <SettingsEthernetIcon style={{ color: theme.palette.info.main }} />;
      case ActivityType.STATUS_CHANGE:
        return <InfoIcon style={{ color: theme.palette.primary.main }} />;
      case ActivityType.RESOURCE_USAGE:
        return <SpeedIcon style={{ color: theme.palette.secondary.main }} />;
      default:
        return <InfoIcon />;
    }
  };

  // Get agent icon based on agent type
  const getAgentIcon = (agentType: AgentType) => {
    switch (agentType) {
      case AgentType.VALIDATOR:
        return <CheckCircleIcon />;
      case AgentType.DESIGNER:
        return <CodeIcon />;
      case AgentType.ARCHITECT:
        return <BuildIcon />;
      case AgentType.SECURITY:
        return <SecurityIcon />;
      case AgentType.PERFORMANCE:
        return <SpeedIcon />;
      case AgentType.ADMIN:
        return <SettingsEthernetIcon />;
      default:
        return <InfoIcon />;
    }
  };

  // Get avatar background color based on agent type
  const getAvatarColor = (agentType: AgentType) => {
    switch (agentType) {
      case AgentType.VALIDATOR:
        return theme.palette.purple.main;
      case AgentType.DESIGNER:
        return theme.palette.blue.main;
      case AgentType.ARCHITECT:
        return theme.palette.green.main;
      case AgentType.SECURITY:
        return theme.palette.red.main;
      case AgentType.PERFORMANCE:
        return theme.palette.orange.main;
      case AgentType.ADMIN:
        return theme.palette.blueGrey.main;
      default:
        return theme.palette.grey[500];
    }
  };

  // Get severity color
  const getSeverityColor = (severity?: 'low' | 'medium' | 'high') => {
    switch (severity) {
      case 'high':
        return theme.palette.error.main;
      case 'medium':
        return theme.palette.warning.main;
      case 'low':
        return theme.palette.info.main;
      default:
        return undefined;
    }
  };

  // Get agent by ID
  const getAgentById = (id: string) => {
    return agents.find(agent => agent.id === id);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Search and filter bar */}
      <Box sx={{ mb: 2 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Search activities..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon fontSize="small" />
              </InputAdornment>
            ),
            endAdornment: (
              <InputAdornment position="end">
                <IconButton 
                  size="small" 
                  onClick={toggleSortDirection}
                  title={sortDirection === 'desc' ? 'Newest first' : 'Oldest first'}
                >
                  {sortDirection === 'desc' ? <ArrowDownwardIcon fontSize="small" /> : <ArrowUpwardIcon fontSize="small" />}
                </IconButton>
                <IconButton 
                  size="small"
                  onClick={() => {
                    // Show filter options popup or toggle all/none
                    if (selectedTypes.length === Object.values(ActivityType).length) {
                      setSelectedTypes([]);
                    } else {
                      setSelectedTypes(Object.values(ActivityType));
                    }
                  }}
                >
                  <Badge 
                    badgeContent={selectedTypes.length > 0 ? selectedTypes.length : undefined} 
                    color="primary"
                  >
                    <FilterListIcon fontSize="small" />
                  </Badge>
                </IconButton>
              </InputAdornment>
            )
          }}
        />
      </Box>
      
      {/* Activity type filters */}
      <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
        {Object.values(ActivityType).map(type => (
          <Chip
            key={type}
            size="small"
            icon={getActivityIcon(type)}
            label={type.replace('_', ' ')}
            variant={selectedTypes.includes(type) ? 'filled' : 'outlined'}
            onClick={() => toggleActivityTypeFilter(type)}
            sx={{ 
              opacity: selectedTypes.length === 0 || selectedTypes.includes(type) ? 1 : 0.6,
              '& .MuiChip-icon': { fontSize: '1rem' }
            }}
          />
        ))}
      </Box>
      
      {/* Activity timeline */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {filteredActivities.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <Typography variant="body2" color="textSecondary">
              No activities found matching your filters
            </Typography>
          </Box>
        ) : (
          <List sx={{ width: '100%' }}>
            {filteredActivities.map((activity, index) => {
              const agent = getAgentById(activity.agentId);
              if (!agent) return null;
              
              return (
                <React.Fragment key={activity.id}>
                  <ListItem 
                    alignItems="flex-start"
                    sx={{ 
                      cursor: 'pointer',
                      '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.08) },
                      ...(selectedAgentId === activity.agentId ? { bgcolor: alpha(theme.palette.primary.main, 0.12) } : {})
                    }}
                    onClick={() => onActivitySelect && onActivitySelect(activity)}
                  >
                    <ListItemAvatar>
                      <Badge
                        overlap="circular"
                        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                        badgeContent={
                          <Avatar 
                            sx={{ 
                              width: 22, 
                              height: 22,
                              bgcolor: theme.palette.background.paper,
                              border: `2px solid ${theme.palette.background.paper}`
                            }}
                          >
                            {getActivityIcon(activity.type)}
                          </Avatar>
                        }
                      >
                        <Avatar sx={{ bgcolor: getAvatarColor(agent.type) }}>
                          {getAgentIcon(agent.type)}
                        </Avatar>
                      </Badge>
                    </ListItemAvatar>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="body1" component="span" fontWeight="medium">
                            {activity.title}
                          </Typography>
                          <Typography variant="caption" color="textSecondary" component="span">
                            <AccessTimeIcon fontSize="inherit" sx={{ verticalAlign: 'middle', mr: 0.5 }} />
                            {formatTimestamp(activity.timestamp)}
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <React.Fragment>
                          <Typography
                            component="span"
                            variant="body2"
                            color="textSecondary"
                          >
                            {activity.description}
                          </Typography>
                          <Box sx={{ mt: 0.5, display: 'flex', gap: 1 }}>
                            {activity.severity && (
                              <Chip 
                                size="small" 
                                label={`Severity: ${activity.severity}`}
                                sx={{ 
                                  height: 20, 
                                  fontSize: '0.7rem',
                                  bgcolor: alpha(getSeverityColor(activity.severity) || theme.palette.grey[500], 0.1),
                                  color: getSeverityColor(activity.severity),
                                  borderColor: getSeverityColor(activity.severity)
                                }}
                                variant="outlined"
                              />
                            )}
                            {activity.relatedAgentIds && activity.relatedAgentIds.map(relatedId => {
                              const relatedAgent = getAgentById(relatedId);
                              if (!relatedAgent) return null;
                              
                              return (
                                <Chip
                                  key={relatedId}
                                  size="small"
                                  avatar={
                                    <Avatar sx={{ bgcolor: getAvatarColor(relatedAgent.type) }}>
                                      {getAgentIcon(relatedAgent.type)}
                                    </Avatar>
                                  }
                                  label={relatedAgent.name}
                                  sx={{ height: 20, fontSize: '0.7rem' }}
                                  variant="outlined"
                                />
                              );
                            })}
                          </Box>
                        </React.Fragment>
                      }
                    />
                  </ListItem>
                  {index < filteredActivities.length - 1 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              );
            })}
          </List>
        )}
      </Box>
    </Box>
  );
};

export default AgentActivityTimeline;
