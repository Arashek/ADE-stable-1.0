import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Tabs,
  Tab,
  TextField,
  Button,
  Switch,
  FormControlLabel,
  Alert,
  Divider,
  Grid,
  IconButton,
} from '@mui/material';
import {
  GitHub as GitHubIcon,
  Save as SaveIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => {
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`settings-tabpanel-${index}`}
      aria-labelledby={`settings-tab-${index}`}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
};

interface Integration {
  id: string;
  name: string;
  type: string;
  enabled: boolean;
  config: Record<string, string>;
}

const Settings: React.FC = () => {
  const [activeTab, setActiveTab] = useState(0);
  const [integrations, setIntegrations] = useState<Integration[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    // TODO: Fetch integrations from API
    setIntegrations([
      {
        id: '1',
        name: 'GitHub',
        type: 'github',
        enabled: false,
        config: {
          clientId: '',
          clientSecret: '',
          webhookUrl: '',
        },
      },
    ]);
    setLoading(false);
  }, []);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const handleIntegrationToggle = (integrationId: string) => {
    setIntegrations((prev) =>
      prev.map((integration) =>
        integration.id === integrationId
          ? { ...integration, enabled: !integration.enabled }
          : integration
      )
    );
  };

  const handleConfigChange = (
    integrationId: string,
    key: string,
    value: string
  ) => {
    setIntegrations((prev) =>
      prev.map((integration) =>
        integration.id === integrationId
          ? {
              ...integration,
              config: { ...integration.config, [key]: value },
            }
          : integration
      )
    );
  };

  const handleSaveIntegration = async (integration: Integration) => {
    try {
      // TODO: Save integration config to API
      console.log('Saving integration:', integration);
      setSuccess('Integration settings saved successfully');
    } catch (err) {
      setError('Failed to save integration settings');
    }
  };

  const handleDeleteIntegration = async (integrationId: string) => {
    try {
      // TODO: Delete integration via API
      console.log('Deleting integration:', integrationId);
      setIntegrations((prev) =>
        prev.filter((integration) => integration.id !== integrationId)
      );
      setSuccess('Integration deleted successfully');
    } catch (err) {
      setError('Failed to delete integration');
    }
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Typography variant="h4" gutterBottom>
        Settings
      </Typography>

      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Paper sx={{ width: '100%', mt: 3 }}>
        <Tabs
          value={activeTab}
          onChange={handleTabChange}
          aria-label="settings tabs"
        >
          <Tab label="Integrations" />
          <Tab label="General" />
          <Tab label="Appearance" />
          <Tab label="Advanced" />
        </Tabs>

        <TabPanel value={activeTab} index={0}>
          <Typography variant="h6" gutterBottom>
            Manage Integrations
          </Typography>

          {integrations.map((integration) => (
            <Paper key={integration.id} sx={{ p: 3, mb: 2 }}>
              <Grid container spacing={2} alignItems="center">
                <Grid item>
                  <GitHubIcon fontSize="large" />
                </Grid>
                <Grid item xs>
                  <Typography variant="h6">{integration.name}</Typography>
                </Grid>
                <Grid item>
                  <FormControlLabel
                    control={
                      <Switch
                        checked={integration.enabled}
                        onChange={() =>
                          handleIntegrationToggle(integration.id)
                        }
                      />
                    }
                    label={integration.enabled ? 'Enabled' : 'Disabled'}
                  />
                </Grid>
              </Grid>

              <Divider sx={{ my: 2 }} />

              {integration.enabled && (
                <Box sx={{ mt: 2 }}>
                  {Object.entries(integration.config).map(([key, value]) => (
                    <TextField
                      key={key}
                      fullWidth
                      label={key
                        .split(/(?=[A-Z])/)
                        .join(' ')
                        .toLowerCase()}
                      value={value}
                      onChange={(e) =>
                        handleConfigChange(
                          integration.id,
                          key,
                          e.target.value
                        )
                      }
                      margin="normal"
                      type={key.toLowerCase().includes('secret') ? 'password' : 'text'}
                    />
                  ))}

                  <Box sx={{ mt: 2, display: 'flex', gap: 1 }}>
                    <Button
                      variant="contained"
                      startIcon={<SaveIcon />}
                      onClick={() => handleSaveIntegration(integration)}
                    >
                      Save Changes
                    </Button>
                    <IconButton
                      color="error"
                      onClick={() => handleDeleteIntegration(integration.id)}
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Box>
                </Box>
              )}
            </Paper>
          ))}
        </TabPanel>

        <TabPanel value={activeTab} index={1}>
          <Typography>General settings coming soon...</Typography>
        </TabPanel>

        <TabPanel value={activeTab} index={2}>
          <Typography>Appearance settings coming soon...</Typography>
        </TabPanel>

        <TabPanel value={activeTab} index={3}>
          <Typography>Advanced settings coming soon...</Typography>
        </TabPanel>
      </Paper>
    </Container>
  );
};

export default Settings; 