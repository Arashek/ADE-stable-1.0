import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  List,
  ListItem,
  ListItemText,
  Divider,
  CircularProgress,
  Chip,
  Alert
} from '@mui/material';
import { ChatInteractionManager } from '../../../core/models/chat/ChatInteractionManager';
import { ChatResponse, ImplementationOption, ImplementationPlan } from '../../../core/models/analysis/types';

interface Message {
  type: 'user' | 'system';
  content: string;
  timestamp: Date;
  suggestions?: string[];
  options?: ImplementationOption[];
}

interface CodebaseChatProps {
  codebasePath: string;
  onComplete: (plan: ImplementationPlan) => void;
  onCancel: () => void;
}

export const CodebaseChat: React.FC<CodebaseChatProps> = ({
  codebasePath,
  onComplete,
  onCancel
}) => {
  const [chatManager] = useState(() => new ChatInteractionManager());
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    initializeChat();
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const initializeChat = async () => {
    try {
      setLoading(true);
      await chatManager.handleCodebaseUpload(codebasePath);
      const initialResponse = await chatManager.handleUserInput('');
      handleResponse(initialResponse);
    } catch (err) {
      setError('Failed to initialize chat. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || loading) return;

    try {
      setLoading(true);
      setError(null);
      
      // Add user message
      const userMessage: Message = {
        type: 'user',
        content: input,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, userMessage]);
      
      // Get system response
      const response = await chatManager.handleUserInput(input);
      handleResponse(response);
      
      setInput('');
    } catch (err) {
      setError('Failed to process message. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResponse = (response: ChatResponse) => {
    const systemMessage: Message = {
      type: 'system',
      content: response.content,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, systemMessage]);

    // Handle different response types
    switch (response.type) {
      case 'plan':
        if (response.plan) {
          onComplete(response.plan);
        }
        break;
      case 'error':
        setError(response.content);
        break;
      // Add more cases as needed
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const renderMessage = (message: Message) => {
    const isUser = message.type === 'user';
    
    return (
      <ListItem
        key={message.timestamp.getTime()}
        sx={{
          flexDirection: isUser ? 'row-reverse' : 'row',
          justifyContent: isUser ? 'flex-end' : 'flex-start'
        }}
      >
        <Paper
          sx={{
            p: 2,
            maxWidth: '70%',
            backgroundColor: isUser ? 'primary.light' : 'background.paper',
            color: isUser ? 'primary.contrastText' : 'text.primary'
          }}
        >
          <Typography variant="body1">{message.content}</Typography>
          {message.type === 'system' && 'suggestions' in message && message.suggestions && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Suggestions:
              </Typography>
              <List>
                {message.suggestions.map((suggestion: string, index: number) => (
                  <ListItem key={index}>
                    <ListItemText primary={suggestion} />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
          {message.type === 'system' && 'options' in message && message.options && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>
                Implementation Options:
              </Typography>
              <List>
                {message.options.map((option: ImplementationOption, index: number) => (
                  <ListItem key={index}>
                    <ListItemText
                      primary={option.name}
                      secondary={
                        <>
                          <Typography component="span" variant="body2">
                            Duration: {option.duration}
                          </Typography>
                          <br />
                          <Typography component="span" variant="body2">
                            Risk Level: {option.riskLevel}
                          </Typography>
                          <br />
                          <Typography component="span" variant="body2">
                            Quality Improvement: {option.qualityImprovement}
                          </Typography>
                          <br />
                          <Typography component="span" variant="body2">
                            {option.description}
                          </Typography>
                        </>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </Paper>
      </ListItem>
    );
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper sx={{ flex: 1, overflow: 'auto', p: 2, mb: 2 }}>
        <List>
          {messages.map(renderMessage)}
          <div ref={messagesEndRef} />
        </List>
      </Paper>
      
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      
      <form onSubmit={handleSubmit}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={loading}
          />
          <Button
            type="submit"
            variant="contained"
            disabled={loading || !input.trim()}
          >
            {loading ? <CircularProgress size={24} /> : 'Send'}
          </Button>
          <Button
            variant="outlined"
            onClick={onCancel}
            disabled={loading}
          >
            Cancel
          </Button>
        </Box>
      </form>
    </Box>
  );
}; 