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
  Chip,
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
  Psychology as PsychologyIcon,
  Route as RouteIcon,
  Code as CodeIcon,
  Extension as ExtensionIcon,
} from '@mui/icons-material';

// Mock data - Replace with API calls
const mockModels = [
  {
    id: 1,
    name: 'GPT-4',
    version: '1.0.0',
    status: 'Active',
    capabilities: ['Text Generation', 'Code Completion', 'Analysis'],
    performance: {
      accuracy: 95,
      latency: 200,
      throughput: 1000,
    },
    lastModified: '2024-03-15',
  },
  {
    id: 2,
    name: 'DALL-E 3',
    version: '2.1.0',
    status: 'Active',
    capabilities: ['Image Generation', 'Image Editing', 'Style Transfer'],
    performance: {
      accuracy: 92,
      latency: 500,
      throughput: 500,
    },
    lastModified: '2024-03-14',
  },
  {
    id: 3,
    name: 'Whisper',
    version: '1.5.0',
    status: 'Active',
    capabilities: ['Speech Recognition', 'Translation', 'Transcription'],
    performance: {
      accuracy: 98,
      latency: 300,
      throughput: 800,
    },
    lastModified: '2024-03-13',
  },
];

const mockRoutes = [
  {
    id: 1,
    name: 'Text Generation Route',
    source: 'API Gateway',
    target: 'GPT-4',
    priority: 1,
    conditions: ['Content-Type: text/plain', 'Request Size < 1MB'],
    status: 'Active',
    lastModified: '2024-03-15',
  },
  {
    id: 2,
    name: 'Image Generation Route',
    source: 'API Gateway',
    target: 'DALL-E 3',
    priority: 2,
    conditions: ['Content-Type: image/*', 'Request Size < 5MB'],
    status: 'Active',
    lastModified: '2024-03-14',
  },
];

const mockCapabilities = [
  {
    id: 1,
    name: 'Text Generation',
    models: ['GPT-4', 'GPT-3.5'],
    status: 'Enabled',
    lastModified: '2024-03-15',
  },
  {
    id: 2,
    name: 'Image Generation',
    models: ['DALL-E 3', 'Stable Diffusion'],
    status: 'Enabled',
    lastModified: '2024-03-14',
  },
  {
    id: 3,
    name: 'Speech Recognition',
    models: ['Whisper', 'DeepSpeech'],
    status: 'Enabled',
    lastModified: '2024-03-13',
  },
];

// Add new mock data for model analytics
const mockModelAnalytics = {
  performanceMetrics: {
    accuracy: {
      current: 95.5,
      trend: 'up',
      history: [94.2, 94.8, 95.1, 95.3, 95.5],
    },
    latency: {
      current: 180,
      trend: 'down',
      history: [220, 210, 200, 190, 180],
    },
    throughput: {
      current: 1200,
      trend: 'up',
      history: [1000, 1050, 1100, 1150, 1200],
    },
  },
  usageStats: {
    totalRequests: 150000,
    successRate: 98.5,
    errorRate: 1.5,
    averageResponseTime: 185,
    peakLoad: 2500,
  },
  errorAnalysis: [
    {
      type: 'Timeout',
      count: 150,
      percentage: 0.1,
      trend: 'down',
    },
    {
      type: 'Validation Error',
      count: 800,
      percentage: 0.5,
      trend: 'stable',
    },
    {
      type: 'Resource Exhaustion',
      count: 100,
      percentage: 0.1,
      trend: 'up',
    },
  ],
};

const ModelManagementPanel = () => {
  const [models, setModels] = useState(mockModels);
  const [routes, setRoutes] = useState(mockRoutes);
  const [capabilities, setCapabilities] = useState(mockCapabilities);
  const [selectedModel, setSelectedModel] = useState(null);
  const [selectedRoute, setSelectedRoute] = useState(null);
  const [selectedCapability, setSelectedCapability] = useState(null);
  const [showModelDialog, setShowModelDialog] = useState(false);
  const [showRouteDialog, setShowRouteDialog] = useState(false);
  const [showCapabilityDialog, setShowCapabilityDialog] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [activeTab, setActiveTab] = useState(0);
  const [deploymentProgress, setDeploymentProgress] = useState(0);
  const [analyticsData, setAnalyticsData] = useState(mockModelAnalytics);
  const [showAnalyticsDialog, setShowAnalyticsDialog] = useState(false);
  const [selectedModelForAnalytics, setSelectedModelForAnalytics] = useState(null);
  const [timeRange, setTimeRange] = useState('7d');

  const handleEditModel = (model) => {
    setSelectedModel(model);
    setShowModelDialog(true);
  };

  const handleSaveModel = () => {
    // Implement save logic
    setShowModelDialog(false);
    setNotification({
      open: true,
      message: 'Model configuration updated successfully',
      severity: 'success',
    });
  };

  const handleDeployModel = () => {
    // Simulate deployment progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      setDeploymentProgress(progress);
      if (progress >= 100) {
        clearInterval(interval);
        setNotification({
          open: true,
          message: 'Model deployed successfully',
          severity: 'success',
        });
      }
    }, 500);
  };

  // Add new handler for analytics
  const handleAnalyticsClick = (model) => {
    setSelectedModelForAnalytics(model);
    setShowAnalyticsDialog(true);
  };

  // Add new handler for time range change
  const handleTimeRangeChange = (event) => {
    setTimeRange(event.target.value);
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

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Model Management Panel
      </Typography>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Models" />
          <Tab label="Routing" />
          <Tab label="Capabilities" />
        </Tabs>
      </Paper>

      {/* Models Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <PsychologyIcon sx={{ mr: 1 }} />
                  AI Models
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setShowModelDialog(true)}
                >
                  Add Model
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Version</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Capabilities</TableCell>
                      <TableCell>Performance</TableCell>
                      <TableCell>Last Modified</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {models.map((model) => (
                      <TableRow key={model.id}>
                        <TableCell>{model.name}</TableCell>
                        <TableCell>{model.version}</TableCell>
                        <TableCell>
                          <Chip
                            label={model.status}
                            color={getStatusColor(model.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {model.capabilities.map((capability) => (
                              <Chip key={capability} label={capability} size="small" />
                            ))}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                            <Typography variant="body2">Accuracy: {model.performance.accuracy}%</Typography>
                            <Typography variant="body2">Latency: {model.performance.latency}ms</Typography>
                            <Typography variant="body2">Throughput: {model.performance.throughput}/s</Typography>
                          </Box>
                        </TableCell>
                        <TableCell>{model.lastModified}</TableCell>
                        <TableCell>
                          <Tooltip title="Edit">
                            <IconButton onClick={() => handleEditModel(model)}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Deploy">
                            <IconButton onClick={handleDeployModel}>
                              <RefreshIcon />
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

      {/* Routing Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <RouteIcon sx={{ mr: 1 }} />
                  Model Routing
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setShowRouteDialog(true)}
                >
                  Add Route
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Source</TableCell>
                      <TableCell>Target</TableCell>
                      <TableCell>Priority</TableCell>
                      <TableCell>Conditions</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Last Modified</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {routes.map((route) => (
                      <TableRow key={route.id}>
                        <TableCell>{route.name}</TableCell>
                        <TableCell>{route.source}</TableCell>
                        <TableCell>{route.target}</TableCell>
                        <TableCell>{route.priority}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {route.conditions.map((condition) => (
                              <Chip key={condition} label={condition} size="small" />
                            ))}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={route.status}
                            color={getStatusColor(route.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{route.lastModified}</TableCell>
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

      {/* Capabilities Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <ExtensionIcon sx={{ mr: 1 }} />
                  Model Capabilities
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setShowCapabilityDialog(true)}
                >
                  Add Capability
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Models</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Last Modified</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {capabilities.map((capability) => (
                      <TableRow key={capability.id}>
                        <TableCell>{capability.name}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {capability.models.map((model) => (
                              <Chip key={model} label={model} size="small" />
                            ))}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={capability.status}
                            color={getStatusColor(capability.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{capability.lastModified}</TableCell>
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

      {/* Model Dialog */}
      <Dialog open={showModelDialog} onClose={() => setShowModelDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <PsychologyIcon sx={{ mr: 1 }} />
          {selectedModel ? 'Edit Model' : 'Add New Model'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                defaultValue={selectedModel?.name}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Version"
                defaultValue={selectedModel?.version}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select defaultValue={selectedModel?.status}>
                  <MenuItem value="Active">Active</MenuItem>
                  <MenuItem value="Inactive">Inactive</MenuItem>
                  <MenuItem value="Pending">Pending</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Capabilities
              </Typography>
              <FormGroup>
                {['Text Generation', 'Code Completion', 'Analysis', 'Image Generation', 'Speech Recognition'].map((capability) => (
                  <FormControlLabel
                    key={capability}
                    control={
                      <Checkbox
                        defaultChecked={selectedModel?.capabilities.includes(capability)}
                      />
                    }
                    label={capability}
                  />
                ))}
              </FormGroup>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Performance Settings
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="Accuracy Target (%)"
                    type="number"
                    defaultValue={selectedModel?.performance.accuracy}
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="Max Latency (ms)"
                    type="number"
                    defaultValue={selectedModel?.performance.latency}
                  />
                </Grid>
                <Grid item xs={4}>
                  <TextField
                    fullWidth
                    label="Target Throughput (/s)"
                    type="number"
                    defaultValue={selectedModel?.performance.throughput}
                  />
                </Grid>
              </Grid>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowModelDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveModel} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Deployment Progress */}
      {deploymentProgress > 0 && (
        <Dialog open={deploymentProgress < 100} maxWidth="sm" fullWidth>
          <DialogTitle>Deploying Model</DialogTitle>
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

      {/* Add Analytics Overview Card */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Model Performance Overview"
              avatar={<ActivityIcon />}
              action={
                <FormControl size="small">
                  <Select value={timeRange} onChange={handleTimeRangeChange}>
                    <MenuItem value="24h">Last 24 Hours</MenuItem>
                    <MenuItem value="7d">Last 7 Days</MenuItem>
                    <MenuItem value="30d">Last 30 Days</MenuItem>
                  </Select>
                </FormControl>
              }
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={4}>
                  <Box>
                    <Typography variant="body2">Accuracy</Typography>
                    <LinearProgress variant="determinate" value={analyticsData.performanceMetrics.accuracy.current} />
                    <Typography variant="caption" color="text.secondary">
                      {analyticsData.performanceMetrics.accuracy.current}%
                      {analyticsData.performanceMetrics.accuracy.trend === 'up' ? ' ↑' : ' ↓'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box>
                    <Typography variant="body2">Latency</Typography>
                    <LinearProgress variant="determinate" value={analyticsData.performanceMetrics.latency.current / 2} />
                    <Typography variant="caption" color="text.secondary">
                      {analyticsData.performanceMetrics.latency.current}ms
                      {analyticsData.performanceMetrics.latency.trend === 'down' ? ' ↓' : ' ↑'}
                    </Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={4}>
                  <Box>
                    <Typography variant="body2">Throughput</Typography>
                    <LinearProgress variant="determinate" value={analyticsData.performanceMetrics.throughput.current / 20} />
                    <Typography variant="caption" color="text.secondary">
                      {analyticsData.performanceMetrics.throughput.current}/s
                      {analyticsData.performanceMetrics.throughput.trend === 'up' ? ' ↑' : ' ↓'}
                    </Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader
              title="Usage Statistics"
              avatar={<NetworkCheckIcon />}
            />
            <CardContent>
              <Grid container spacing={2}>
                <Grid item xs={12} md={6}>
                  <Box>
                    <Typography variant="body2">Total Requests</Typography>
                    <Typography variant="h6">{analyticsData.usageStats.totalRequests.toLocaleString()}</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box>
                    <Typography variant="body2">Success Rate</Typography>
                    <Typography variant="h6">{analyticsData.usageStats.successRate}%</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box>
                    <Typography variant="body2">Average Response Time</Typography>
                    <Typography variant="h6">{analyticsData.usageStats.averageResponseTime}ms</Typography>
                  </Box>
                </Grid>
                <Grid item xs={12} md={6}>
                  <Box>
                    <Typography variant="body2">Peak Load</Typography>
                    <Typography variant="h6">{analyticsData.usageStats.peakLoad}/s</Typography>
                  </Box>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>

      {/* Add Analytics Dialog */}
      <Dialog open={showAnalyticsDialog} onClose={() => setShowAnalyticsDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <ActivityIcon sx={{ mr: 1 }} />
          Model Analytics: {selectedModelForAnalytics?.name}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Performance Metrics
              </Typography>
              <Box sx={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">
                  Performance metrics chart will be displayed here
                </Typography>
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Error Analysis
              </Typography>
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell>Error Type</TableCell>
                      <TableCell>Count</TableCell>
                      <TableCell>Percentage</TableCell>
                      <TableCell>Trend</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {analyticsData.errorAnalysis.map((error) => (
                      <TableRow key={error.type}>
                        <TableCell>{error.type}</TableCell>
                        <TableCell>{error.count}</TableCell>
                        <TableCell>{error.percentage}%</TableCell>
                        <TableCell>
                          {error.trend === 'up' ? '↑' : error.trend === 'down' ? '↓' : '→'}
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Usage Patterns
              </Typography>
              <Box sx={{ height: 200, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                <Typography color="text.secondary">
                  Usage patterns chart will be displayed here
                </Typography>
              </Box>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowAnalyticsDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ModelManagementPanel; 