import React, { useState } from 'react';
import {
  Box,
  TextField,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  Paper,
} from '@mui/material';
import { Terminal as TerminalIcon, Person as PersonIcon } from '@mui/icons-material';

interface Agent {
  id: string;
  name: string;
  status: 'active' | 'idle' | 'busy';
  currentTask?: string;
}

const CommandPanel: React.FC = () => {
  const [command, setCommand] = useState('');
  const [activeAgents] = useState<Agent[]>([
    { id: '1', name: 'Code Generator', status: 'active', currentTask: 'Implementing new feature' },
    { id: '2', name: 'Code Reviewer', status: 'idle' },
    { id: '3', name: 'Architect', status: 'busy', currentTask: 'Designing system architecture' },
  ]);

  const handleCommandSubmit = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      // TODO: Implement command processing
      console.log('Command submitted:', command);
      setCommand('');
    }
  };

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'busy':
        return 'warning';
      case 'idle':
        return 'default';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" gutterBottom>
        Command Hub
      </Typography>
      
      {/* Active Agents Section */}
      <Paper sx={{ p: 2, mb: 2, bgcolor: 'background.paper' }}>
        <Typography variant="subtitle1" gutterBottom>
          Active Agents
        </Typography>
        <List dense>
          {activeAgents.map((agent) => (
            <ListItem key={agent.id}>
              <ListItemIcon>
                <PersonIcon />
              </ListItemIcon>
              <ListItemText
                primary={agent.name}
                secondary={agent.currentTask}
              />
              <Chip
                label={agent.status}
                color={getStatusColor(agent.status)}
                size="small"
              />
            </ListItem>
          ))}
        </List>
      </Paper>

      {/* Command Input */}
      <Box sx={{ mt: 'auto' }}>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Enter command..."
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyPress={handleCommandSubmit}
          InputProps={{
            startAdornment: <TerminalIcon sx={{ mr: 1, color: 'primary.main' }} />,
          }}
        />
      </Box>
    </Box>
  );
};

export default CommandPanel; 