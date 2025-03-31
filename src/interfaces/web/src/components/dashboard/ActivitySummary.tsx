import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  Box,
  Typography,
  CircularProgress,
  Alert,
} from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
} from '@mui/lab';
import {
  Code as CodeIcon,
  Task as TaskIcon,
  Build as BuildIcon,
  BugReport as BugIcon,
} from '@mui/icons-material';
import Card from '../common/Card';
import { dashboardService } from '../../services/dashboardService';
import { useWebSocket } from '../../hooks/useWebSocket';

export interface Activity {
  id: string;
  type: 'code' | 'task' | 'build' | 'bug';
  title: string;
  description: string;
  timestamp: string;
  status: 'completed' | 'in_progress' | 'failed';
}

const mockActivities: Activity[] = [
  {
    id: '1',
    type: 'code',
    title: 'Code Review',
    description: 'Reviewed pull request #123',
    timestamp: '2024-03-20T10:30:00Z',
    status: 'completed',
  },
  {
    id: '2',
    type: 'task',
    title: 'Task Assignment',
    description: 'New task assigned: Implement dashboard',
    timestamp: '2024-03-20T09:45:00Z',
    status: 'in_progress',
  },
  {
    id: '3',
    type: 'build',
    title: 'Build Pipeline',
    description: 'Build #456 completed successfully',
    timestamp: '2024-03-20T09:00:00Z',
    status: 'completed',
  },
  {
    id: '4',
    type: 'bug',
    title: 'Bug Fix',
    description: 'Fixed authentication issue',
    timestamp: '2024-03-20T08:15:00Z',
    status: 'completed',
  },
];

const getActivityIcon = (type: Activity['type']) => {
  switch (type) {
    case 'code':
      return <CodeIcon />;
    case 'task':
      return <TaskIcon />;
    case 'build':
      return <BuildIcon />;
    case 'bug':
      return <BugIcon />;
    default:
      return <TaskIcon />;
  }
};

const getStatusColor = (status: Activity['status']) => {
  switch (status) {
    case 'completed':
      return 'success.main';
    case 'in_progress':
      return 'info.main';
    case 'failed':
      return 'error.main';
    default:
      return 'grey.500';
  }
};

const ActivitySummary: React.FC = () => {
  useWebSocket('activity');

  const { data: activities, isLoading, error } = useQuery<Activity[]>({
    queryKey: ['activities'],
    queryFn: dashboardService.getActivities,
  });

  if (isLoading) {
    return (
      <Card title="Activity Summary">
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Activity Summary">
        <Alert severity="error">Failed to load activities</Alert>
      </Card>
    );
  }

  return (
    <Card
      title="Activity Summary"
      subtitle="Recent platform activities and updates"
    >
      <Timeline>
        {activities?.map((activity) => (
          <TimelineItem key={activity.id}>
            <TimelineSeparator>
              <TimelineDot sx={{ bgcolor: getStatusColor(activity.status) }}>
                {getActivityIcon(activity.type)}
              </TimelineDot>
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent>
              <Typography variant="subtitle2">{activity.title}</Typography>
              <Typography variant="body2" color="text.secondary">
                {activity.description}
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {new Date(activity.timestamp).toLocaleString()}
              </Typography>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
    </Card>
  );
};

export default ActivitySummary; 