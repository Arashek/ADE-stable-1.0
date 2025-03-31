import React, { useState, useRef, useEffect } from 'react';
import {
  Paper,
  Box,
  Typography,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
} from '@mui/material';
import {
  Send as SendIcon,
  Terminal as TerminalIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
} from '@mui/icons-material';
import { useCommandStore } from '../store/commandStore';

interface ActiveAgent {
  id: string;
  name: string;
  status: 'idle' | 'running' | 'error';
  currentTask?: string;
}

const CommandPanel: React.FC = () => {
  const [command, setCommand] = useState('');
  const [activeAgents, setActiveAgents] = useState<ActiveAgent[]>([]);
  const commandHistory = useCommandStore((state) => state.history);
  const addToHistory = useCommandStore((state) => state.addToHistory);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Focus command input on mount
    inputRef.current?.focus();
    
    // Set up keyboard shortcuts
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, []);

  const handleCommandSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!command.trim()) return;

    // Add command to history
    addToHistory({
      command,
      timestamp: new Date(),
      status: 'success',
    });

    // TODO: Send command to ADE API
    console.log('Executing command:', command);
    
    setCommand('');
  };

  const getStatusColor = (status: ActiveAgent['status']) => {
    switch (status) {
      case 'running':
        return 'success';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  return (
    <Paper
      elevation={3}
      sx={{
        p: 2,
        mb: 2,
        backgroundColor: 'background.paper',
        height: '300px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <TerminalIcon sx={{ mr: 1 }} />
        <Typography variant="h6">Command Hub</Typography>
      </Box>

      {/* Active Agents List */}
      <List dense sx={{ flex: 1, overflow: 'auto' }}>
        {activeAgents.map((agent) => (
          <ListItem key={agent.id}>
            <ListItemIcon>
              <Chip
                label={agent.status}
                color={getStatusColor(agent.status)}
                size="small"
              />
            </ListItemIcon>
            <ListItemText
              primary={agent.name}
              secondary={agent.currentTask}
            />
          </ListItem>
        ))}
      </List>

      {/* Command Input */}
      <Box
        component="form"
        onSubmit={handleCommandSubmit}
        sx={{
          display: 'flex',
          gap: 1,
          mt: 2,
        }}
      >
        <TextField
          inputRef={inputRef}
          fullWidth
          variant="outlined"
          placeholder="Enter command (Ctrl+K to focus)"
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          InputProps={{
            startAdornment: (
              <Typography
                component="span"
                sx={{ color: 'text.secondary', mr: 1 }}
              >
                $
              </Typography>
            ),
          }}
        />
        <IconButton
          type="submit"
          color="primary"
          disabled={!command.trim()}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Paper>
  );
};

export default CommandPanel; 