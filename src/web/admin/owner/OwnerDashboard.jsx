import React, { useState } from 'react';
import { 
  Box, 
  Grid, 
  Paper, 
  Typography, 
  useTheme, 
  useMediaQuery,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  IconButton,
  Tooltip,
  Badge,
  LinearProgress,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Assessment as AssessmentIcon,
  Warning as WarningIcon,
  Timeline as TimelineIcon,
  People as PeopleIcon,
  Storage as StorageIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  Settings as SettingsIcon,
  Notifications as NotificationsIcon,
  Refresh as RefreshIcon,
  TrendingUp as TrendingUpIcon,
  Memory as MemoryIcon,
  Cloud as CloudIcon,
} from '@mui/icons-material';

// Enhanced MetricsSummary component with more specific KPIs
const MetricsSummary = () => (
  <Paper sx={{ p: 2, height: '100%' }}>
    <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
      <Typography variant="h6">
        <AssessmentIcon sx={{ mr: 1 }} />
        Key Performance Indicators
      </Typography>
      <Tooltip title="Refresh metrics">
        <IconButton size="small">
          <RefreshIcon />
        </IconButton>
      </Tooltip>
    </Box>
    <Grid container spacing={2}>
      {/* User Metrics */}
      <Grid item xs={12} sm={6} md={3}>
        <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
          <PeopleIcon color="primary" sx={{ mb: 1 }} />
          <Typography variant="h4">1,234</Typography>
          <Typography variant="body2" color="text.secondary">Total Users</Typography>
          <Typography variant="caption" color="success.main">
            +12% from last month
          </Typography>
        </Paper>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
          <SpeedIcon color="primary" sx={{ mb: 1 }} />
          <Typography variant="h4">98.5%</Typography>
          <Typography variant="body2" color="text.secondary">System Uptime</Typography>
          <Typography variant="caption" color="success.main">
            Last 30 days
          </Typography>
        </Paper>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
          <MemoryIcon color="primary" sx={{ mb: 1 }} />
          <Typography variant="h4">45%</Typography>
          <Typography variant="body2" color="text.secondary">CPU Usage</Typography>
          <LinearProgress 
            variant="determinate" 
            value={45} 
            sx={{ mt: 1 }}
            color={45 > 80 ? "error" : 45 > 60 ? "warning" : "success"}
          />
        </Paper>
      </Grid>
      <Grid item xs={12} sm={6} md={3}>
        <Paper variant="outlined" sx={{ p: 2, textAlign: 'center' }}>
          <StorageIcon color="primary" sx={{ mb: 1 }} />
          <Typography variant="h4">2.3 TB</Typography>
          <Typography variant="body2" color="text.secondary">Storage Used</Typography>
          <LinearProgress 
            variant="determinate" 
            value={65} 
            sx={{ mt: 1 }}
            color={65 > 80 ? "error" : 65 > 60 ? "warning" : "success"}
          />
        </Paper>
      </Grid>
    </Grid>
  </Paper>
);

// Enhanced SystemHealth component with more detailed status
const SystemHealth = () => (
  <Paper sx={{ p: 2, height: '100%' }}>
    <Typography variant="h6" gutterBottom>
      <WarningIcon sx={{ mr: 1 }} />
      System Health Status
    </Typography>
    <List>
      <ListItem>
        <ListItemIcon>
          <CloudIcon color="success" />
        </ListItemIcon>
        <ListItemText 
          primary="API Service" 
          secondary="All endpoints responding normally"
        />
      </ListItem>
      <ListItem>
        <ListItemIcon>
          <StorageIcon color="success" />
        </ListItemIcon>
        <ListItemText 
          primary="Database" 
          secondary="Connected and optimized"
        />
      </ListItem>
      <ListItem>
        <ListItemIcon>
          <SecurityIcon color="warning" />
        </ListItemIcon>
        <ListItemText 
          primary="Security" 
          secondary="2 failed login attempts detected"
        />
      </ListItem>
      <ListItem>
        <ListItemIcon>
          <SpeedIcon color="success" />
        </ListItemIcon>
        <ListItemText 
          primary="Performance" 
          secondary="Average response time: 120ms"
        />
      </ListItem>
    </List>
  </Paper>
);

// Enhanced UsageAnalytics component with placeholder charts
const UsageAnalytics = () => (
  <Paper sx={{ p: 2, height: '100%' }}>
    <Typography variant="h6" gutterBottom>
      <TimelineIcon sx={{ mr: 1 }} />
      Usage Analytics
    </Typography>
    <Box sx={{ mt: 2, height: '200px', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
      <Typography variant="body1" color="text.secondary">
        Analytics charts will be implemented here
      </Typography>
    </Box>
  </Paper>
);

// Enhanced Sidebar with navigation items
const Sidebar = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [selectedItem, setSelectedItem] = useState('dashboard');

  if (isMobile) return null;

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: <DashboardIcon /> },
    { id: 'users', label: 'User Management', icon: <PeopleIcon /> },
    { id: 'analytics', label: 'Analytics', icon: <TrendingUpIcon /> },
    { id: 'system', label: 'System Settings', icon: <SettingsIcon /> },
  ];

  return (
    <Paper sx={{ p: 2, height: '100%', minHeight: 'calc(100vh - 64px)' }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <DashboardIcon sx={{ mr: 1 }} />
          Admin Panel
        </Typography>
        <Box sx={{ flexGrow: 1 }} />
        <Tooltip title="Notifications">
          <IconButton size="small">
            <Badge badgeContent={3} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
        </Tooltip>
      </Box>
      <Divider sx={{ mb: 2 }} />
      <List>
        {menuItems.map((item) => (
          <ListItem key={item.id} disablePadding>
            <ListItemButton
              selected={selectedItem === item.id}
              onClick={() => setSelectedItem(item.id)}
            >
              <ListItemIcon>{item.icon}</ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItemButton>
          </ListItem>
        ))}
      </List>
    </Paper>
  );
};

const OwnerDashboard = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  return (
    <Box sx={{ flexGrow: 1, p: 3 }}>
      <Grid container spacing={3}>
        {/* Sidebar */}
        <Grid item xs={12} md={2}>
          <Sidebar />
        </Grid>

        {/* Main Content */}
        <Grid item xs={12} md={10}>
          <Grid container spacing={3}>
            {/* Metrics Summary */}
            <Grid item xs={12}>
              <MetricsSummary />
            </Grid>

            {/* System Health */}
            <Grid item xs={12} md={6}>
              <SystemHealth />
            </Grid>

            {/* Usage Analytics */}
            <Grid item xs={12} md={6}>
              <UsageAnalytics />
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Box>
  );
};

export default OwnerDashboard; 