import React from 'react';
import { Box, Grid, Paper, Typography, Button } from '@mui/material';
import { useNavigate } from 'react-router-dom';
import {
  Extension as ExtensionIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  Assessment as AssessmentIcon,
  Dashboard as DashboardIcon,
} from '@mui/icons-material';

const Home: React.FC = () => {
  const navigate = useNavigate();
  
  const features = [
    {
      title: 'Command Hub',
      description: 'Access the command center with design tools and AI assistants.',
      icon: <DashboardIcon sx={{ fontSize: 40 }} />,
      path: '/command-hub',
      primary: true,
    },
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
      
      {/* Prominent Command Hub Button */}
      <Box sx={{ mb: 4, mt: 2, display: 'flex', justifyContent: 'center' }}>
        <Button
          variant="contained"
          color="primary"
          size="large"
          startIcon={<DashboardIcon />}
          onClick={() => navigate('/command-hub')}
          sx={{ py: 1.5, px: 4, fontSize: '1.1rem' }}
        >
          Open Command Hub
        </Button>
      </Box>
      
      <Grid container spacing={3}>
        {features.map((feature) => (
          <Grid item xs={12} sm={6} md={feature.primary ? 12 : 3} key={feature.title}>
            <Paper
              sx={{
                p: 3,
                display: 'flex',
                flexDirection: 'column',
                height: '100%',
                cursor: 'pointer',
                transition: 'transform 0.2s, box-shadow 0.2s',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: 4,
                },
                ...(feature.primary && {
                  bgcolor: 'primary.light',
                  color: 'primary.contrastText',
                }),
              }}
              onClick={() => navigate(feature.path)}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  mb: 2,
                  color: feature.primary ? 'inherit' : 'primary.main',
                }}
              >
                {feature.icon}
                <Typography variant="h6" sx={{ ml: 1 }}>
                  {feature.title}
                </Typography>
              </Box>
              <Typography variant="body2" color={feature.primary ? 'inherit' : 'text.secondary'}>
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