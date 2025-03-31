import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Divider,
  Alert,
  LinearProgress,
  Card,
  CardContent,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Chip
} from '@mui/material';
import {
  Save as SaveIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  Security as SecurityIcon,
  Notifications as NotificationsIcon,
  Storage as StorageIcon,
  Api as ApiIcon
} from '@mui/icons-material';

interface ApiKey {
  id: string;
  name: string;
  created_at: string;
  last_used: string;
}

interface NotificationRule {
  id: string;
  name: string;
  type: string;
  threshold: number;
  enabled: boolean;
}

const Settings: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [settings, setSettings] = useState({
    maxConcurrentRequests: 100,
    requestTimeout: 30,
    retryAttempts: 3,
    enableLogging: true,
    enableMetrics: true,
    enableNotifications: true,
    defaultModel: 'gpt-4',
    costThreshold: 1000,
    performanceThreshold: 2000
  });
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [notificationRules, setNotificationRules] = useState<NotificationRule[]>([]);
  const [openApiKeyDialog, setOpenApiKeyDialog] = useState(false);
  const [openNotificationDialog, setOpenNotificationDialog] = useState(false);
  const [newApiKey, setNewApiKey] = useState({ name: '' });
  const [newNotificationRule, setNewNotificationRule] = useState({
    name: '',
    type: 'cost',
    threshold: 0,
    enabled: true
  });

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/settings');
      const data = await response.json();
      setSettings(data.settings);
      setApiKeys(data.api_keys);
      setNotificationRules(data.notification_rules);
    } catch (err) {
      setError('Failed to fetch settings');
    } finally {
      setLoading(false);
    }
  };

  const handleSettingChange = (field: string) => (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.type === 'checkbox' ? event.target.checked : Number(event.target.value);
    setSettings(prev => ({ ...prev, [field]: value }));
  };

  const handleSaveSettings = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/settings', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });
      if (response.ok) {
        setSuccess('Settings saved successfully');
      } else {
        throw new Error('Failed to save settings');
      }
    } catch (err) {
      setError('Failed to save settings');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateApiKey = async () => {
    try {
      const response = await fetch('/api/settings/api-keys', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newApiKey),
      });
      if (response.ok) {
        const data = await response.json();
        setApiKeys(prev => [...prev, data]);
        setOpenApiKeyDialog(false);
        setNewApiKey({ name: '' });
        setSuccess('API key created successfully');
      } else {
        throw new Error('Failed to create API key');
      }
    } catch (err) {
      setError('Failed to create API key');
    }
  };

  const handleDeleteApiKey = async (id: string) => {
    try {
      const response = await fetch(`/api/settings/api-keys/${id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setApiKeys(prev => prev.filter(key => key.id !== id));
        setSuccess('API key deleted successfully');
      } else {
        throw new Error('Failed to delete API key');
      }
    } catch (err) {
      setError('Failed to delete API key');
    }
  };

  const handleCreateNotificationRule = async () => {
    try {
      const response = await fetch('/api/settings/notification-rules', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newNotificationRule),
      });
      if (response.ok) {
        const data = await response.json();
        setNotificationRules(prev => [...prev, data]);
        setOpenNotificationDialog(false);
        setNewNotificationRule({
          name: '',
          type: 'cost',
          threshold: 0,
          enabled: true
        });
        setSuccess('Notification rule created successfully');
      } else {
        throw new Error('Failed to create notification rule');
      }
    } catch (err) {
      setError('Failed to create notification rule');
    }
  };

  const handleDeleteNotificationRule = async (id: string) => {
    try {
      const response = await fetch(`/api/settings/notification-rules/${id}`, {
        method: 'DELETE',
      });
      if (response.ok) {
        setNotificationRules(prev => prev.filter(rule => rule.id !== id));
        setSuccess('Notification rule deleted successfully');
      } else {
        throw new Error('Failed to delete notification rule');
      }
    } catch (err) {
      setError('Failed to delete notification rule');
    }
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 4 }}>
        <Grid container spacing={3}>
          {/* Header */}
          <Grid item xs={12}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
              <Typography variant="h4">Settings</Typography>
              <Box>
                <Tooltip title="Refresh">
                  <IconButton onClick={fetchSettings}>
                    <RefreshIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Save Changes">
                  <IconButton onClick={handleSaveSettings}>
                    <SaveIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>
          </Grid>

          {/* Error Alert */}
          {error && (
            <Grid item xs={12}>
              <Alert severity="error" onClose={() => setError(null)}>
                {error}
              </Alert>
            </Grid>
          )}

          {/* Success Alert */}
          {success && (
            <Grid item xs={12}>
              <Alert severity="success" onClose={() => setSuccess(null)}>
                {success}
              </Alert>
            </Grid>
          )}

          {/* General Settings */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <StorageIcon sx={{ mr: 1 }} />
                  <Typography variant="h6">General Settings</Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Max Concurrent Requests"
                      type="number"
                      value={settings.maxConcurrentRequests}
                      onChange={handleSettingChange('maxConcurrentRequests')}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Request Timeout (seconds)"
                      type="number"
                      value={settings.requestTimeout}
                      onChange={handleSettingChange('requestTimeout')}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Retry Attempts"
                      type="number"
                      value={settings.retryAttempts}
                      onChange={handleSettingChange('retryAttempts')}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Default Model"
                      value={settings.defaultModel}
                      onChange={handleSettingChange('defaultModel')}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* Monitoring Settings */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <SecurityIcon sx={{ mr: 1 }} />
                  <Typography variant="h6">Monitoring Settings</Typography>
                </Box>
                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.enableLogging}
                          onChange={handleSettingChange('enableLogging')}
                        />
                      }
                      label="Enable Logging"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.enableMetrics}
                          onChange={handleSettingChange('enableMetrics')}
                        />
                      }
                      label="Enable Metrics Collection"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <FormControlLabel
                      control={
                        <Switch
                          checked={settings.enableNotifications}
                          onChange={handleSettingChange('enableNotifications')}
                        />
                      }
                      label="Enable Notifications"
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Cost Threshold ($)"
                      type="number"
                      value={settings.costThreshold}
                      onChange={handleSettingChange('costThreshold')}
                    />
                  </Grid>
                  <Grid item xs={12}>
                    <TextField
                      fullWidth
                      label="Performance Threshold (ms)"
                      type="number"
                      value={settings.performanceThreshold}
                      onChange={handleSettingChange('performanceThreshold')}
                    />
                  </Grid>
                </Grid>
              </CardContent>
            </Card>
          </Grid>

          {/* API Keys */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <ApiIcon sx={{ mr: 1 }} />
                  <Typography variant="h6">API Keys</Typography>
                </Box>
                <List>
                  {apiKeys.map((key) => (
                    <ListItem key={key.id}>
                      <ListItemText
                        primary={key.name}
                        secondary={`Created: ${new Date(key.created_at).toLocaleDateString()} | Last Used: ${new Date(key.last_used).toLocaleDateString()}`}
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          aria-label="delete"
                          onClick={() => handleDeleteApiKey(key.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
                <Button
                  startIcon={<AddIcon />}
                  onClick={() => setOpenApiKeyDialog(true)}
                  sx={{ mt: 2 }}
                >
                  Add API Key
                </Button>
              </CardContent>
            </Card>
          </Grid>

          {/* Notification Rules */}
          <Grid item xs={12} md={6}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  <NotificationsIcon sx={{ mr: 1 }} />
                  <Typography variant="h6">Notification Rules</Typography>
                </Box>
                <List>
                  {notificationRules.map((rule) => (
                    <ListItem key={rule.id}>
                      <ListItemText
                        primary={rule.name}
                        secondary={`Type: ${rule.type} | Threshold: ${rule.threshold} | Status: ${rule.enabled ? 'Enabled' : 'Disabled'}`}
                      />
                      <ListItemSecondaryAction>
                        <IconButton
                          edge="end"
                          aria-label="delete"
                          onClick={() => handleDeleteNotificationRule(rule.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </ListItemSecondaryAction>
                    </ListItem>
                  ))}
                </List>
                <Button
                  startIcon={<AddIcon />}
                  onClick={() => setOpenNotificationDialog(true)}
                  sx={{ mt: 2 }}
                >
                  Add Notification Rule
                </Button>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* API Key Dialog */}
        <Dialog open={openApiKeyDialog} onClose={() => setOpenApiKeyDialog(false)}>
          <DialogTitle>Create New API Key</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Key Name"
              fullWidth
              value={newApiKey.name}
              onChange={(e) => setNewApiKey({ name: e.target.value })}
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenApiKeyDialog(false)}>Cancel</Button>
            <Button onClick={handleCreateApiKey} variant="contained" color="primary">
              Create
            </Button>
          </DialogActions>
        </Dialog>

        {/* Notification Rule Dialog */}
        <Dialog open={openNotificationDialog} onClose={() => setOpenNotificationDialog(false)}>
          <DialogTitle>Create New Notification Rule</DialogTitle>
          <DialogContent>
            <TextField
              autoFocus
              margin="dense"
              label="Rule Name"
              fullWidth
              value={newNotificationRule.name}
              onChange={(e) => setNewNotificationRule({ ...newNotificationRule, name: e.target.value })}
            />
            <TextField
              margin="dense"
              label="Type"
              fullWidth
              value={newNotificationRule.type}
              onChange={(e) => setNewNotificationRule({ ...newNotificationRule, type: e.target.value })}
            />
            <TextField
              margin="dense"
              label="Threshold"
              type="number"
              fullWidth
              value={newNotificationRule.threshold}
              onChange={(e) => setNewNotificationRule({ ...newNotificationRule, threshold: Number(e.target.value) })}
            />
            <FormControlLabel
              control={
                <Switch
                  checked={newNotificationRule.enabled}
                  onChange={(e) => setNewNotificationRule({ ...newNotificationRule, enabled: e.target.checked })}
                />
              }
              label="Enabled"
            />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpenNotificationDialog(false)}>Cancel</Button>
            <Button onClick={handleCreateNotificationRule} variant="contained" color="primary">
              Create
            </Button>
          </DialogActions>
        </Dialog>
      </Box>
    </Container>
  );
};

export default Settings; 