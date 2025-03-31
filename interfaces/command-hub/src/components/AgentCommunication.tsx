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
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as AgentIcon,
  Person as UserIcon,
  Code as CodeIcon,
  AttachFile as AttachFileIcon,
} from '@mui/icons-material';
import { useChatStore } from '../store/chatStore';

interface Message {
  id: string;
  content: string;
  sender: {
    id: string;
    name: string;
    type: 'agent' | 'user';
    avatar?: string;
  };
  timestamp: Date;
  type: 'text' | 'code' | 'file';
  metadata?: {
    language?: string;
    fileName?: string;
    fileSize?: number;
  };
}

interface Agent {
  id: string;
  name: string;
  status: 'online' | 'busy' | 'offline';
  currentTask?: string;
  avatar?: string;
}

const AgentCommunication: React.FC = () => {
  const [message, setMessage] = useState('');
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const messages = useChatStore((state) => state.messages);
  const addMessage = useChatStore((state) => state.addMessage);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Mock data - replace with actual data from API
  const agents: Agent[] = [
    {
      id: '1',
      name: 'System Agent',
      status: 'online',
      currentTask: 'Code Review',
    },
    {
      id: '2',
      name: 'Architecture Agent',
      status: 'busy',
      currentTask: 'Design Review',
    },
  ];

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim() || !selectedAgent) return;

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

    // TODO: Send message to selected agent via WebSocket
    console.log('Sending message to agent:', selectedAgent.name, message);
    
    setMessage('');
  };

  const getStatusColor = (status: Agent['status']) => {
    switch (status) {
      case 'online':
        return 'success';
      case 'busy':
        return 'warning';
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
        height: '400px',
        display: 'flex',
        flexDirection: 'column',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
        <AgentIcon sx={{ mr: 1 }} />
        <Typography variant="h6">Agent Communication</Typography>
      </Box>

      {/* Agent List */}
      <Box sx={{ display: 'flex', gap: 1, mb: 2, overflowX: 'auto' }}>
        {agents.map((agent) => (
          <Chip
            key={agent.id}
            label={agent.name}
            color={getStatusColor(agent.status)}
            onClick={() => setSelectedAgent(agent)}
            variant={selectedAgent?.id === agent.id ? 'filled' : 'outlined'}
            icon={<AgentIcon />}
          />
        ))}
      </Box>

      {/* Messages */}
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
              <Typography variant="body2">{msg.content}</Typography>
              <Typography variant="caption" sx={{ opacity: 0.7 }}>
                {msg.timestamp.toLocaleTimeString()}
              </Typography>
            </Box>
          </Box>
        ))}
        <div ref={messagesEndRef} />
      </Box>

      {/* Message Input */}
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
          placeholder={selectedAgent ? `Message ${selectedAgent.name}...` : 'Select an agent to chat'}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          disabled={!selectedAgent}
        />
        <Tooltip title="Attach File">
          <IconButton disabled={!selectedAgent}>
            <AttachFileIcon />
          </IconButton>
        </Tooltip>
        <IconButton
          type="submit"
          color="primary"
          disabled={!message.trim() || !selectedAgent}
        >
          <SendIcon />
        </IconButton>
      </Box>
    </Paper>
  );
};

export default AgentCommunication; 