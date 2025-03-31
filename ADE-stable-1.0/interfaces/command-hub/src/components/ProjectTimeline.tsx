import React from 'react';
import {
  Paper,
  Box,
  Typography,
  Timeline,
  TimelineItem,
  TimelineSeparator,
  TimelineConnector,
  TimelineContent,
  TimelineDot,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Add as AddIcon,
} from '@mui/icons-material';

interface Milestone {
  id: string;
  title: string;
  description: string;
  status: 'completed' | 'in-progress' | 'pending';
  date: Date;
  decisionPoints: DecisionPoint[];
}

interface DecisionPoint {
  id: string;
  title: string;
  description: string;
  status: 'resolved' | 'pending' | 'blocked';
  impact: 'high' | 'medium' | 'low';
}

const ProjectTimeline: React.FC = () => {
  // Mock data - replace with actual data from API
  const milestones: Milestone[] = [
    {
      id: '1',
      title: 'Initial Architecture Design',
      description: 'Define system architecture and component relationships',
      status: 'completed',
      date: new Date('2024-03-01'),
      decisionPoints: [
        {
          id: 'dp1',
          title: 'Database Schema Design',
          description: 'Choose between SQL and NoSQL approach',
          status: 'resolved',
          impact: 'high',
        },
      ],
    },
    {
      id: '2',
      title: 'Core Components Implementation',
      description: 'Implement basic system components and interfaces',
      status: 'in-progress',
      date: new Date('2024-03-15'),
      decisionPoints: [
        {
          id: 'dp2',
          title: 'Authentication System',
          description: 'Select authentication provider and method',
          status: 'pending',
          impact: 'high',
        },
      ],
    },
  ];

  const getStatusColor = (status: Milestone['status']) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in-progress':
        return 'primary';
      default:
        return 'default';
    }
  };

  const getDecisionPointColor = (status: DecisionPoint['status']) => {
    switch (status) {
      case 'resolved':
        return 'success';
      case 'blocked':
        return 'error';
      default:
        return 'warning';
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        mb: 2,
        backgroundColor: 'background.paper',
        height: '300px',
        overflow: 'auto',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <TimelineIcon sx={{ mr: 1 }} />
        <Typography variant="h6">Project Timeline</Typography>
        <Tooltip title="Add Milestone">
          <IconButton size="small" sx={{ ml: 'auto' }}>
            <AddIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Timeline>
        {milestones.map((milestone, index) => (
          <TimelineItem key={milestone.id}>
            <TimelineSeparator>
              <TimelineDot color={getStatusColor(milestone.status)} />
              {index < milestones.length - 1 && <TimelineConnector />}
            </TimelineSeparator>
            <TimelineContent>
              <Box sx={{ mb: 2 }}>
                <Typography variant="subtitle1" component="div">
                  {milestone.title}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {milestone.description}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {milestone.date.toLocaleDateString()}
                </Typography>
              </Box>

              {milestone.decisionPoints.map((dp) => (
                <Box
                  key={dp.id}
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    mb: 1,
                  }}
                >
                  <Chip
                    label={dp.title}
                    size="small"
                    color={getDecisionPointColor(dp.status)}
                    variant="outlined"
                  />
                  <Chip
                    label={`Impact: ${dp.impact}`}
                    size="small"
                    variant="outlined"
                  />
                </Box>
              ))}
            </TimelineContent>
          </TimelineItem>
        ))}
      </Timeline>
    </Paper>
  );
};

export default ProjectTimeline; 