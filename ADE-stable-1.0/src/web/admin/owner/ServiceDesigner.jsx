import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Switch,
  FormControlLabel,
  TextField,
  Button,
  Card,
  CardContent,
  IconButton,
  Divider,
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
  Alert,
  Snackbar,
  Tooltip,
  Autocomplete,
  Chip,
  Stack,
  Slider,
  FormHelperText,
  ButtonGroup,
  DialogContentText,
  DialogActions as MuiDialogActions,
  DialogContent as MuiDialogContent,
  DialogTitle as MuiDialogTitle,
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Save as SaveIcon,
  Settings as SettingsIcon,
  AttachMoney as AttachMoneyIcon,
  Category as CategoryIcon,
  Build as BuildIcon,
  Info as InfoIcon,
  Warning as WarningIcon,
  Download as DownloadIcon,
  Upload as UploadIcon,
  Refresh as RefreshIcon,
  Backup as BackupIcon,
  Restore as RestoreIcon,
} from '@mui/icons-material';
import { useFormik } from 'formik';
import * as Yup from 'yup';

// Enhanced validation schemas
const featureSchema = Yup.object().shape({
  name: Yup.string()
    .required('Feature name is required')
    .min(3, 'Feature name must be at least 3 characters')
    .max(50, 'Feature name must not exceed 50 characters')
    .matches(/^[a-zA-Z0-9_-]+$/, 'Feature name can only contain letters, numbers, underscores, and hyphens'),
  description: Yup.string()
    .required('Description is required')
    .min(10, 'Description must be at least 10 characters')
    .max(200, 'Description must not exceed 200 characters'),
  enabled: Yup.boolean(),
  category: Yup.string().required('Category is required'),
  priority: Yup.number().min(1, 'Priority must be at least 1').max(5, 'Priority must not exceed 5'),
  dependencies: Yup.array(),
  rolloutPercentage: Yup.number().min(0, 'Rollout percentage must be at least 0').max(100, 'Rollout percentage must not exceed 100'),
});

const tierSchema = Yup.object().shape({
  name: Yup.string()
    .required('Tier name is required')
    .min(3, 'Tier name must be at least 3 characters')
    .max(50, 'Tier name must not exceed 50 characters'),
  price: Yup.number()
    .required('Price is required')
    .min(0, 'Price must be at least 0')
    .max(10000, 'Price must not exceed 10000'),
  maxUsers: Yup.number()
    .required('Maximum users is required')
    .min(1, 'Maximum users must be at least 1')
    .max(1000, 'Maximum users must not exceed 1000'),
  storage: Yup.number()
    .required('Storage is required')
    .min(1, 'Storage must be at least 1GB')
    .max(1000, 'Storage must not exceed 1000GB'),
  features: Yup.array().min(1, 'At least one feature must be selected'),
  priority: Yup.number().min(1, 'Priority must be at least 1').max(5, 'Priority must not exceed 5'),
  customLimits: Yup.object().shape({
    apiCalls: Yup.number().min(0, 'API calls must be at least 0'),
    bandwidth: Yup.number().min(0, 'Bandwidth must be at least 0'),
    concurrentUsers: Yup.number().min(1, 'Concurrent users must be at least 1'),
  }),
});

const bundleSchema = Yup.object().shape({
  name: Yup.string()
    .required('Bundle name is required')
    .min(3, 'Bundle name must be at least 3 characters')
    .max(50, 'Bundle name must not exceed 50 characters'),
  description: Yup.string()
    .required('Description is required')
    .min(10, 'Description must be at least 10 characters')
    .max(200, 'Description must not exceed 200 characters'),
  price: Yup.number()
    .required('Price is required')
    .min(0, 'Price must be at least 0')
    .max(10000, 'Price must not exceed 10000'),
  features: Yup.array().min(1, 'At least one feature must be selected'),
  validityPeriod: Yup.number().min(1, 'Validity period must be at least 1 month').max(36, 'Validity period must not exceed 36 months'),
  autoRenew: Yup.boolean(),
  discountPercentage: Yup.number().min(0, 'Discount percentage must be at least 0').max(100, 'Discount percentage must not exceed 100'),
});

// Feature Flag Management Component
const FeatureFlagManager = () => {
  const [features, setFeatures] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingFeature, setEditingFeature] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [confirmDialog, setConfirmDialog] = useState({ open: false, title: '', message: '', action: null });

  useEffect(() => {
    loadFeatures();
  }, []);

  const loadFeatures = () => {
    const savedFeatures = localStorage.getItem('serviceFeatures');
    if (savedFeatures) {
      setFeatures(JSON.parse(savedFeatures));
    }
  };

  const formik = useFormik({
    initialValues: {
      name: '',
      description: '',
      enabled: true,
      category: '',
      priority: 3,
      dependencies: [],
      rolloutPercentage: 100,
    },
    validationSchema: featureSchema,
    onSubmit: (values) => {
      const newFeature = {
        id: editingFeature?.id || Date.now(),
        ...values,
      };
      
      const updatedFeatures = editingFeature
        ? features.map(f => f.id === editingFeature.id ? newFeature : f)
        : [...features, newFeature];
      
      setFeatures(updatedFeatures);
      localStorage.setItem('serviceFeatures', JSON.stringify(updatedFeatures));
      setOpenDialog(false);
      setNotification({
        open: true,
        message: `Feature ${editingFeature ? 'updated' : 'added'} successfully`,
        severity: 'success',
      });
    },
  });

  const handleDelete = (feature) => {
    setConfirmDialog({
      open: true,
      title: 'Delete Feature',
      message: `Are you sure you want to delete the feature "${feature.name}"? This action cannot be undone.`,
      action: () => {
        const updatedFeatures = features.filter(f => f.id !== feature.id);
        setFeatures(updatedFeatures);
        localStorage.setItem('serviceFeatures', JSON.stringify(updatedFeatures));
        setNotification({
          open: true,
          message: 'Feature deleted successfully',
          severity: 'success',
        });
      },
    });
  };

  const handleEdit = (feature) => {
    setEditingFeature(feature);
    formik.setValues({
      name: feature.name,
      description: feature.description,
      enabled: feature.enabled,
      category: feature.category,
      priority: feature.priority,
      dependencies: feature.dependencies || [],
      rolloutPercentage: feature.rolloutPercentage || 100,
    });
    setOpenDialog(true);
  };

  const handleExport = () => {
    const data = JSON.stringify(features, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'service-features.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImport = (event) => {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedFeatures = JSON.parse(e.target.result);
        if (Array.isArray(importedFeatures)) {
          setFeatures(importedFeatures);
          localStorage.setItem('serviceFeatures', JSON.stringify(importedFeatures));
          setNotification({
            open: true,
            message: 'Features imported successfully',
            severity: 'success',
          });
        } else {
          throw new Error('Invalid data format');
        }
      } catch (error) {
        setNotification({
          open: true,
          message: 'Error importing features: Invalid file format',
          severity: 'error',
        });
      }
    };
    reader.readAsText(file);
  };

  const featureCategories = [
    'Core',
    'Security',
    'Analytics',
    'Integration',
    'Customization',
    'Performance',
    'Compliance',
  ];

  const availableDependencies = features.map(f => f.name);

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <SettingsIcon sx={{ mr: 1 }} />
          Feature Flag Management
        </Typography>
        <Box>
          <Tooltip title="Export features">
            <IconButton onClick={handleExport} sx={{ mr: 1 }}>
              <DownloadIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Import features">
            <IconButton component="label" sx={{ mr: 1 }}>
              <UploadIcon />
              <input
                type="file"
                hidden
                accept=".json"
                onChange={handleImport}
              />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh">
            <IconButton onClick={loadFeatures} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Add new feature">
            <IconButton
              onClick={() => {
                setEditingFeature(null);
                formik.resetForm();
                setOpenDialog(true);
              }}
            >
              <AddIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      <List>
        {features.map((feature) => (
          <React.Fragment key={feature.id}>
            <ListItem>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <Typography variant="subtitle1">{feature.name}</Typography>
                    <Chip
                      label={feature.category}
                      size="small"
                      color="primary"
                      variant="outlined"
                      sx={{ ml: 1 }}
                    />
                    <Chip
                      label={`Priority: ${feature.priority}`}
                      size="small"
                      color="secondary"
                      variant="outlined"
                      sx={{ ml: 1 }}
                    />
                  </Box>
                }
                secondary={
                  <Box>
                    <Typography variant="body2" color="text.secondary">
                      {feature.description}
                    </Typography>
                    {feature.dependencies && feature.dependencies.length > 0 && (
                      <Box sx={{ mt: 1 }}>
                        <Typography variant="caption" color="text.secondary">
                          Dependencies:
                        </Typography>
                        <Stack direction="row" spacing={1} sx={{ mt: 0.5, flexWrap: 'wrap', gap: 1 }}>
                          {feature.dependencies.map((dep, index) => (
                            <Chip
                              key={index}
                              label={dep}
                              size="small"
                              color="info"
                              variant="outlined"
                            />
                          ))}
                        </Stack>
                      </Box>
                    )}
                    <Box sx={{ mt: 1, display: 'flex', alignItems: 'center', gap: 2 }}>
                      <Typography variant="caption" color="text.secondary">
                        Rollout: {feature.rolloutPercentage}%
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        Status: {feature.enabled ? 'Enabled' : 'Disabled'}
                      </Typography>
                    </Box>
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                <FormControlLabel
                  control={
                    <Switch
                      checked={feature.enabled}
                      onChange={() => {
                        const updatedFeatures = features.map(f =>
                          f.id === feature.id
                            ? { ...f, enabled: !f.enabled }
                            : f
                        );
                        setFeatures(updatedFeatures);
                        localStorage.setItem('serviceFeatures', JSON.stringify(updatedFeatures));
                      }}
                    />
                  }
                />
                <IconButton onClick={() => handleEdit(feature)} sx={{ mr: 1 }}>
                  <EditIcon />
                </IconButton>
                <IconButton onClick={() => handleDelete(feature)}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
            <Divider />
          </React.Fragment>
        ))}
      </List>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingFeature ? 'Edit Feature' : 'Add New Feature'}</DialogTitle>
        <form onSubmit={formik.handleSubmit}>
          <DialogContent>
            <TextField
              fullWidth
              name="name"
              label="Feature Name"
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
            <FormControl fullWidth margin="normal">
              <InputLabel>Category</InputLabel>
              <Select
                name="category"
                value={formik.values.category}
                label="Category"
                onChange={formik.handleChange}
                error={formik.touched.category && Boolean(formik.errors.category)}
              >
                {featureCategories.map((category) => (
                  <MenuItem key={category} value={category}>
                    {category}
                  </MenuItem>
                ))}
              </Select>
              {formik.touched.category && formik.errors.category && (
                <FormHelperText error>{formik.errors.category}</FormHelperText>
              )}
            </FormControl>
            <FormControl fullWidth margin="normal">
              <InputLabel>Priority</InputLabel>
              <Select
                name="priority"
                value={formik.values.priority}
                label="Priority"
                onChange={formik.handleChange}
                error={formik.touched.priority && Boolean(formik.errors.priority)}
              >
                {[1, 2, 3, 4, 5].map((priority) => (
                  <MenuItem key={priority} value={priority}>
                    {priority}
                  </MenuItem>
                ))}
              </Select>
              {formik.touched.priority && formik.errors.priority && (
                <FormHelperText error>{formik.errors.priority}</FormHelperText>
              )}
            </FormControl>
            <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
              Dependencies
            </Typography>
            <Autocomplete
              multiple
              options={availableDependencies}
              value={formik.values.dependencies}
              onChange={(_, newValue) => formik.setFieldValue('dependencies', newValue)}
              renderInput={(params) => <TextField {...params} />}
              sx={{ mb: 2 }}
            />
            <Typography gutterBottom>Rollout Percentage: {formik.values.rolloutPercentage}%</Typography>
            <Slider
              name="rolloutPercentage"
              value={formik.values.rolloutPercentage}
              onChange={(_, value) => formik.setFieldValue('rolloutPercentage', value)}
              min={0}
              max={100}
              step={5}
              marks
              valueLabelDisplay="auto"
              sx={{ mb: 2 }}
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
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button type="submit" variant="contained" color="primary">
              {editingFeature ? 'Update' : 'Add'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      <Dialog
        open={confirmDialog.open}
        onClose={() => setConfirmDialog({ ...confirmDialog, open: false })}
      >
        <MuiDialogTitle>{confirmDialog.title}</MuiDialogTitle>
        <MuiDialogContent>
          <DialogContentText>{confirmDialog.message}</DialogContentText>
        </MuiDialogContent>
        <MuiDialogActions>
          <Button onClick={() => setConfirmDialog({ ...confirmDialog, open: false })}>
            Cancel
          </Button>
          <Button
            onClick={() => {
              confirmDialog.action();
              setConfirmDialog({ ...confirmDialog, open: false });
            }}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </MuiDialogActions>
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

// Service Tier Configuration Component
const ServiceTierConfig = () => {
  const [tiers, setTiers] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingTier, setEditingTier] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [confirmDialog, setConfirmDialog] = useState({ open: false, title: '', message: '', action: null });

  useEffect(() => {
    loadTiers();
  }, []);

  const loadTiers = () => {
    const savedTiers = localStorage.getItem('serviceTiers');
    if (savedTiers) {
      setTiers(JSON.parse(savedTiers));
    }
  };

  const formik = useFormik({
    initialValues: {
      name: '',
      price: 0,
      maxUsers: 1,
      storage: 1,
      features: [],
      priority: 3,
      customLimits: {
        apiCalls: 1000,
        bandwidth: 100,
        concurrentUsers: 10,
      },
    },
    validationSchema: tierSchema,
    onSubmit: (values) => {
      const newTier = {
        id: editingTier?.id || Date.now(),
        ...values,
      };
      
      const updatedTiers = editingTier
        ? tiers.map(t => t.id === editingTier.id ? newTier : t)
        : [...tiers, newTier];
      
      setTiers(updatedTiers);
      localStorage.setItem('serviceTiers', JSON.stringify(updatedTiers));
      setOpenDialog(false);
      setNotification({
        open: true,
        message: `Tier ${editingTier ? 'updated' : 'added'} successfully`,
        severity: 'success',
      });
    },
  });

  const handleDelete = (tier) => {
    setConfirmDialog({
      open: true,
      title: 'Delete Tier',
      message: `Are you sure you want to delete the tier "${tier.name}"? This action cannot be undone.`,
      action: () => {
        const updatedTiers = tiers.filter(t => t.id !== tier.id);
        setTiers(updatedTiers);
        localStorage.setItem('serviceTiers', JSON.stringify(updatedTiers));
        setNotification({
          open: true,
          message: 'Tier deleted successfully',
          severity: 'success',
        });
      },
    });
  };

  const handleEdit = (tier) => {
    setEditingTier(tier);
    formik.setValues({
      name: tier.name,
      price: tier.price,
      maxUsers: tier.maxUsers,
      storage: tier.storage,
      features: tier.features,
      priority: tier.priority,
      customLimits: tier.customLimits,
    });
    setOpenDialog(true);
  };

  const handleExport = () => {
    const data = JSON.stringify(tiers, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'service-tiers.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImport = (event) => {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedTiers = JSON.parse(e.target.result);
        if (Array.isArray(importedTiers)) {
          setTiers(importedTiers);
          localStorage.setItem('serviceTiers', JSON.stringify(importedTiers));
          setNotification({
            open: true,
            message: 'Tiers imported successfully',
            severity: 'success',
          });
        } else {
          throw new Error('Invalid data format');
        }
      } catch (error) {
        setNotification({
          open: true,
          message: 'Error importing tiers: Invalid file format',
          severity: 'error',
        });
      }
    };
    reader.readAsText(file);
  };

  const availableFeatures = JSON.parse(localStorage.getItem('serviceFeatures') || '[]');

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <CategoryIcon sx={{ mr: 1 }} />
          Service Tier Configuration
        </Typography>
        <Box>
          <Tooltip title="Export tiers">
            <IconButton onClick={handleExport} sx={{ mr: 1 }}>
              <DownloadIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Import tiers">
            <IconButton component="label" sx={{ mr: 1 }}>
              <UploadIcon />
              <input
                type="file"
                hidden
                accept=".json"
                onChange={handleImport}
              />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh">
            <IconButton onClick={loadTiers} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Add new tier">
            <IconButton
              onClick={() => {
                setEditingTier(null);
                formik.resetForm();
                setOpenDialog(true);
              }}
            >
              <AddIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      <Grid container spacing={2}>
        {tiers.map((tier) => (
          <Grid item xs={12} md={6} key={tier.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">{tier.name}</Typography>
                  <Chip
                    label={`Priority: ${tier.priority}`}
                    size="small"
                    color="secondary"
                    variant="outlined"
                  />
                </Box>
                <Typography variant="h4" color="primary" gutterBottom>
                  ${tier.price}
                  <Typography component="span" variant="body2" color="text.secondary">
                    /month
                  </Typography>
                </Typography>
                <Box sx={{ display: 'flex', gap: 2, mb: 2 }}>
                  <Typography variant="body2">
                    <strong>{tier.maxUsers}</strong> users
                  </Typography>
                  <Typography variant="body2">
                    <strong>{tier.storage}GB</strong> storage
                  </Typography>
                </Box>
                <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
                  {tier.features.map((feature, index) => (
                    <Chip
                      key={index}
                      label={feature}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Stack>
                <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                  <Button
                    startIcon={<EditIcon />}
                    variant="outlined"
                    size="small"
                    onClick={() => handleEdit(tier)}
                  >
                    Edit
                  </Button>
                  <Button
                    startIcon={<DeleteIcon />}
                    variant="outlined"
                    color="error"
                    size="small"
                    onClick={() => handleDelete(tier)}
                  >
                    Delete
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingTier ? 'Edit Service Tier' : 'Create New Tier'}</DialogTitle>
        <form onSubmit={formik.handleSubmit}>
          <DialogContent>
            <TextField
              fullWidth
              name="name"
              label="Tier Name"
              margin="normal"
              value={formik.values.name}
              onChange={formik.handleChange}
              error={formik.touched.name && Boolean(formik.errors.name)}
              helperText={formik.touched.name && formik.errors.name}
            />
            <TextField
              fullWidth
              name="price"
              label="Price"
              type="number"
              margin="normal"
              value={formik.values.price}
              onChange={formik.handleChange}
              error={formik.touched.price && Boolean(formik.errors.price)}
              helperText={formik.touched.price && formik.errors.price}
              InputProps={{
                startAdornment: <AttachMoneyIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
            <TextField
              fullWidth
              name="maxUsers"
              label="Maximum Users"
              type="number"
              margin="normal"
              value={formik.values.maxUsers}
              onChange={formik.handleChange}
              error={formik.touched.maxUsers && Boolean(formik.errors.maxUsers)}
              helperText={formik.touched.maxUsers && formik.errors.maxUsers}
            />
            <TextField
              fullWidth
              name="storage"
              label="Storage (GB)"
              type="number"
              margin="normal"
              value={formik.values.storage}
              onChange={formik.handleChange}
              error={formik.touched.storage && Boolean(formik.errors.storage)}
              helperText={formik.touched.storage && formik.errors.storage}
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Priority</InputLabel>
              <Select
                name="priority"
                value={formik.values.priority}
                label="Priority"
                onChange={formik.handleChange}
                error={formik.touched.priority && Boolean(formik.errors.priority)}
              >
                {[1, 2, 3, 4, 5].map((priority) => (
                  <MenuItem key={priority} value={priority}>
                    {priority}
                  </MenuItem>
                ))}
              </Select>
              {formik.touched.priority && formik.errors.priority && (
                <FormHelperText error>{formik.errors.priority}</FormHelperText>
              )}
            </FormControl>
            <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
              Features
            </Typography>
            <Autocomplete
              multiple
              options={availableFeatures.map(f => f.name)}
              value={formik.values.features}
              onChange={(_, newValue) => formik.setFieldValue('features', newValue)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  error={formik.touched.features && Boolean(formik.errors.features)}
                  helperText={formik.touched.features && formik.errors.features}
                />
              )}
              sx={{ mb: 2 }}
            />
            <Typography variant="subtitle1" gutterBottom>
              Custom Limits
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  name="customLimits.apiCalls"
                  label="API Calls"
                  type="number"
                  value={formik.values.customLimits.apiCalls}
                  onChange={formik.handleChange}
                  error={formik.touched.customLimits?.apiCalls && Boolean(formik.errors.customLimits?.apiCalls)}
                  helperText={formik.touched.customLimits?.apiCalls && formik.errors.customLimits?.apiCalls}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  name="customLimits.bandwidth"
                  label="Bandwidth (GB)"
                  type="number"
                  value={formik.values.customLimits.bandwidth}
                  onChange={formik.handleChange}
                  error={formik.touched.customLimits?.bandwidth && Boolean(formik.errors.customLimits?.bandwidth)}
                  helperText={formik.touched.customLimits?.bandwidth && formik.errors.customLimits?.bandwidth}
                />
              </Grid>
              <Grid item xs={12} sm={4}>
                <TextField
                  fullWidth
                  name="customLimits.concurrentUsers"
                  label="Concurrent Users"
                  type="number"
                  value={formik.values.customLimits.concurrentUsers}
                  onChange={formik.handleChange}
                  error={formik.touched.customLimits?.concurrentUsers && Boolean(formik.errors.customLimits?.concurrentUsers)}
                  helperText={formik.touched.customLimits?.concurrentUsers && formik.errors.customLimits?.concurrentUsers}
                />
              </Grid>
            </Grid>
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button type="submit" variant="contained" color="primary">
              {editingTier ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      <Dialog
        open={confirmDialog.open}
        onClose={() => setConfirmDialog({ ...confirmDialog, open: false })}
      >
        <MuiDialogTitle>{confirmDialog.title}</MuiDialogTitle>
        <MuiDialogContent>
          <DialogContentText>{confirmDialog.message}</DialogContentText>
        </MuiDialogContent>
        <MuiDialogActions>
          <Button onClick={() => setConfirmDialog({ ...confirmDialog, open: false })}>
            Cancel
          </Button>
          <Button
            onClick={() => {
              confirmDialog.action();
              setConfirmDialog({ ...confirmDialog, open: false });
            }}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </MuiDialogActions>
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

// Pricing Configuration Component
const PricingConfig = () => {
  const [config, setConfig] = useState({
    basePrice: 0,
    currency: 'USD',
    billingCycle: 'monthly',
    volumeDiscounts: [],
  });
  const [openDialog, setOpenDialog] = useState(false);
  const [editingDiscount, setEditingDiscount] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = () => {
    const savedConfig = localStorage.getItem('pricingConfig');
    if (savedConfig) {
      setConfig(JSON.parse(savedConfig));
    }
  };

  const handleSave = () => {
    localStorage.setItem('pricingConfig', JSON.stringify(config));
    setNotification({
      open: true,
      message: 'Pricing configuration saved successfully',
      severity: 'success',
    });
  };

  const handleAddDiscount = () => {
    setEditingDiscount(null);
    setOpenDialog(true);
  };

  const handleEditDiscount = (discount) => {
    setEditingDiscount(discount);
    setOpenDialog(true);
  };

  const handleDeleteDiscount = (index) => {
    const updatedDiscounts = config.volumeDiscounts.filter((_, i) => i !== index);
    setConfig({ ...config, volumeDiscounts: updatedDiscounts });
    localStorage.setItem('pricingConfig', JSON.stringify({ ...config, volumeDiscounts: updatedDiscounts }));
    setNotification({
      open: true,
      message: 'Volume discount deleted successfully',
      severity: 'success',
    });
  };

  const handleSaveDiscount = (discount) => {
    const updatedDiscounts = editingDiscount
      ? config.volumeDiscounts.map((d, i) => (i === editingDiscount.index ? discount : d))
      : [...config.volumeDiscounts, discount];
    
    setConfig({ ...config, volumeDiscounts: updatedDiscounts });
    localStorage.setItem('pricingConfig', JSON.stringify({ ...config, volumeDiscounts: updatedDiscounts }));
    setOpenDialog(false);
    setNotification({
      open: true,
      message: `Volume discount ${editingDiscount ? 'updated' : 'added'} successfully`,
      severity: 'success',
    });
  };

  const currencies = ['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD'];
  const billingCycles = ['monthly', 'quarterly', 'annually', 'biennially'];

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <AttachMoneyIcon sx={{ mr: 1 }} />
          Pricing Configuration
        </Typography>
        <Tooltip title="Configure pricing and billing options">
          <InfoIcon color="action" />
        </Tooltip>
      </Box>
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <TextField
            fullWidth
            label="Base Price"
            type="number"
            value={config.basePrice}
            onChange={(e) => setConfig({ ...config, basePrice: Number(e.target.value) })}
            InputProps={{
              startAdornment: <AttachMoneyIcon sx={{ mr: 1, color: 'text.secondary' }} />,
            }}
          />
        </Grid>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Currency</InputLabel>
            <Select
              value={config.currency}
              label="Currency"
              onChange={(e) => setConfig({ ...config, currency: e.target.value })}
            >
              {currencies.map((currency) => (
                <MenuItem key={currency} value={currency}>
                  {currency}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} md={4}>
          <FormControl fullWidth>
            <InputLabel>Billing Cycle</InputLabel>
            <Select
              value={config.billingCycle}
              label="Billing Cycle"
              onChange={(e) => setConfig({ ...config, billingCycle: e.target.value })}
            >
              {billingCycles.map((cycle) => (
                <MenuItem key={cycle} value={cycle}>
                  {cycle.charAt(0).toUpperCase() + cycle.slice(1)}
                </MenuItem>
              ))}
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      <Box sx={{ mt: 3 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
          <Typography variant="subtitle1">Volume Discounts</Typography>
          <Button
            startIcon={<AddIcon />}
            variant="outlined"
            onClick={handleAddDiscount}
          >
            Add Discount
          </Button>
        </Box>
        <List>
          {config.volumeDiscounts.map((discount, index) => (
            <ListItem key={index}>
              <ListItemText
                primary={`${discount.minQuantity}+ units`}
                secondary={`${discount.discountPercentage}% discount`}
              />
              <ListItemSecondaryAction>
                <IconButton onClick={() => handleEditDiscount({ ...discount, index })} sx={{ mr: 1 }}>
                  <EditIcon />
                </IconButton>
                <IconButton onClick={() => handleDeleteDiscount(index)}>
                  <DeleteIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
          ))}
        </List>
      </Box>

      <Button
        startIcon={<SaveIcon />}
        variant="contained"
        fullWidth
        sx={{ mt: 2 }}
        onClick={handleSave}
      >
        Save Pricing Configuration
      </Button>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingDiscount ? 'Edit Volume Discount' : 'Add Volume Discount'}</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Minimum Quantity"
            type="number"
            margin="normal"
            value={editingDiscount?.minQuantity || ''}
            onChange={(e) => {
              const value = Number(e.target.value);
              if (value >= 0) {
                setEditingDiscount({ ...editingDiscount, minQuantity: value });
              }
            }}
          />
          <TextField
            fullWidth
            label="Discount Percentage"
            type="number"
            margin="normal"
            value={editingDiscount?.discountPercentage || ''}
            onChange={(e) => {
              const value = Number(e.target.value);
              if (value >= 0 && value <= 100) {
                setEditingDiscount({ ...editingDiscount, discountPercentage: value });
              }
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            color="primary"
            onClick={() => handleSaveDiscount(editingDiscount)}
          >
            {editingDiscount ? 'Update' : 'Add'}
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
    </Paper>
  );
};

// Service Bundle Component
const ServiceBundle = () => {
  const [bundles, setBundles] = useState([]);
  const [openDialog, setOpenDialog] = useState(false);
  const [editingBundle, setEditingBundle] = useState(null);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [confirmDialog, setConfirmDialog] = useState({ open: false, title: '', message: '', action: null });

  useEffect(() => {
    loadBundles();
  }, []);

  const loadBundles = () => {
    const savedBundles = localStorage.getItem('serviceBundles');
    if (savedBundles) {
      setBundles(JSON.parse(savedBundles));
    }
  };

  const formik = useFormik({
    initialValues: {
      name: '',
      description: '',
      price: 0,
      features: [],
      validityPeriod: 12,
      autoRenew: true,
      discountPercentage: 0,
    },
    validationSchema: bundleSchema,
    onSubmit: (values) => {
      const newBundle = {
        id: editingBundle?.id || Date.now(),
        ...values,
      };
      
      const updatedBundles = editingBundle
        ? bundles.map(b => b.id === editingBundle.id ? newBundle : b)
        : [...bundles, newBundle];
      
      setBundles(updatedBundles);
      localStorage.setItem('serviceBundles', JSON.stringify(updatedBundles));
      setOpenDialog(false);
      setNotification({
        open: true,
        message: `Bundle ${editingBundle ? 'updated' : 'added'} successfully`,
        severity: 'success',
      });
    },
  });

  const handleDelete = (bundle) => {
    setConfirmDialog({
      open: true,
      title: 'Delete Bundle',
      message: `Are you sure you want to delete the bundle "${bundle.name}"? This action cannot be undone.`,
      action: () => {
        const updatedBundles = bundles.filter(b => b.id !== bundle.id);
        setBundles(updatedBundles);
        localStorage.setItem('serviceBundles', JSON.stringify(updatedBundles));
        setNotification({
          open: true,
          message: 'Bundle deleted successfully',
          severity: 'success',
        });
      },
    });
  };

  const handleEdit = (bundle) => {
    setEditingBundle(bundle);
    formik.setValues({
      name: bundle.name,
      description: bundle.description,
      price: bundle.price,
      features: bundle.features,
      validityPeriod: bundle.validityPeriod,
      autoRenew: bundle.autoRenew,
      discountPercentage: bundle.discountPercentage,
    });
    setOpenDialog(true);
  };

  const handleExport = () => {
    const data = JSON.stringify(bundles, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'service-bundles.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const handleImport = (event) => {
    const file = event.target.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const importedBundles = JSON.parse(e.target.result);
        if (Array.isArray(importedBundles)) {
          setBundles(importedBundles);
          localStorage.setItem('serviceBundles', JSON.stringify(importedBundles));
          setNotification({
            open: true,
            message: 'Bundles imported successfully',
            severity: 'success',
          });
        } else {
          throw new Error('Invalid data format');
        }
      } catch (error) {
        setNotification({
          open: true,
          message: 'Error importing bundles: Invalid file format',
          severity: 'error',
        });
      }
    };
    reader.readAsText(file);
  };

  const availableFeatures = JSON.parse(localStorage.getItem('serviceFeatures') || '[]');

  return (
    <Paper sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <BuildIcon sx={{ mr: 1 }} />
          Service Bundles
        </Typography>
        <Box>
          <Tooltip title="Export bundles">
            <IconButton onClick={handleExport} sx={{ mr: 1 }}>
              <DownloadIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Import bundles">
            <IconButton component="label" sx={{ mr: 1 }}>
              <UploadIcon />
              <input
                type="file"
                hidden
                accept=".json"
                onChange={handleImport}
              />
            </IconButton>
          </Tooltip>
          <Tooltip title="Refresh">
            <IconButton onClick={loadBundles} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Add new bundle">
            <IconButton
              onClick={() => {
                setEditingBundle(null);
                formik.resetForm();
                setOpenDialog(true);
              }}
            >
              <AddIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>
      <Grid container spacing={2}>
        {bundles.map((bundle) => (
          <Grid item xs={12} md={6} key={bundle.id}>
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom>
                  {bundle.name}
                </Typography>
                <Typography variant="body2" color="text.secondary" paragraph>
                  {bundle.description}
                </Typography>
                <Typography variant="h4" color="primary" gutterBottom>
                  ${bundle.price}
                  <Typography component="span" variant="body2" color="text.secondary">
                    /{bundle.validityPeriod} months
                  </Typography>
                </Typography>
                {bundle.discountPercentage > 0 && (
                  <Typography variant="body2" color="success.main" gutterBottom>
                    {bundle.discountPercentage}% discount applied
                  </Typography>
                )}
                <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
                  {bundle.features.map((feature, index) => (
                    <Chip
                      key={index}
                      label={feature}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  ))}
                </Stack>
                <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
                  <Button
                    startIcon={<EditIcon />}
                    variant="outlined"
                    size="small"
                    onClick={() => handleEdit(bundle)}
                  >
                    Edit
                  </Button>
                  <Button
                    startIcon={<DeleteIcon />}
                    variant="outlined"
                    color="error"
                    size="small"
                    onClick={() => handleDelete(bundle)}
                  >
                    Delete
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>{editingBundle ? 'Edit Service Bundle' : 'Create New Bundle'}</DialogTitle>
        <form onSubmit={formik.handleSubmit}>
          <DialogContent>
            <TextField
              fullWidth
              name="name"
              label="Bundle Name"
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
            <TextField
              fullWidth
              name="price"
              label="Price"
              type="number"
              margin="normal"
              value={formik.values.price}
              onChange={formik.handleChange}
              error={formik.touched.price && Boolean(formik.errors.price)}
              helperText={formik.touched.price && formik.errors.price}
              InputProps={{
                startAdornment: <AttachMoneyIcon sx={{ mr: 1, color: 'text.secondary' }} />,
              }}
            />
            <Typography variant="subtitle1" sx={{ mt: 2, mb: 1 }}>
              Features
            </Typography>
            <Autocomplete
              multiple
              options={availableFeatures.map(f => f.name)}
              value={formik.values.features}
              onChange={(_, newValue) => formik.setFieldValue('features', newValue)}
              renderInput={(params) => (
                <TextField
                  {...params}
                  error={formik.touched.features && Boolean(formik.errors.features)}
                  helperText={formik.touched.features && formik.errors.features}
                />
              )}
              sx={{ mb: 2 }}
            />
            <TextField
              fullWidth
              name="validityPeriod"
              label="Validity Period (months)"
              type="number"
              margin="normal"
              value={formik.values.validityPeriod}
              onChange={formik.handleChange}
              error={formik.touched.validityPeriod && Boolean(formik.errors.validityPeriod)}
              helperText={formik.touched.validityPeriod && formik.errors.validityPeriod}
            />
            <FormControlLabel
              control={
                <Switch
                  name="autoRenew"
                  checked={formik.values.autoRenew}
                  onChange={formik.handleChange}
                />
              }
              label="Auto-renew"
              sx={{ mt: 2 }}
            />
            <Typography gutterBottom sx={{ mt: 2 }}>
              Discount Percentage: {formik.values.discountPercentage}%
            </Typography>
            <Slider
              name="discountPercentage"
              value={formik.values.discountPercentage}
              onChange={(_, value) => formik.setFieldValue('discountPercentage', value)}
              min={0}
              max={100}
              step={5}
              marks
              valueLabelDisplay="auto"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
            <Button type="submit" variant="contained" color="primary">
              {editingBundle ? 'Update' : 'Create'}
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      <Dialog
        open={confirmDialog.open}
        onClose={() => setConfirmDialog({ ...confirmDialog, open: false })}
      >
        <MuiDialogTitle>{confirmDialog.title}</MuiDialogTitle>
        <MuiDialogContent>
          <DialogContentText>{confirmDialog.message}</DialogContentText>
        </MuiDialogContent>
        <MuiDialogActions>
          <Button onClick={() => setConfirmDialog({ ...confirmDialog, open: false })}>
            Cancel
          </Button>
          <Button
            onClick={() => {
              confirmDialog.action();
              setConfirmDialog({ ...confirmDialog, open: false });
            }}
            color="error"
            variant="contained"
          >
            Delete
          </Button>
        </MuiDialogActions>
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

// Backup Manager Component
const BackupManager = () => {
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [confirmDialog, setConfirmDialog] = useState({ open: false, title: '', message: '', action: null });

  const handleBackup = () => {
    try {
      const backupData = {
        features: JSON.parse(localStorage.getItem('serviceFeatures') || '[]'),
        tiers: JSON.parse(localStorage.getItem('serviceTiers') || '[]'),
        pricing: JSON.parse(localStorage.getItem('pricingConfig') || '{}'),
        bundles: JSON.parse(localStorage.getItem('serviceBundles') || '[]'),
      };

      const data = JSON.stringify(backupData, null, 2);
      const blob = new Blob([data], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `service-config-backup-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);

      setNotification({
        open: true,
        message: 'Backup created successfully',
        severity: 'success',
      });
    } catch (error) {
      setNotification({
        open: true,
        message: 'Error creating backup: ' + error.message,
        severity: 'error',
      });
    }
  };

  const validateBackupData = (data) => {
    const requiredKeys = ['features', 'tiers', 'pricing', 'bundles'];
    const missingKeys = requiredKeys.filter(key => !(key in data));
    
    if (missingKeys.length > 0) {
      throw new Error(`Invalid backup file: Missing required keys: ${missingKeys.join(', ')}`);
    }

    // Validate features
    if (!Array.isArray(data.features)) {
      throw new Error('Invalid backup file: Features must be an array');
    }

    // Validate tiers
    if (!Array.isArray(data.tiers)) {
      throw new Error('Invalid backup file: Tiers must be an array');
    }

    // Validate pricing
    if (typeof data.pricing !== 'object' || data.pricing === null) {
      throw new Error('Invalid backup file: Pricing must be an object');
    }

    // Validate bundles
    if (!Array.isArray(data.bundles)) {
      throw new Error('Invalid backup file: Bundles must be an array');
    }

    return true;
  };

  const handleRestore = (event) => {
    const file = event.target.files[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const backupData = JSON.parse(e.target.result);
        validateBackupData(backupData);

        setConfirmDialog({
          open: true,
          title: 'Confirm Restore',
          message: 'This will replace all current service configuration data. This action cannot be undone. Are you sure you want to proceed?',
          action: () => {
            localStorage.setItem('serviceFeatures', JSON.stringify(backupData.features));
            localStorage.setItem('serviceTiers', JSON.stringify(backupData.tiers));
            localStorage.setItem('pricingConfig', JSON.stringify(backupData.pricing));
            localStorage.setItem('serviceBundles', JSON.stringify(backupData.bundles));

            setNotification({
              open: true,
              message: 'Backup restored successfully. Please refresh the page to see the changes.',
              severity: 'success',
            });
          },
        });
      } catch (error) {
        setNotification({
          open: true,
          message: 'Error restoring backup: ' + error.message,
          severity: 'error',
        });
      }
    };
    reader.readAsText(file);
  };

  return (
    <Paper sx={{ p: 2, mb: 3 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">
          <BackupIcon sx={{ mr: 1 }} />
          Backup & Restore
        </Typography>
        <Tooltip title="Manage service configuration backups">
          <InfoIcon color="action" />
        </Tooltip>
      </Box>
      <Grid container spacing={2}>
        <Grid item xs={12} md={6}>
          <Button
            fullWidth
            variant="contained"
            startIcon={<BackupIcon />}
            onClick={handleBackup}
          >
            Create Backup
          </Button>
        </Grid>
        <Grid item xs={12} md={6}>
          <Button
            fullWidth
            variant="outlined"
            component="label"
            startIcon={<RestoreIcon />}
          >
            Restore from Backup
            <input
              type="file"
              hidden
              accept=".json"
              onChange={handleRestore}
            />
          </Button>
        </Grid>
      </Grid>

      <Dialog
        open={confirmDialog.open}
        onClose={() => setConfirmDialog({ ...confirmDialog, open: false })}
      >
        <MuiDialogTitle>{confirmDialog.title}</MuiDialogTitle>
        <MuiDialogContent>
          <DialogContentText>{confirmDialog.message}</DialogContentText>
        </MuiDialogContent>
        <MuiDialogActions>
          <Button onClick={() => setConfirmDialog({ ...confirmDialog, open: false })}>
            Cancel
          </Button>
          <Button
            onClick={() => {
              confirmDialog.action();
              setConfirmDialog({ ...confirmDialog, open: false });
            }}
            color="primary"
            variant="contained"
          >
            Restore
          </Button>
        </MuiDialogActions>
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

const ServiceDesigner = () => {
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Service Configuration
      </Typography>
      <Grid container spacing={3}>
        <Grid item xs={12}>
          <BackupManager />
        </Grid>
        <Grid item xs={12}>
          <FeatureFlagManager />
        </Grid>
        <Grid item xs={12}>
          <ServiceTierConfig />
        </Grid>
        <Grid item xs={12}>
          <PricingConfig />
        </Grid>
        <Grid item xs={12}>
          <ServiceBundle />
        </Grid>
      </Grid>
    </Box>
  );
};

export default ServiceDesigner; 