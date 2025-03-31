import React, { useEffect, useRef, useState } from 'react';
import { Box, Typography, IconButton, TextField } from '@mui/material';
import { Clear as ClearIcon, Send as SendIcon } from '@mui/icons-material';
import { Terminal as XTerm } from 'xterm';
import { FitAddon } from 'xterm-addon-fit';
import { WebLinksAddon } from 'xterm-addon-web-links';
import 'xterm/css/xterm.css';

interface TerminalProps {
  projectId: string;
}

const Terminal: React.FC<TerminalProps> = ({ projectId }) => {
  const terminalRef = useRef<HTMLDivElement>(null);
  const xtermRef = useRef<XTerm | null>(null);
  const fitAddonRef = useRef<FitAddon | null>(null);
  const [command, setCommand] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [output, setOutput] = useState<string[]>([]);
  const [currentDir, setCurrentDir] = useState('/workspace');

  useEffect(() => {
    if (terminalRef.current && !xtermRef.current) {
      const xterm = new XTerm({
        cursorBlink: true,
        fontSize: 14,
        fontFamily: 'Menlo, Monaco, "Courier New", monospace',
        theme: {
          background: '#1e1e1e',
          foreground: '#ffffff',
          cursor: '#ffffff'
        }
      });

      const fitAddon = new FitAddon();
      xterm.loadAddon(fitAddon);
      xterm.loadAddon(new WebLinksAddon());

      xterm.open(terminalRef.current);
      fitAddon.fit();

      xtermRef.current = xterm;
      fitAddonRef.current = fitAddon;

      // Connect to WebSocket
      const ws = new WebSocket(`ws://${window.location.host}/api/terminal/${projectId}`);
      
      ws.onopen = () => {
        setIsConnected(true);
        xterm.writeln('Connected to terminal');
      };

      ws.onmessage = (event) => {
        xterm.write(event.data);
      };

      ws.onclose = () => {
        setIsConnected(false);
        xterm.writeln('\r\nDisconnected from terminal');
      };

      // Handle window resize
      const handleResize = () => {
        fitAddon.fit();
      };
      window.addEventListener('resize', handleResize);

      return () => {
        window.removeEventListener('resize', handleResize);
        ws.close();
        xterm.dispose();
      };
    }
  }, [projectId]);

  useEffect(() => {
    // Scroll to bottom when output changes
    if (terminalRef.current) {
      terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
    }
  }, [output]);

  const handleCommandSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!command.trim() || !isConnected) return;

    try {
      const [cmd, ...args] = command.trim().split(' ');
      
      if (cmd === 'cd') {
        const targetDir = args[0];
        if (!targetDir) {
          setOutput(prev => [...prev, 'Usage: cd <directory>']);
          return;
        }
        
        // Update current directory
        const newDir = targetDir === '..' 
          ? currentDir.split('/').slice(0, -1).join('/') || '/'
          : targetDir.startsWith('/') 
            ? targetDir 
            : `${currentDir}/${targetDir}`.replace(/\/+/g, '/');
        
        setCurrentDir(newDir);
        setOutput(prev => [...prev, `$ ${command}`, `Changed directory to ${newDir}`]);
        return;
      }

      // For other commands, include current directory in API call
      const response = await fetch('/api/terminal', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          command,
          currentDir
        }),
      });

      const data = await response.json();
      setOutput(prev => [...prev, `$ ${command}`, data.output]);
    } catch (error: unknown) {
      setOutput(prev => [...prev, `$ ${command}`, `Error: ${error instanceof Error ? error.message : String(error)}`]);
    }
  };

  const handleClear = () => {
    if (xtermRef.current) {
      xtermRef.current.clear();
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter') {
      handleCommandSubmit(event);
      setCommand('');
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 1, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center' }}>
        <Typography variant="subtitle1" sx={{ flex: 1 }}>
          Terminal
        </Typography>
        <IconButton size="small" onClick={handleClear}>
          <ClearIcon />
        </IconButton>
      </Box>
      <Box
        ref={terminalRef}
        sx={{
          flex: 1,
          overflowY: 'auto',
          bgcolor: 'black',
          color: 'white',
          fontFamily: 'monospace',
          p: 2,
          mb: 2,
          borderRadius: 1,
        }}
      >
        {output.map((line, index) => (
          <Typography key={index} component="pre" sx={{ m: 0, whiteSpace: 'pre-wrap' }}>
            {line}
          </Typography>
        ))}
      </Box>
      <Box
        component="form"
        onSubmit={handleCommandSubmit}
        sx={{
          p: 1,
          borderTop: 1,
          borderColor: 'divider',
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}
      >
        <TextField
          fullWidth
          size="small"
          placeholder="Enter command..."
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          disabled={!isConnected}
          onKeyPress={handleKeyPress}
        />
        <IconButton
          type="submit"
          disabled={!isConnected || !command.trim()}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
};

export default Terminal; 