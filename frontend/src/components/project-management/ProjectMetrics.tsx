import React from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
} from '@mui/material';
import {
  Assignment as TaskIcon,
  Timeline as SprintIcon,
  Assessment as MetricsIcon,
  Speed as VelocityIcon,
  TrendingUp as ProgressIcon,
} from '@mui/icons-material';

interface ProjectMetricsProps {
  metrics: {
    total_tasks: number;
    completed_tasks: number;
    total_sprints: number;
    completed_sprints: number;
    total_story_points: number;
    completed_story_points: number;
    average_velocity: number;
  };
}

const ProjectMetrics: React.FC<ProjectMetricsProps> = ({ metrics }) => {
  const taskCompletionRate = (metrics.completed_tasks / metrics.total_tasks) * 100;
  const sprintCompletionRate = (metrics.completed_sprints / metrics.total_sprints) * 100;
  const storyPointsCompletionRate = (metrics.completed_story_points / metrics.total_story_points) * 100;

  const MetricCard: React.FC<{
    title: string;
    value: number | string;
    icon: React.ReactNode;
    progress?: number;
  }> = ({ title, value, icon, progress }) => (
    <Paper sx={{ p: 2, height: '100%' }}>
      <Box display="flex" alignItems="center" mb={2}>
        <ListItemIcon>{icon}</ListItemIcon>
        <Typography variant="h6">{title}</Typography>
      </Box>
      <Typography variant="h4" gutterBottom>
        {value}
      </Typography>
      {progress !== undefined && (
        <Box mt={2}>
          <LinearProgress
            variant="determinate"
            value={progress}
            sx={{ height: 8, borderRadius: 4 }}
          />
          <Typography variant="caption" color="textSecondary">
            {progress.toFixed(1)}% Complete
          </Typography>
        </Box>
      )}
    </Paper>
  );

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Project Analytics
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12} md={6} lg={3}>
          <MetricCard
            title="Tasks"
            value={`${metrics.completed_tasks}/${metrics.total_tasks}`}
            icon={<TaskIcon />}
            progress={taskCompletionRate}
          />
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <MetricCard
            title="Sprints"
            value={`${metrics.completed_sprints}/${metrics.total_sprints}`}
            icon={<SprintIcon />}
            progress={sprintCompletionRate}
          />
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <MetricCard
            title="Story Points"
            value={`${metrics.completed_story_points}/${metrics.total_story_points}`}
            icon={<ProgressIcon />}
            progress={storyPointsCompletionRate}
          />
        </Grid>
        <Grid item xs={12} md={6} lg={3}>
          <MetricCard
            title="Velocity"
            value={`${metrics.average_velocity.toFixed(1)}`}
            icon={<VelocityIcon />}
          />
        </Grid>
      </Grid>

      <Box mt={4}>
        <Typography variant="h6" gutterBottom>
          Performance Insights
        </Typography>
        <List>
          <ListItem>
            <ListItemIcon>
              <TaskIcon />
            </ListItemIcon>
            <ListItemText
              primary="Task Completion Rate"
              secondary={`${taskCompletionRate.toFixed(1)}% of tasks completed`}
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <SprintIcon />
            </ListItemIcon>
            <ListItemText
              primary="Sprint Completion Rate"
              secondary={`${sprintCompletionRate.toFixed(1)}% of sprints completed`}
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <ProgressIcon />
            </ListItemIcon>
            <ListItemText
              primary="Story Points Progress"
              secondary={`${storyPointsCompletionRate.toFixed(1)}% of story points completed`}
            />
          </ListItem>
          <ListItem>
            <ListItemIcon>
              <VelocityIcon />
            </ListItemIcon>
            <ListItemText
              primary="Team Velocity"
              secondary={`Average of ${metrics.average_velocity.toFixed(1)} story points per sprint`}
            />
          </ListItem>
        </List>
      </Box>
    </Box>
  );
};

export default ProjectMetrics; 