import React from 'react';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
} from '@mui/lab';
import { Paper, Typography, Box } from '@mui/material';
import {
  Code as CodeIcon,
  BugReport as BugIcon,
  CheckCircle as CheckIcon,
  Build as BuildIcon,
} from '@mui/icons-material';

interface TimelineEvent {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  type: 'code' | 'bug' | 'build' | 'complete';
  status: 'completed' | 'in-progress' | 'pending';
}

const getEventIcon = (type: TimelineEvent['type']) => {
  switch (type) {
    case 'code':
      return <CodeIcon />;
    case 'bug':
      return <BugIcon />;
    case 'build':
      return <BuildIcon />;
    case 'complete':
      return <CheckIcon />;
    default:
      return <CodeIcon />;
  }
};

const getEventColor = (status: TimelineEvent['status']) => {
  switch (status) {
    case 'completed':
      return 'success';
    case 'in-progress':
      return 'primary';
    case 'pending':
      return 'grey';
    default:
      return 'grey';
  }
};

const ProjectTimeline: React.FC = () => {
  const events: TimelineEvent[] = [
    {
      id: '1',
      title: 'Project Setup',
      description: 'Initial project structure and dependencies',
      timestamp: '2h ago',
      type: 'code',
      status: 'completed',
    },
    {
      id: '2',
      title: 'Core Components',
      description: 'Implementing main interface components',
      timestamp: '1h ago',
      type: 'code',
      status: 'in-progress',
    },
    {
      id: '3',
      title: 'Bug Fixes',
      description: 'Resolving component integration issues',
      timestamp: '30m ago',
      type: 'bug',
      status: 'pending',
    },
    {
      id: '4',
      title: 'Build Pipeline',
      description: 'Setting up CI/CD workflow',
      timestamp: '10m ago',
      type: 'build',
      status: 'pending',
    },
  ];

  return (
    <Box sx={{ maxHeight: '400px', overflow: 'auto' }}>
      <Timeline position="right">
        {events.map((event) => (
          <TimelineItem key={event.id}>
            <TimelineSeparator>
              <TimelineDot color={getEventColor(event.status)}>
                {getEventIcon(event.type)}
              </TimelineDot>
              <TimelineConnector />
            </TimelineSeparator>
            <TimelineContent>
              <Paper
                elevation={1}
                sx={{
                  p: 2,
                  mb: 2,
                  backgroundColor: (theme) =>
                    event.status === 'completed'
                      ? theme.palette.action.hover
                      : theme.palette.background.paper,
                }}
              >
                <Typography variant="h6" component="h3">
                  {event.title}
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {event.description}
                </Typography>
                <Typography variant="caption" color="textSecondary">
                  {event.timestamp}
                </Typography>
              </Paper>
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
    </Box>
  );
};

export default ProjectTimeline; 