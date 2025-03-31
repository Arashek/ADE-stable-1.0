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
  Link as LinkIcon,
  Webhook as WebhookIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';

// Mock data - Replace with API calls
const mockExternalServices = [
  {
    id: 1,
    name: 'OpenAI API',
    type: 'AI Service',
    status: 'Active',
    apiKey: 'sk-********************',
    lastUsed: '2024-03-15 10:30:00',
    health: 'Healthy',
    webhooks: 2,
  },
  {
    id: 2,
    name: 'AWS S3',
    type: 'Storage',
    status: 'Active',
    apiKey: 'AKIA****************',
    lastUsed: '2024-03-15 09:15:00',
    health: 'Warning',
    webhooks: 1,
  },
  {
    id: 3,
    name: 'Stripe',
    type: 'Payment',
    status: 'Active',
    apiKey: 'sk_test_****************',
    lastUsed: '2024-03-15 08:45:00',
    health: 'Healthy',
    webhooks: 3,
  },
];

const mockWebhooks = [
  {
    id: 1,
    name: 'Payment Success',
    service: 'Stripe',
    endpoint: 'https://api.example.com/webhooks/stripe',
    events: ['payment.succeeded', 'payment.failed'],
    status: 'Active',
    lastTriggered: '2024-03-15 10:15:00',
  },
  {
    id: 2,
    name: 'File Upload',
    service: 'AWS S3',
    endpoint: 'https://api.example.com/webhooks/s3',
    events: ['object.created', 'object.deleted'],
    status: 'Active',
    lastTriggered: '2024-03-15 09:30:00',
  },
];

const mockHealthChecks = {
  services: [
    {
      id: 1,
      name: 'OpenAI API',
      status: 'Healthy',
      responseTime: 120,
      uptime: '99.9%',
      lastCheck: '2024-03-15 10:30:00',
    },
    {
      id: 2,
      name: 'AWS S3',
      status: 'Warning',
      responseTime: 250,
      uptime: '99.8%',
      lastCheck: '2024-03-15 10:30:00',
    },
    {
      id: 3,
      name: 'Stripe',
      status: 'Healthy',
      responseTime: 150,
      uptime: '99.95%',
      lastCheck: '2024-03-15 10:30:00',
    },
  ],
  metrics: {
    totalServices: 3,
    healthyServices: 2,
    warningServices: 1,
    averageResponseTime: 173,
  },
};

const ExternalServicesPanel = () => {
  const [services, setServices] = useState(mockExternalServices);
  const [webhooks, setWebhooks] = useState(mockWebhooks);
  const [healthChecks, setHealthChecks] = useState(mockHealthChecks);
  const [selectedService, setSelectedService] = useState(null);
  const [selectedWebhook, setSelectedWebhook] = useState(null);
  const [showServiceDialog, setShowServiceDialog] = useState(false);
  const [showWebhookDialog, setShowWebhookDialog] = useState(false);
  const [showApiKeyDialog, setShowApiKeyDialog] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [activeTab, setActiveTab] = useState(0);
  const [showApiKey, setShowApiKey] = useState(false);

  const handleEditService = (service) => {
    setSelectedService(service);
    setShowServiceDialog(true);
  };

  const handleEditWebhook = (webhook) => {
    setSelectedWebhook(webhook);
    setShowWebhookDialog(true);
  };

  const handleSaveService = () => {
    // Implement save logic
    setShowServiceDialog(false);
    setNotification({
      open: true,
      message: 'Service configuration updated successfully',
      severity: 'success',
    });
  };

  const handleSaveWebhook = () => {
    // Implement save logic
    setShowWebhookDialog(false);
    setNotification({
      open: true,
      message: 'Webhook configuration updated successfully',
      severity: 'success',
    });
  };

  const handleRotateApiKey = () => {
    // Implement API key rotation logic
    setShowApiKeyDialog(false);
    setNotification({
      open: true,
      message: 'API key rotated successfully',
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

  const getHealthColor = (health) => {
    switch (health) {
      case 'Healthy':
        return 'success';
      case 'Warning':
        return 'warning';
      case 'Error':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        External Services Panel
      </Typography>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Services" />
          <Tab label="Webhooks" />
          <Tab label="Health" />
        </Tabs>
      </Paper>

      {/* Services Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <LinkIcon sx={{ mr: 1 }} />
                  External Services
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setShowServiceDialog(true)}
                >
                  Add Service
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Type</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>API Key</TableCell>
                      <TableCell>Health</TableCell>
                      <TableCell>Last Used</TableCell>
                      <TableCell>Webhooks</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {services.map((service) => (
                      <TableRow key={service.id}>
                        <TableCell>{service.name}</TableCell>
                        <TableCell>{service.type}</TableCell>
                        <TableCell>
                          <Chip
                            label={service.status}
                            color={getStatusColor(service.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Typography variant="body2">
                              {showApiKey ? service.apiKey : '••••••••••••••••'}
                            </Typography>
                            <IconButton size="small" onClick={() => setShowApiKey(!showApiKey)}>
                              {showApiKey ? <VisibilityOffIcon /> : <VisibilityIcon />}
                            </IconButton>
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={service.health}
                            color={getHealthColor(service.health)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{service.lastUsed}</TableCell>
                        <TableCell>{service.webhooks}</TableCell>
                        <TableCell>
                          <Tooltip title="Edit">
                            <IconButton onClick={() => handleEditService(service)}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Rotate API Key">
                            <IconButton onClick={() => setShowApiKeyDialog(true)}>
                              <KeyIcon />
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

      {/* Webhooks Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <WebhookIcon sx={{ mr: 1 }} />
                  Webhook Configuration
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setShowWebhookDialog(true)}
                >
                  Add Webhook
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Service</TableCell>
                      <TableCell>Endpoint</TableCell>
                      <TableCell>Events</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Last Triggered</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {webhooks.map((webhook) => (
                      <TableRow key={webhook.id}>
                        <TableCell>{webhook.name}</TableCell>
                        <TableCell>{webhook.service}</TableCell>
                        <TableCell>{webhook.endpoint}</TableCell>
                        <TableCell>
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap' }}>
                            {webhook.events.map((event) => (
                              <Chip key={event} label={event} size="small" />
                            ))}
                          </Box>
                        </TableCell>
                        <TableCell>
                          <Chip
                            label={webhook.status}
                            color={getStatusColor(webhook.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{webhook.lastTriggered}</TableCell>
                        <TableCell>
                          <Tooltip title="Edit">
                            <IconButton onClick={() => handleEditWebhook(webhook)}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Test">
                            <IconButton>
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

      {/* Health Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardHeader
                title="Service Health Overview"
                avatar={<ActivityIcon />}
              />
              <CardContent>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box>
                    <Typography variant="body2">Total Services</Typography>
                    <Typography variant="h6">{healthChecks.metrics.totalServices}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2">Healthy Services</Typography>
                    <Typography variant="h6" color="success.main">
                      {healthChecks.metrics.healthyServices}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2">Warning Services</Typography>
                    <Typography variant="h6" color="warning.main">
                      {healthChecks.metrics.warningServices}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2">Average Response Time</Typography>
                    <Typography variant="h6">{healthChecks.metrics.averageResponseTime}ms</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={8}>
            <Card>
              <CardHeader
                title="Service Health Details"
                avatar={<NetworkCheckIcon />}
              />
              <CardContent>
                <TableContainer>
                  <Table size="small">
                    <TableHead>
                      <TableRow>
                        <TableCell>Service</TableCell>
                        <TableCell>Status</TableCell>
                        <TableCell>Response Time</TableCell>
                        <TableCell>Uptime</TableCell>
                        <TableCell>Last Check</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {healthChecks.services.map((service) => (
                        <TableRow key={service.id}>
                          <TableCell>{service.name}</TableCell>
                          <TableCell>
                            <Chip
                              label={service.status}
                              color={getHealthColor(service.status)}
                              size="small"
                            />
                          </TableCell>
                          <TableCell>{service.responseTime}ms</TableCell>
                          <TableCell>{service.uptime}</TableCell>
                          <TableCell>{service.lastCheck}</TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      )}

      {/* Service Dialog */}
      <Dialog open={showServiceDialog} onClose={() => setShowServiceDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <LinkIcon sx={{ mr: 1 }} />
          {selectedService ? 'Edit Service' : 'Add New Service'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                defaultValue={selectedService?.name}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select defaultValue={selectedService?.type}>
                  <MenuItem value="AI Service">AI Service</MenuItem>
                  <MenuItem value="Storage">Storage</MenuItem>
                  <MenuItem value="Payment">Payment</MenuItem>
                  <MenuItem value="Analytics">Analytics</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="API Key"
                type="password"
                defaultValue={selectedService?.apiKey}
                helperText="API keys are encrypted at rest"
              />
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={<Switch defaultChecked={selectedService?.status === 'Active'} />}
                label="Active"
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowServiceDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveService} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Webhook Dialog */}
      <Dialog open={showWebhookDialog} onClose={() => setShowWebhookDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <WebhookIcon sx={{ mr: 1 }} />
          {selectedWebhook ? 'Edit Webhook' : 'Add New Webhook'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                defaultValue={selectedWebhook?.name}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Service</InputLabel>
                <Select defaultValue={selectedWebhook?.service}>
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
                label="Endpoint URL"
                defaultValue={selectedWebhook?.endpoint}
                helperText="HTTPS endpoint required"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Events
              </Typography>
              <FormGroup>
                {['payment.succeeded', 'payment.failed', 'object.created', 'object.deleted'].map((event) => (
                  <FormControlLabel
                    key={event}
                    control={
                      <Checkbox
                        defaultChecked={selectedWebhook?.events.includes(event)}
                      />
                    }
                    label={event}
                  />
                ))}
              </FormGroup>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowWebhookDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveWebhook} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* API Key Rotation Dialog */}
      <Dialog open={showApiKeyDialog} onClose={() => setShowApiKeyDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <SecurityIcon sx={{ mr: 1 }} />
          Rotate API Key
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              This will invalidate the current API key and generate a new one. Make sure to update any applications using this key.
            </Typography>
            <TextField
              fullWidth
              label="New API Key"
              type="password"
              defaultValue="••••••••••••••••"
              disabled
              sx={{ mt: 2 }}
            />
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowApiKeyDialog(false)}>Cancel</Button>
          <Button onClick={handleRotateApiKey} variant="contained" color="warning">
            Rotate Key
          </Button>
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

export default ExternalServicesPanel; 