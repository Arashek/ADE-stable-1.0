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
  Tabs,
  Tab,
} from '@mui/material';
import { Send as SendIcon, SmartToy as AgentIcon } from '@mui/icons-material';

interface Message {
  id: string;
  sender: string;
  content: string;
  timestamp: string;
  type: 'agent' | 'user' | 'system';
}

interface ChatThread {
  id: string;
  title: string;
  agent: string;
  messages: Message[];
}

const ChatPanel: React.FC = () => {
  const [tabValue, setTabValue] = useState(0);
  const [message, setMessage] = useState('');
  const [chatThreads] = useState<ChatThread[]>([
    {
      id: '1',
      title: 'Feature Implementation',
      agent: 'Code Generator',
      messages: [
        {
          id: '1',
          sender: 'Code Generator',
          content: 'I\'ve started implementing the new feature.',
          timestamp: '14:30',
          type: 'agent',
        },
        {
          id: '2',
          sender: 'User',
          content: 'Please add error handling.',
          timestamp: '14:31',
          type: 'user',
        },
      ],
    },
    {
      id: '2',
      title: 'Code Review',
      agent: 'Code Reviewer',
      messages: [
        {
          id: '3',
          sender: 'Code Reviewer',
          content: 'I\'ve reviewed the changes. There are a few issues to address.',
          timestamp: '14:32',
          type: 'agent',
        },
      ],
    },
  ]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

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
        Agent Chat
      </Typography>

      <Paper sx={{ flex: 1, overflow: 'hidden', mb: 2, bgcolor: 'background.paper' }}>
        <Tabs
          value={tabValue}
          onChange={handleTabChange}
          aria-label="chat threads"
          sx={{ borderBottom: 1, borderColor: 'divider' }}
        >
          {chatThreads.map((thread) => (
            <Tab
              key={thread.id}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <AgentIcon fontSize="small" />
                  <Typography variant="body2">{thread.title}</Typography>
                </Box>
              }
            />
          ))}
        </Tabs>

        <Box sx={{ height: 'calc(100% - 48px)', overflow: 'auto' }}>
          {chatThreads.map((thread, index) => (
            <Box
              key={thread.id}
              role="tabpanel"
              hidden={tabValue !== index}
              id={`chat-thread-${index}`}
              aria-labelledby={`chat-tab-${index}`}
            >
              <List>
                {thread.messages.map((msg, msgIndex) => (
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
                    {msgIndex < thread.messages.length - 1 && (
                      <Divider variant="inset" component="li" />
                    )}
                  </React.Fragment>
                ))}
              </List>
            </Box>
          ))}
        </Box>
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

export default ChatPanel; 