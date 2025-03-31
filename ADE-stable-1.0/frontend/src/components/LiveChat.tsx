import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  CircularProgress,
  makeStyles,
  Theme,
  createStyles,
} from '@material-ui/core';
import {
  Send as SendIcon,
  Code as CodeIcon,
  Stop as StopIcon,
} from '@material-ui/icons';
import SyntaxHighlighter from 'react-syntax-highlighter';
import { vs2015 } from 'react-syntax-highlighter/dist/esm/styles/hljs';

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    root: {
      height: '100%',
      display: 'flex',
      flexDirection: 'column',
    },
    chatContainer: {
      flex: 1,
      overflow: 'auto',
      padding: theme.spacing(2),
      backgroundColor: theme.palette.background.default,
    },
    message: {
      marginBottom: theme.spacing(2),
      maxWidth: '80%',
    },
    userMessage: {
      marginLeft: 'auto',
      backgroundColor: theme.palette.primary.main,
      color: theme.palette.primary.contrastText,
      padding: theme.spacing(1, 2),
      borderRadius: theme.shape.borderRadius,
    },
    agentMessage: {
      backgroundColor: theme.palette.background.paper,
      padding: theme.spacing(1, 2),
      borderRadius: theme.shape.borderRadius,
    },
    codeBlock: {
      margin: theme.spacing(1, 0),
      borderRadius: theme.shape.borderRadius,
      overflow: 'hidden',
    },
    inputContainer: {
      padding: theme.spacing(2),
      borderTop: `1px solid ${theme.palette.divider}`,
      backgroundColor: theme.palette.background.paper,
    },
    input: {
      flex: 1,
    },
    streamingContainer: {
      display: 'flex',
      alignItems: 'center',
      gap: theme.spacing(1),
      padding: theme.spacing(1, 2),
      backgroundColor: theme.palette.action.hover,
      borderRadius: theme.shape.borderRadius,
    },
    streamingDot: {
      width: 8,
      height: 8,
      borderRadius: '50%',
      backgroundColor: theme.palette.primary.main,
      animation: '$pulse 1.5s infinite',
    },
    '@keyframes pulse': {
      '0%': {
        opacity: 1,
      },
      '50%': {
        opacity: 0.4,
      },
      '100%': {
        opacity: 1,
      },
    },
  })
);

interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
  codeBlocks?: Array<{
    language: string;
    code: string;
  }>;
  isStreaming?: boolean;
}

interface LiveChatProps {
  projectId: string;
  onSendMessage: (message: string) => Promise<void>;
  onStopGeneration: () => void;
}

const LiveChat: React.FC<LiveChatProps> = ({
  projectId,
  onSendMessage,
  onStopGeneration,
}) => {
  const classes = useStyles();
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Scroll to bottom when new messages arrive
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSend = async () => {
    if (!inputValue.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInputValue('');
    setIsGenerating(true);

    try {
      // Start streaming placeholder
      const streamingMessage: Message = {
        id: 'streaming',
        type: 'agent',
        content: '',
        timestamp: new Date(),
        isStreaming: true,
      };
      setMessages((prev) => [...prev, streamingMessage]);

      // Send message and wait for response
      await onSendMessage(inputValue);
      
      // Remove streaming placeholder when done
      setMessages((prev) => prev.filter((m) => m.id !== 'streaming'));
    } catch (error) {
      console.error('Error sending message:', error);
    } finally {
      setIsGenerating(false);
    }
  };

  const handleKeyPress = (event: React.KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleSend();
    }
  };

  return (
    <div className={classes.root}>
      <div className={classes.chatContainer}>
        {messages.map((message) => (
          <Box
            key={message.id}
            className={classes.message}
            alignSelf={message.type === 'user' ? 'flex-end' : 'flex-start'}
          >
            <Paper
              className={
                message.type === 'user' ? classes.userMessage : classes.agentMessage
              }
              elevation={1}
            >
              <Typography variant="body1">{message.content}</Typography>
              
              {message.codeBlocks?.map((block, index) => (
                <div key={index} className={classes.codeBlock}>
                  <SyntaxHighlighter
                    language={block.language}
                    style={vs2015}
                    customStyle={{ margin: 0 }}
                  >
                    {block.code}
                  </SyntaxHighlighter>
                </div>
              ))}

              {message.isStreaming && (
                <Box className={classes.streamingContainer}>
                  <div className={classes.streamingDot} />
                  <Typography variant="caption">Generating response...</Typography>
                </Box>
              )}
            </Paper>
          </Box>
        ))}
        <div ref={chatEndRef} />
      </div>

      <Box className={classes.inputContainer} display="flex" gap={1}>
        <TextField
          className={classes.input}
          variant="outlined"
          size="small"
          placeholder="Type your message..."
          multiline
          maxRows={4}
          value={inputValue}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          disabled={isGenerating}
        />
        {isGenerating ? (
          <IconButton color="secondary" onClick={onStopGeneration}>
            <StopIcon />
          </IconButton>
        ) : (
          <IconButton
            color="primary"
            onClick={handleSend}
            disabled={!inputValue.trim()}
          >
            <SendIcon />
          </IconButton>
        )}
      </Box>
    </div>
  );
};

export default LiveChat; 