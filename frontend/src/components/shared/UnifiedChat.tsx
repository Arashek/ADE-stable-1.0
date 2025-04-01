import React, { useState, useRef, useEffect } from 'react';
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
  Chip,
  Divider,
  Tooltip,
  Menu,
  MenuItem,
  Tab,
  Tabs,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
} from '@mui/material';
import {
  Send as SendIcon,
  SmartToy as AgentIcon,
  Person as UserIcon,
  Code as CodeIcon,
  AttachFile as AttachFileIcon,
  MoreVert as MoreVertIcon,
  ContentCopy as CopyIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Save as SaveIcon,
  Close as CloseIcon,
  Chat as ChatIcon,
  GitHub as GitHubIcon,
  Terminal as TerminalIcon,
  Reply as ReplyIcon,
  Error as ErrorIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Editor } from '@monaco-editor/react';

interface Message {
  id: string;
  content: string;
  sender: {
    id: string;
    name: string;
    avatar?: string;
    type: 'user' | 'agent' | 'system';
  };
  timestamp: string;
  threadId?: string;
  parentId?: string;
  codeBlock?: {
    language: string;
    code: string;
  };
  status?: 'sending' | 'sent' | 'error';
  error?: {
    message: string;
    code: string;
    retryable: boolean;
  };
}

interface ChatThread {
  id: string;
  title: string;
  type: 'task' | 'decision' | 'general' | 'review';
  lastMessage: string;
  timestamp: Date;
  unreadCount: number;
  participants: Array<{
    id: string;
    name: string;
    type: 'agent' | 'user';
    avatar?: string;
  }>;
}

interface Agent {
  id: string;
  name: string;
  type: 'agent';
  capabilities: string[];
}

interface UnifiedChatProps {
  threads?: ChatThread[];
  onSendMessage: (message: string, threadId?: string) => Promise<void>;
  onCreateThread?: (title: string, type: ChatThread['type']) => Promise<void>;
  onEditMessage?: (messageId: string, content: string) => Promise<void>;
  onDeleteMessage?: (messageId: string) => Promise<void>;
  onReactToMessage?: (messageId: string, reaction: string) => Promise<void>;
  onFileUpload?: (file: File, threadId?: string) => Promise<void>;
  onCodeExecute?: (code: string, language: string) => Promise<void>;
  showThreads?: boolean;
  currentAgent?: Agent;
  isOffline?: boolean;
  onRetryMessage?: (messageId: string) => Promise<void>;
}

const UnifiedChat: React.FC<UnifiedChatProps> = ({
  threads = [],
  onSendMessage,
  onCreateThread,
  onEditMessage,
  onDeleteMessage,
  onReactToMessage,
  onFileUpload,
  onCodeExecute,
  showThreads = true,
  currentAgent,
  isOffline = false,
  onRetryMessage,
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState('');
  const [activeThread, setActiveThread] = useState<string | null>(null);
  const [menuAnchorEl, setMenuAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedMessage, setSelectedMessage] = useState<Message | null>(null);
  const [showNewThreadDialog, setShowNewThreadDialog] = useState(false);
  const [newThreadTitle, setNewThreadTitle] = useState('');
  const [newThreadType, setNewThreadType] = useState<ChatThread['type']>('general');
  const [codeEditorOpen, setCodeEditorOpen] = useState(false);
  const [codeContent, setCodeContent] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('typescript');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<{ message: string; code: string } | null>(null);
  const [retryQueue, setRetryQueue] = useState<Message[]>([]);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOffline) {
      setError({
        message: 'You are currently offline. Messages will be queued and sent when connection is restored.',
        code: 'OFFLINE_MODE'
      });
    } else {
      setError(null);
      if (retryQueue.length > 0) {
        processRetryQueue();
      }
    }
  }, [isOffline]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const processRetryQueue = async () => {
    for (const message of retryQueue) {
      try {
        await onRetryMessage?.(message.id);
        setMessages(prev => prev.map(m => 
          m.id === message.id ? { ...m, status: 'sent', error: undefined } : m
        ));
      } catch (err) {
        console.error('Failed to retry message:', err);
      }
    }
    setRetryQueue([]);
  };

  const handleSend = async () => {
    if (!newMessage.trim() || isLoading) return;

    const messageToSend: Message = {
      id: Date.now().toString(),
      content: newMessage,
      sender: {
        id: 'user',
        name: 'You',
        type: 'user'
      },
      timestamp: new Date().toISOString(),
      status: 'sending'
    };

    setMessages(prev => [...prev, messageToSend]);
    setNewMessage('');
    setIsLoading(true);

    try {
      await onSendMessage(messageToSend.content, activeThread || undefined);
      setMessages(prev => prev.map(m => 
        m.id === messageToSend.id ? { ...m, status: 'sent' } : m
      ));
    } catch (err) {
      const errorMessage: Message['error'] = {
        message: err instanceof Error ? err.message : 'Failed to send message',
        code: 'SEND_ERROR',
        retryable: true
      };
      
      setMessages(prev => prev.map(m => 
        m.id === messageToSend.id ? { ...m, status: 'error', error: errorMessage } : m
      ));
      
      if (isOffline) {
        setRetryQueue(prev => [...prev, messageToSend]);
      }
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

  const handleMessageMenu = (event: React.MouseEvent<HTMLElement>, message: Message) => {
    event.preventDefault();
    setSelectedMessage(message);
    setMenuAnchorEl(event.currentTarget);
  };

  const handleMenuClose = () => {
    setMenuAnchorEl(null);
    setSelectedMessage(null);
  };

  const handleReply = () => {
    if (selectedMessage) {
      setActiveThread(selectedMessage.id);
    }
    handleMenuClose();
  };

  const handleAddCodeBlock = () => {
    setNewMessage((prev) => `${prev}\n\`\`\`\n// Add your code here\n\`\`\``);
    handleMenuClose();
  };

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && onFileUpload) {
      onFileUpload(file, activeThread || undefined);
    }
  };

  const handleCreateThread = () => {
    if (!newThreadTitle.trim() || !onCreateThread) return;
    onCreateThread(newThreadTitle, newThreadType);
    setShowNewThreadDialog(false);
    setNewThreadTitle('');
  };

  const handleCodeSubmit = () => {
    if (!codeContent.trim() || !onCodeExecute) return;
    onCodeExecute(codeContent, selectedLanguage);
    setCodeEditorOpen(false);
    setCodeContent('');
  };

  const handleRetry = async (messageId: string) => {
    const message = messages.find(m => m.id === messageId);
    if (!message || !message.error?.retryable) return;

    setIsLoading(true);
    try {
      await onRetryMessage?.(messageId);
      setMessages(prev => prev.map(m => 
        m.id === messageId ? { ...m, status: 'sent', error: undefined } : m
      ));
    } catch (err) {
      setError({
        message: 'Failed to retry message',
        code: 'RETRY_ERROR'
      });
    } finally {
      setIsLoading(false);
    }
  };

  const renderMessage = (message: Message) => {
    const isCurrentUser = message.sender.type === 'user';
    const hasCodeBlock = message.content.includes('```');

    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: isCurrentUser ? 'row-reverse' : 'row',
          mb: 2,
          gap: 1,
        }}
      >
        <Avatar
          src={message.sender.avatar}
          sx={{
            bgcolor: message.sender.type === 'agent' ? 'primary.main' : 'secondary.main',
          }}
        >
          {message.sender.name[0]}
        </Avatar>
        <Box sx={{ maxWidth: '70%' }}>
          <Box
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1,
              mb: 0.5,
              flexDirection: isCurrentUser ? 'row-reverse' : 'row',
            }}
          >
            <Typography variant="subtitle2">{message.sender.name}</Typography>
            <Typography variant="caption" color="text.secondary">
              {new Date(message.timestamp).toLocaleTimeString()}
            </Typography>
          </Box>
          <Paper
            sx={{
              p: 1.5,
              backgroundColor: isCurrentUser ? 'primary.light' : 'background.paper',
              color: isCurrentUser ? 'primary.contrastText' : 'text.primary',
            }}
          >
            {hasCodeBlock ? (
              message.content.split('```').map((part, index) => {
                if (index % 2 === 1) {
                  // Code block
                  const [language, ...codeLines] = part.trim().split('\n');
                  const code = codeLines.join('\n');
                  return (
                    <Box key={index} sx={{ my: 1 }}>
                      <SyntaxHighlighter
                        language={language || 'typescript'}
                        style={vscDarkPlus}
                        customStyle={{ margin: 0 }}
                      >
                        {code}
                      </SyntaxHighlighter>
                    </Box>
                  );
                }
                // Regular text
                return part && (
                  <Typography key={index} sx={{ whiteSpace: 'pre-wrap' }}>
                    {part}
                  </Typography>
                );
              })
            ) : (
              <Typography sx={{ whiteSpace: 'pre-wrap' }}>{message.content}</Typography>
            )}
          </Paper>
          {message.threadId && showThreads && (
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ mt: 0.5, display: 'block' }}
            >
              In thread
            </Typography>
          )}
        </Box>
        <IconButton
          size="small"
          onClick={(e) => handleMessageMenu(e, message)}
          sx={{ alignSelf: 'flex-start' }}
        >
          <MoreVertIcon fontSize="small" />
        </IconButton>
      </Box>
    );
  };

  return (
    <Paper sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {error && (
        <Paper 
          sx={{ 
            p: 2, 
            mb: 2, 
            bgcolor: error.code === 'OFFLINE_MODE' ? 'warning.light' : 'error.light',
            color: error.code === 'OFFLINE_MODE' ? 'warning.dark' : 'error.dark'
          }}
        >
          <Typography variant="body2">{error.message}</Typography>
        </Paper>
      )}

      {showThreads && (
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', p: 2 }}>
            <Typography variant="h6">Conversations</Typography>
            <Button
              startIcon={<ChatIcon />}
              onClick={() => setShowNewThreadDialog(true)}
            >
              New Thread
            </Button>
          </Box>
          <List>
            {threads.map((thread) => (
              <ListItem
                key={thread.id}
                button
                selected={activeThread === thread.id}
                onClick={() => setActiveThread(thread.id)}
              >
                <ListItemAvatar>
                  <Avatar>
                    {thread.type === 'task' ? (
                      <CodeIcon />
                    ) : thread.type === 'review' ? (
                      <GitHubIcon />
                    ) : (
                      <ChatIcon />
                    )}
                  </Avatar>
                </ListItemAvatar>
                <ListItemText
                  primary={thread.title}
                  secondary={`${thread.lastMessage} · ${thread.timestamp.toLocaleTimeString()}`}
                />
                {thread.unreadCount > 0 && (
                  <Chip
                    label={thread.unreadCount}
                    color="primary"
                    size="small"
                  />
                )}
              </ListItem>
            ))}
          </List>
        </Box>
      )}

      <Box sx={{ flex: 1, overflow: 'auto', p: 2 }}>
        <List>
          {messages.map((message) => (
            <React.Fragment key={message.id}>
              {renderMessage(message)}
            </React.Fragment>
          ))}
          <div ref={messagesEndRef} />
        </List>
      </Box>

      <Box
        component="form"
        onSubmit={handleSend}
        sx={{
          p: 2,
          borderTop: 1,
          borderColor: 'divider',
          backgroundColor: 'background.paper',
        }}
      >
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Type a message..."
            variant="outlined"
            size="small"
          />
          <Tooltip title="Attach File">
            <IconButton onClick={() => fileInputRef.current?.click()}>
              <AttachFileIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Code Editor">
            <IconButton onClick={() => setCodeEditorOpen(true)}>
              <CodeIcon />
            </IconButton>
          </Tooltip>
          <IconButton
            color="primary"
            type="submit"
            disabled={!newMessage.trim()}
          >
            <SendIcon />
          </IconButton>
        </Box>
      </Box>

      <input
        type="file"
        ref={fileInputRef}
        style={{ display: 'none' }}
        onChange={handleFileUpload}
      />

      {/* Message Actions Menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
      >
        {showThreads && (
          <MenuItem onClick={handleReply}>
            <ReplyIcon sx={{ mr: 1 }} /> Reply in Thread
          </MenuItem>
        )}
        <MenuItem onClick={handleAddCodeBlock}>
          <CodeIcon sx={{ mr: 1 }} /> Add Code Block
        </MenuItem>
      </Menu>

      {/* New Thread Dialog */}
      <Dialog
        open={showNewThreadDialog}
        onClose={() => setShowNewThreadDialog(false)}
      >
        <DialogTitle>Create New Thread</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Thread Title"
            value={newThreadTitle}
            onChange={(e) => setNewThreadTitle(e.target.value)}
            margin="normal"
          />
          <Tabs
            value={newThreadType}
            onChange={(_, value) => setNewThreadType(value)}
            sx={{ mb: 2 }}
          >
            <Tab label="General" value="general" />
            <Tab label="Task" value="task" />
            <Tab label="Decision" value="decision" />
            <Tab label="Review" value="review" />
          </Tabs>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowNewThreadDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateThread}
            disabled={!newThreadTitle.trim()}
          >
            Create
          </Button>
        </DialogActions>
      </Dialog>

      {/* Code Editor Dialog */}
      <Dialog
        open={codeEditorOpen}
        onClose={() => setCodeEditorOpen(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Code Editor</DialogTitle>
        <DialogContent>
          <Box sx={{ mb: 2 }}>
            <Tabs
              value={selectedLanguage}
              onChange={(_, value) => setSelectedLanguage(value)}
            >
              <Tab label="TypeScript" value="typescript" />
              <Tab label="JavaScript" value="javascript" />
              <Tab label="Python" value="python" />
              <Tab label="JSON" value="json" />
            </Tabs>
          </Box>
          <Editor
            height="400px"
            language={selectedLanguage}
            value={codeContent}
            onChange={(value: string | undefined) => setCodeContent(value || '')}
            theme="vs-dark"
            options={{
              minimap: { enabled: false },
              fontSize: 14,
            }}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCodeEditorOpen(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCodeSubmit}
            disabled={!codeContent.trim()}
          >
            Send
          </Button>
        </DialogActions>
      </Dialog>
    </Paper>
  );
};

export default UnifiedChat; 