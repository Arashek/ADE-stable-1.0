import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  TextField,
  IconButton,
  Avatar,
} from '@mui/material';
import { Send as SendIcon, SmartToy as AgentIcon } from '@mui/icons-material';

interface Message {
  id: string;
  content: string;
  sender: string;
  timestamp: string;
  type: 'agent' | 'system' | 'user';
}

interface AgentCommunicationProps {
  activeAgent: string | null;
}

const AgentCommunication: React.FC<AgentCommunicationProps> = ({ activeAgent }) => {
  const [message, setMessage] = useState('');
  const [messages] = useState<Message[]>([
    {
      id: '1',
      content: 'Hello! I am the Code Assistant. How can I help you today?',
      sender: 'Code Assistant',
      timestamp: '10:30 AM',
      type: 'agent',
    },
    {
      id: '2',
      content: 'Running code analysis on the current project...',
      sender: 'System',
      timestamp: '10:31 AM',
      type: 'system',
    },
    {
      id: '3',
      content: 'Analysis complete. I found several opportunities for optimization.',
      sender: 'Code Assistant',
      timestamp: '10:32 AM',
      type: 'agent',
    },
  ]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement message sending logic
    setMessage('');
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper
        sx={{
          flex: 1,
          mb: 2,
          maxHeight: 'calc(100vh - 200px)',
          overflow: 'auto',
          backgroundColor: (theme) => theme.palette.background.default,
        }}
      >
        <List>
          {messages.map((msg) => (
            <ListItem
              key={msg.id}
              sx={{
                flexDirection: 'column',
                alignItems: msg.type === 'system' ? 'center' : 'flex-start',
                py: 1,
              }}
            >
              {msg.type !== 'system' && (
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    alignSelf: 'flex-start',
                    mb: 0.5,
                  }}
                >
                  <Avatar
                    sx={{
                      mr: 1,
                      bgcolor: msg.type === 'agent' ? 'primary.main' : 'secondary.main',
                    }}
                  >
                    {msg.type === 'agent' && <AgentIcon />}
                  </Avatar>
                  <Typography variant="subtitle2">{msg.sender}</Typography>
                  <Typography variant="caption" sx={{ ml: 1, color: 'text.secondary' }}>
                    {msg.timestamp}
                  </Typography>
                </Box>
              )}
              <Paper
                sx={{
                  p: 1.5,
                  backgroundColor:
                    msg.type === 'system'
                      ? 'background.paper'
                      : msg.type === 'agent'
                      ? 'primary.dark'
                      : 'secondary.dark',
                  color: msg.type !== 'system' ? 'common.white' : 'text.primary',
                  maxWidth: '80%',
                  alignSelf: msg.type === 'system' ? 'center' : 'flex-start',
                }}
              >
                <Typography variant="body1">{msg.content}</Typography>
              </Paper>
            </ListItem>
          ))}
        </List>
      </Paper>

      <Box
        component="form"
        onSubmit={handleSendMessage}
        sx={{
          display: 'flex',
          gap: 1,
          mt: 'auto',
        }}
      >
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Type your message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={!activeAgent}
        />
        <IconButton
          type="submit"
          color="primary"
          disabled={!activeAgent || !message.trim()}
          sx={{ alignSelf: 'center' }}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
};

export default AgentCommunication; 