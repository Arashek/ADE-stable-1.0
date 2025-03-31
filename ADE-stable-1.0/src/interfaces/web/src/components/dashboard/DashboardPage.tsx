import React from 'react';
import { Grid, Box, Typography, useTheme, useMediaQuery } from '@mui/material';
import ActivitySummary from './ActivitySummary';
import ProjectsOverview from './ProjectsOverview';
import AgentStatusCard from './AgentStatusCard';
import RecentTasks from './RecentTasks';
import QuickActions from './QuickActions';
import Card from '../common/Card';

const DashboardPage: React.FC = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box sx={{ p: 3 }}>
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom>
          Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Welcome to your Autonomous Development Environment
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Quick Actions - Full width on mobile, 1/3 on desktop */}
        <Grid item xs={12} md={4}>
          <QuickActions />
        </Grid>

        {/* Activity Summary - Full width on mobile, 2/3 on desktop */}
        <Grid item xs={12} md={8}>
          <ActivitySummary />
        </Grid>

        {/* Projects Overview - Full width */}
        <Grid item xs={12}>
          <ProjectsOverview />
        </Grid>

        {/* Agent Status - Full width on mobile, 1/2 on desktop */}
        <Grid item xs={12} md={6}>
          <AgentStatusCard />
        </Grid>

        {/* Recent Tasks - Full width on mobile, 1/2 on desktop */}
        <Grid item xs={12} md={6}>
          <Card
            title="Recent Tasks"
            subtitle="Latest tasks and their status"
            sx={{ height: '100%' }}
          >
            <RecentTasks />
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default DashboardPage; 