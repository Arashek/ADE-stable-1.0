import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Divider,
  Chip,
  Tooltip,
  CircularProgress
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as AgentIcon,
  Person as UserIcon,
  Code as CodeIcon,
  Palette as DesignIcon,
  Architecture as ArchitectIcon,
  BugReport as TesterIcon,
  Description as DocIcon,
  IntegrationInstructions as IntegrationIcon
} from '@mui/icons-material';
import { AgentType, Agent } from '../services/AgentCollaborationService';

interface Message {
  id: string;
  content: string;
  sender: string;
  senderType: 'user' | 'agent';
  agentType?: AgentType;
  timestamp: Date;
  status: 'sending' | 'sent' | 'error';
}

interface AgentChatProps {
  projectId: string;
  agentType: AgentType;
  onClose?: () => void;
}

const getAgentIcon = (type: AgentType) => {
  switch (type) {
    case 'code-implementer':
      return <CodeIcon />;
    case 'designer':
      return <DesignIcon />;
    case 'architect':
      return <ArchitectIcon />;
    case 'tester':
      return <TesterIcon />;
    case 'documentation':
      return <DocIcon />;
    case 'integration':
      return <IntegrationIcon />;
    default:
      return <AgentIcon />;
  }
};

const getAgentColor = (type: AgentType) => {
  switch (type) {
    case 'code-implementer':
      return '#2196F3';
    case 'designer':
      return '#E91E63';
    case 'architect':
      return '#9C27B0';
    case 'tester':
      return '#F44336';
    case 'documentation':
      return '#4CAF50';
    case 'integration':
      return '#FF9800';
    default:
      return '#757575';
  }
};

export const AgentChat: React.FC<AgentChatProps> = ({
  projectId,
  agentType,
  onClose
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const newMessage: Message = {
      id: Date.now().toString(),
      content: input.trim(),
      sender: 'User',
      senderType: 'user',
      timestamp: new Date(),
      status: 'sending'
    };

    setMessages(prev => [...prev, newMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Here we would send the message to the appropriate agent
      // and handle the response
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulated delay

      const response: Message = {
        id: (Date.now() + 1).toString(),
        content: `This is a response from the ${agentType} agent.`,
        sender: agentType,
        senderType: 'agent',
        agentType,
        timestamp: new Date(),
        status: 'sent'
      };

      setMessages(prev => [...prev, response]);
    } catch (error) {
      console.error('Error sending message:', error);
      setMessages(prev => prev.map(msg => 
        msg.id === newMessage.id 
          ? { ...msg, status: 'error' }
          : msg
      ));
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Avatar sx={{ bgcolor: getAgentColor(agentType) }}>
            {getAgentIcon(agentType)}
          </Avatar>
          <Typography variant="h6">
            {agentType.split('-').map(word => 
              word.charAt(0).toUpperCase() + word.slice(1)
            ).join(' ')} Agent
          </Typography>
        </Box>
      </Paper>

      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        <List>
          {messages.map((message) => (
            <ListItem
              key={message.id}
              sx={{
                flexDirection: message.senderType === 'user' ? 'row-reverse' : 'row',
                gap: 1
              }}
            >
              <ListItemAvatar>
                <Avatar
                  sx={{
                    bgcolor: message.senderType === 'user'
                      ? 'primary.main'
                      : getAgentColor(message.agentType || 'project-manager')
                  }}
                >
                  {message.senderType === 'user' ? <UserIcon /> : getAgentIcon(message.agentType || 'project-manager')}
                </Avatar>
              </ListItemAvatar>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle2">
                      {message.sender}
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      {message.timestamp.toLocaleTimeString()}
                    </Typography>
                    {message.status === 'sending' && (
                      <CircularProgress size={12} />
                    )}
                    {message.status === 'error' && (
                      <Chip
                        size="small"
                        label="Error"
                        color="error"
                        variant="outlined"
                      />
                    )}
                  </Box>
                }
                secondary={
                  <Typography
                    variant="body2"
                    sx={{
                      whiteSpace: 'pre-wrap',
                      wordBreak: 'break-word'
                    }}
                  >
                    {message.content}
                  </Typography>
                }
              />
            </ListItem>
          ))}
          <div ref={messagesEndRef} />
        </List>
      </Box>

      <Paper sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type your message..."
            disabled={isLoading}
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: 2
              }
            }}
          />
          <Tooltip title="Send message">
            <IconButton
              color="primary"
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
            >
              <SendIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>
    </Box>
  );
}; 