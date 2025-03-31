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
  Store as StoreIcon,
  Extension as ExtensionIcon,
  MonetizationOn as MonetizationOnIcon,
  BugReport as BugReportIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';

// Mock data - Replace with API calls
const mockExtensions = [
  {
    id: 1,
    name: 'Advanced Analytics',
    developer: 'TechCorp Inc.',
    version: '1.2.0',
    status: 'Pending Review',
    revenue: 15000,
    downloads: 1200,
    rating: 4.8,
    lastUpdated: '2024-03-15',
  },
  {
    id: 2,
    name: 'AI Image Generator',
    developer: 'AI Solutions Ltd',
    version: '2.1.0',
    status: 'Active',
    revenue: 25000,
    downloads: 2500,
    rating: 4.9,
    lastUpdated: '2024-03-14',
  },
  {
    id: 3,
    name: 'Data Export Tool',
    developer: 'DataFlow Systems',
    version: '1.0.0',
    status: 'Rejected',
    revenue: 0,
    downloads: 0,
    rating: 0,
    lastUpdated: '2024-03-13',
  },
];

const mockRevenueSharing = {
  tiers: [
    {
      name: 'Basic',
      platformShare: 30,
      developerShare: 70,
      minimumRevenue: 0,
    },
    {
      name: 'Premium',
      platformShare: 25,
      developerShare: 75,
      minimumRevenue: 10000,
    },
    {
      name: 'Enterprise',
      platformShare: 20,
      developerShare: 80,
      minimumRevenue: 50000,
    },
  ],
  totalRevenue: 50000,
  totalPayouts: 35000,
  pendingPayouts: 5000,
};

const mockTestResults = {
  extensions: [
    {
      id: 1,
      name: 'Advanced Analytics',
      securityScore: 95,
      performanceScore: 90,
      compatibilityScore: 100,
      issues: [
        {
          type: 'Performance',
          description: 'High memory usage during data processing',
          severity: 'Medium',
        },
      ],
      lastTested: '2024-03-15',
    },
    {
      id: 2,
      name: 'AI Image Generator',
      securityScore: 100,
      performanceScore: 95,
      compatibilityScore: 95,
      issues: [],
      lastTested: '2024-03-14',
    },
  ],
  metrics: {
    totalExtensions: 2,
    passingExtensions: 1,
    failingExtensions: 1,
    averageSecurityScore: 97.5,
  },
};

const MarketplaceManagement = () => {
  const [extensions, setExtensions] = useState(mockExtensions);
  const [revenueSharing, setRevenueSharing] = useState(mockRevenueSharing);
  const [testResults, setTestResults] = useState(mockTestResults);
  const [selectedExtension, setSelectedExtension] = useState(null);
  const [showExtensionDialog, setShowExtensionDialog] = useState(false);
  const [showRevenueDialog, setShowRevenueDialog] = useState(false);
  const [showTestDialog, setShowTestDialog] = useState(false);
  const [notification, setNotification] = useState({ open: false, message: '', severity: 'success' });
  const [activeTab, setActiveTab] = useState(0);

  const handleReviewExtension = (extension) => {
    setSelectedExtension(extension);
    setShowExtensionDialog(true);
  };

  const handleSaveExtension = () => {
    // Implement save logic
    setShowExtensionDialog(false);
    setNotification({
      open: true,
      message: 'Extension review completed successfully',
      severity: 'success',
    });
  };

  const handleSaveRevenueSharing = () => {
    // Implement save logic
    setShowRevenueDialog(false);
    setNotification({
      open: true,
      message: 'Revenue sharing configuration updated successfully',
      severity: 'success',
    });
  };

  const handleRunTests = () => {
    // Implement test logic
    setShowTestDialog(false);
    setNotification({
      open: true,
      message: 'Extension tests completed successfully',
      severity: 'success',
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Active':
        return 'success';
      case 'Pending Review':
        return 'warning';
      case 'Rejected':
        return 'error';
      default:
        return 'default';
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'High':
        return 'error';
      case 'Medium':
        return 'warning';
      case 'Low':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Marketplace Management
      </Typography>

      {/* Tabs */}
      <Paper sx={{ mb: 3 }}>
        <Tabs value={activeTab} onChange={(e, newValue) => setActiveTab(newValue)}>
          <Tab label="Extensions" />
          <Tab label="Revenue Sharing" />
          <Tab label="Testing" />
        </Tabs>
      </Paper>

      {/* Extensions Tab */}
      {activeTab === 0 && (
        <Grid container spacing={3}>
          <Grid item xs={12}>
            <Paper sx={{ p: 2 }}>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                <Typography variant="h6">
                  <ExtensionIcon sx={{ mr: 1 }} />
                  Extension Management
                </Typography>
                <Button
                  variant="contained"
                  startIcon={<AddIcon />}
                  onClick={() => setShowExtensionDialog(true)}
                >
                  Add Extension
                </Button>
              </Box>
              <TableContainer>
                <Table>
                  <TableHead>
                    <TableRow>
                      <TableCell>Name</TableCell>
                      <TableCell>Developer</TableCell>
                      <TableCell>Version</TableCell>
                      <TableCell>Status</TableCell>
                      <TableCell>Revenue</TableCell>
                      <TableCell>Downloads</TableCell>
                      <TableCell>Rating</TableCell>
                      <TableCell>Last Updated</TableCell>
                      <TableCell>Actions</TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {extensions.map((extension) => (
                      <TableRow key={extension.id}>
                        <TableCell>{extension.name}</TableCell>
                        <TableCell>{extension.developer}</TableCell>
                        <TableCell>{extension.version}</TableCell>
                        <TableCell>
                          <Chip
                            label={extension.status}
                            color={getStatusColor(extension.status)}
                            size="small"
                          />
                        </TableCell>
                        <TableCell>${extension.revenue.toLocaleString()}</TableCell>
                        <TableCell>{extension.downloads.toLocaleString()}</TableCell>
                        <TableCell>{extension.rating}</TableCell>
                        <TableCell>{extension.lastUpdated}</TableCell>
                        <TableCell>
                          <Tooltip title="Review">
                            <IconButton onClick={() => handleReviewExtension(extension)}>
                              <CheckCircleIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit">
                            <IconButton>
                              <EditIcon />
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

      {/* Revenue Sharing Tab */}
      {activeTab === 1 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardHeader
                title="Revenue Overview"
                avatar={<MonetizationOnIcon />}
              />
              <CardContent>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box>
                    <Typography variant="body2">Total Revenue</Typography>
                    <Typography variant="h6">${revenueSharing.totalRevenue.toLocaleString()}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2">Total Payouts</Typography>
                    <Typography variant="h6">${revenueSharing.totalPayouts.toLocaleString()}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2">Pending Payouts</Typography>
                    <Typography variant="h6">${revenueSharing.pendingPayouts.toLocaleString()}</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={8}>
            <Card>
              <CardHeader
                title="Revenue Sharing Tiers"
                avatar={<BalanceIcon />}
                action={
                  <Button
                    startIcon={<EditIcon />}
                    onClick={() => setShowRevenueDialog(true)}
                  >
                    Edit Tiers
                  </Button>
                }
              />
              <CardContent>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Tier</TableCell>
                        <TableCell>Platform Share</TableCell>
                        <TableCell>Developer Share</TableCell>
                        <TableCell>Minimum Revenue</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {revenueSharing.tiers.map((tier) => (
                        <TableRow key={tier.name}>
                          <TableCell>{tier.name}</TableCell>
                          <TableCell>{tier.platformShare}%</TableCell>
                          <TableCell>{tier.developerShare}%</TableCell>
                          <TableCell>${tier.minimumRevenue.toLocaleString()}</TableCell>
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

      {/* Testing Tab */}
      {activeTab === 2 && (
        <Grid container spacing={3}>
          <Grid item xs={12} md={4}>
            <Card>
              <CardHeader
                title="Test Results Overview"
                avatar={<BugReportIcon />}
              />
              <CardContent>
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Box>
                    <Typography variant="body2">Total Extensions</Typography>
                    <Typography variant="h6">{testResults.metrics.totalExtensions}</Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2">Passing Extensions</Typography>
                    <Typography variant="h6" color="success.main">
                      {testResults.metrics.passingExtensions}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2">Failing Extensions</Typography>
                    <Typography variant="h6" color="error.main">
                      {testResults.metrics.failingExtensions}
                    </Typography>
                  </Box>
                  <Box>
                    <Typography variant="body2">Average Security Score</Typography>
                    <Typography variant="h6">{testResults.metrics.averageSecurityScore}</Typography>
                  </Box>
                </Box>
              </CardContent>
            </Card>
          </Grid>
          <Grid item xs={12} md={8}>
            <Card>
              <CardHeader
                title="Extension Test Results"
                avatar={<SecurityIcon />}
                action={
                  <Button
                    startIcon={<RefreshIcon />}
                    onClick={() => setShowTestDialog(true)}
                  >
                    Run Tests
                  </Button>
                }
              />
              <CardContent>
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Extension</TableCell>
                        <TableCell>Security Score</TableCell>
                        <TableCell>Performance Score</TableCell>
                        <TableCell>Compatibility Score</TableCell>
                        <TableCell>Issues</TableCell>
                        <TableCell>Last Tested</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {testResults.extensions.map((extension) => (
                        <TableRow key={extension.id}>
                          <TableCell>{extension.name}</TableCell>
                          <TableCell>{extension.securityScore}</TableCell>
                          <TableCell>{extension.performanceScore}</TableCell>
                          <TableCell>{extension.compatibilityScore}</TableCell>
                          <TableCell>
                            {extension.issues.map((issue) => (
                              <Chip
                                key={issue.description}
                                label={issue.severity}
                                color={getSeverityColor(issue.severity)}
                                size="small"
                                sx={{ mr: 0.5 }}
                              />
                            ))}
                          </TableCell>
                          <TableCell>{extension.lastTested}</TableCell>
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

      {/* Extension Review Dialog */}
      <Dialog open={showExtensionDialog} onClose={() => setShowExtensionDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <ExtensionIcon sx={{ mr: 1 }} />
          Review Extension: {selectedExtension?.name}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <Typography variant="subtitle2" gutterBottom>
                Extension Details
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                <Typography variant="body2">Developer: {selectedExtension?.developer}</Typography>
                <Typography variant="body2">Version: {selectedExtension?.version}</Typography>
                <Typography variant="body2">Downloads: {selectedExtension?.downloads.toLocaleString()}</Typography>
                <Typography variant="body2">Rating: {selectedExtension?.rating}</Typography>
              </Box>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select defaultValue={selectedExtension?.status}>
                  <MenuItem value="Active">Approve</MenuItem>
                  <MenuItem value="Rejected">Reject</MenuItem>
                  <MenuItem value="Pending Review">Request Changes</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Review Notes"
                placeholder="Enter your review notes here..."
              />
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowExtensionDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveExtension} variant="contained">
            Submit Review
          </Button>
        </DialogActions>
      </Dialog>

      {/* Revenue Sharing Dialog */}
      <Dialog open={showRevenueDialog} onClose={() => setShowRevenueDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          <MonetizationOnIcon sx={{ mr: 1 }} />
          Configure Revenue Sharing Tiers
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            {revenueSharing.tiers.map((tier, index) => (
              <Grid item xs={12} key={tier.name}>
                <Typography variant="subtitle2" gutterBottom>
                  {tier.name} Tier
                </Typography>
                <Grid container spacing={2}>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Platform Share (%)"
                      type="number"
                      defaultValue={tier.platformShare}
                    />
                  </Grid>
                  <Grid item xs={6}>
                    <TextField
                      fullWidth
                      label="Developer Share (%)"
                      type="number"
                      defaultValue={tier.developerShare}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Minimum Revenue ($)"
                      type="number"
                      defaultValue={tier.minimumRevenue}
                    />
                  </Grid>
                </Grid>
              </Grid>
            ))}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowRevenueDialog(false)}>Cancel</Button>
          <Button onClick={handleSaveRevenueSharing} variant="contained">
            Save Configuration
          </Button>
        </DialogActions>
      </Dialog>

      {/* Test Dialog */}
      <Dialog open={showTestDialog} onClose={() => setShowTestDialog(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          <BugReportIcon sx={{ mr: 1 }} />
          Run Extension Tests
        </DialogTitle>
        <DialogContent>
          <Box sx={{ mt: 2 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              This will run comprehensive tests on all extensions, including:
            </Typography>
            <List>
              <ListItem>
                <ListItemText primary="Security Testing" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Performance Testing" />
              </ListItem>
              <ListItem>
                <ListItemText primary="Compatibility Testing" />
              </ListItem>
            </List>
          </Box>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTestDialog(false)}>Cancel</Button>
          <Button onClick={handleRunTests} variant="contained">
            Run Tests
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

export default MarketplaceManagement; 