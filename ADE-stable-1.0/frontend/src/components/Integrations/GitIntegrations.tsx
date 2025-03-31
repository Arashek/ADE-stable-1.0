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
  CircularProgress,
} from '@mui/material';
import {
  GitHub as GitHubIcon,
  GitLab as GitLabIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

interface GitProvider {
  id: string;
  name: string;
  icon: React.ReactNode;
  isConnected: boolean;
  repositories: Repository[];
  lastSync?: string;
  error?: string;
}

interface Repository {
  id: string;
  name: string;
  fullName: string;
  private: boolean;
  defaultBranch: string;
  lastUpdated: string;
}

const GitIntegrations: React.FC = () => {
  const [providers, setProviders] = useState<GitProvider[]>([
    {
      id: 'github',
      name: 'GitHub',
      icon: <GitHubIcon />,
      isConnected: false,
      repositories: [],
    },
    {
      id: 'gitlab',
      name: 'GitLab',
      icon: <GitLabIcon />,
      isConnected: false,
      repositories: [],
    },
  ]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openSettings, setOpenSettings] = useState(false);
  const [selectedProvider, setSelectedProvider] = useState<GitProvider | null>(null);
  const [settings, setSettings] = useState({
    accessToken: '',
    organization: '',
    webhookSecret: '',
  });

  useEffect(() => {
    checkConnections();
  }, []);

  const checkConnections = async () => {
    setLoading(true);
    try {
      // Check GitHub connection
      const githubResponse = await fetch('/api/github/status');
      const githubData = await githubResponse.json();
      
      // Check GitLab connection
      const gitlabResponse = await fetch('/api/gitlab/status');
      const gitlabData = await gitlabResponse.json();

      setProviders(prev => prev.map(provider => {
        if (provider.id === 'github') {
          return {
            ...provider,
            isConnected: githubData.connected,
            repositories: githubData.repositories || [],
            lastSync: githubData.lastSync,
            error: githubData.error,
          };
        }
        if (provider.id === 'gitlab') {
          return {
            ...provider,
            isConnected: gitlabData.connected,
            repositories: gitlabData.repositories || [],
            lastSync: gitlabData.lastSync,
            error: gitlabData.error,
          };
        }
        return provider;
      }));
    } catch (err) {
      setError('Failed to check provider connections');
    } finally {
      setLoading(false);
    }
  };

  const handleGitHubConnect = async () => {
    try {
      // Redirect to GitHub OAuth flow
      window.location.href = '/api/github/auth';
    } catch (err) {
      setError('Failed to initiate GitHub connection');
    }
  };

  const handleGitLabConnect = async () => {
    try {
      // Redirect to GitLab OAuth flow
      window.location.href = '/api/gitlab/auth';
    } catch (err) {
      setError('Failed to initiate GitLab connection');
    }
  };

  const handleDisconnect = async (providerId: string) => {
    try {
      await fetch(`/api/${providerId}/disconnect`, { method: 'POST' });
      checkConnections();
    } catch (err) {
      setError(`Failed to disconnect from ${providerId}`);
    }
  };

  const handleOpenSettings = (provider: GitProvider) => {
    setSelectedProvider(provider);
    setOpenSettings(true);
  };

  const handleSaveSettings = async () => {
    if (!selectedProvider) return;

    try {
      await fetch(`/api/${selectedProvider.id}/settings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(settings),
      });
      setOpenSettings(false);
      checkConnections();
    } catch (err) {
      setError('Failed to save settings');
    }
  };

  const handleRefresh = async (providerId: string) => {
    try {
      await fetch(`/api/${providerId}/refresh`, { method: 'POST' });
      checkConnections();
    } catch (err) {
      setError(`Failed to refresh ${providerId} data`);
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
        {providers.map((provider) => (
          <Grid item xs={12} md={6} key={provider.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                  {provider.icon}
                  <Typography variant="h6" sx={{ ml: 1 }}>
                    {provider.name}
                  </Typography>
                  <Chip
                    icon={provider.isConnected ? <CheckCircleIcon /> : <ErrorIcon />}
                    label={provider.isConnected ? 'Connected' : 'Disconnected'}
                    color={provider.isConnected ? 'success' : 'error'}
                    size="small"
                    sx={{ ml: 2 }}
                  />
                </Box>

                {provider.isConnected && (
                  <>
                    <Typography variant="body2" color="text.secondary" gutterBottom>
                      Last synced: {provider.lastSync ? new Date(provider.lastSync).toLocaleString() : 'Never'}
                    </Typography>
                    <Typography variant="subtitle2" gutterBottom>
                      Connected Repositories:
                    </Typography>
                    <List dense>
                      {provider.repositories.map((repo) => (
                        <ListItem key={repo.id}>
                          <ListItemText
                            primary={repo.name}
                            secondary={`Last updated: ${new Date(repo.lastUpdated).toLocaleString()}`}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </>
                )}

                {provider.error && (
                  <Alert severity="error" sx={{ mt: 2 }}>
                    {provider.error}
                  </Alert>
                )}
              </CardContent>
              <CardActions>
                {provider.isConnected ? (
                  <>
                    <Button
                      startIcon={<RefreshIcon />}
                      onClick={() => handleRefresh(provider.id)}
                    >
                      Refresh
                    </Button>
                    <Button
                      startIcon={<SettingsIcon />}
                      onClick={() => handleOpenSettings(provider)}
                    >
                      Settings
                    </Button>
                    <Button
                      color="error"
                      onClick={() => handleDisconnect(provider.id)}
                    >
                      Disconnect
                    </Button>
                  </>
                ) : (
                  <Button
                    variant="contained"
                    startIcon={provider.icon}
                    onClick={provider.id === 'github' ? handleGitHubConnect : handleGitLabConnect}
                  >
                    Connect {provider.name}
                  </Button>
                )}
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Settings Dialog */}
      <Dialog open={openSettings} onClose={() => setOpenSettings(false)}>
        <DialogTitle>
          {selectedProvider?.name} Settings
        </DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="Access Token"
            type="password"
            fullWidth
            value={settings.accessToken}
            onChange={(e) => setSettings({ ...settings, accessToken: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Organization"
            fullWidth
            value={settings.organization}
            onChange={(e) => setSettings({ ...settings, organization: e.target.value })}
          />
          <TextField
            margin="dense"
            label="Webhook Secret"
            type="password"
            fullWidth
            value={settings.webhookSecret}
            onChange={(e) => setSettings({ ...settings, webhookSecret: e.target.value })}
          />
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

export default GitIntegrations; 