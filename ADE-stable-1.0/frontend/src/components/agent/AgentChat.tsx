import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  TextField,
  IconButton,
  List,
  ListItem,
  ListItemText,
  ListItemAvatar,
  Avatar,
  Typography,
  Paper,
  Divider,
  Chip,
  CircularProgress,
  Tooltip,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Send,
  AttachFile,
  Code,
  Build,
  BugReport,
  CheckCircle,
  Warning,
  Info,
  MoreVert,
} from '@mui/icons-material';
import { formatDistanceToNow } from 'date-fns';
import { useAgentContext } from './AgentContext';

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'agent';
  agentId?: string;
  timestamp: Date;
  type: 'text' | 'code' | 'error' | 'warning' | 'success' | 'info';
  metadata?: {
    file?: string;
    line?: number;
    suggestion?: string;
    action?: string;
  };
}

interface AgentChatProps {
  projectId: string;
  currentFile?: string;
}

const AgentChat: React.FC<AgentChatProps> = ({ projectId, currentFile }) => {
  const { agents, getAgentById } = useAgentContext();
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<string | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || !selectedAgent) return;

    const userMessage: Message = {
      id: Math.random().toString(36).substr(2, 9),
      content: input,
      sender: 'user',
      timestamp: new Date(),
      type: 'text',
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    // Simulate agent response
    setTimeout(() => {
      const agent = getAgentById(selectedAgent);
      if (!agent) return;

      const agentMessage: Message = {
        id: Math.random().toString(36).substr(2, 9),
        content: `I'm ${agent.name}, and I received your message: "${input}"`,
        sender: 'agent',
        agentId: agent.id,
        timestamp: new Date(),
        type: 'text',
      };

      setMessages((prev) => [...prev, agentMessage]);
      setLoading(false);
    }, 1000);
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
  };

  const handleAgentSelect = (agentId: string) => {
    setSelectedAgent(agentId);
    handleMenuClose();
  };

  const getMessageIcon = (type: Message['type']) => {
    switch (type) {
      case 'code':
        return <Code />;
      case 'error':
        return <BugReport />;
      case 'warning':
        return <Warning />;
      case 'success':
        return <CheckCircle />;
      case 'info':
        return <Info />;
      default:
        return <Build />;
    }
  };

  const getMessageColor = (type: Message['type']) => {
    switch (type) {
      case 'error':
        return 'error';
      case 'warning':
        return 'warning';
      case 'success':
        return 'success';
      case 'info':
        return 'info';
      default:
        return 'default';
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Typography variant="h6">Chat with Agents</Typography>
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          {selectedAgent && (
            <Chip
              label={getAgentById(selectedAgent)?.name}
              color="primary"
              size="small"
              onDelete={() => setSelectedAgent(null)}
            />
          )}
          <Tooltip title="Select Agent">
            <IconButton onClick={handleMenuOpen} size="small">
              <MoreVert />
            </IconButton>
          </Tooltip>
          <Menu
            anchorEl={anchorEl}
            open={Boolean(anchorEl)}
            onClose={handleMenuClose}
          >
            {agents.map((agent) => (
              <MenuItem
                key={agent.id}
                onClick={() => handleAgentSelect(agent.id)}
                selected={selectedAgent === agent.id}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                  <Avatar sx={{ width: 24, height: 24 }}>
                    {agent.name[0]}
                  </Avatar>
                  <Typography variant="body2">{agent.name}</Typography>
                </Box>
              </MenuItem>
            ))}
          </Menu>
        </Box>
      </Box>

      <Paper
        sx={{
          flex: 1,
          overflow: 'auto',
          mb: 2,
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
        }}
      >
        {messages.map((message, index) => (
          <React.Fragment key={message.id}>
            {index > 0 && <Divider />}
            <Box
              sx={{
                display: 'flex',
                flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                gap: 1,
              }}
            >
              <ListItemAvatar>
                <Avatar
                  sx={{
                    bgcolor: message.sender === 'user' ? 'primary.main' : 'secondary.main',
                  }}
                >
                  {message.sender === 'user' ? 'U' : getMessageIcon(message.type)}
                </Avatar>
              </ListItemAvatar>
              <Box
                sx={{
                  maxWidth: '70%',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: 0.5,
                }}
              >
                <Box
                  sx={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: 1,
                    flexDirection: message.sender === 'user' ? 'row-reverse' : 'row',
                  }}
                >
                  {message.sender === 'agent' && message.agentId && (
                    <Chip
                      label={getAgentById(message.agentId)?.name}
                      size="small"
                      color={getMessageColor(message.type)}
                    />
                  )}
                  <Typography variant="caption" color="text.secondary">
                    {formatDistanceToNow(message.timestamp, { addSuffix: true })}
                  </Typography>
                </Box>
                <Typography
                  variant="body2"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    wordBreak: 'break-word',
                  }}
                >
                  {message.content}
                </Typography>
                {message.metadata && (
                  <Box sx={{ mt: 1 }}>
                    {message.metadata.file && (
                      <Typography variant="caption" color="text.secondary">
                        File: {message.metadata.file}
                        {message.metadata.line && `:${message.metadata.line}`}
                      </Typography>
                    )}
                    {message.metadata.suggestion && (
                      <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                        Suggestion: {message.metadata.suggestion}
                      </Typography>
                    )}
                    {message.metadata.action && (
                      <Typography variant="caption" color="text.secondary" sx={{ ml: 1 }}>
                        Action: {message.metadata.action}
                      </Typography>
                    )}
                  </Box>
                )}
              </Box>
            </Box>
          </React.Fragment>
        ))}
        <div ref={messagesEndRef} />
      </Paper>

      <Box sx={{ display: 'flex', gap: 1 }}>
        <TextField
          fullWidth
          multiline
          maxRows={4}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder={selectedAgent ? "Type your message..." : "Select an agent to start chatting"}
          disabled={!selectedAgent}
          InputProps={{
            startAdornment: (
              <Tooltip title="Attach File">
                <IconButton size="small" disabled={!selectedAgent}>
                  <AttachFile />
                </IconButton>
              </Tooltip>
            ),
          }}
        />
        <IconButton
          color="primary"
          onClick={handleSend}
          disabled={!input.trim() || !selectedAgent || loading}
        >
          {loading ? <CircularProgress size={24} /> : <Send />}
        </IconButton>
      </Box>
    </Box>
  );
};

export default AgentChat; 