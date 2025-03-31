import React, { useState, useEffect } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Divider,
  CircularProgress,
} from '@mui/material';
import {
  Code,
  Build,
  BugReport,
  CheckCircle,
  Error,
  Warning,
  Info,
  Refresh,
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import { useAgentContext } from './AgentContext';

interface Activity {
  id: string;
  type: 'code_change' | 'task_update' | 'review' | 'build' | 'test' | 'deploy' | 'error';
  agentId: string;
  description: string;
  timestamp: Date;
  status: 'success' | 'warning' | 'error' | 'info';
  details?: {
    file?: string;
    line?: number;
    changes?: number;
    duration?: number;
  };
}

interface AgentActivityStreamProps {
  projectId: string;
}

const getActivityIcon = (type: Activity['type']) => {
  switch (type) {
    case 'code_change':
      return <Code />;
    case 'task_update':
      return <Build />;
    case 'review':
      return <Info />;
    case 'build':
      return <Build />;
    case 'test':
      return <CheckCircle />;
    case 'deploy':
      return <Build />;
    case 'error':
      return <BugReport />;
    default:
      return <Info />;
  }
};

const getStatusColor = (status: Activity['status']) => {
  switch (status) {
    case 'success':
      return 'success';
    case 'warning':
      return 'warning';
    case 'error':
      return 'error';
    case 'info':
      return 'info';
    default:
      return 'default';
  }
};

const AgentActivityStream: React.FC<AgentActivityStreamProps> = ({ projectId }) => {
  const { agents, getAgentById } = useAgentContext();
  const [activities, setActivities] = useState<Activity[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<Activity['type'] | 'all'>('all');

  // Simulate real-time activities
  useEffect(() => {
    const generateActivity = () => {
      const types: Activity['type'][] = [
        'code_change',
        'task_update',
        'review',
        'build',
        'test',
        'deploy',
        'error',
      ];
      const statuses: Activity['status'][] = ['success', 'warning', 'error', 'info'];
      const agent = agents[Math.floor(Math.random() * agents.length)];

      return {
        id: Math.random().toString(36).substr(2, 9),
        type: types[Math.floor(Math.random() * types.length)],
        agentId: agent.id,
        description: `Agent ${agent.name} performed an action`,
        timestamp: new Date(),
        status: statuses[Math.floor(Math.random() * statuses.length)],
        details: {
          file: 'example.ts',
          line: Math.floor(Math.random() * 100),
          changes: Math.floor(Math.random() * 10),
          duration: Math.floor(Math.random() * 1000),
        },
      };
    };

    const interval = setInterval(() => {
      setActivities((prev) => [generateActivity(), ...prev].slice(0, 50));
    }, 3000);

    setLoading(false);

    return () => clearInterval(interval);
  }, [agents]);

  const filteredActivities = activities.filter(
    (activity) => filter === 'all' || activity.type === filter
  );

  const handleRefresh = () => {
    setLoading(true);
    setActivities([]);
    setTimeout(() => setLoading(false), 1000);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Activity Stream</Typography>
        <Tooltip title="Refresh">
          <IconButton onClick={handleRefresh} size="small">
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      <Box sx={{ display: 'flex', gap: 1, mb: 2, flexWrap: 'wrap' }}>
        <Chip
          label="All"
          onClick={() => setFilter('all')}
          color={filter === 'all' ? 'primary' : 'default'}
          size="small"
        />
        <Chip
          label="Code Changes"
          onClick={() => setFilter('code_change')}
          color={filter === 'code_change' ? 'primary' : 'default'}
          size="small"
        />
        <Chip
          label="Tasks"
          onClick={() => setFilter('task_update')}
          color={filter === 'task_update' ? 'primary' : 'default'}
          size="small"
        />
        <Chip
          label="Reviews"
          onClick={() => setFilter('review')}
          color={filter === 'review' ? 'primary' : 'default'}
          size="small"
        />
        <Chip
          label="Builds"
          onClick={() => setFilter('build')}
          color={filter === 'build' ? 'primary' : 'default'}
          size="small"
        />
        <Chip
          label="Tests"
          onClick={() => setFilter('test')}
          color={filter === 'test' ? 'primary' : 'default'}
          size="small"
        />
        <Chip
          label="Deployments"
          onClick={() => setFilter('deploy')}
          color={filter === 'deploy' ? 'primary' : 'default'}
          size="small"
        />
        <Chip
          label="Errors"
          onClick={() => setFilter('error')}
          color={filter === 'error' ? 'primary' : 'default'}
          size="small"
        />
      </Box>

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', flex: 1 }}>
          <CircularProgress />
        </Box>
      ) : (
        <List sx={{ flex: 1, overflow: 'auto' }}>
          {filteredActivities.map((activity, index) => {
            const agent = getAgentById(activity.agentId);
            return (
              <React.Fragment key={activity.id}>
                {index > 0 && <Divider variant="inset" component="li" />}
                <ListItem alignItems="flex-start">
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: getStatusColor(activity.status) }}>
                      {getActivityIcon(activity.type)}
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        <Typography component="span" variant="subtitle2">
                          {agent?.name}
                        </Typography>
                        <Typography component="span" variant="body2" color="text.secondary">
                          {formatDistanceToNow(activity.timestamp, { addSuffix: true })}
                        </Typography>
                        <Chip
                          label={activity.type.replace('_', ' ')}
                          size="small"
                          color={getStatusColor(activity.status)}
                        />
                      </Box>
                    }
                    secondary={
                      <Box>
                        <Typography
                          component="span"
                          variant="body2"
                          color="text.primary"
                          sx={{ display: 'block' }}
                        >
                          {activity.description}
                        </Typography>
                        {activity.details && (
                          <Box sx={{ mt: 1 }}>
                            {activity.details.file && (
                              <Typography variant="caption" color="text.secondary">
                                File: {activity.details.file}
                                {activity.details.line && `:${activity.details.line}`}
                              </Typography>
                            )}
                            {activity.details.changes && (
                              <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                                Changes: {activity.details.changes}
                              </Typography>
                            )}
                            {activity.details.duration && (
                              <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                                Duration: {activity.details.duration}ms
                              </Typography>
                            )}
                          </Box>
                        )}
                      </Box>
                    }
                  />
                </ListItem>
              </React.Fragment>
            );
          })}
        </List>
      )}
    </Box>
  );
};

export default AgentActivityStream; 