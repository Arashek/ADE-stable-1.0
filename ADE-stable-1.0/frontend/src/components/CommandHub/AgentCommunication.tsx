import React, { useState } from 'react';
import {
  Box,
  Typography,
  Paper,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  TextField,
  IconButton,
  Divider,
} from '@mui/material';
import { Send as SendIcon, SmartToy as AgentIcon } from '@mui/icons-material';

interface Message {
  id: string;
  sender: string;
  content: string;
  timestamp: string;
  type: 'agent' | 'system';
}

const AgentCommunication: React.FC = () => {
  const [message, setMessage] = useState('');
  const [messages] = useState<Message[]>([
    {
      id: '1',
      sender: 'Code Generator',
      content: 'I\'ve completed the implementation of the new feature.',
      timestamp: '14:30',
      type: 'agent',
    },
    {
      id: '2',
      sender: 'Code Reviewer',
      content: 'Please review the changes in the PR.',
      timestamp: '14:31',
      type: 'agent',
    },
    {
      id: '3',
      sender: 'System',
      content: 'New task assigned: Implement authentication system',
      timestamp: '14:32',
      type: 'system',
    },
  ]);

  const handleSendMessage = () => {
    if (message.trim()) {
      // TODO: Implement message sending
      console.log('Sending message:', message);
      setMessage('');
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Typography variant="h6" gutterBottom>
        Agent Communication
      </Typography>

      <Paper sx={{ flex: 1, overflow: 'auto', mb: 2, bgcolor: 'background.paper' }}>
        <List>
          {messages.map((msg, index) => (
            <React.Fragment key={msg.id}>
              <ListItem alignItems="flex-start">
                <ListItemAvatar>
                  <Avatar>
                    <AgentIcon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={
                    <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
                      <Typography
                        component="span"
                        variant="subtitle2"
                        color={msg.type === 'system' ? 'primary' : 'text.primary'}
                      >
                        {msg.sender}
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {msg.timestamp}
                      </Typography>
                    </Box>
                  }
                  secondary={
                    <Typography
                      component="span"
                      variant="body2"
                      color={msg.type === 'system' ? 'primary' : 'text.primary'}
                    >
                      {msg.content}
                    </Typography>
                  }
                />
              </ListItem>
              {index < messages.length - 1 && <Divider variant="inset" component="li" />}
            </React.Fragment>
          ))}
        </List>
      </Paper>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          size="small"
          placeholder="Type a message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
        />
        <IconButton color="primary" onClick={handleSendMessage}>
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
};

export default AgentCommunication; 