import React from 'react';
import { Box, Grid, Paper, Typography } from '@mui/material';
import {
  Extension as ExtensionIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  Assessment as AssessmentIcon,
} from '@mui/icons-material';

const Home: React.FC = () => {
  const features = [
    {
      title: 'Model Management',
      description: 'Monitor and manage your AI models with comprehensive metrics and controls.',
      icon: <ExtensionIcon sx={{ fontSize: 40 }} />,
      path: '/models',
    },
    {
      title: 'Performance Analytics',
      description: 'Track model performance, resource usage, and efficiency metrics.',
      icon: <SpeedIcon sx={{ fontSize: 40 }} />,
      path: '/analytics',
    },
    {
      title: 'Security & Compliance',
      description: 'Ensure your models meet security standards and compliance requirements.',
      icon: <SecurityIcon sx={{ fontSize: 40 }} />,
      path: '/security',
    },
    {
      title: 'Quality Assurance',
      description: 'Monitor and improve model quality through comprehensive testing.',
      icon: <AssessmentIcon sx={{ fontSize: 40 }} />,
      path: '/quality',
    },
  ];

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Welcome to ADE Platform
      </Typography>
      <Typography variant="subtitle1" color="text.secondary" paragraph>
        Your comprehensive solution for managing and monitoring AI models.
      </Typography>
      <Grid container spacing={3}>
        {features.map((feature) => (
          <Grid item xs={12} sm={6} md={3} key={feature.title}>
            <Paper
              sx={{
                p: 3,
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                textAlign: 'center',
                cursor: 'pointer',
                '&:hover': {
                  backgroundColor: 'action.hover',
                },
              }}
              onClick={() => window.location.href = feature.path}
            >
              <Box sx={{ color: 'primary.main', mb: 2 }}>
                {feature.icon}
              </Box>
              <Typography variant="h6" gutterBottom>
                {feature.title}
              </Typography>
              <Typography variant="body2" color="text.secondary">
                {feature.description}
              </Typography>
            </Paper>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default Home; 