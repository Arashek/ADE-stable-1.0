import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Tabs,
  Tab,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Grid,
  Alert,
  CircularProgress
} from '@mui/material';
import { Add as AddIcon, Refresh as RefreshIcon } from '@mui/icons-material';
import AgentVisualization from './AgentVisualization';
import { AgentConfig, AgentRegistration } from '../../../backend/src/services/agent/AgentRegistry';
import { LLMEndpoint, LLMProvider } from '../../../backend/src/services/agent/LLMProviderService';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

const TabPanel: React.FC<TabPanelProps> = ({ children, value, index }) => (
  <Box role="tabpanel" hidden={value !== index} sx={{ p: 3 }}>
    {value === index && children}
  </Box>
);

const AgentCommandCenter: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [agents, setAgents] = useState<AgentConfig[]>([]);
  const [registrations, setRegistrations] = useState<AgentRegistration[]>([]);
  const [llmEndpoints, setLLMEndpoints] = useState<LLMEndpoint[]>([]);
  const [providers, setProviders] = useState<LLMProvider[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogType, setDialogType] = useState<'agent' | 'endpoint'>('agent');

  // Form states
  const [newAgent, setNewAgent] = useState<Partial<AgentConfig>>({
    name: '',
    description: '',
    capabilities: [],
    defaultLLM: '',
    fallbackLLMs: [],
    isActive: true
  });

  const [newEndpoint, setNewEndpoint] = useState<Partial<LLMEndpoint>>({
    url: '',
    model: '',
    provider: '',
    maxTokens: 2048,
    temperature: 0.7,
    isActive: true
  });

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [agentsRes, registrationsRes, endpointsRes, providersRes] = await Promise.all([
        fetch('/api/agents'),
        fetch('/api/agents/registrations'),
        fetch('/api/llm/endpoints'),
        fetch('/api/llm/providers')
      ]);

      if (!agentsRes.ok || !registrationsRes.ok || !endpointsRes.ok || !providersRes.ok) {
        throw new Error('Failed to fetch data');
      }

      const [agentsData, registrationsData, endpointsData, providersData] = await Promise.all([
        agentsRes.json(),
        registrationsRes.json(),
        endpointsRes.json(),
        providersRes.json()
      ]);

      setAgents(agentsData);
      setRegistrations(registrationsData);
      setLLMEndpoints(endpointsData);
      setProviders(providersData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setLoading(false);
    }
  };

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleOpenDialog = (type: 'agent' | 'endpoint') => {
    setDialogType(type);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setNewAgent({
      name: '',
      description: '',
      capabilities: [],
      defaultLLM: '',
      fallbackLLMs: [],
      isActive: true
    });
    setNewEndpoint({
      url: '',
      model: '',
      provider: '',
      maxTokens: 2048,
      temperature: 0.7,
      isActive: true
    });
  };

  const handleSubmit = async () => {
    try {
      if (dialogType === 'agent') {
        const response = await fetch('/api/agents', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newAgent)
        });

        if (!response.ok) throw new Error('Failed to create agent');
      } else {
        const response = await fetch('/api/llm/endpoints', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(newEndpoint)
        });

        if (!response.ok) throw new Error('Failed to create endpoint');
      }

      handleCloseDialog();
      fetchData();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs value={tabValue} onChange={handleTabChange}>
          <Tab label="Overview" />
          <Tab label="Agents" />
          <Tab label="LLM Endpoints" />
        </Tabs>
      </Box>

      {error && (
        <Alert severity="error" sx={{ m: 2 }}>
          {error}
        </Alert>
      )}

      <TabPanel value={tabValue} index={0}>
        <Box display="flex" justifyContent="space-between" mb={2}>
          <Typography variant="h6">Agent Ecosystem Overview</Typography>
          <Button startIcon={<RefreshIcon />} onClick={fetchData}>
            Refresh
          </Button>
        </Box>
        <AgentVisualization
          agents={agents}
          registrations={registrations}
          llmEndpoints={llmEndpoints}
          onNodeClick={(node) => console.log('Node clicked:', node)}
        />
      </TabPanel>

      <TabPanel value={tabValue} index={1}>
        <Box display="flex" justifyContent="space-between" mb={2}>
          <Typography variant="h6">Agent Management</Typography>
          <Button startIcon={<AddIcon />} onClick={() => handleOpenDialog('agent')}>
            Add Agent
          </Button>
        </Box>
        <Grid container spacing={2}>
          {agents.map(agent => (
            <Grid item xs={12} md={6} key={agent.id}>
              <Paper elevation={2} sx={{ p: 2 }}>
                <Typography variant="h6">{agent.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {agent.description}
                </Typography>
                <Box mt={1}>
                  <Typography variant="body2">
                    Status: {registrations.find(r => r.agentId === agent.id)?.status || 'Unknown'}
                  </Typography>
                  <Typography variant="body2">
                    Capabilities: {agent.capabilities.length}
                  </Typography>
                  <Typography variant="body2">
                    Default LLM: {agent.defaultLLM}
                  </Typography>
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <TabPanel value={tabValue} index={2}>
        <Box display="flex" justifyContent="space-between" mb={2}>
          <Typography variant="h6">LLM Endpoint Management</Typography>
          <Button startIcon={<AddIcon />} onClick={() => handleOpenDialog('endpoint')}>
            Add Endpoint
          </Button>
        </Box>
        <Grid container spacing={2}>
          {llmEndpoints.map(endpoint => (
            <Grid item xs={12} md={6} key={endpoint.id}>
              <Paper elevation={2} sx={{ p: 2 }}>
                <Typography variant="h6">{endpoint.provider} - {endpoint.model}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {endpoint.url}
                </Typography>
                <Box mt={1}>
                  <Typography variant="body2">
                    Status: {endpoint.isActive ? 'Active' : 'Inactive'}
                  </Typography>
                  <Typography variant="body2">
                    Max Tokens: {endpoint.maxTokens}
                  </Typography>
                  <Typography variant="body2">
                    Temperature: {endpoint.temperature}
                  </Typography>
                </Box>
              </Paper>
            </Grid>
          ))}
        </Grid>
      </TabPanel>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="md" fullWidth>
        <DialogTitle>
          {dialogType === 'agent' ? 'Add New Agent' : 'Add New LLM Endpoint'}
        </DialogTitle>
        <DialogContent>
          {dialogType === 'agent' ? (
            <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                label="Name"
                value={newAgent.name}
                onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                fullWidth
              />
              <TextField
                label="Description"
                value={newAgent.description}
                onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })}
                multiline
                rows={3}
                fullWidth
              />
              <FormControl fullWidth>
                <InputLabel>Default LLM</InputLabel>
                <Select
                  value={newAgent.defaultLLM}
                  onChange={(e) => setNewAgent({ ...newAgent, defaultLLM: e.target.value })}
                >
                  {providers.flatMap(provider =>
                    provider.models.map(model => (
                      <MenuItem key={model} value={model}>
                        {provider.name} - {model}
                      </MenuItem>
                    ))
                  )}
                </Select>
              </FormControl>
            </Box>
          ) : (
            <Box sx={{ mt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
              <FormControl fullWidth>
                <InputLabel>Provider</InputLabel>
                <Select
                  value={newEndpoint.provider}
                  onChange={(e) => setNewEndpoint({ ...newEndpoint, provider: e.target.value })}
                >
                  {providers.map(provider => (
                    <MenuItem key={provider.name} value={provider.name}>
                      {provider.name}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
              <FormControl fullWidth>
                <InputLabel>Model</InputLabel>
                <Select
                  value={newEndpoint.model}
                  onChange={(e) => setNewEndpoint({ ...newEndpoint, model: e.target.value })}
                >
                  {providers
                    .find(p => p.name === newEndpoint.provider)
                    ?.models.map(model => (
                      <MenuItem key={model} value={model}>
                        {model}
                      </MenuItem>
                    )) || []}
                </Select>
              </FormControl>
              <TextField
                label="URL"
                value={newEndpoint.url}
                onChange={(e) => setNewEndpoint({ ...newEndpoint, url: e.target.value })}
                fullWidth
              />
              <TextField
                label="Max Tokens"
                type="number"
                value={newEndpoint.maxTokens}
                onChange={(e) => setNewEndpoint({ ...newEndpoint, maxTokens: parseInt(e.target.value) })}
                fullWidth
              />
              <TextField
                label="Temperature"
                type="number"
                inputProps={{ step: 0.1, min: 0, max: 1 }}
                value={newEndpoint.temperature}
                onChange={(e) => setNewEndpoint({ ...newEndpoint, temperature: parseFloat(e.target.value) })}
                fullWidth
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            Add {dialogType === 'agent' ? 'Agent' : 'Endpoint'}
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default AgentCommandCenter; 