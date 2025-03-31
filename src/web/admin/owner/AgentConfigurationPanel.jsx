import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  TextField,
  Button,
  Card,
  CardContent,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Stack,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  Snackbar,
  Tooltip,
  Autocomplete,
  Slider,
  FormHelperText,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Security as SecurityIcon,
  Psychology as PsychologyIcon,
  Build as BuildIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';

// Validation schemas
const roleSchema = Yup.object().shape({
  name: Yup.string().required('Role name is required'),
  description: Yup.string().required('Description is required'),
  permissions: Yup.array().min(1, 'At least one permission is required'),
  maxTokens: Yup.number().min(100, 'Minimum 100 tokens').max(4000, 'Maximum 4000 tokens'),
  temperature: Yup.number().min(0, 'Minimum 0').max(1, 'Maximum 1'),
});

const capabilitySchema = Yup.object().shape({
  name: Yup.string().required('Capability name is required'),
  description: Yup.string().required('Description is required'),
  enabled: Yup.boolean(),
  parameters: Yup.array().min(1, 'At least one parameter is required'),
});

// Agent Role Definition Component
const AgentRoleManager = () => {
  const [roles, setRoles] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingRole, setEditingRole] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    // Load roles from localStorage
    const savedRoles = localStorage.getItem('agentRoles');
    if (savedRoles) {
      setRoles(JSON.parse(savedRoles));
    }
  }, []);

  const formik = useFormik({
    initialValues: {
      name: '',
      description: '',
      permissions: [],
      maxTokens: 2000,
      temperature: 0.7,
      modelAccess: ['gpt-4'],
    },
    validationSchema: roleSchema,
    onSubmit: (values) => {
      const newRole = {
        id: editingRole?.id || Date.now(),
        ...values,
      };
      
      const updatedRoles = editingRole
        ? roles.map(r => r.id === editingRole.id ? newRole : r)
        : [...roles, newRole];
      
      setRoles(updatedRoles);
      localStorage.setItem('agentRoles', JSON.stringify(updatedRoles));
      setOpenDialog(false);
      setNotification({
        open: true,
        message: `Role ${editingRole ? 'updated' : 'added'} successfully`,
        severity: 'success',
      });
    },
  });

  const handleEdit = (role) => {
    setEditingRole(role);
    formik.setValues({
      name: role.name,
      description: role.description,
      permissions: role.permissions,
      maxTokens: role.maxTokens,
      temperature: role.temperature,
      modelAccess: role.modelAccess,
    });
    setOpenDialog(true);
  };

  const availablePermissions = [
    'read_tickets',
    'respond_tickets',
    'view_customer_data',
    'analyze_data',
    'generate_reports',
    'manage_users',
    'configure_system',
    'access_api',
  ];

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <SecurityIcon sx={{ mr: 1 }} />
          Agent Roles
        </Typography>
        <Tooltip title="Define roles and permissions for different agent types">
          <InfoIcon color="action" />
        </Tooltip>
      </Box>
      <Grid container spacing={2}>
        {roles.map((role) => (
          <Grid item xs={12} md={6} key={role.id}>
            <Card>
              <CardContent>
                <Typography variant="h6">{role.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {role.description}
                </Typography>
                <Stack direction="row" spacing={1} sx={{ mt: 2, flexWrap: 'wrap', gap: 1 }}>
                  {role.permissions.map((permission, index) => (
                    <Chip
                      key={index}
                      label={permission}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Stack>
                <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                  <Button
                    startIcon={<EditIcon />}
                    variant="outlined"
                    size="small"
                    onClick={() => handleEdit(role)}
                  >
                    Edit
                  </Button>
                  <Button
                    startIcon={<DeleteIcon />}
                    variant="outlined"
                    color="error"
                    size="small"
                  >
                    Delete
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
      <Button
        startIcon={<AddIcon />}
        variant="outlined"
        fullWidth
        sx={{ mt: 2 }}
        onClick={() => {
          setEditingRole(null);
          formik.resetForm();
          setOpenDialog(true);
        }}
      >
        Create New Role
      </Button>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingRole ? 'Edit Agent Role' : 'Create New Role'}</DialogTitle>
        <form onSubmit={formik.handleSubmit}>
          <DialogContent>
            <TextField
              fullWidth
              name="name"
              label="Role Name"
              margin="normal"
              value={formik.values.name}
              onChange={formik.handleChange}
              error={formik.touched.name && Boolean(formik.errors.name)}
              helperText={formik.touched.name && formik.errors.name}
            />
            <TextField
              fullWidth
              name="description"
              label="Description"
              margin="normal"
              multiline
              rows={3}
              value={formik.values.description}
              onChange={formik.handleChange}
              error={formik.touched.description && Boolean(formik.errors.description)}
              helperText={formik.touched.description && formik.errors.description}
            />
            <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
              Permissions
            </Typography>
            <Autocomplete
              multiple
              options={availablePermissions}
              value={formik.values.permissions}
              onChange={(_, newValue) => formik.setFieldValue('permissions', newValue)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  error={formik.touched.permissions && Boolean(formik.errors.permissions)}
                  helperText={formik.touched.permissions && formik.errors.permissions}
                />
              )}
              sx={{ mb: 2 }}
            />
            <Typography variant="subtitle1" gutterBottom>
              Model Access
            </Typography>
            <Autocomplete
              multiple
              options={['gpt-4', 'gpt-3.5-turbo', 'claude-2']}
              value={formik.values.modelAccess}
              onChange={(_, newValue) => formik.setFieldValue('modelAccess', newValue)}
              renderInput={(params) => <TextField {...params} />}
              sx={{ mb: 2 }}
            />
            <Typography variant="subtitle1" gutterBottom>
              Max Tokens: {formik.values.maxTokens}
            </Typography>
            <Slider
              name="maxTokens"
              value={formik.values.maxTokens}
              onChange={(_, value) => formik.setFieldValue('maxTokens', value)}
              min={100}
              max={4000}
              step={100}
              marks
              valueLabelDisplay="auto"
              sx={{ mb: 2 }}
            />
            <Typography variant="subtitle1" gutterBottom>
              Temperature: {formik.values.temperature}
            </Typography>
            <Slider
              name="temperature"
              value={formik.values.temperature}
              onChange={(_, value) => formik.setFieldValue('temperature', value)}
              min={0}
              max={1}
              step={0.1}
              marks
              valueLabelDisplay="auto"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button type="submit" variant="contained" color="primary">
              {editingRole ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
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
    </Paper>
  );
};

// Model Selection Component
const ModelSelector = () => {
  const [selectedModel, setSelectedModel] = useState('gpt-4');
  const [config, setConfig] = useState({
    temperature: 0.7,
    maxTokens: 2000,
    topP: 0.9,
    frequencyPenalty: 0,
    presencePenalty: 0,
  });
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    // Load model configuration from localStorage
    const savedConfig = localStorage.getItem('modelConfig');
    if (savedConfig) {
      setConfig(JSON.parse(savedConfig));
    }
  }, []);

  const handleSave = () => {
    localStorage.setItem('modelConfig', JSON.stringify(config));
    setNotification({
      open: true,
      message: 'Model configuration saved successfully',
      severity: 'success',
    });
  };

  const models = [
    { id: 'gpt-4', name: 'GPT-4', description: 'Most capable model for complex tasks' },
    { id: 'gpt-3.5-turbo', name: 'GPT-3.5 Turbo', description: 'Fast and efficient for most tasks' },
    { id: 'claude-2', name: 'Claude 2', description: 'Advanced reasoning and analysis' },
  ];

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <PsychologyIcon sx={{ mr: 1 }} />
          Model Configuration
        </Typography>
        <Tooltip title="Configure model parameters and behavior">
          <InfoIcon color="action" />
        </Tooltip>
      </Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Select Model</InputLabel>
            <Select
              value={selectedModel}
              label="Select Model"
              onChange={(e) => setSelectedModel(e.target.value)}
            >
              {models.map((model) => (
                <MenuItem key={model.id} value={model.id}>
                  {model.name}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
            {models.find(m => m.id === selectedModel)?.description}
          </Typography>
        </Grid>
        <Grid item xs={12} md={8}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography gutterBottom>Temperature: {config.temperature}</Typography>
              <Slider
                value={config.temperature}
                onChange={(_, value) => setConfig({ ...config, temperature: value })}
                min={0}
                max={1}
                step={0.1}
                marks
                valueLabelDisplay="auto"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography gutterBottom>Max Tokens: {config.maxTokens}</Typography>
              <Slider
                value={config.maxTokens}
                onChange={(_, value) => setConfig({ ...config, maxTokens: value })}
                min={100}
                max={4000}
                step={100}
                marks
                valueLabelDisplay="auto"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography gutterBottom>Top P: {config.topP}</Typography>
              <Slider
                value={config.topP}
                onChange={(_, value) => setConfig({ ...config, topP: value })}
                min={0}
                max={1}
                step={0.1}
                marks
                valueLabelDisplay="auto"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography gutterBottom>Frequency Penalty: {config.frequencyPenalty}</Typography>
              <Slider
                value={config.frequencyPenalty}
                onChange={(_, value) => setConfig({ ...config, frequencyPenalty: value })}
                min={-2}
                max={2}
                step={0.1}
                marks
                valueLabelDisplay="auto"
              />
            </Grid>
          </Grid>
        </Grid>
      </Grid>
      <Button
        startIcon={<SaveIcon />}
        variant="contained"
        fullWidth
        sx={{ mt: 2 }}
        onClick={handleSave}
      >
        Save Model Configuration
      </Button>

      <Snackbar
        open={notification.open}
        autoHideDuration={6000}
        onClose={() => setNotification({ ...notification, open: false })}
      >
        <Alert severity={notification.severity} onClose={() => setNotification({ ...notification, open: false })}>
          {notification.message}
        </Alert>
      </Snackbar>
    </Paper>
  );
};

// Capability Assignment Component
const CapabilityManager = () => {
  const [capabilities, setCapabilities] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingCapability, setEditingCapability] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    // Load capabilities from localStorage
    const savedCapabilities = localStorage.getItem('agentCapabilities');
    if (savedCapabilities) {
      setCapabilities(JSON.parse(savedCapabilities));
    }
  }, []);

  const formik = useFormik({
    initialValues: {
      name: '',
      description: '',
      enabled: true,
      parameters: [],
      rateLimit: 100,
      timeout: 30,
    },
    validationSchema: capabilitySchema,
    onSubmit: (values) => {
      const newCapability = {
        id: editingCapability?.id || Date.now(),
        ...values,
      };
      
      const updatedCapabilities = editingCapability
        ? capabilities.map(c => c.id === editingCapability.id ? newCapability : c)
        : [...capabilities, newCapability];
      
      setCapabilities(updatedCapabilities);
      localStorage.setItem('agentCapabilities', JSON.stringify(updatedCapabilities));
      setOpenDialog(false);
      setNotification({
        open: true,
        message: `Capability ${editingCapability ? 'updated' : 'added'} successfully`,
        severity: 'success',
      });
    },
  });

  const handleEdit = (capability) => {
    setEditingCapability(capability);
    formik.setValues({
      name: capability.name,
      description: capability.description,
      enabled: capability.enabled,
      parameters: capability.parameters,
      rateLimit: capability.rateLimit,
      timeout: capability.timeout,
    });
    setOpenDialog(true);
  };

  const availableParameters = [
    'max_length',
    'temperature',
    'top_p',
    'language',
    'complexity_level',
    'data_format',
    'analysis_type',
  ];

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <BuildIcon sx={{ mr: 1 }} />
          Agent Capabilities
        </Typography>
        <Tooltip title="Configure agent capabilities and parameters">
          <InfoIcon color="action" />
        </Tooltip>
      </Box>
      <List>
        {capabilities.map((capability) => (
          <React.Fragment key={capability.id}>
            <ListItem>
              <ListItemText
                primary={capability.name}
                secondary={capability.description}
              />
              <ListItemSecondaryAction>
                <FormControlLabel
                  control={
                    <Switch
                      checked={capability.enabled}
                      onChange={() => {
                        const updatedCapabilities = capabilities.map(cap =>
                          cap.id === capability.id
                            ? { ...cap, enabled: !cap.enabled }
                            : cap
                        );
                        setCapabilities(updatedCapabilities);
                        localStorage.setItem('agentCapabilities', JSON.stringify(updatedCapabilities));
                      }}
                    />
                  }
                />
                <IconButton onClick={() => handleEdit(capability)}>
                  <EditIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
            {capability.enabled && (
              <ListItem>
                <Box sx={{ pl: 4, width: '100%' }}>
                  <Typography variant="subtitle2" color="text.secondary" gutterBottom>
                    Parameters:
                  </Typography>
                  <Stack direction="row" spacing={1} sx={{ flexWrap: 'wrap', gap: 1 }}>
                    {capability.parameters.map((param, index) => (
                      <Chip
                        key={index}
                        label={param}
                        size="small"
                        color="primary"
                        variant="outlined"
                      />
                    ))}
                  </Stack>
                  <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                    <Typography variant="body2">
                      Rate Limit: {capability.rateLimit}/min
                    </Typography>
                    <Typography variant="body2">
                      Timeout: {capability.timeout}s
                    </Typography>
                  </Box>
                </Box>
              </ListItem>
            )}
            <Divider />
          </React.Fragment>
        ))}
      </List>
      <Button
        startIcon={<AddIcon />}
        variant="outlined"
        fullWidth
        sx={{ mt: 2 }}
        onClick={() => {
          setEditingCapability(null);
          formik.resetForm();
          setOpenDialog(true);
        }}
      >
        Add New Capability
      </Button>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingCapability ? 'Edit Capability' : 'Add New Capability'}</DialogTitle>
        <form onSubmit={formik.handleSubmit}>
          <DialogContent>
            <TextField
              fullWidth
              name="name"
              label="Capability Name"
              margin="normal"
              value={formik.values.name}
              onChange={formik.handleChange}
              error={formik.touched.name && Boolean(formik.errors.name)}
              helperText={formik.touched.name && formik.errors.name}
            />
            <TextField
              fullWidth
              name="description"
              label="Description"
              margin="normal"
              multiline
              rows={3}
              value={formik.values.description}
              onChange={formik.handleChange}
              error={formik.touched.description && Boolean(formik.errors.description)}
              helperText={formik.touched.description && formik.errors.description}
            />
            <FormControlLabel
              control={
                <Switch
                  name="enabled"
                  checked={formik.values.enabled}
                  onChange={formik.handleChange}
                />
              }
              label="Enabled"
            />
            <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
              Parameters
            </Typography>
            <Autocomplete
              multiple
              options={availableParameters}
              value={formik.values.parameters}
              onChange={(_, newValue) => formik.setFieldValue('parameters', newValue)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  error={formik.touched.parameters && Boolean(formik.errors.parameters)}
                  helperText={formik.touched.parameters && formik.errors.parameters}
                />
              )}
              sx={{ mb: 2 }}
            />
            <Typography gutterBottom>Rate Limit (requests/minute)</Typography>
            <Slider
              name="rateLimit"
              value={formik.values.rateLimit}
              onChange={(_, value) => formik.setFieldValue('rateLimit', value)}
              min={1}
              max={1000}
              step={10}
              marks
              valueLabelDisplay="auto"
              sx={{ mb: 2 }}
            />
            <Typography gutterBottom>Timeout (seconds)</Typography>
            <Slider
              name="timeout"
              value={formik.values.timeout}
              onChange={(_, value) => formik.setFieldValue('timeout', value)}
              min={1}
              max={300}
              step={5}
              marks
              valueLabelDisplay="auto"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button type="submit" variant="contained" color="primary">
              {editingCapability ? 'Update' : 'Add'}
            </Button>
          </DialogActions>
        </form>
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
    </Paper>
  );
};

const AgentConfigurationPanel = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Agent Configuration
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <AgentRoleManager />
        </Grid>
        <Grid item xs={12}>
          <ModelSelector />
        </Grid>
        <Grid item xs={12}>
          <CapabilityManager />
        </Grid>
      </Grid>
    </Box>
  );
};

export default AgentConfigurationPanel; 