import React, { KeyboardEvent, useCallback, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Avatar,
  useTheme,
  useMediaQuery,
  Tooltip,
  Divider,
} from '@mui/material';
import {
  Send as SendIcon,
  Clear as ClearIcon,
  MoreVert as MoreVertIcon,
  Assistant as AssistantIcon,
  Mic as MicIcon,
  MicOff as MicOffIcon,
} from '@mui/icons-material';

// Add type definitions for the Web Speech API
interface SpeechRecognitionEvent extends Event {
  results: SpeechRecognitionResultList;
  resultIndex: number;
  error: any;
}

interface SpeechRecognitionResult {
  isFinal: boolean;
  [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionAlternative {
  transcript: string;
  confidence: number;
}

interface SpeechRecognitionResultList {
  length: number;
  item(index: number): SpeechRecognitionResult;
  [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognition extends EventTarget {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any) | null;
  onend: ((this: SpeechRecognition, ev: Event) => any) | null;
  onerror: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => any) | null;
  start(): void;
  stop(): void;
  abort(): void;
}

interface SpeechRecognitionConstructor {
  new (): SpeechRecognition;
}

declare global {
  interface Window {
    SpeechRecognition?: SpeechRecognitionConstructor;
    webkitSpeechRecognition?: SpeechRecognitionConstructor;
  }
}

interface Message {
  id: string;
  content: string;
  sender: 'user' | 'assistant';
  timestamp: Date;
}

interface ChatPanelProps {
  className?: string;
}

// Custom visually hidden component 
const visuallyHiddenStyles = {
  border: 0,
  clip: 'rect(0 0 0 0)',
  height: '1px',
  margin: -1,
  overflow: 'hidden',
  padding: 0,
  position: 'absolute',
  whiteSpace: 'nowrap',
  width: '1px'
};

const VisuallyHidden: React.FC<{ children: React.ReactNode, id?: string }> = ({ children, id }) => (
  <Box sx={visuallyHiddenStyles} id={id}>{children}</Box>
);

export const ChatPanel: React.FC<ChatPanelProps> = ({ className }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [message, setMessage] = React.useState('');
  const [messages, setMessages] = React.useState<Message[]>([]);
  const messagesEndRef = React.useRef<HTMLDivElement>(null);
  const messageInputRef = React.useRef<HTMLInputElement>(null);
  const [isListening, setIsListening] = React.useState(false);
  const [speechSupported, setSpeechSupported] = React.useState(false);
  const recognitionRef = React.useRef<SpeechRecognition | null>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  React.useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check for browser support of speech recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      setSpeechSupported(true);
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = true;
      recognitionRef.current.interimResults = true;

      recognitionRef.current.onresult = (event) => {
        const transcript = Array.from(event.results)
          .map(result => result[0].transcript)
          .join('');

        setMessage(transcript);
      };

      recognitionRef.current.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        setIsListening(false);
      };

      recognitionRef.current.onend = () => {
        setIsListening(false);
      };
    }
  }, []);

  const toggleListening = useCallback(() => {
    if (!recognitionRef.current) return;

    if (isListening) {
      recognitionRef.current.stop();
      setIsListening(false);
    } else {
      recognitionRef.current.start();
      setIsListening(true);
    }
  }, [isListening]);

  const handleMessageSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (message.trim()) {
      const newMessage: Message = {
        id: Date.now().toString(),
        content: message,
        sender: 'user',
        timestamp: new Date(),
      };
      setMessages([...messages, newMessage]);
      setMessage('');
    }
  };

  const handleKeyDown = (event: KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleMessageSubmit(event);
    }
  };

  const handleClearChat = () => {
    if (window.confirm('Are you sure you want to clear all messages?')) {
      setMessages([]);
      messageInputRef.current?.focus();
    }
  };

  const handleToolbarKeyDown = (event: KeyboardEvent, action: string) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      if (action === 'clear') {
        handleClearChat();
      } else {
        console.log(`Toolbar action: ${action}`);
      }
    }
  };

  return (
    <Box
      className={className}
      role="region"
      aria-label="Chat Assistant"
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100%',
        overflow: 'hidden',
      }}
    >
      <Paper
        elevation={0}
        component="header"
        sx={{
          p: 2,
          borderBottom: 1,
          borderColor: 'divider',
          display: 'flex',
          alignItems: 'center',
          gap: 1,
          backgroundColor: theme.palette.mode === 'dark' 
            ? theme.palette.grey[900] 
            : theme.palette.background.paper,
        }}
      >
        <AssistantIcon color="primary" aria-hidden="true" />
        <Typography variant="h6" component="h2" sx={{ flexGrow: 1 }}>
          Assistant
        </Typography>
        <Box role="toolbar" aria-label="Chat controls">
          <Tooltip title="Clear chat">
            <IconButton
              onClick={handleClearChat}
              aria-label="Clear chat history"
              tabIndex={0}
              onKeyDown={(e) => handleToolbarKeyDown(e, 'clear')}
              sx={{
                '&:focus': {
                  outline: `2px solid ${theme.palette.primary.main}`,
                  outlineOffset: 2,
                },
              }}
            >
              <ClearIcon />
              <VisuallyHidden>Clear chat history</VisuallyHidden>
            </IconButton>
          </Tooltip>
          <Tooltip title="More options">
            <IconButton
              aria-label="More options"
              aria-haspopup="menu"
              tabIndex={0}
              onKeyDown={(e) => handleToolbarKeyDown(e, 'more')}
              sx={{
                '&:focus': {
                  outline: `2px solid ${theme.palette.primary.main}`,
                  outlineOffset: 2,
                },
              }}
            >
              <MoreVertIcon />
              <VisuallyHidden>Open more options</VisuallyHidden>
            </IconButton>
          </Tooltip>
        </Box>
      </Paper>

      <Box
        role="log"
        aria-label="Chat messages"
        aria-live="polite"
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 2,
          display: 'flex',
          flexDirection: 'column',
          gap: 2,
          backgroundColor: theme.palette.mode === 'dark' 
            ? theme.palette.grey[900] 
            : theme.palette.background.default,
        }}
      >
        {messages.map((msg, index) => (
          <Box
            key={msg.id}
            role="article"
            aria-label={`${msg.sender} message`}
            sx={{
              display: 'flex',
              gap: 1,
              alignItems: 'flex-start',
              flexDirection: msg.sender === 'user' ? 'row-reverse' : 'row',
            }}
          >
            <Avatar
              aria-hidden="true"
              sx={{
                bgcolor: msg.sender === 'user' 
                  ? theme.palette.primary.main 
                  : theme.palette.secondary.main,
              }}
            >
              {msg.sender === 'user' ? 'U' : 'A'}
            </Avatar>
            <Paper
              elevation={1}
              sx={{
                p: 2,
                maxWidth: '70%',
                bgcolor: msg.sender === 'user' 
                  ? theme.palette.primary.main 
                  : theme.palette.mode === 'dark'
                    ? theme.palette.grey[800]
                    : theme.palette.background.paper,
                color: msg.sender === 'user' 
                  ? theme.palette.primary.contrastText 
                  : theme.palette.text.primary,
                borderRadius: 2,
              }}
            >
              <Typography variant="body1">{msg.content}</Typography>
              <Typography
                variant="caption"
                component="time"
                dateTime={msg.timestamp.toISOString()}
                sx={{
                  display: 'block',
                  mt: 1,
                  color: msg.sender === 'user' 
                    ? theme.palette.primary.contrastText 
                    : theme.palette.text.secondary,
                  opacity: 0.8,
                }}
              >
                {msg.timestamp.toLocaleTimeString()}
              </Typography>
            </Paper>
          </Box>
        ))}
        <div ref={messagesEndRef} tabIndex={-1} />
      </Box>

      <Divider />
      <Paper
        component="form"
        onSubmit={handleMessageSubmit}
        role="group"
        aria-label="Message input"
        sx={{
          p: 2,
          display: 'flex',
          gap: 1,
          backgroundColor: theme.palette.mode === 'dark' 
            ? theme.palette.grey[900] 
            : theme.palette.background.paper,
        }}
      >
        <TextField
          fullWidth
          inputRef={messageInputRef}
          placeholder="Type a message..."
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={handleKeyDown}
          size="small"
          multiline
          maxRows={4}
          aria-label="Message input"
          InputProps={{
            'aria-describedby': 'message-help-text',
          }}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: 2,
              backgroundColor: theme.palette.mode === 'dark' 
                ? theme.palette.grey[800] 
                : theme.palette.background.paper,
            },
          }}
        />
        {speechSupported && (
          <Tooltip title={isListening ? "Stop voice input" : "Start voice input"}>
            <IconButton
              onClick={toggleListening}
              aria-label={isListening ? "Stop voice input" : "Start voice input"}
              aria-pressed={isListening}
              color={isListening ? "secondary" : "default"}
              sx={{
                borderRadius: 2,
                '&:focus': {
                  outline: `2px solid ${theme.palette.primary.main}`,
                  outlineOffset: 2,
                },
              }}
            >
              {isListening ? <MicOffIcon /> : <MicIcon />}
              <VisuallyHidden>
                {isListening ? "Stop voice input" : "Start voice input"}
              </VisuallyHidden>
            </IconButton>
          </Tooltip>
        )}
        <IconButton
          color="primary"
          type="submit"
          disabled={!message.trim()}
          aria-label="Send message"
          sx={{
            borderRadius: 2,
            bgcolor: theme.palette.primary.main,
            color: theme.palette.primary.contrastText,
            '&:hover': {
              bgcolor: theme.palette.primary.dark,
            },
            '&.Mui-disabled': {
              bgcolor: theme.palette.action.disabledBackground,
              color: theme.palette.action.disabled,
            },
            '&:focus': {
              outline: `2px solid ${theme.palette.primary.main}`,
              outlineOffset: 2,
            },
          }}
        >
          <SendIcon />
          <VisuallyHidden>Send message</VisuallyHidden>
        </IconButton>
      </Paper>
      <VisuallyHidden id="message-help-text">
        Press Enter to send message. Use Shift + Enter for a new line.
        {speechSupported && " Press the microphone button to use voice input."}
      </VisuallyHidden>
    </Box>
  );
}; 