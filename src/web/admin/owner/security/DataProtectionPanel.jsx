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
} from '@mui/material';
import {
  Security as SecurityIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Add as AddIcon,
  History as HistoryIcon,
  Lock as LockIcon,
  Storage as StorageIcon,
  PrivacyTip as PrivacyTipIcon,
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
} from '@mui/icons-material';

// Mock data - Replace with API calls
const mockEncryptionSettings = [
  {
    id: 1,
    name: 'Database Encryption',
    status: 'Active',
    algorithm: 'AES-256',
    lastRotated: '2024-03-15',
    nextRotation: '2024-04-15',
  },
  {
    id: 2,
    name: 'File Storage',
    status: 'Active',
    algorithm: 'AES-256',
    lastRotated: '2024-03-10',
    nextRotation: '2024-04-10',
  },
  {
    id: 3,
    name: 'API Communications',
    status: 'Active',
    algorithm: 'TLS 1.3',
    lastRotated: '2024-03-01',
    nextRotation: '2024-04-01',
  },
];

const mockRetentionPolicies = [
  {
    id: 1,
    dataType: 'User Data',
    retentionPeriod: '2 years',
    deletionMethod: 'Secure Deletion',
    status: 'Active',
    lastReview: '2024-03-15',
  },
  {
    id: 2,
    dataType: 'Audit Logs',
    retentionPeriod: '1 year',
    deletionMethod: 'Archive & Delete',
    status: 'Active',
    lastReview: '2024-03-14',
  },
  {
    id: 3,
    dataType: 'Backup Data',
    retentionPeriod: '6 months',
    deletionMethod: 'Secure Deletion',
    status: 'Active',
    lastReview: '2024-03-13',
  },
];

const mockPrivacyControls = [
  {
    id: 1,
    name: 'Data Collection',
    status: 'Enabled',
    description: 'Collect user activity data',
    lastModified: '2024-03-15',
  },
  {
    id: 2,
    name: 'Data Sharing',
    status: 'Disabled',
    description: 'Share data with third parties',
    lastModified: '2024-03-14',
  },
  {
    id: 3,
    name: 'Analytics',
    status: 'Enabled',
    description: 'Enable usage analytics',
    lastModified: '2024-03-13',
  },
];

const DataProtectionPanel = () => {
  const [encryptionSettings, setEncryptionSettings] = useState(mockEncryptionSettings);
  const [retentionPolicies, setRetentionPolicies] = useState(mockRetentionPolicies);
  const [privacyControls, setPrivacyControls] = useState(mockPrivacyControls);
  const [selectedSetting, setSelectedSetting] = useState(null);
  const [showEncryptionDialog, setShowEncryptionDialog] = useState(false);
  const [showRetentionDialog, setShowRetentionDialog] = useState(false);
  const [showPrivacyDialog, setShowPrivacyDialog] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [activeTab, setActiveTab] = useState(0);
  const [keyRotationProgress, setKeyRotationProgress] = useState(0);

  const handleEditSetting = (setting) => {
    setSelectedSetting(setting);
    setShowEncryptionDialog(true);
  };

  const handleSaveSetting = () => {
    // Implement save logic
    setShowEncryptionDialog(false);
    setNotification({
      open: true,
      message: 'Encryption settings updated successfully',
      severity: 'success',
    });
  };

  const handleKeyRotation = () => {
    // Simulate key rotation progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += 10;
      setKeyRotationProgress(progress);
      if (progress >= 100) {
        clearInterval(interval);
        setNotification({
          open: true,
          message: 'Key rotation completed successfully',
          severity: 'success',
        });
      }
    }, 500);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
      case 'Enabled':
        return 'success';
      case 'Inactive':
      case 'Disabled':
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
        Data Protection Panel
      </Typography>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Encryption" />
          <Tab label="Retention" />
          <Tab label="Privacy" />
        </Tabs>
      </Paper>

      {/* Encryption Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <LockIcon sx={{ mr: 1 }} />
                  Encryption Management
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setShowEncryptionDialog(true)}
                >
                  Add Setting
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Algorithm</TableCell>
                      <TableCell>Last Rotated</TableCell>
                      <TableCell>Next Rotation</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {encryptionSettings.map((setting) => (
                      <TableRow key={setting.id}>
                        <TableCell>{setting.name}</TableCell>
                        <TableCell>
                          <Chip
                            label={setting.status}
                            color={getStatusColor(setting.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{setting.algorithm}</TableCell>
                        <TableCell>{setting.lastRotated}</TableCell>
                        <TableCell>{setting.nextRotation}</TableCell>
                        <TableCell>
                          <Tooltip title="Edit">
                            <IconButton onClick={() => handleEditSetting(setting)}>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Rotate Key">
                            <IconButton onClick={handleKeyRotation}>
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

      {/* Retention Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <StorageIcon sx={{ mr: 1 }} />
                  Data Retention Policies
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setShowRetentionDialog(true)}
                >
                  Add Policy
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Data Type</TableCell>
                      <TableCell>Retention Period</TableCell>
                      <TableCell>Deletion Method</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Last Review</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {retentionPolicies.map((policy) => (
                      <TableRow key={policy.id}>
                        <TableCell>{policy.dataType}</TableCell>
                        <TableCell>{policy.retentionPeriod}</TableCell>
                        <TableCell>{policy.deletionMethod}</TableCell>
                        <TableCell>
                          <Chip
                            label={policy.status}
                            color={getStatusColor(policy.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{policy.lastReview}</TableCell>
                        <TableCell>
                          <Tooltip title="Edit">
                            <IconButton>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Review">
                            <IconButton>
                              <HistoryIcon />
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

      {/* Privacy Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <PrivacyTipIcon sx={{ mr: 1 }} />
                  Privacy Controls
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setShowPrivacyDialog(true)}
                >
                  Add Control
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Description</TableCell>
                      <TableCell>Last Modified</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {privacyControls.map((control) => (
                      <TableRow key={control.id}>
                        <TableCell>{control.name}</TableCell>
                        <TableCell>
                          <Chip
                            label={control.status}
                            color={getStatusColor(control.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>{control.description}</TableCell>
                        <TableCell>{control.lastModified}</TableCell>
                        <TableCell>
                          <Tooltip title="Edit">
                            <IconButton>
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Toggle">
                            <IconButton>
                              <Switch
                                size="small"
                                checked={control.status === 'Enabled'}
                                onChange={() => {/* Toggle logic */}}
                              />
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

      {/* Encryption Dialog */}
      <Dialog open={showEncryptionDialog} onClose={() => setShowEncryptionDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <LockIcon sx={{ mr: 1 }} />
          {selectedSetting ? 'Edit Encryption Setting' : 'Add New Encryption Setting'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                defaultValue={selectedSetting?.name}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Algorithm</InputLabel>
                <Select defaultValue={selectedSetting?.algorithm}>
                  <MenuItem value="AES-256">AES-256</MenuItem>
                  <MenuItem value="AES-192">AES-192</MenuItem>
                  <MenuItem value="AES-128">AES-128</MenuItem>
                  <MenuItem value="TLS 1.3">TLS 1.3</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControlLabel
                control={<Switch defaultChecked={selectedSetting?.status === 'Active'} />}
                label="Active"
              />
            </Grid>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Key Rotation Schedule
              </Typography>
              <Slider
                defaultValue={30}
                min={1}
                max={90}
                marks
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${value} days`}
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowEncryptionDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveSetting} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>

      {/* Key Rotation Progress */}
      {keyRotationProgress > 0 && (
        <Dialog open={keyRotationProgress < 100} maxWidth="sm" fullWidth>
          <DialogTitle>Rotating Encryption Key</DialogTitle>
          <DialogContent>
            <Box sx={{ mt: 2 }}>
              <LinearProgress variant="determinate" value={keyRotationProgress} />
              <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                {keyRotationProgress}% complete
              </Typography>
            </Box>
          </DialogContent>
        </Dialog>
      )}

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

export default DataProtectionPanel; 