import React, { useState } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Typography,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  Avatar,
  Chip,
} from '@mui/material';
import { Send as SendIcon } from '@mui/icons-material';

interface Message {
  id: string;
  content: string;
  sender: string;
  timestamp: string;
  type: 'agent' | 'user' | 'system';
}

interface ChatThread {
  id: string;
  title: string;
  messages: Message[];
  lastActivity: string;
}

const ChatPanel: React.FC = () => {
  const [currentTab, setCurrentTab] = useState(0);
  const [messageInput, setMessageInput] = useState('');
  const [threads] = useState<ChatThread[]>([
    {
      id: '1',
      title: 'Project Planning',
      lastActivity: '2 min ago',
      messages: [
        {
          id: '1',
          content: 'Let\'s discuss the project architecture.',
          sender: 'Architect Agent',
          timestamp: '10:00 AM',
          type: 'agent',
        },
        {
          id: '2',
          content: 'I suggest we start with the core components.',
          sender: 'User',
          timestamp: '10:01 AM',
          type: 'user',
        },
      ],
    },
    {
      id: '2',
      title: 'Code Review',
      lastActivity: '5 min ago',
      messages: [
        {
          id: '3',
          content: 'I\'ve analyzed the current codebase.',
          sender: 'Code Review Agent',
          timestamp: '09:55 AM',
          type: 'agent',
        },
      ],
    },
  ]);

  const handleTabChange = (_: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    // TODO: Implement message sending
    setMessageInput('');
  };

  const currentThread = threads[currentTab];

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
        <Tabs
          value={currentTab}
          onChange={handleTabChange}
          variant="scrollable"
          scrollButtons="auto"
        >
          {threads.map((thread, index) => (
            <Tab
              key={thread.id}
              label={
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Typography>{thread.title}</Typography>
                  <Chip
                    label={thread.lastActivity}
                    size="small"
                    sx={{ height: 20 }}
                  />
                </Box>
              }
            />
          ))}
        </Tabs>
      </Box>

      <Paper
        sx={{
          flex: 1,
          my: 2,
          p: 2,
          maxHeight: 'calc(100vh - 300px)',
          overflow: 'auto',
          backgroundColor: 'background.default',
        }}
      >
        <List>
          {currentThread?.messages.map((message) => (
            <ListItem
              key={message.id}
              sx={{
                flexDirection: 'column',
                alignItems: message.type === 'user' ? 'flex-end' : 'flex-start',
                py: 1,
              }}
            >
              <Box
                sx={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: 1,
                  mb: 0.5,
                  flexDirection: message.type === 'user' ? 'row-reverse' : 'row',
                }}
              >
                <Avatar
                  sx={{
                    bgcolor: message.type === 'agent' ? 'primary.main' : 'secondary.main',
                  }}
                >
                  {message.sender[0]}
                </Avatar>
                <Typography variant="subtitle2">{message.sender}</Typography>
                <Typography variant="caption" color="text.secondary">
                  {message.timestamp}
                </Typography>
              </Box>
              <Paper
                sx={{
                  p: 1.5,
                  maxWidth: '70%',
                  backgroundColor:
                    message.type === 'user' ? 'secondary.main' : 'primary.main',
                  color: 'common.white',
                }}
              >
                <Typography>{message.content}</Typography>
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
        }}
      >
        <TextField
          fullWidth
          multiline
          maxRows={4}
          variant="outlined"
          placeholder="Type your message..."
          value={messageInput}
          onChange={(e) => setMessageInput(e.target.value)}
        />
        <IconButton
          type="submit"
          color="primary"
          disabled={!messageInput.trim()}
          sx={{ alignSelf: 'flex-end' }}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Box>
  );
};

export default ChatPanel; 