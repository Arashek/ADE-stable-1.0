import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  Avatar,
  IconButton,
  Divider,
  CircularProgress,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Send as SendIcon,
  Code as CodeIcon,
  Stop as StopIcon,
  Close as CloseIcon,
} from '@mui/icons-material';

const CodeDisplay = styled(Box)(({ theme }) => ({
  backgroundColor: '#1E1E1E', // VS Code-like dark background
  color: '#D4D4D4',  // Light gray text
  padding: theme.spacing(2),
  borderRadius: theme.shape.borderRadius,
  fontFamily: 'Consolas, Monaco, "Andale Mono", "Ubuntu Mono", monospace',
  fontSize: '0.875rem',
  overflow: 'auto',
  marginBottom: theme.spacing(2),
}));

const Root = styled('div')(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
}));

const ChatContainer = styled('div')(({ theme }) => ({
  flex: 1,
  overflow: 'auto',
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.default,
}));

const Message = styled('div')(({ theme }) => ({
  marginBottom: theme.spacing(2),
  maxWidth: '80%',
}));

const UserMessage = styled(Paper)(({ theme }) => ({
  marginLeft: 'auto',
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  padding: theme.spacing(1, 2),
  borderRadius: theme.shape.borderRadius,
}));

const AgentMessage = styled(Paper)(({ theme }) => ({
  backgroundColor: theme.palette.background.paper,
  padding: theme.spacing(1, 2),
  borderRadius: theme.shape.borderRadius,
}));

const InputContainer = styled('div')(({ theme }) => ({
  padding: theme.spacing(2),
  borderTop: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
}));

const Input = styled(TextField)(({ theme }) => ({
  flex: 1,
}));

const StreamingContainer = styled('div')(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  gap: theme.spacing(1),
  padding: theme.spacing(1, 2),
  backgroundColor: theme.palette.action.hover,
  borderRadius: theme.shape.borderRadius,
}));

const StreamingDot = styled('div')(({ theme }) => ({
  width: 8,
  height: 8,
  borderRadius: '50%',
  backgroundColor: theme.palette.primary.main,
  animation: '$pulse 1.5s infinite',
}));

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
    <Root>
      <ChatContainer>
        {messages.map((message) => (
          <Message
            key={message.id}
            style={{ alignSelf: message.type === 'user' ? 'flex-end' : 'flex-start' }}
          >
            {message.type === 'user' ? (
              <UserMessage elevation={1}>
                <Typography variant="body1">{message.content}</Typography>
                
                {message.codeBlocks?.map((block, index) => (
                  <CodeDisplay key={index}>
                    <pre>
                      <code>{block.code}</code>
                    </pre>
                  </CodeDisplay>
                ))}

                {message.isStreaming && (
                  <StreamingContainer>
                    <StreamingDot />
                    <Typography variant="caption">Generating response...</Typography>
                  </StreamingContainer>
                )}
              </UserMessage>
            ) : (
              <AgentMessage elevation={1}>
                <Typography variant="body1">{message.content}</Typography>
                
                {message.codeBlocks?.map((block, index) => (
                  <CodeDisplay key={index}>
                    <pre>
                      <code>{block.code}</code>
                    </pre>
                  </CodeDisplay>
                ))}

                {message.isStreaming && (
                  <StreamingContainer>
                    <StreamingDot />
                    <Typography variant="caption">Generating response...</Typography>
                  </StreamingContainer>
                )}
              </AgentMessage>
            )}
          </Message>
        ))}
        <div ref={chatEndRef} />
      </ChatContainer>

      <InputContainer>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Input
            variant="outlined"
            size="small"
            placeholder="Type your message..."
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyPress={handleKeyPress}
            fullWidth
            disabled={isGenerating}
          />
          
          {isGenerating ? (
            <IconButton color="primary" onClick={onStopGeneration}>
              <CloseIcon />
            </IconButton>
          ) : (
            <IconButton color="primary" onClick={handleSend} disabled={!inputValue.trim()}>
              <SendIcon />
            </IconButton>
          )}
        </Box>
      </InputContainer>
    </Root>
  );
};

export default LiveChat;