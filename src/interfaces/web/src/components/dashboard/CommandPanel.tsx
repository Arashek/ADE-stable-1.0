import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Typography,
  Chip,
} from '@mui/material';
import { Send as SendIcon, SmartToy as AgentIcon } from '@mui/icons-material';
import { styled } from '@mui/material/styles';

interface CommandPanelProps {
  onAgentSelect: (agentId: string) => void;
}

interface Agent {
  id: string;
  name: string;
  status: 'active' | 'idle' | 'busy';
  type: string;
}

const StyledTerminal = styled(TextField)(({ theme }) => ({
  '& .MuiInputBase-root': {
    backgroundColor: theme.palette.grey[900],
    color: theme.palette.common.white,
    fontFamily: 'monospace',
  },
  '& .MuiOutlinedInput-notchedOutline': {
    borderColor: theme.palette.grey[800],
  },
}));

const CommandPanel: React.FC<CommandPanelProps> = ({ onAgentSelect }) => {
  const [command, setCommand] = useState('');
  const [activeAgents] = useState<Agent[]>([
    { id: '1', name: 'Code Assistant', status: 'active', type: 'development' },
    { id: '2', name: 'Test Runner', status: 'idle', type: 'testing' },
    { id: '3', name: 'Deployment Agent', status: 'busy', type: 'deployment' },
  ]);
  const terminalRef = useRef<HTMLDivElement>(null);

  const handleCommand = (e: React.FormEvent) => {
    e.preventDefault();
    // Process command
    setCommand('');
  };

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'idle':
        return 'warning';
      case 'busy':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Active Agents List */}
      <Paper sx={{ mb: 2, maxHeight: '200px', overflow: 'auto' }}>
        <List>
          {activeAgents.map((agent) => (
            <ListItem
              key={agent.id}
              button
              onClick={() => onAgentSelect(agent.id)}
              sx={{ '&:hover': { backgroundColor: 'action.hover' } }}
            >
              <ListItemAvatar>
                <Avatar>
                  <AgentIcon />
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={agent.name}
                secondary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="body2" component="span">
                      {agent.type}
                    </Typography>
                    <Chip
                      label={agent.status}
                      size="small"
                      color={getStatusColor(agent.status)}
                      sx={{ height: 20 }}
                    />
                  </Box>
                }
              />
            </ListItem>
          ))}
        </List>
      </Paper>

      {/* Command Input */}
      <Box
        component="form"
        onSubmit={handleCommand}
        sx={{
          display: 'flex',
          gap: 1,
          mt: 'auto',
        }}
      >
        <StyledTerminal
          fullWidth
          variant="outlined"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          placeholder="Enter command..."
          multiline
          maxRows={4}
        />
        <IconButton type="submit" color="primary" sx={{ alignSelf: 'flex-end' }}>
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
};

export default CommandPanel; 