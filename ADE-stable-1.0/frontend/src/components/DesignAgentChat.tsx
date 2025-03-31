import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  IconButton,
  Button,
  Grid,
  Divider,
  Tooltip,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  Close as CloseIcon,
  Add as AddIcon,
  DragIndicator as DragIcon,
  Resize as ResizeIcon,
  Save as SaveIcon,
  Undo as UndoIcon,
  Redo as RedoIcon,
} from '@mui/icons-material';
import { DndProvider } from 'react-dnd';
import { HTML5Backend } from 'react-dnd-html5-backend';
import { v4 as uuidv4 } from 'uuid';

interface DesignComponent {
  id: string;
  type: 'container' | 'button' | 'input' | 'text' | 'image' | 'card';
  content: string;
  style: React.CSSProperties;
  position: { x: number; y: number };
  size: { width: number; height: number };
  children?: DesignComponent[];
}

interface DesignAgentChatProps {
  projectId: string;
  onClose?: () => void;
}

export const DesignAgentChat: React.FC<DesignAgentChatProps> = ({ projectId, onClose }) => {
  const [messages, setMessages] = useState<Array<{
    id: string;
    content: string;
    sender: 'user' | 'agent';
    timestamp: Date;
  }>>([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [designComponents, setDesignComponents] = useState<DesignComponent[]>([]);
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null);
  const [history, setHistory] = useState<DesignComponent[][]>([]);
  const [historyIndex, setHistoryIndex] = useState(-1);
  const [notification, setNotification] = useState<{
    message: string;
    severity: 'success' | 'error' | 'info';
  } | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim()) return;

    const userMessage = {
      id: uuidv4(),
      content: input,
      sender: 'user' as const,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Simulate agent response
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      const agentMessage = {
        id: uuidv4(),
        content: 'I understand your request. Let me help you with that.',
        sender: 'agent' as const,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      setNotification({
        message: 'Failed to send message',
        severity: 'error',
      });
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  const addComponent = (type: DesignComponent['type']) => {
    const newComponent: DesignComponent = {
      id: uuidv4(),
      type,
      content: '',
      style: {},
      position: { x: 0, y: 0 },
      size: { width: 200, height: 100 },
    };

    setDesignComponents(prev => [...prev, newComponent]);
    saveToHistory([...designComponents, newComponent]);
  };

  const updateComponent = (id: string, updates: Partial<DesignComponent>) => {
    setDesignComponents(prev =>
      prev.map(comp =>
        comp.id === id ? { ...comp, ...updates } : comp
      )
    );
  };

  const saveToHistory = (components: DesignComponent[]) => {
    const newHistory = history.slice(0, historyIndex + 1);
    newHistory.push(components);
    setHistory(newHistory);
    setHistoryIndex(newHistory.length - 1);
  };

  const undo = () => {
    if (historyIndex > 0) {
      setHistoryIndex(prev => prev - 1);
      setDesignComponents(history[historyIndex - 1]);
    }
  };

  const redo = () => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(prev => prev + 1);
      setDesignComponents(history[historyIndex + 1]);
    }
  };

  const saveDesign = async () => {
    try {
      // Save design to backend
      await new Promise(resolve => setTimeout(resolve, 1000));
      setNotification({
        message: 'Design saved successfully',
        severity: 'success',
      });
    } catch (error) {
      setNotification({
        message: 'Failed to save design',
        severity: 'error',
      });
    }
  };

  return (
    <DndProvider backend={HTML5Backend}>
      <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
        <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6">UI/UX Design Agent</Typography>
          <IconButton onClick={onClose}>
            <CloseIcon />
          </IconButton>
        </Box>

        <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
          {messages.map(message => (
            <Box
              key={message.id}
              sx={{
                display: 'flex',
                justifyContent: message.sender === 'user' ? 'flex-end' : 'flex-start',
                mb: 2,
              }}
            >
              <Paper
                sx={{
                  p: 2,
                  maxWidth: '70%',
                  bgcolor: message.sender === 'user' ? 'primary.light' : 'background.paper',
                  color: message.sender === 'user' ? 'primary.contrastText' : 'text.primary',
                }}
              >
                <Typography variant="body1">{message.content}</Typography>
                <Typography variant="caption" sx={{ display: 'block', mt: 1 }}>
                  {message.timestamp.toLocaleTimeString()}
                </Typography>
              </Paper>
            </Box>
          ))}
          <div ref={messagesEndRef} />
        </Box>

        <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
          <Grid container spacing={1}>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 1, mb: 1 }}>
                <Tooltip title="Add Container">
                  <IconButton onClick={() => addComponent('container')}>
                    <AddIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Add Button">
                  <IconButton onClick={() => addComponent('button')}>
                    <AddIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Add Input">
                  <IconButton onClick={() => addComponent('input')}>
                    <AddIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Undo">
                  <IconButton onClick={undo}>
                    <UndoIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Redo">
                  <IconButton onClick={redo}>
                    <RedoIcon />
                  </IconButton>
                </Tooltip>
                <Tooltip title="Save Design">
                  <IconButton onClick={saveDesign}>
                    <SaveIcon />
                  </IconButton>
                </Tooltip>
              </Box>
            </Grid>
            <Grid item xs={12}>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Type your message..."
                  style={{ flex: 1, padding: '8px', borderRadius: '4px', border: '1px solid #ccc' }}
                />
                <Button
                  variant="contained"
                  onClick={handleSend}
                  disabled={loading || !input.trim()}
                >
                  Send
                </Button>
              </Box>
            </Grid>
          </Grid>
        </Box>

        <Snackbar
          open={!!notification}
          autoHideDuration={6000}
          onClose={() => setNotification(null)}
        >
          <Alert
            onClose={() => setNotification(null)}
            severity={notification?.severity}
            sx={{ width: '100%' }}
          >
            {notification?.message}
          </Alert>
        </Snackbar>
      </Box>
    </DndProvider>
  );
}; 