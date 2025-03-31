import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  IconButton,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar,
  Tooltip,
  Chip,
  Card,
  CardContent,
  CardHeader,
  CardActions,
  Tabs,
  Tab,
  Badge,
  CircularProgress,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  LinearProgress,
  ListItemIcon,
  ListItemButton,
  ListItemAvatar,
  Avatar,
} from '@mui/material';
import {
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Schedule as ScheduleIcon,
  History as HistoryIcon,
  Warning as WarningIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  CloudUpload as CloudUploadIcon,
  CloudDownload as CloudDownloadIcon,
  Build as BuildIcon,
  Security as SecurityIcon,
  Speed as SpeedIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  BugReport as BugReportIcon,
  Memory as MemoryIcon,
  Storage as StorageIcon,
  NetworkCheck as NetworkCheckIcon,
  Settings as SettingsIcon,
  CompareArrows as CompareArrowsIcon,
} from '@mui/icons-material';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';

// Mock data - Replace with API calls
const mockServices = [
  {
    id: 1,
    name: 'API Gateway',
    version: '1.2.3',
    status: 'Running',
    lastDeployed: '2024-03-15 14:30:00',
    health: 'Healthy',
    instances: 3,
  },
  {
    id: 2,
    name: 'User Service',
    version: '2.1.0',
    status: 'Stopped',
    lastDeployed: '2024-03-14 09:15:00',
    health: 'Degraded',
    instances: 2,
  },
  // Add more mock services...
];

const mockDeployments = [
  {
    id: 1,
    service: 'API Gateway',
    version: '1.2.3',
    status: 'Completed',
    timestamp: '2024-03-15 14:30:00',
    duration: '2m 30s',
    result: 'Success',
  },
  // Add more mock deployments...
];

const mockMaintenance = [
  {
    id: 1,
    service: 'User Service',
    type: 'Scheduled',
    startTime: '2024-03-20 02:00:00',
    endTime: '2024-03-20 04:00:00',
    status: 'Scheduled',
    description: 'Database migration',
  },
  // Add more mock maintenance...
];

const mockAnalytics = {
  deploymentSuccess: 95,
  averageDeploymentTime: '2m 30s',
  rollbackRate: 2.5,
  serviceHealth: {
    apiGateway: { status: 'healthy', uptime: 99.9, latency: 120 },
    userService: { status: 'degraded', uptime: 99.5, latency: 250 },
    authService: { status: 'healthy', uptime: 99.8, latency: 150 },
  },
  resourceUsage: {
    cpu: 65,
    memory: 75,
    disk: 45,
    network: 30,
  },
};

const DeploymentManager = () => {
  const [services, setServices] = useState(mockServices);
  const [deployments, setDeployments] = useState(mockDeployments);
  const [maintenance, setMaintenance] = useState(mockMaintenance);
  const [selectedService, setSelectedService] = useState(null);
  const [showDeployDialog, setShowDeployDialog] = useState(false);
  const [showMaintenanceDialog, setShowMaintenanceDialog] = useState(false);
  const [showHistoryDialog, setShowHistoryDialog] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [activeStep, setActiveStep] = useState(-1);
  const [deploymentStatus, setDeploymentStatus] = useState('idle');
  const [maintenanceSchedule, setMaintenanceSchedule] = useState({
    service: '',
    type: 'Scheduled',
    startTime: new Date(),
    endTime: new Date(),
    description: '',
  });
  const [activeTab, setActiveTab] = useState(0);
  const [analytics, setAnalytics] = useState(mockAnalytics);
  const [showHealthDialog, setShowHealthDialog] = useState(false);
  const [showCompareDialog, setShowCompareDialog] = useState(false);
  const [selectedVersions, setSelectedVersions] = useState([]);
  const [healthCheckResults, setHealthCheckResults] = useState([]);

  const handleDeploy = (service) => {
    setSelectedService(service);
    setShowDeployDialog(true);
  };

  const handleScheduleMaintenance = (service) => {
    setSelectedService(service);
    setMaintenanceSchedule({
      ...maintenanceSchedule,
      service: service.name,
    });
    setShowMaintenanceDialog(true);
  };

  const handleStartDeployment = () => {
    setDeploymentStatus('in_progress');
    setActiveStep(0);
    // Simulate deployment steps
    const steps = ['Preparing', 'Building', 'Testing', 'Deploying'];
    steps.forEach((step, index) => {
      setTimeout(() => {
        setActiveStep(index + 1);
        if (index === steps.length - 1) {
          setDeploymentStatus('completed');
          setShowDeployDialog(false);
          setNotification({
            open: true,
            message: 'Deployment completed successfully',
            severity: 'success',
          });
        }
      }, 2000);
    });
  };

  const handleSaveMaintenance = () => {
    // Implement save logic
    setShowMaintenanceDialog(false);
    setNotification({
      open: true,
      message: 'Maintenance scheduled successfully',
      severity: 'success',
    });
  };

  const handleHealthCheck = async (service) => {
    // Simulate health check
    setHealthCheckResults([
      { check: 'Database Connection', status: 'success', message: 'Connected successfully' },
      { check: 'API Endpoints', status: 'success', message: 'All endpoints responding' },
      { check: 'Cache Service', status: 'warning', message: 'High latency detected' },
    ]);
    setShowHealthDialog(true);
  };

  const handleCompareVersions = (service) => {
    setSelectedService(service);
    setShowCompareDialog(true);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Running':
      case 'Completed':
      case 'Success':
        return 'success';
      case 'Stopped':
      case 'Failed':
        return 'error';
      case 'Degraded':
        return 'warning';
      case 'Scheduled':
        return 'info';
      default:
        return 'default';
    }
  };

  const getHealthStatusColor = (status) => {
    switch (status) {
      case 'healthy':
        return 'success';
      case 'degraded':
        return 'warning';
      case 'unhealthy':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Deployment Manager
      </Typography>

      {/* Analytics Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <CheckCircleIcon color="success" sx={{ mr: 1 }} />
                <Typography variant="h6">Deployment Success</Typography>
              </Box>
              <Typography variant="h4">{analytics.deploymentSuccess}%</Typography>
              <Typography variant="body2" color="text.secondary">
                Last 30 days
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <SpeedIcon color="primary" sx={{ mr: 1 }} />
                <Typography variant="h6">Avg. Deployment Time</Typography>
              </Box>
              <Typography variant="h4">{analytics.averageDeploymentTime}</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <TimelineIcon color="warning" sx={{ mr: 1 }} />
                <Typography variant="h6">Rollback Rate</Typography>
              </Box>
              <Typography variant="h4">{analytics.rollbackRate}%</Typography>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                <AssessmentIcon color="info" sx={{ mr: 1 }} />
                <Typography variant="h6">Services Health</Typography>
              </Box>
              <Typography variant="h4">
                {Object.values(analytics.serviceHealth).filter(s => s.status === 'healthy').length}/
                {Object.keys(analytics.serviceHealth).length}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Services" />
          <Tab label="Deployments" />
          <Tab label="Health" />
          <Tab label="Analytics" />
        </Tabs>
      </Paper>

      {/* Services Overview */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                <BuildIcon sx={{ mr: 1 }} />
                Services
              </Typography>
              <Box>
                <Button
                  variant="outlined"
                  startIcon={<CompareArrowsIcon />}
                  onClick={() => setShowCompareDialog(true)}
                  sx={{ mr: 1 }}
                >
                  Compare Versions
                </Button>
                <Button
                  variant="contained"
                  startIcon={<CloudUploadIcon />}
                  onClick={() => setShowDeployDialog(true)}
                >
                  Deploy New Version
                </Button>
              </Box>
            </Box>
            <TableContainer>
              <Table>
                <TableHead>
                  <TableRow>
                    <TableCell>Service</TableCell>
                    <TableCell>Version</TableCell>
                    <TableCell>Status</TableCell>
                    <TableCell>Health</TableCell>
                    <TableCell>Resources</TableCell>
                    <TableCell>Last Deployed</TableCell>
                    <TableCell>Actions</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {services.map((service) => (
                    <TableRow key={service.id}>
                      <TableCell>
                        <Box sx={{ display: 'flex', alignItems: 'center' }}>
                          <Avatar sx={{ mr: 1, bgcolor: 'primary.main' }}>
                            {service.name[0]}
                          </Avatar>
                          {service.name}
                        </Box>
                      </TableCell>
                      <TableCell>{service.version}</TableCell>
                      <TableCell>
                        <Chip
                          label={service.status}
                          color={getStatusColor(service.status)}
                          size="small"
                        />
                      </TableCell>
                      <TableCell>
                        <Chip
                          label={service.health}
                          color={getStatusColor(service.health)}
                          size="small"
                          onClick={() => handleHealthCheck(service)}
                          sx={{ cursor: 'pointer' }}
                        />
                      </TableCell>
                      <TableCell>
                        <Box sx={{ display: 'flex', gap: 1 }}>
                          <Tooltip title="CPU Usage">
                            <Chip
                              icon={<MemoryIcon />}
                              label={`${analytics.resourceUsage.cpu}%`}
                              size="small"
                            />
                          </Tooltip>
                          <Tooltip title="Memory Usage">
                            <Chip
                              icon={<StorageIcon />}
                              label={`${analytics.resourceUsage.memory}%`}
                              size="small"
                            />
                          </Tooltip>
                        </Box>
                      </TableCell>
                      <TableCell>{service.lastDeployed}</TableCell>
                      <TableCell>
                        <Tooltip title="Deploy">
                          <IconButton onClick={() => handleDeploy(service)}>
                            <CloudUploadIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Health Check">
                          <IconButton onClick={() => handleHealthCheck(service)}>
                            <BugReportIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Schedule Maintenance">
                          <IconButton onClick={() => handleScheduleMaintenance(service)}>
                            <ScheduleIcon />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="View History">
                          <IconButton onClick={() => setShowHistoryDialog(true)}>
                            <HistoryIcon />
                          </IconButton>
                        </Tooltip>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </TableContainer>
          </Paper>
        </Grid>

        {/* Health Monitoring */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                <BugReportIcon sx={{ mr: 1 }} />
                Health Monitoring
              </Typography>
              <Button
                variant="outlined"
                startIcon={<RefreshIcon />}
                onClick={() => {/* Refresh health data */}}
              >
                Refresh
              </Button>
            </Box>
            <List>
              {Object.entries(analytics.serviceHealth).map(([service, health]) => (
                <ListItem key={service}>
                  <ListItemAvatar>
                    <Avatar sx={{ bgcolor: `${getHealthStatusColor(health.status)}.main` }}>
                      {service[0]}
                    </Avatar>
                  </ListItemAvatar>
                  <ListItemText
                    primary={service}
                    secondary={
                      <>
                        <Typography variant="body2" color="text.secondary">
                          Uptime: {health.uptime}% | Latency: {health.latency}ms
                        </Typography>
                        <LinearProgress
                          variant="determinate"
                          value={health.uptime}
                          color={getHealthStatusColor(health.status)}
                          sx={{ mt: 1 }}
                        />
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* Health Check Dialog */}
      <Dialog open={showHealthDialog} onClose={() => setShowHealthDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <BugReportIcon sx={{ mr: 1 }} />
          Health Check Results
        </DialogTitle>
        <DialogContent>
          <List>
            {healthCheckResults.map((result, index) => (
              <ListItem key={index}>
                <ListItemIcon>
                  {result.status === 'success' ? (
                    <CheckCircleIcon color="success" />
                  ) : result.status === 'warning' ? (
                    <WarningIcon color="warning" />
                  ) : (
                    <ErrorIcon color="error" />
                  )}
                </ListItemIcon>
                <ListItemText
                  primary={result.check}
                  secondary={result.message}
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHealthDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Version Comparison Dialog */}
      <Dialog open={showCompareDialog} onClose={() => setShowCompareDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <CompareArrowsIcon sx={{ mr: 1 }} />
          Version Comparison
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Current Version</InputLabel>
                <Select
                  value={selectedVersions[0] || ''}
                  onChange={(e) => setSelectedVersions([e.target.value, selectedVersions[1]])}
                >
                  {services.map((service) => (
                    <MenuItem key={service.id} value={service.version}>
                      {service.version}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Target Version</InputLabel>
                <Select
                  value={selectedVersions[1] || ''}
                  onChange={(e) => setSelectedVersions([selectedVersions[0], e.target.value])}
                >
                  {services.map((service) => (
                    <MenuItem key={service.id} value={service.version}>
                      {service.version}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Paper sx={{ p: 2, mt: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Changes
                </Typography>
                <List>
                  <ListItem>
                    <ListItemText
                      primary="Breaking Changes"
                      secondary="None"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="New Features"
                      secondary="Improved error handling, New API endpoints"
                    />
                  </ListItem>
                  <ListItem>
                    <ListItemText
                      primary="Bug Fixes"
                      secondary="Fixed memory leak in worker process"
                    />
                  </ListItem>
                </List>
              </Paper>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowCompareDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Deployment Dialog */}
      <Dialog open={showDeployDialog} onClose={() => setShowDeployDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <CloudUploadIcon sx={{ mr: 1 }} />
          Deploy New Version
        </DialogTitle>
        <DialogContent>
          <Stepper activeStep={activeStep} orientation="vertical">
            <Step>
              <StepLabel>Prepare Deployment</StepLabel>
              <StepContent>
                <Grid container spacing={2} sx={{ mt: 1 }}>
                  <Grid item xs={12}>
                    <FormControl fullWidth>
                      <InputLabel>Service</InputLabel>
                      <Select defaultValue={selectedService?.name}>
                        {services.map((service) => (
                          <MenuItem key={service.id} value={service.name}>
                            {service.name}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Version"
                      placeholder="e.g., 1.2.4"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Release Notes"
                      multiline
                      rows={4}
                    />
                  </Grid>
                </Grid>
              </StepContent>
            </Step>
            <Step>
              <StepLabel>Build</StepLabel>
              <StepContent>
                <Box sx={{ mt: 2 }}>
                  <LinearProgress />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Building service package...
                  </Typography>
                </Box>
              </StepContent>
            </Step>
            <Step>
              <StepLabel>Test</StepLabel>
              <StepContent>
                <Box sx={{ mt: 2 }}>
                  <LinearProgress />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Running automated tests...
                  </Typography>
                </Box>
              </StepContent>
            </Step>
            <Step>
              <StepLabel>Deploy</StepLabel>
              <StepContent>
                <Box sx={{ mt: 2 }}>
                  <LinearProgress />
                  <Typography variant="body2" sx={{ mt: 1 }}>
                    Deploying to production...
                  </Typography>
                </Box>
              </StepContent>
            </Step>
          </Stepper>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowDeployDialog(false)}>Cancel</Button>
          <Button
            onClick={handleStartDeployment}
            variant="contained"
            disabled={deploymentStatus === 'in_progress'}
          >
            {deploymentStatus === 'in_progress' ? 'Deploying...' : 'Start Deployment'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Maintenance Schedule Dialog */}
      <Dialog open={showMaintenanceDialog} onClose={() => setShowMaintenanceDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <ScheduleIcon sx={{ mr: 1 }} />
          Schedule Maintenance
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Service</InputLabel>
                <Select
                  value={maintenanceSchedule.service}
                  onChange={(e) => setMaintenanceSchedule({ ...maintenanceSchedule, service: e.target.value })}
                >
                  {services.map((service) => (
                    <MenuItem key={service.id} value={service.name}>
                      {service.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={maintenanceSchedule.type}
                  onChange={(e) => setMaintenanceSchedule({ ...maintenanceSchedule, type: e.target.value })}
                >
                  <MenuItem value="Scheduled">Scheduled</MenuItem>
                  <MenuItem value="Emergency">Emergency</MenuItem>
                  <MenuItem value="Routine">Routine</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateTimePicker
                  label="Start Time"
                  value={maintenanceSchedule.startTime}
                  onChange={(newValue) => setMaintenanceSchedule({ ...maintenanceSchedule, startTime: newValue })}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </LocalizationProvider>
            </Grid>
            <Grid item xs={12}>
              <LocalizationProvider dateAdapter={AdapterDateFns}>
                <DateTimePicker
                  label="End Time"
                  value={maintenanceSchedule.endTime}
                  onChange={(newValue) => setMaintenanceSchedule({ ...maintenanceSchedule, endTime: newValue })}
                  renderInput={(params) => <TextField {...params} fullWidth />}
                />
              </LocalizationProvider>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Description"
                multiline
                rows={4}
                value={maintenanceSchedule.description}
                onChange={(e) => setMaintenanceSchedule({ ...maintenanceSchedule, description: e.target.value })}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowMaintenanceDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveMaintenance} variant="contained">
            Schedule
          </Button>
        </DialogActions>
      </Dialog>

      {/* History Dialog */}
      <Dialog open={showHistoryDialog} onClose={() => setShowHistoryDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <HistoryIcon sx={{ mr: 1 }} />
          Deployment History
        </DialogTitle>
        <DialogContent>
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Service</TableCell>
                  <TableCell>Version</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell>Timestamp</TableCell>
                  <TableCell>Duration</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {deployments.map((deployment) => (
                  <TableRow key={deployment.id}>
                    <TableCell>{deployment.service}</TableCell>
                    <TableCell>{deployment.version}</TableCell>
                    <TableCell>
                      <Chip
                        label={deployment.result}
                        color={getStatusColor(deployment.result)}
                        size="small"
                      />
                    </TableCell>
                    <TableCell>{deployment.timestamp}</TableCell>
                    <TableCell>{deployment.duration}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHistoryDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Box>
  );
};

export default DeploymentManager; 