import React, { useState } from 'react';
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
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Switch,
  FormControlLabel,
  Alert,
  Snackbar,
  Tooltip,
  Card,
  CardContent,
  Divider,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Collapse,
  Checkbox,
  Menu,
  FormGroup,
  FormLabel,
  FormHelperText,
  Badge,
  Avatar,
  Tabs,
  Tab,
  CardHeader,
  CardActions,
  TextField,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  LinearProgress,
  Slider,
  Typography as MuiTypography,
  Stack,
  ListItemIcon,
} from '@mui/material';
import {
  Settings as SettingsIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  History as HistoryIcon,
  Build as BuildIcon,
  Balance as BalanceIcon,
  Memory as MemoryIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  FilterList as FilterListIcon,
  MoreVert as MoreVertIcon,
  Block as BlockIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  AccessTime as AccessTimeIcon,
  Activity as ActivityIcon,
  Visibility as VisibilityIcon,
  VisibilityOff as VisibilityOffIcon,
  Key as KeyIcon,
  Audit as AuditIcon,
  Settings as SettingsIcon,
  Backup as BackupIcon,
  DeleteForever as DeleteForeverIcon,
  Shield as ShieldIcon,
  Speed as SpeedIcon,
  Storage as StorageIcon,
  NetworkCheck as NetworkCheckIcon,
  PlayArrow as PlayArrowIcon,
  Stop as StopIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useUser, RequirePermission } from '../../context/UserContext';

// Mock data - Replace with API calls
const mockComponents = [
  {
    id: 1,
    name: 'API Gateway',
    type: 'Gateway',
    status: 'Active',
    instances: 3,
    resources: {
      cpu: '2 cores',
      memory: '4GB',
      storage: '20GB',
    },
    lastModified: '2024-03-15',
  },
  {
    id: 2,
    name: 'User Service',
    type: 'Microservice',
    status: 'Active',
    instances: 5,
    resources: {
      cpu: '1 core',
      memory: '2GB',
      storage: '10GB',
    },
    lastModified: '2024-03-14',
  },
  {
    id: 3,
    name: 'Database',
    type: 'Database',
    status: 'Active',
    instances: 2,
    resources: {
      cpu: '4 cores',
      memory: '8GB',
      storage: '100GB',
    },
    lastModified: '2024-03-13',
  },
];

const mockLoadBalancers = [
  {
    id: 1,
    name: 'Main Load Balancer',
    algorithm: 'Round Robin',
    healthCheck: 'Active',
    instances: 2,
    lastModified: '2024-03-15',
  },
  {
    id: 2,
    name: 'API Load Balancer',
    algorithm: 'Least Connections',
    healthCheck: 'Active',
    instances: 3,
    lastModified: '2024-03-14',
  },
];

const mockResourcePools = [
  {
    id: 1,
    name: 'Production Pool',
    totalResources: {
      cpu: '16 cores',
      memory: '32GB',
      storage: '500GB',
    },
    allocatedResources: {
      cpu: '8 cores',
      memory: '16GB',
      storage: '200GB',
    },
    lastModified: '2024-03-15',
  },
  {
    id: 2,
    name: 'Development Pool',
    totalResources: {
      cpu: '8 cores',
      memory: '16GB',
      storage: '200GB',
    },
    allocatedResources: {
      cpu: '4 cores',
      memory: '8GB',
      storage: '100GB',
    },
    lastModified: '2024-03-14',
  },
];

// Add new mock data for monitoring
const mockMonitoringData = {
  metrics: {
    cpu: {
      current: 45,
      peak: 75,
      average: 55,
    },
    memory: {
      current: 60,
      peak: 85,
      average: 65,
    },
    network: {
      current: 120,
      peak: 200,
      average: 150,
    },
  },
  healthChecks: [
    {
      id: 1,
      name: 'API Gateway Health',
      status: 'Healthy',
      lastCheck: '2024-03-15 10:30:00',
      responseTime: 120,
      uptime: '99.9%',
    },
    {
      id: 2,
      name: 'Database Health',
      status: 'Healthy',
      lastCheck: '2024-03-15 10:30:00',
      responseTime: 80,
      uptime: '99.95%',
    },
    {
      id: 3,
      name: 'Cache Health',
      status: 'Warning',
      lastCheck: '2024-03-15 10:30:00',
      responseTime: 150,
      uptime: '99.8%',
    },
  ],
};

const ComponentManager = () => {
  const { user, logAuditEvent, hasPermission } = useUser();
  const [components, setComponents] = useState(mockComponents);
  const [loadBalancers, setLoadBalancers] = useState(mockLoadBalancers);
  const [resourcePools, setResourcePools] = useState(mockResourcePools);
  const [selectedComponent, setSelectedComponent] = useState(null);
  const [showComponentDialog, setShowComponentDialog] = useState(false);
  const [showLoadBalancerDialog, setShowLoadBalancerDialog] = useState(false);
  const [showResourceDialog, setShowResourceDialog] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [activeTab, setActiveTab] = useState(0);
  const [deploymentProgress, setDeploymentProgress] = useState(0);
  const [monitoringData, setMonitoringData] = useState(mockMonitoringData);
  const [showMonitoringDialog, setShowMonitoringDialog] = useState(false);
  const [selectedComponentForMonitoring, setSelectedComponentForMonitoring] = useState(null);
  const [timeRange, setTimeRange] = useState('24h');

  const handleEditComponent = (component) => {
    if (!hasPermission('architecture.components.edit')) {
      setNotification({
        open: true,
        message: 'You do not have permission to edit components',
        severity: 'error',
      });
      return;
    }
    setSelectedComponent(component);
    setShowComponentDialog(true);
    logAuditEvent('COMPONENT_EDIT_START', { componentId: component.id });
  };

  const handleSaveComponent = () => {
    if (!hasPermission('architecture.components.edit')) {
      setNotification({
        open: true,
        message: 'You do not have permission to save component changes',
        severity: 'error',
      });
      return;
    }

    if (selectedComponent) {
      setComponents(components.map(comp =>
        comp.id === selectedComponent.id ? selectedComponent : comp
      ));
      logAuditEvent('COMPONENT_UPDATE', {
        componentId: selectedComponent.id,
        changes: selectedComponent,
      });
    } else {
      const newComponent = {
        id: components.length + 1,
        ...selectedComponent,
      };
      setComponents([...components, newComponent]);
      logAuditEvent('COMPONENT_CREATE', { componentId: newComponent.id });
    }
    setShowComponentDialog(false);
    setSelectedComponent(null);
    setNotification({
      open: true,
      message: `Component ${selectedComponent ? 'updated' : 'created'} successfully`,
      severity: 'success',
    });
  };

  const handleDeployComponent = () => {
    if (!hasPermission('architecture.components.deploy')) {
      setNotification({
        open: true,
        message: 'You do not have permission to deploy components',
        severity: 'error',
      });
      return;
    }

    setSelectedComponent(components.find(c => c.id === selectedComponent.id));
    setDeploymentProgress(0);
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      setDeploymentProgress(progress);
      if (progress >= 100) {
        clearInterval(interval);
        setComponents(components.map(comp =>
          comp.id === selectedComponent.id ? { ...comp, status: 'Active' } : comp
        ));
        setNotification({
          open: true,
          message: 'Component deployed successfully',
          severity: 'success',
        });
        logAuditEvent('COMPONENT_DEPLOY_SUCCESS', { componentId: selectedComponent.id });
      }
    }, 500);
  };

  const handleDeleteComponent = (component) => {
    if (!hasPermission('architecture.components.delete')) {
      setNotification({
        open: true,
        message: 'You do not have permission to delete components',
        severity: 'error',
      });
      return;
    }

    setComponents(components.filter(comp => comp.id !== component.id));
    logAuditEvent('COMPONENT_DELETE', { componentId: component.id });
    setNotification({
      open: true,
      message: 'Component deleted successfully',
      severity: 'success',
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
        return 'success';
      case 'Inactive':
        return 'error';
      case 'Pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const calculateResourceUsage = (pool) => {
    const cpuUsage = (parseInt(pool.allocatedResources.cpu) / parseInt(pool.totalResources.cpu)) * 100;
    const memoryUsage = (parseInt(pool.allocatedResources.memory) / parseInt(pool.totalResources.memory)) * 100;
    const storageUsage = (parseInt(pool.allocatedResources.storage) / parseInt(pool.totalResources.storage)) * 100;
    return { cpuUsage, memoryUsage, storageUsage };
  };

  const handleMonitoringClick = (component) => {
    if (!hasPermission('architecture.components.monitor')) {
      setNotification({
        open: true,
        message: 'You do not have permission to view monitoring data',
        severity: 'error',
      });
      return;
    }

    setSelectedComponentForMonitoring(component);
    setShowMonitoringDialog(true);
    logAuditEvent('COMPONENT_MONITORING_VIEW', { componentId: component.id });
  };

  const handleTimeRangeChange = (event) => {
    setTimeRange(event.target.value);
    logAuditEvent('MONITORING_TIME_RANGE_CHANGE', {
      componentId: selectedComponentForMonitoring.id,
      timeRange: event.target.value,
    });
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Component Manager
      </Typography>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Components" />
          <Tab label="Load Balancing" />
          <Tab label="Resources" />
        </Tabs>
      </Paper>

      {/* Components Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <BuildIcon sx={{ mr: 1 }} />
                  Service Components
                </Typography>
                <RequirePermission permission="architecture.components.create">
                  <Button
                    variant="contained"
                    startIcon={<AddIcon />}
                    onClick={() => {
                      setSelectedComponent(null);
                      setShowComponentDialog(true);
                      logAuditEvent('COMPONENT_CREATE_START');
                    }}
                  >
                    Add Component
                  </Button>
                </RequirePermission>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Instances</TableCell>
                      <TableCell>Resources</TableCell>
                      <TableCell>Last Modified</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {components.map((component) => (
                      <TableRow key={component.id}>
                        <TableCell>{component.name}</TableCell>
                        <TableCell>{component.type}</TableCell>
                        <TableCell>
                          <Chip
                            label={component.status}
                            color={getStatusColor(component.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{component.instances}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                            <Typography variant="body2">CPU: {component.resources.cpu}</Typography>
                            <Typography variant="body2">Memory: {component.resources.memory}</Typography>
                            <Typography variant="body2">Storage: {component.resources.storage}</Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{component.lastModified}</TableCell>
                        <TableCell>
                          <Stack direction="row" spacing={1}>
                            <RequirePermission permission="architecture.components.edit">
                              <Tooltip title="Edit">
                                <IconButton
                                  size="small"
                                  onClick={() => handleEditComponent(component)}
                                >
                                  <EditIcon />
                                </IconButton>
                              </Tooltip>
                            </RequirePermission>
                            <RequirePermission permission="architecture.components.deploy">
                              <Tooltip title={component.status === 'Active' ? 'Stop' : 'Deploy'}>
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeployComponent()}
                                >
                                  {component.status === 'Active' ? <StopIcon /> : <PlayArrowIcon />}
                                </IconButton>
                              </Tooltip>
                            </RequirePermission>
                            <RequirePermission permission="architecture.components.monitor">
                              <Tooltip title="Monitor">
                                <IconButton
                                  size="small"
                                  onClick={() => handleMonitoringClick(component)}
                                >
                                  <RefreshIcon />
                                </IconButton>
                              </Tooltip>
                            </RequirePermission>
                            <RequirePermission permission="architecture.components.delete">
                              <Tooltip title="Delete">
                                <IconButton
                                  size="small"
                                  onClick={() => handleDeleteComponent(component)}
                                >
                                  <DeleteIcon />
                                </IconButton>
                              </Tooltip>
                            </RequirePermission>
                          </Stack>
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Load Balancing Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <BalanceIcon sx={{ mr: 1 }} />
                  Load Balancers
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setShowLoadBalancerDialog(true)}
                >
                  Add Load Balancer
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Algorithm</TableCell>
                      <TableCell>Health Check</TableCell>
                      <TableCell>Instances</TableCell>
                      <TableCell>Last Modified</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {loadBalancers.map((lb) => (
                      <TableRow key={lb.id}>
                        <TableCell>{lb.name}</TableCell>
                        <TableCell>{lb.algorithm}</TableCell>
                        <TableCell>
                          <Chip
                            label={lb.healthCheck}
                            color={getStatusColor(lb.healthCheck)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{lb.instances}</TableCell>
                        <TableCell>{lb.lastModified}</TableCell>
                        <TableCell>
                          <Tooltip title="Edit">
                            <IconButton>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Configure">
                            <IconButton>
                              <SettingsIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete">
                            <IconButton color="error">
                              <DeleteIcon />
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
        </Grid>
      )}

      {/* Resources Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <MemoryIcon sx={{ mr: 1 }} />
                  Resource Pools
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setShowResourceDialog(true)}
                >
                  Add Resource Pool
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Total Resources</TableCell>
                      <TableCell>Allocated Resources</TableCell>
                      <TableCell>Usage</TableCell>
                      <TableCell>Last Modified</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {resourcePools.map((pool) => {
                      const usage = calculateResourceUsage(pool);
                      return (
                        <TableRow key={pool.id}>
                          <TableCell>{pool.name}</TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                              <Typography variant="body2">CPU: {pool.totalResources.cpu}</Typography>
                              <Typography variant="body2">Memory: {pool.totalResources.memory}</Typography>
                              <Typography variant="body2">Storage: {pool.totalResources.storage}</Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                              <Typography variant="body2">CPU: {pool.allocatedResources.cpu}</Typography>
                              <Typography variant="body2">Memory: {pool.allocatedResources.memory}</Typography>
                              <Typography variant="body2">Storage: {pool.allocatedResources.storage}</Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                              <Box>
                                <Typography variant="body2">CPU</Typography>
                                <LinearProgress variant="determinate" value={usage.cpuUsage} />
                              </Box>
                              <Box>
                                <Typography variant="body2">Memory</Typography>
                                <LinearProgress variant="determinate" value={usage.memoryUsage} />
                              </Box>
                              <Box>
                                <Typography variant="body2">Storage</Typography>
                                <LinearProgress variant="determinate" value={usage.storageUsage} />
                              </Box>
                            </Box>
                          </TableCell>
                          <TableCell>{pool.lastModified}</TableCell>
                          <TableCell>
                            <Tooltip title="Edit">
                              <IconButton>
                                <EditIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Scale">
                              <IconButton>
                                <SpeedIcon />
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Delete">
                              <IconButton color="error">
                                <DeleteIcon />
                              </IconButton>
                            </Tooltip>
                          </TableCell>
                        </TableRow>
                      );
                    })}
                  </TableBody>
                </Table>
              </TableContainer>
            </Paper>
          </Grid>
        </Grid>
      )}

      {/* Component Dialog */}
      <Dialog open={showComponentDialog} onClose={() => setShowComponentDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <BuildIcon sx={{ mr: 1 }} />
          {selectedComponent ? 'Edit Component' : 'Add New Component'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                defaultValue={selectedComponent?.name}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select defaultValue={selectedComponent?.type}>
                  <MenuItem value="Gateway">Gateway</MenuItem>
                  <MenuItem value="Microservice">Microservice</MenuItem>
                  <MenuItem value="Database">Database</MenuItem>
                  <MenuItem value="Cache">Cache</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                type="number"
                label="Instances"
                defaultValue={selectedComponent?.instances}
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Resource Allocation
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="CPU Cores"
                    type="number"
                    defaultValue={selectedComponent?.resources.cpu.split(' ')[0]}
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="Memory (GB)"
                    type="number"
                    defaultValue={selectedComponent?.resources.memory.split(' ')[0]}
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="Storage (GB)"
                    type="number"
                    defaultValue={selectedComponent?.resources.storage.split(' ')[0]}
                  />
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowComponentDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveComponent} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Deployment Progress */}
      {deploymentProgress > 0 && (
        <Dialog open={deploymentProgress < 100} maxWidth="sm" fullWidth>
          <DialogTitle>Deploying Component</DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              <LinearProgress variant="determinate" value={deploymentProgress} />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {deploymentProgress}% complete
              </Typography>
            </Box>
          </DialogContent>
        </Dialog>
      )}

      {/* Add Monitoring Overview Card */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={4}>
          <Card>
            <CardHeader
              title="System Health Overview"
              avatar={<ActivityIcon />}
            />
            <CardContent>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {monitoringData.healthChecks.map((check) => (
                  <Box key={check.id} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Typography variant="body2">{check.name}</Typography>
                    <Chip
                      label={check.status}
                      color={check.status === 'Healthy' ? 'success' : check.status === 'Warning' ? 'warning' : 'error'}
                      size="small"
                    />
                  </Box>
                ))}
              </Box>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader
              title="Resource Usage"
              avatar={<MemoryIcon />}
              action={
                <FormControl size="small">
                  <Select value={timeRange} onChange={handleTimeRangeChange}>
                    <MenuItem value="1h">Last Hour</MenuItem>
                    <MenuItem value="24h">Last 24 Hours</MenuItem>
                    <MenuItem value="7d">Last 7 Days</MenuItem>
                  </Select>
                </FormControl>
              }
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Box>
                    <Typography variant="body2">CPU Usage</Typography>
                    <LinearProgress variant="determinate" value={monitoringData.metrics.cpu.current} />
                    <Typography variant="caption" color="text.secondary">
                      {monitoringData.metrics.cpu.current}% (Peak: {monitoringData.metrics.cpu.peak}%)
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box>
                    <Typography variant="body2">Memory Usage</Typography>
                    <LinearProgress variant="determinate" value={monitoringData.metrics.memory.current} />
                    <Typography variant="caption" color="text.secondary">
                      {monitoringData.metrics.memory.current}% (Peak: {monitoringData.metrics.memory.peak}%)
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box>
                    <Typography variant="body2">Network Usage</Typography>
                    <LinearProgress variant="determinate" value={monitoringData.metrics.network.current} />
                    <Typography variant="caption" color="text.secondary">
                      {monitoringData.metrics.network.current} MB/s (Peak: {monitoringData.metrics.network.peak} MB/s)
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Add Monitoring Dialog */}
      <Dialog open={showMonitoringDialog} onClose={() => setShowMonitoringDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <ActivityIcon sx={{ mr: 1 }} />
          Component Monitoring: {selectedComponentForMonitoring?.name}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Health Status
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                <Chip
                  label="Status"
                  color={selectedComponentForMonitoring?.status === 'Active' ? 'success' : 'error'}
                  size="small"
                />
                <Chip
                  label={`Uptime: ${monitoringData.healthChecks[0].uptime}`}
                  color="primary"
                  size="small"
                />
                <Chip
                  label={`Response Time: ${monitoringData.healthChecks[0].responseTime}ms`}
                  color="info"
                  size="small"
                />
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Resource Usage History
              </Typography>
              <Box sx={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">
                  Resource usage history chart will be displayed here
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Recent Events
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="Component Started"
                    secondary="2024-03-15 10:00:00"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Configuration Updated"
                    secondary="2024-03-15 09:30:00"
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Health Check Passed"
                    secondary="2024-03-15 09:00:00"
                  />
                </ListItem>
              </List>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowMonitoringDialog(false)}>Close</Button>
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

export default ComponentManager; 