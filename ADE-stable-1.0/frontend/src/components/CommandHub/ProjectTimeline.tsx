import React from 'react';
import { Box, Typography, Paper } from '@mui/material';
import {
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
} from '@mui/lab';
import { CheckCircle, RadioButtonUnchecked, Warning } from '@mui/icons-material';

interface Milestone {
  id: string;
  title: string;
  description: string;
  status: 'completed' | 'in-progress' | 'pending';
  date: string;
}

const ProjectTimeline: React.FC = () => {
  const milestones: Milestone[] = [
    {
      id: '1',
      title: 'Initial Setup',
      description: 'Project structure and basic components',
      status: 'completed',
      date: '2024-03-20',
    },
    {
      id: '2',
      title: 'Core Features',
      description: 'Implementation of main functionality',
      status: 'in-progress',
      date: '2024-03-25',
    },
    {
      id: '3',
      title: 'Testing & QA',
      description: 'Comprehensive testing and quality assurance',
      status: 'pending',
      date: '2024-03-30',
    },
    {
      id: '4',
      title: 'Deployment',
      description: 'Production deployment and monitoring setup',
      status: 'pending',
      date: '2024-04-05',
    },
  ];

  const getStatusIcon = (status: Milestone['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle color="success" />;
      case 'in-progress':
        return <RadioButtonUnchecked color="primary" />;
      case 'pending':
        return <Warning color="warning" />;
      default:
        return <RadioButtonUnchecked />;
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" gutterBottom>
        Project Timeline
      </Typography>
      
      <Timeline position="right" sx={{ flex: 1, overflow: 'auto' }}>
        {milestones.map((milestone, index) => (
          <TimelineItem key={milestone.id}>
            <TimelineSeparator>
              <TimelineDot color={milestone.status === 'completed' ? 'success' : 'primary'}>
                {getStatusIcon(milestone.status)}
              </TimelineDot>
              {index < milestones.length - 1 && <TimelineConnector />}
            </TimelineSeparator>
            <TimelineContent>
              <Paper sx={{ p: 2, bgcolor: 'background.paper' }}>
                <Typography variant="subtitle1" component="div">
                  {milestone.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {milestone.description}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {milestone.date}
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