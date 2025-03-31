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
  ListItemAvatar,
  Avatar,
  Chip,
  Divider,
  Tooltip,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as AgentIcon,
  Person as UserIcon,
  Code as CodeIcon,
  AttachFile as AttachFileIcon,
  Chat as ChatIcon,
} from '@mui/icons-material';
import { useChatStore } from '../store/chatStore';
import Editor from '@monaco-editor/react';

interface ChatThread {
  id: string;
  title: string;
  type: 'task' | 'decision' | 'general';
  lastMessage: string;
  timestamp: Date;
  unreadCount: number;
}

const ChatPanel: React.FC = () => {
  const [message, setMessage] = useState('');
  const [activeTab, setActiveTab] = useState(0);
  const [selectedThread, setSelectedThread] = useState<ChatThread | null>(null);
  const messages = useChatStore((state) => state.messages);
  const addMessage = useChatStore((state) => state.addMessage);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Mock data - replace with actual data from API
  const chatThreads: ChatThread[] = [
    {
      id: '1',
      title: 'Authentication Implementation',
      type: 'task',
      lastMessage: 'Let\'s discuss the authentication flow',
      timestamp: new Date('2024-03-19T10:00:00'),
      unreadCount: 2,
    },
    {
      id: '2',
      title: 'Database Schema Decision',
      type: 'decision',
      lastMessage: 'We need to choose between SQL and NoSQL',
      timestamp: new Date('2024-03-19T09:30:00'),
      unreadCount: 0,
    },
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || !selectedThread) return;

    addMessage({
      id: Date.now().toString(),
      content: message,
      sender: {
        id: 'user',
        name: 'You',
        type: 'user',
      },
      timestamp: new Date(),
      type: 'text',
    });

    // TODO: Send message to AI agent
    console.log('Sending message to thread:', selectedThread.title, message);
    
    setMessage('');
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setActiveTab(newValue);
  };

  const getThreadTypeColor = (type: ChatThread['type']) => {
    switch (type) {
      case 'task':
        return 'primary';
      case 'decision':
        return 'secondary';
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
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <ChatIcon sx={{ mr: 1 }} />
        <Typography variant="h6">Contextual Chat</Typography>
      </Box>

      <Tabs
        value={activeTab}
        onChange={handleTabChange}
        sx={{ borderBottom: 1, borderColor: 'divider', mb: 2 }}
      >
        <Tab label="Threads" />
        <Tab label="Messages" />
      </Tabs>

      {activeTab === 0 ? (
        // Threads List
        <List sx={{ flex: 1, overflow: 'auto' }}>
          {chatThreads.map((thread) => (
            <ListItem
              key={thread.id}
              button
              selected={selectedThread?.id === thread.id}
              onClick={() => setSelectedThread(thread)}
            >
              <ListItemAvatar>
                <Avatar>
                  <AgentIcon />
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle2">{thread.title}</Typography>
                    <Chip
                      label={thread.type}
                      size="small"
                      color={getThreadTypeColor(thread.type)}
                    />
                  </Box>
                }
                secondary={
                  <Typography variant="body2" color="text.secondary">
                    {thread.lastMessage}
                  </Typography>
                }
              />
              {thread.unreadCount > 0 && (
                <Chip
                  label={thread.unreadCount}
                  size="small"
                  color="primary"
                />
              )}
            </ListItem>
          ))}
        </List>
      ) : (
        // Messages View
        <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
          <Box
            sx={{
              flex: 1,
              overflow: 'auto',
              mb: 2,
              display: 'flex',
              flexDirection: 'column',
              gap: 1,
            }}
          >
            {messages.map((msg) => (
              <Box
                key={msg.id}
                sx={{
                  display: 'flex',
                  flexDirection: msg.sender.type === 'user' ? 'row-reverse' : 'row',
                  gap: 1,
                }}
              >
                <Avatar>
                  {msg.sender.type === 'user' ? <UserIcon /> : <AgentIcon />}
                </Avatar>
                <Box
                  sx={{
                    maxWidth: '70%',
                    backgroundColor: msg.sender.type === 'user' ? 'primary.main' : 'background.default',
                    color: msg.sender.type === 'user' ? 'primary.contrastText' : 'text.primary',
                    borderRadius: 2,
                    p: 1,
                  }}
                >
                  {msg.type === 'code' ? (
                    <Editor
                      height="200px"
                      defaultLanguage={msg.metadata?.language || 'typescript'}
                      defaultValue={msg.content}
                      options={{
                        readOnly: true,
                        minimap: { enabled: false },
                        scrollBeyondLastLine: false,
                        fontSize: 14,
                        lineNumbers: 'on',
                        theme: 'vs-dark',
                      }}
                    />
                  ) : (
                    <Typography variant="body2">{msg.content}</Typography>
                  )}
                  <Typography variant="caption" sx={{ opacity: 0.7 }}>
                    {msg.timestamp.toLocaleTimeString()}
                  </Typography>
                </Box>
              </Box>
            ))}
            <div ref={messagesEndRef} />
          </Box>

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
              variant="outlined"
              placeholder={selectedThread ? `Message in ${selectedThread.title}...` : 'Select a thread to chat'}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              disabled={!selectedThread}
            />
            <Tooltip title="Attach File">
              <IconButton disabled={!selectedThread}>
                <AttachFileIcon />
              </IconButton>
            </Tooltip>
            <IconButton
              type="submit"
              color="primary"
              disabled={!message.trim() || !selectedThread}
            >
              <SendIcon />
            </IconButton>
          </Box>
        </Box>
      )}
    </Paper>
  );
};

export default ChatPanel; 