import React, { useEffect, useRef, useState } from 'react';
import { Box, Paper, Typography, IconButton, TextField } from '@mui/material';
import { Clear, Send } from '@mui/icons-material';
import { ContainerService } from '../../services/ContainerService';

interface ContainerTerminalProps {
  containerId: string;
  containerName: string;
}

export const ContainerTerminal: React.FC<ContainerTerminalProps> = ({
  containerId,
  containerName,
}) => {
  const [terminalOutput, setTerminalOutput] = useState<string[]>([]);
  const [command, setCommand] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const terminalRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const containerService = new ContainerService();

  useEffect(() => {
    connectWebSocket();
    return () => {
      disconnectWebSocket();
    };
  }, [containerId]);

  useEffect(() => {
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [terminalOutput]);

  const connectWebSocket = async () => {
    try {
      // Get WebSocket URL from the container service
      const wsUrl = await containerService.getTerminalWebSocketUrl(containerId);
      const ws = new WebSocket(wsUrl);

      ws.onopen = () => {
        setIsConnected(true);
        appendOutput('Connected to terminal');
      };

      ws.onmessage = (event) => {
        appendOutput(event.data);
      };

      ws.onclose = () => {
        setIsConnected(false);
        appendOutput('Disconnected from terminal');
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        appendOutput('Error: Failed to connect to terminal');
      };

      wsRef.current = ws;
    } catch (error) {
      console.error('Failed to connect to terminal:', error);
      appendOutput('Error: Failed to connect to terminal');
    }
  };

  const disconnectWebSocket = () => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  };

  const appendOutput = (text: string) => {
    setTerminalOutput((prev) => [...prev, text]);
  };

  const handleCommandSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!command.trim() || !wsRef.current || !isConnected) return;

    try {
      wsRef.current.send(command);
      appendOutput(`$ ${command}`);
      setCommand('');
    } catch (error) {
      console.error('Failed to send command:', error);
      appendOutput('Error: Failed to send command');
    }
  };

  const handleClear = () => {
    setTerminalOutput([]);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center' }}>
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          Terminal - {containerName}
        </Typography>
        <IconButton onClick={handleClear} size="small">
          <Clear />
        </IconButton>
      </Box>

      <Paper
        ref={terminalRef}
        sx={{
          flexGrow: 1,
          p: 2,
          bgcolor: '#1e1e1e',
          color: '#fff',
          fontFamily: 'monospace',
          overflow: 'auto',
          whiteSpace: 'pre-wrap',
          wordBreak: 'break-word',
        }}
      >
        {terminalOutput.map((line, index) => (
          <div key={index}>{line}</div>
        ))}
      </Paper>

      <Box
        component="form"
        onSubmit={handleCommandSubmit}
        sx={{
          p: 2,
          borderTop: 1,
          borderColor: 'divider',
          display: 'flex',
          gap: 1,
        }}
      >
        <TextField
          fullWidth
          size="small"
          placeholder="Enter command..."
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          disabled={!isConnected}
          sx={{
            '& .MuiInputBase-root': {
              fontFamily: 'monospace',
            },
          }}
        />
        <IconButton
          type="submit"
          color="primary"
          disabled={!isConnected || !command.trim()}
        >
          <Send />
        </IconButton>
      </Box>
    </Box>
  );
}; 