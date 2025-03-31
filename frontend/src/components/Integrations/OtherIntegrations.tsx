import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  Card,
  CardContent,
  CardActions,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Divider,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Switch,
  FormControlLabel,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Slack as SlackIcon,
  Email as EmailIcon,
  Notifications as NotificationsIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

interface Integration {
  id: string;
  name: string;
  icon: React.ReactNode;
  isEnabled: boolean;
  settings: {
    [key: string]: any;
  };
  lastSync?: string;
  error?: string;
}

const defaultIntegrations: Integration[] = [
  {
    id: 'slack',
    name: 'Slack',
    icon: <SlackIcon />,
    isEnabled: false,
    settings: {
      webhookUrl: '',
      channel: '',
      notifications: {
        pullRequests: true,
        issues: true,
        comments: true,
      },
    },
  },
  {
    id: 'email',
    name: 'Email',
    icon: <EmailIcon />,
    isEnabled: false,
    settings: {
      smtpServer: '',
      smtpPort: '',
      username: '',
      password: '',
      fromAddress: '',
      recipients: [],
      notifications: {
        pullRequests: true,
        issues: true,
        comments: true,
      },
    },
  },
];

const OtherIntegrations: React.FC = () => {
  const [integrations, setIntegrations] = useState<Integration[]>(defaultIntegrations);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openSettings, setOpenSettings] = useState(false);
  const [selectedIntegration, setSelectedIntegration] = useState<Integration | null>(null);
  const [settings, setSettings] = useState<any>({});

  useEffect(() => {
    loadIntegrations();
  }, []);

  const loadIntegrations = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/integrations');
      const data = await response.json();
      setIntegrations(prev => prev.map(integration => ({
        ...integration,
        ...data[integration.id],
      })));
    } catch (err) {
      setError('Failed to load integrations');
    } finally {
      setLoading(false);
    }
  };

  const handleToggleIntegration = async (integrationId: string) => {
    try {
      const integration = integrations.find(i => i.id === integrationId);
      if (!integration) return;

      await fetch(`/api/integrations/${integrationId}/toggle`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ enabled: !integration.isEnabled }),
      });

      setIntegrations(prev => prev.map(i =>
        i.id === integrationId
          ? { ...i, isEnabled: !i.isEnabled }
          : i
      ));
    } catch (err) {
      setError(`Failed to toggle ${integrationId} integration`);
    }
  };

  const handleOpenSettings = (integration: Integration) => {
    setSelectedIntegration(integration);
    setSettings(integration.settings);
    setOpenSettings(true);
  };

  const handleSaveSettings = async () => {
    if (!selectedIntegration) return;

    try {
      await fetch(`/api/integrations/${selectedIntegration.id}/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });

      setIntegrations(prev => prev.map(i =>
        i.id === selectedIntegration.id
          ? { ...i, settings }
          : i
      ));

      setOpenSettings(false);
    } catch (err) {
      setError('Failed to save settings');
    }
  };

  const handleTestConnection = async (integrationId: string) => {
    try {
      const response = await fetch(`/api/integrations/${integrationId}/test`, {
        method: 'POST',
      });
      const data = await response.json();
      
      if (data.success) {
        setIntegrations(prev => prev.map(i =>
          i.id === integrationId
            ? { ...i, error: undefined }
            : i
        ));
      } else {
        setIntegrations(prev => prev.map(i =>
          i.id === integrationId
            ? { ...i, error: data.error }
            : i
        ));
      }
    } catch (err) {
      setError(`Failed to test ${integrationId} connection`);
    }
  };

  const renderSettingsFields = () => {
    if (!selectedIntegration) return null;

    switch (selectedIntegration.id) {
      case 'slack':
        return (
          <>
            <TextField
              autoFocus
              margin="dense"
              label="Webhook URL"
              fullWidth
              value={settings.webhookUrl || ''}
              onChange={(e) => setSettings({ ...settings, webhookUrl: e.target.value })}
            />
            <TextField
              margin="dense"
              label="Channel"
              fullWidth
              value={settings.channel || ''}
              onChange={(e) => setSettings({ ...settings, channel: e.target.value })}
            />
            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
              Notifications
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.notifications?.pullRequests || false}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: {
                      ...settings.notifications,
                      pullRequests: e.target.checked,
                    },
                  })
                }
              }
              label="Pull Requests"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={settings.notifications?.issues || false}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: {
                      ...settings.notifications,
                      issues: e.target.checked,
                    },
                  })
                }
              }
              label="Issues"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={settings.notifications?.comments || false}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: {
                      ...settings.notifications,
                      comments: e.target.checked,
                    },
                  })
                }
              }
              label="Comments"
            />
          </>
        );
      case 'email':
        return (
          <>
            <TextField
              autoFocus
              margin="dense"
              label="SMTP Server"
              fullWidth
              value={settings.smtpServer || ''}
              onChange={(e) => setSettings({ ...settings, smtpServer: e.target.value })}
            />
            <TextField
              margin="dense"
              label="SMTP Port"
              fullWidth
              value={settings.smtpPort || ''}
              onChange={(e) => setSettings({ ...settings, smtpPort: e.target.value })}
            />
            <TextField
              margin="dense"
              label="Username"
              fullWidth
              value={settings.username || ''}
              onChange={(e) => setSettings({ ...settings, username: e.target.value })}
            />
            <TextField
              margin="dense"
              label="Password"
              type="password"
              fullWidth
              value={settings.password || ''}
              onChange={(e) => setSettings({ ...settings, password: e.target.value })}
            />
            <TextField
              margin="dense"
              label="From Address"
              fullWidth
              value={settings.fromAddress || ''}
              onChange={(e) => setSettings({ ...settings, fromAddress: e.target.value })}
            />
            <FormControl fullWidth margin="dense">
              <InputLabel>Recipients</InputLabel>
              <Select
                multiple
                value={settings.recipients || []}
                label="Recipients"
                onChange={(e) => setSettings({ ...settings, recipients: e.target.value })}
              >
                <MenuItem value="team@example.com">Team</MenuItem>
                <MenuItem value="managers@example.com">Managers</MenuItem>
                <MenuItem value="stakeholders@example.com">Stakeholders</MenuItem>
              </Select>
            </FormControl>
            <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
              Notifications
            </Typography>
            <FormControlLabel
              control={
                <Switch
                  checked={settings.notifications?.pullRequests || false}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: {
                      ...settings.notifications,
                      pullRequests: e.target.checked,
                    },
                  })
                }
              }
              label="Pull Requests"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={settings.notifications?.issues || false}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: {
                      ...settings.notifications,
                      issues: e.target.checked,
                    },
                  })
                }
              }
              label="Issues"
            />
            <FormControlLabel
              control={
                <Switch
                  checked={settings.notifications?.comments || false}
                  onChange={(e) => setSettings({
                    ...settings,
                    notifications: {
                      ...settings.notifications,
                      comments: e.target.checked,
                    },
                  })
                }
              }
              label="Comments"
            />
          </>
        );
      default:
        return null;
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }} onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {integrations.map((integration) => (
          <Grid item xs={12} md={6} key={integration.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {integration.icon}
                  <Typography variant="h6" sx={{ ml: 1 }}>
                    {integration.name}
                  </Typography>
                  <Chip
                    icon={integration.isEnabled ? <CheckCircleIcon /> : <ErrorIcon />}
                    label={integration.isEnabled ? 'Enabled' : 'Disabled'}
                    color={integration.isEnabled ? 'success' : 'error'}
                    size="small"
                    sx={{ ml: 2 }}
                  />
                </Box>

                {integration.isEnabled && (
                  <>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Last synced: {integration.lastSync ? new Date(integration.lastSync).toLocaleString() : 'Never'}
                    </Typography>
                    {integration.error && (
                      <Alert severity="error" sx={{ mt: 2 }}>
                        {integration.error}
                      </Alert>
                    )}
                  </>
                )}
              </CardContent>
              <CardActions>
                <FormControlLabel
                  control={
                    <Switch
                      checked={integration.isEnabled}
                      onChange={() => handleToggleIntegration(integration.id)}
                    />
                  }
                  label="Enable"
                />
                <Button
                  startIcon={<SettingsIcon />}
                  onClick={() => handleOpenSettings(integration)}
                >
                  Settings
                </Button>
                {integration.isEnabled && (
                  <Button
                    color="primary"
                    onClick={() => handleTestConnection(integration.id)}
                  >
                    Test Connection
                  </Button>
                )}
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Settings Dialog */}
      <Dialog open={openSettings} onClose={() => setOpenSettings(false)} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedIntegration?.name} Settings
        </DialogTitle>
        <DialogContent>
          {renderSettingsFields()}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenSettings(false)}>Cancel</Button>
          <Button onClick={handleSaveSettings} variant="contained">
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default OtherIntegrations; 