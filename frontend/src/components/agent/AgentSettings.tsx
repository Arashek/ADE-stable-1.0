import React from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  Switch,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  Button,
  Divider,
  Grid,
  Chip,
  IconButton,
  Tooltip
} from '@mui/material';
import {
  Save as SaveIcon,
  Delete as DeleteIcon,
  Add as AddIcon
} from '@mui/icons-material';
import { useAgentContext } from '../../contexts/AgentContext';

interface AgentSettingsProps {
  projectId: string;
}

interface SavedQuery {
  id: string;
  name: string;
  query: string;
}

const AgentSettings: React.FC<AgentSettingsProps> = ({ projectId }) => {
  const { state, actions } = useAgentContext();
  const [savedQueries, setSavedQueries] = React.useState<SavedQuery[]>([]);
  const [newQuery, setNewQuery] = React.useState({ name: '', query: '' });
  const [isAddingQuery, setIsAddingQuery] = React.useState(false);

  const handleThemeChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    actions.updateSettings({
      theme: event.target.checked ? 'dark' : 'light'
    });
  };

  const handleNotificationChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    actions.updateSettings({
      notifications: event.target.checked
    });
  };

  const handleAutoFocusChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    actions.updateSettings({
      autoFocus: event.target.checked
    });
  };

  const handleSaveQuery = () => {
    if (newQuery.name && newQuery.query) {
      setSavedQueries([
        ...savedQueries,
        {
          id: Date.now().toString(),
          name: newQuery.name,
          query: newQuery.query
        }
      ]);
      setNewQuery({ name: '', query: '' });
      setIsAddingQuery(false);
    }
  };

  const handleDeleteQuery = (id: string) => {
    setSavedQueries(savedQueries.filter(query => query.id !== id));
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Agent Settings
      </Typography>

      <Grid container spacing={3}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Display Preferences
            </Typography>
            <List>
              <ListItem>
                <ListItemText
                  primary="Dark Theme"
                  secondary="Use dark theme for the agent panel"
                />
                <ListItemSecondaryAction>
                  <Switch
                    edge="end"
                    checked={state.settings.theme === 'dark'}
                    onChange={handleThemeChange}
                  />
                </ListItemSecondaryAction>
              </ListItem>
              <Divider />
              <ListItem>
                <ListItemText
                  primary="Notifications"
                  secondary="Receive notifications for agent activities"
                />
                <ListItemSecondaryAction>
                  <Switch
                    edge="end"
                    checked={state.settings.notifications}
                    onChange={handleNotificationChange}
                  />
                </ListItemSecondaryAction>
              </ListItem>
              <Divider />
              <ListItem>
                <ListItemText
                  primary="Auto-Focus"
                  secondary="Automatically focus relevant agents based on current file"
                />
                <ListItemSecondaryAction>
                  <Switch
                    edge="end"
                    checked={state.settings.autoFocus}
                    onChange={handleAutoFocusChange}
                  />
                </ListItemSecondaryAction>
              </ListItem>
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 2, mb: 2 }}>
            <Typography variant="subtitle1" gutterBottom>
              Agent Team Configuration
            </Typography>
            <List>
              {state.agents.map((agent) => (
                <React.Fragment key={agent.id}>
                  <ListItem>
                    <ListItemText
                      primary={agent.name}
                      secondary={agent.role}
                    />
                    <ListItemSecondaryAction>
                      <Chip
                        label={agent.status}
                        color={agent.status === 'active' ? 'success' : 'default'}
                        size="small"
                      />
                    </ListItemSecondaryAction>
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
              <Typography variant="subtitle1">
                Saved Queries
              </Typography>
              <Button
                startIcon={<AddIcon />}
                onClick={() => setIsAddingQuery(true)}
              >
                Add Query
              </Button>
            </Box>

            {isAddingQuery && (
              <Box sx={{ mb: 2 }}>
                <TextField
                  fullWidth
                  label="Query Name"
                  value={newQuery.name}
                  onChange={(e) => setNewQuery({ ...newQuery, name: e.target.value })}
                  sx={{ mb: 1 }}
                />
                <TextField
                  fullWidth
                  label="Query"
                  value={newQuery.query}
                  onChange={(e) => setNewQuery({ ...newQuery, query: e.target.value })}
                  multiline
                  rows={3}
                  sx={{ mb: 1 }}
                />
                <Box display="flex" gap={1}>
                  <Button
                    variant="contained"
                    startIcon={<SaveIcon />}
                    onClick={handleSaveQuery}
                  >
                    Save
                  </Button>
                  <Button
                    onClick={() => {
                      setIsAddingQuery(false);
                      setNewQuery({ name: '', query: '' });
                    }}
                  >
                    Cancel
                  </Button>
                </Box>
              </Box>
            )}

            <List>
              {savedQueries.map((query) => (
                <React.Fragment key={query.id}>
                  <ListItem>
                    <ListItemText
                      primary={query.name}
                      secondary={query.query}
                    />
                    <ListItemSecondaryAction>
                      <Tooltip title="Delete Query">
                        <IconButton
                          edge="end"
                          onClick={() => handleDeleteQuery(query.id)}
                        >
                          <DeleteIcon />
                        </IconButton>
                      </Tooltip>
                    </ListItemSecondaryAction>
                  </ListItem>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AgentSettings; 