import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  IconButton,
  Tooltip,
  TextField,
  Tabs,
  Tab,
  Divider,
  Chip,
  CircularProgress,
  Card,
  CardContent,
  CardHeader,
  Avatar,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Menu,
  MenuItem,
} from '@mui/material';
import {
  Send as SendIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Save as SaveIcon,
  Code as CodeIcon,
  BugReport as BugIcon,
  Psychology as AIIcon,
  Palette as DesignIcon,
  Terminal as TerminalIcon,
  SmartToy as RobotIcon,
  Memory as MemoryIcon,
  Storage as DatabaseIcon,
  Analytics as AnalyticsIcon,
  Sync as SyncIcon,
  ExpandMore as ExpandMoreIcon,
  ChevronRight as ChevronRightIcon,
  Description as DocumentIcon,
} from '@mui/icons-material';
import CodeEditor from './CodeEditor';
import { SyntaxHighlighter } from './common/SyntaxHighlighter';

interface CommandHubProps {
  onSave: (design: any) => void;
  onGenerateCode: (design: any) => void;
  isGenerating: boolean;
  activeAgent: string;
}

interface Message {
  id: string;
  role: 'user' | 'agent' | 'system';
  content: string;
  agent?: string;
  timestamp: Date;
  status?: 'sending' | 'sent' | 'error';
  code?: {
    language: string;
    content: string;
  };
}

interface AgentStatus {
  id: string;
  name: string;
  status: 'idle' | 'thinking' | 'working' | 'error';
  lastActivity: Date;
  expertise: string[];
}

const CommandHub: React.FC<CommandHubProps> = ({
  onSave,
  onGenerateCode,
  isGenerating,
  activeAgent,
}) => {
  const [currentTab, setCurrentTab] = useState<number>(0);
  const [prompt, setPrompt] = useState<string>('');
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      role: 'system',
      content: 'Welcome to ADE Command Hub. How can I assist you with your development?',
      timestamp: new Date(),
    },
  ]);
  const [executing, setExecuting] = useState<boolean>(false);
  const [agents, setAgents] = useState<AgentStatus[]>([
    {
      id: 'assistant',
      name: 'Assistant Agent',
      status: 'idle',
      lastActivity: new Date(),
      expertise: ['General', 'Coordination'],
    },
    {
      id: 'developer',
      name: 'Developer Agent',
      status: 'idle',
      lastActivity: new Date(),
      expertise: ['Code', 'Architecture'],
    },
    {
      id: 'designer',
      name: 'Designer Agent',
      status: 'idle',
      lastActivity: new Date(),
      expertise: ['UI/UX', 'Design Systems'],
    },
    {
      id: 'advisor',
      name: 'Advisor Agent',
      status: 'idle',
      lastActivity: new Date(),
      expertise: ['Best Practices', 'Performance'],
    },
  ]);
  const [selectedCode, setSelectedCode] = useState<string>('');
  const [codeLanguage, setCodeLanguage] = useState<string>('javascript');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const [expandedMessage, setExpandedMessage] = useState<string | null>(null);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [activeAgentFilter, setActiveAgentFilter] = useState<string>('all');

  // Auto-scroll to bottom of messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setCurrentTab(newValue);
  };

  const handleSendPrompt = async () => {
    if (!prompt.trim()) return;
    
    const newMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: prompt,
      timestamp: new Date(),
    };
    
    setMessages([...messages, newMessage]);
    setPrompt('');
    setExecuting(true);
    
    // Update agent status
    updateAgentStatus(activeAgent, 'thinking');
    
    try {
      // Simulate API call to fetch agent response
      setTimeout(() => {
        const newAgentMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'agent',
          agent: activeAgent,
          content: `I've analyzed your request: "${prompt}". Here's my response based on ADE platform capabilities.`,
          timestamp: new Date(),
          code: {
            language: 'javascript',
            content: `// Sample code based on your request\nfunction processUserRequest(input) {\n  const result = analyze(input);\n  return optimize(result);\n}\n\n// This would be implemented based on specific requirements`,
          },
        };
        
        setMessages(prev => [...prev, newAgentMessage]);
        setExecuting(false);
        updateAgentStatus(activeAgent, 'idle');
      }, 2000);
    } catch (error) {
      console.error('Error sending prompt:', error);
      setExecuting(false);
      updateAgentStatus(activeAgent, 'error');
    }
  };

  const updateAgentStatus = (agentId: string, status: 'idle' | 'thinking' | 'working' | 'error') => {
    setAgents(prevAgents => 
      prevAgents.map(agent => 
        agent.id === agentId 
          ? { ...agent, status, lastActivity: new Date() } 
          : agent
      )
    );
  };

  const handleCodeSelection = (code: string, language: string = 'javascript') => {
    setSelectedCode(code);
    setCodeLanguage(language);
  };

  const handleOpenMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleCloseMenu = () => {
    setAnchorEl(null);
  };

  const handleExpandMessage = (messageId: string) => {
    setExpandedMessage(expandedMessage === messageId ? null : messageId);
  };

  const filterAgents = (status: string) => {
    setActiveAgentFilter(status);
  };

  const filteredAgents = agents.filter(agent => 
    activeAgentFilter === 'all' || agent.status === activeAgentFilter
  );

  const getAgentStatusColor = (status: string) => {
    switch (status) {
      case 'thinking': return 'primary';
      case 'working': return 'secondary';
      case 'error': return 'error';
      default: return 'default';
    }
  };
  
  const getAgentStatusIcon = (status: string) => {
    switch (status) {
      case 'thinking': return <SyncIcon sx={{ animation: 'spin 2s linear infinite' }} />;
      case 'working': return <MemoryIcon />;
      case 'error': return <BugIcon />;
      default: return <RobotIcon />;
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper sx={{ 
        p: 2, 
        borderRadius: 2,
        mb: 2,
        backgroundColor: 'background.paper',
        boxShadow: 2
      }}>
        <Typography variant="h5" gutterBottom fontWeight="500">
          Command Hub
        </Typography>
        <Typography variant="body2" color="text.secondary">
          Central command center for interaction with specialized ADE agents
        </Typography>
      </Paper>

      <Grid container spacing={2} sx={{ flexGrow: 1 }}>
        {/* Left Panel - Conversation + Input */}
        <Grid item xs={12} md={7} lg={8} sx={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
          <Paper sx={{ 
            p: 2, 
            flexGrow: 1, 
            display: 'flex',
            flexDirection: 'column',
            mb: 2,
            borderRadius: 2,
            boxShadow: 2,
            overflow: 'hidden',
          }}>
            <Tabs 
              value={currentTab} 
              onChange={handleTabChange} 
              aria-label="command hub tabs"
              sx={{ mb: 2, borderBottom: 1, borderColor: 'divider' }}
            >
              <Tab label="Chat" icon={<AIIcon />} iconPosition="start" />
              <Tab label="Code" icon={<CodeIcon />} iconPosition="start" />
              <Tab label="Terminal" icon={<TerminalIcon />} iconPosition="start" />
              <Tab label="Design" icon={<DesignIcon />} iconPosition="start" />
            </Tabs>

            {/* Chat Panel */}
            {currentTab === 0 && (
              <Box sx={{ flexGrow: 1, overflow: 'auto', mb: 2 }}>
                <List>
                  {messages.map((message) => (
                    <ListItem 
                      key={message.id}
                      alignItems="flex-start"
                      sx={{ 
                        mb: 1,
                        backgroundColor: message.role === 'user' ? 'action.hover' : 'background.paper',
                        borderRadius: 2,
                        p: 2
                      }}
                    >
                      <Avatar 
                        sx={{ 
                          mr: 2, 
                          bgcolor: message.role === 'user' ? 'primary.main' : 'secondary.main'
                        }}
                      >
                        {message.role === 'user' ? 'U' : message.agent?.charAt(0).toUpperCase() || 'A'}
                      </Avatar>
                      <Box sx={{ flexGrow: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="subtitle2">
                            {message.role === 'user' ? 'You' : message.agent || 'System'}
                          </Typography>
                          <Typography variant="caption" color="text.secondary">
                            {message.timestamp.toLocaleTimeString()}
                          </Typography>
                        </Box>
                        <Typography variant="body1" sx={{ whiteSpace: 'pre-wrap' }}>
                          {message.content}
                        </Typography>
                        
                        {message.code && (
                          <Box sx={{ mt: 2 }}>
                            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 1 }}>
                              <Chip 
                                label={message.code.language} 
                                size="small" 
                                icon={<CodeIcon />}
                                sx={{ mr: 1 }}
                              />
                              <IconButton 
                                size="small" 
                                onClick={() => handleExpandMessage(message.id)}
                                aria-label="toggle code expansion"
                              >
                                {expandedMessage === message.id ? <ExpandMoreIcon /> : <ChevronRightIcon />}
                              </IconButton>
                            </Box>
                            {(expandedMessage === message.id) && (
                              <Paper variant="outlined" sx={{ p: 1, borderRadius: 1, overflow: 'auto', maxHeight: 200 }}>
                                <SyntaxHighlighter language={message.code.language} code={message.code.content} />
                              </Paper>
                            )}
                          </Box>
                        )}
                      </Box>
                    </ListItem>
                  ))}
                </List>
                <div ref={messagesEndRef} />
              </Box>
            )}

            {/* Code Panel */}
            {currentTab === 1 && (
              <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                <Typography variant="subtitle2" gutterBottom>Code Editor</Typography>
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    flexGrow: 1, 
                    borderRadius: 1,
                    overflow: 'auto',
                    fontFamily: 'monospace',
                    fontSize: '0.9rem',
                    p: 2,
                    backgroundColor: 'action.hover'
                  }}
                >
                  <pre>{selectedCode || '// Your code will appear here\n// Use the chat to generate code'}</pre>
                </Paper>
              </Box>
            )}

            {/* Terminal Panel */}
            {currentTab === 2 && (
              <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                <Typography variant="subtitle2" gutterBottom>Terminal</Typography>
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    flexGrow: 1, 
                    borderRadius: 1,
                    overflow: 'auto',
                    fontFamily: 'monospace',
                    fontSize: '0.9rem',
                    p: 2,
                    backgroundColor: '#1e1e1e',
                    color: '#f0f0f0'
                  }}
                >
                  <Box component="span" sx={{ color: '#50fa7b' }}>user@ade</Box>
                  <Box component="span" sx={{ color: '#f8f8f2' }}>:</Box>
                  <Box component="span" sx={{ color: '#bd93f9' }}>~/project</Box>
                  <Box component="span" sx={{ color: '#f8f8f2' }}>$ </Box>
                  <Box component="span" sx={{ animation: 'blink 1s step-end infinite' }}>_</Box>
                </Paper>
              </Box>
            )}

            {/* Design Panel */}
            {currentTab === 3 && (
              <Box sx={{ flexGrow: 1, display: 'flex', flexDirection: 'column' }}>
                <Typography variant="subtitle2" gutterBottom>Design Canvas</Typography>
                <Paper 
                  variant="outlined" 
                  sx={{ 
                    flexGrow: 1, 
                    borderRadius: 1,
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    bgcolor: 'background.default'
                  }}
                >
                  <Typography variant="body2" color="text.secondary">
                    Design canvas will be implemented in a future update
                  </Typography>
                </Paper>
              </Box>
            )}

            {/* Command Input */}
            <Box sx={{ 
              display: 'flex', 
              mt: 2,
              px: 1,
              py: 1,
              borderRadius: 2,
              backgroundColor: 'background.default'
            }}>
              <TextField
                fullWidth
                placeholder="Enter your command or question..."
                variant="outlined"
                size="small"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                onKeyPress={(e) => {
                  if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    handleSendPrompt();
                  }
                }}
                disabled={executing}
                multiline
                maxRows={4}
                sx={{ mr: 1 }}
              />
              <IconButton 
                color="primary" 
                onClick={handleSendPrompt} 
                disabled={executing || !prompt.trim()}
                aria-label="send command"
              >
                {executing ? <CircularProgress size={24} /> : <SendIcon />}
              </IconButton>
            </Box>
          </Paper>
        </Grid>

        {/* Right Panel - Agent Status + Context */}
        <Grid item xs={12} md={5} lg={4} sx={{ display: 'flex', flexDirection: 'column' }}>
          <Paper sx={{ 
            p: 2, 
            mb: 2, 
            borderRadius: 2,
            boxShadow: 2,
            overflow: 'hidden'
          }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Agent Status</Typography>
              <Box>
                <Button 
                  size="small"
                  onClick={handleOpenMenu}
                  endIcon={<ExpandMoreIcon />}
                >
                  {activeAgentFilter === 'all' ? 'All' : activeAgentFilter}
                </Button>
                <Menu
                  anchorEl={anchorEl}
                  open={Boolean(anchorEl)}
                  onClose={handleCloseMenu}
                >
                  <MenuItem onClick={() => { filterAgents('all'); handleCloseMenu(); }}>
                    All
                  </MenuItem>
                  <MenuItem onClick={() => { filterAgents('idle'); handleCloseMenu(); }}>
                    Idle
                  </MenuItem>
                  <MenuItem onClick={() => { filterAgents('thinking'); handleCloseMenu(); }}>
                    Thinking
                  </MenuItem>
                  <MenuItem onClick={() => { filterAgents('working'); handleCloseMenu(); }}>
                    Working
                  </MenuItem>
                </Menu>
              </Box>
            </Box>
            
            <List sx={{ overflow: 'auto', maxHeight: 200 }}>
              {filteredAgents.map((agent) => (
                <ListItem key={agent.id} sx={{ py: 1 }}>
                  <ListItemIcon>
                    {getAgentStatusIcon(agent.status)}
                  </ListItemIcon>
                  <ListItemText 
                    primary={agent.name}
                    secondary={
                      <>
                        <Chip 
                          label={agent.status} 
                          size="small" 
                          color={getAgentStatusColor(agent.status)} 
                          sx={{ mr: 1, mt: 0.5 }}
                        />
                        {agent.expertise.map(skill => (
                          <Chip 
                            key={skill} 
                            label={skill} 
                            size="small" 
                            variant="outlined"
                            sx={{ mr: 0.5, mt: 0.5 }}
                          />
                        ))}
                      </>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>

          <Paper sx={{ 
            p: 2, 
            flexGrow: 1,
            borderRadius: 2,
            boxShadow: 2,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column'
          }}>
            <Typography variant="h6" gutterBottom>Context & Resources</Typography>
            
            <List sx={{ overflow: 'auto' }}>
              <ListItem>
                <ListItemIcon>
                  <CodeIcon />
                </ListItemIcon>
                <ListItemText primary="Active Project" secondary="ADE-stable-1.0" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <DocumentIcon />
                </ListItemIcon>
                <ListItemText primary="Documentation" secondary="Available" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <DatabaseIcon />
                </ListItemIcon>
                <ListItemText primary="API Access" secondary="Connected" />
              </ListItem>
              <ListItem>
                <ListItemIcon>
                  <AnalyticsIcon />
                </ListItemIcon>
                <ListItemText primary="Analytics" secondary="Available" />
              </ListItem>
            </List>

            <Box sx={{ mt: 'auto', pt: 2 }}>
              <Typography variant="subtitle2" gutterBottom>Quick Actions</Typography>
              <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                <Button 
                  variant="outlined" 
                  size="small"
                  startIcon={<SaveIcon />}
                >
                  Save
                </Button>
                <Button 
                  variant="outlined" 
                  size="small"
                  startIcon={<PlayIcon />}
                >
                  Run
                </Button>
                <Button 
                  variant="outlined" 
                  size="small"
                  startIcon={<TerminalIcon />}
                >
                  Console
                </Button>
              </Box>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default CommandHub;