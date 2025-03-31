import React, { useState } from 'react';
import {
  Box,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Typography,
  Chip,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
  Grid,
  LinearProgress,
  Divider,
} from '@mui/material';
import {
  SmartToy,
  PlayArrow,
  Pause,
  Refresh,
  Settings,
  Code,
  Build,
  BugReport,
  CheckCircle,
  Warning,
  Info,
} from '@mui/icons-material';
import { useAgentContext } from './AgentContext';

interface AgentDirectoryProps {
  projectId: string;
}

interface AgentDetailsDialogProps {
  open: boolean;
  onClose: () => void;
  agent: any;
  onUpdate: (agentId: string, updates: any) => void;
}

const AgentDetailsDialog: React.FC<AgentDetailsDialogProps> = ({
  open,
  onClose,
  agent,
  onUpdate,
}) => {
  const [name, setName] = useState(agent.name);
  const [role, setRole] = useState(agent.role);
  const [capabilities, setCapabilities] = useState(agent.capabilities.join(', '));

  const handleSave = () => {
    onUpdate(agent.id, {
      name,
      role,
      capabilities: capabilities.split(',').map((c: string) => c.trim()),
    });
    onClose();
  };

  return (
    <Dialog open={open} onClose={onClose} maxWidth="sm" fullWidth>
      <DialogTitle>Agent Details</DialogTitle>
      <DialogContent>
        <Box sx={{ pt: 2 }}>
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Role"
                value={role}
                onChange={(e) => setRole(e.target.value)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Capabilities (comma-separated)"
                value={capabilities}
                onChange={(e) => setCapabilities(e.target.value)}
                helperText="Enter capabilities separated by commas"
              />
            </Grid>
          </Grid>
        </Box>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button onClick={handleSave} variant="contained" color="primary">
          Save Changes
        </Button>
      </DialogActions>
    </Dialog>
  );
};

const AgentDirectory: React.FC<AgentDirectoryProps> = ({ projectId }) => {
  const { agents, updateAgentStatus, updateAgentFocus } = useAgentContext();
  const [selectedAgent, setSelectedAgent] = useState<any>(null);
  const [detailsDialogOpen, setDetailsDialogOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');

  const handleStatusToggle = (agentId: string, currentStatus: string) => {
    updateAgentStatus(agentId, currentStatus === 'active' ? 'idle' : 'active');
  };

  const handleFocusUpdate = (agentId: string, focusArea: string) => {
    updateAgentFocus(agentId, focusArea);
  };

  const handleDetailsOpen = (agent: any) => {
    setSelectedAgent(agent);
    setDetailsDialogOpen(true);
  };

  const handleDetailsClose = () => {
    setDetailsDialogOpen(false);
    setSelectedAgent(null);
  };

  const handleAgentUpdate = (agentId: string, updates: any) => {
    // Here you would typically make an API call to update the agent
    console.log('Updating agent:', agentId, updates);
  };

  const filteredAgents = agents.filter((agent) =>
    agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    agent.role.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'idle':
        return 'default';
      case 'busy':
        return 'warning';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getCapabilityIcon = (capability: string) => {
    switch (capability.toLowerCase()) {
      case 'code':
        return <Code />;
      case 'build':
        return <Build />;
      case 'bug':
        return <BugReport />;
      case 'test':
        return <CheckCircle />;
      case 'review':
        return <Info />;
      default:
        return <SmartToy />;
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Agent Directory</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh">
            <IconButton size="small">
              <Refresh />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <TextField
        fullWidth
        size="small"
        placeholder="Search agents..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        sx={{ mb: 2 }}
      />

      <List sx={{ flex: 1, overflow: 'auto' }}>
        {filteredAgents.map((agent, index) => (
          <React.Fragment key={agent.id}>
            {index > 0 && <Divider />}
            <ListItem
              secondaryAction={
                <Box sx={{ display: 'flex', gap: 1 }}>
                  <Tooltip title={agent.status === 'active' ? 'Pause Agent' : 'Activate Agent'}>
                    <IconButton
                      edge="end"
                      onClick={() => handleStatusToggle(agent.id, agent.status)}
                      color={getStatusColor(agent.status)}
                    >
                      {agent.status === 'active' ? <Pause /> : <PlayArrow />}
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="Configure Agent">
                    <IconButton
                      edge="end"
                      onClick={() => handleDetailsOpen(agent)}
                    >
                      <Settings />
                    </IconButton>
                  </Tooltip>
                </Box>
              }
            >
              <ListItemAvatar>
                <Avatar sx={{ bgcolor: getStatusColor(agent.status) }}>
                  <SmartToy />
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle1">{agent.name}</Typography>
                    <Chip
                      label={agent.role}
                      size="small"
                      color="primary"
                      variant="outlined"
                    />
                  </Box>
                }
                secondary={
                  <Box sx={{ mt: 1 }}>
                    <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap', mb: 1 }}>
                      {agent.capabilities.map((capability: string) => (
                        <Chip
                          key={capability}
                          icon={getCapabilityIcon(capability)}
                          label={capability}
                          size="small"
                          variant="outlined"
                        />
                      ))}
                    </Box>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        Status: {agent.status}
                      </Typography>
                      {agent.focusArea && (
                        <Typography variant="caption" color="text.secondary">
                          Focus: {agent.focusArea}
                        </Typography>
                      )}
                    </Box>
                    <Box sx={{ mt: 1 }}>
                      <Typography variant="caption" color="text.secondary">
                        Tasks Completed: {agent.performance.tasksCompleted}
                      </Typography>
                      <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                        Success Rate: {agent.performance.successRate}%
                      </Typography>
                    </Box>
                    <Box sx={{ mt: 1 }}>
                      <LinearProgress
                        variant="determinate"
                        value={agent.performance.successRate}
                        color={agent.performance.successRate >= 90 ? 'success' : 'warning'}
                        sx={{ height: 4, borderRadius: 2 }}
                      />
                    </Box>
                  </Box>
                }
              />
            </ListItem>
          </React.Fragment>
        ))}
      </List>

      {selectedAgent && (
        <AgentDetailsDialog
          open={detailsDialogOpen}
          onClose={handleDetailsClose}
          agent={selectedAgent}
          onUpdate={handleAgentUpdate}
        />
      )}
    </Box>
  );
};

export default AgentDirectory; 