import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  Avatar,
  CircularProgress,
  Chip,
  Tooltip,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Send as SendIcon,
  Code as CodeIcon,
  Stop as StopIcon,
  Psychology as AIIcon,
  Palette as DesignIcon,
  Build as DevIcon,
  Insights as AdvisorIcon,
  ContentCopy as CopyIcon,
  Done as DoneIcon,
  Memory as ArchitectIcon,
} from '@mui/icons-material';
import SyntaxHighlighter from './common/SyntaxHighlighter';

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
  padding: theme.spacing(1.5),
  backgroundColor: theme.palette.primary.main,
  color: theme.palette.primary.contrastText,
  borderRadius: '1rem 0 1rem 1rem',
}));

const AgentMessage = styled(Paper)(({ theme }) => ({
  marginRight: 'auto',
  padding: theme.spacing(1.5),
  backgroundColor: theme.palette.background.paper,
  color: theme.palette.text.primary,
  borderRadius: '0 1rem 1rem 1rem',
  boxShadow: theme.shadows[1],
}));

const SystemMessage = styled(Paper)(({ theme }) => ({
  margin: '0 auto',
  padding: theme.spacing(1),
  backgroundColor: theme.palette.action.hover,
  color: theme.palette.text.secondary,
  borderRadius: '0.5rem',
  maxWidth: '60%',
  textAlign: 'center',
}));

const InputContainer = styled('div')(({ theme }) => ({
  display: 'flex',
  padding: theme.spacing(2),
  backgroundColor: theme.palette.background.paper,
  borderTop: `1px solid ${theme.palette.divider}`,
}));

interface MessageType {
  id: string;
  type: 'user' | 'agent' | 'system';
  content: string;
  timestamp: Date;
  agent?: string;
  codeBlocks?: Array<{
    language: string;
    code: string;
  }>;
  isLoading?: boolean;
  error?: boolean;
}

interface LiveChatProps {
  activeAgent: string;
}

const agentResponses = {
  assistant: [
    "I'm the Assistant Agent. I'll help coordinate all the specialized agents in creating your application.",
    "What kind of application would you like to build today?",
    "I'll analyze your requirements and delegate tasks to the appropriate specialized agents."
  ],
  developer: [
    "Developer Agent here. I'll handle the coding implementation for your application.",
    "I can help with architecture decisions, code structure, and technical implementation.",
    "Let me implement these frontend components with the proper state management patterns."
  ],
  designer: [
    "I'm the Designer Agent. I focus on creating beautiful and functional UI/UX for your application.",
    "Let me create a responsive layout that will work well across all device sizes.",
    "I'll generate the UI components with accessibility and modern design principles in mind."
  ],
  advisor: [
    "Advisor Agent at your service. I provide recommendations on best practices and technology choices.",
    "Based on your requirements, I suggest using React with Material UI for the frontend.",
    "For your cloud deployment needs, I recommend setting up a CI/CD pipeline with GitHub Actions."
  ],
  architect: [
    "Architect Agent here. I'll design the overall system architecture for your application.",
    "I'll create a scalable and maintainable architecture that supports your current needs and future growth.",
    "Let me define the data models and service interactions for your application."
  ]
};

const agentCodeSnippets = {
  developer: [
    {
      language: "javascript",
      code: `// Sample React component implementation
import React, { useState, useEffect } from 'react';
import { Box, Typography, Button } from '@mui/material';

const UserDashboard = ({ userId }) => {
  const [userData, setUserData] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  useEffect(() => {
    fetchUserData(userId)
      .then(data => {
        setUserData(data);
        setIsLoading(false);
      })
      .catch(error => {
        console.error('Error fetching user data:', error);
        setIsLoading(false);
      });
  }, [userId]);
  
  if (isLoading) return <CircularProgress />;
  
  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4">Welcome, {userData.name}</Typography>
      <Typography variant="body1">{userData.email}</Typography>
      <Button variant="contained" color="primary">
        View Projects
      </Button>
    </Box>
  );
};

export default UserDashboard;`
    }
  ],
  designer: [
    {
      language: "css",
      code: `.mission-control-layout {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  grid-template-rows: auto 1fr auto;
  gap: 16px;
  height: 100vh;
  padding: 16px;
  background-color: #f5f5f5;
}

.header {
  grid-column: 1 / -1;
  grid-row: 1;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 16px;
}

.sidebar {
  grid-column: 1 / span 2;
  grid-row: 2;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 16px;
}

.main-content {
  grid-column: 3 / -1;
  grid-row: 2;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 16px;
  overflow: auto;
}

.footer {
  grid-column: 1 / -1;
  grid-row: 3;
  background-color: #ffffff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  padding: 16px;
}

@media (max-width: 768px) {
  .mission-control-layout {
    grid-template-columns: 1fr;
    grid-template-rows: auto auto 1fr auto;
  }
  
  .sidebar {
    grid-column: 1;
    grid-row: 2;
  }
  
  .main-content {
    grid-column: 1;
    grid-row: 3;
  }
  
  .footer {
    grid-row: 4;
  }
}`
    }
  ],
  architect: [
    {
      language: "typescript",
      code: `// System architecture model
interface AgentCoordination {
  registerAgent(agent: SpecializedAgent): void;
  delegateTask(task: Task): Promise<TaskResult>;
  resolveConflicts(conflicts: Conflict[]): Resolution;
}

interface SpecializedAgent {
  id: string;
  type: AgentType;
  capabilities: Capability[];
  processingPower: number;
  status: AgentStatus;
  
  performTask(task: Task): Promise<TaskResult>;
  communicateWith(agent: SpecializedAgent, message: Message): void;
  reportStatus(): AgentStatus;
}

enum AgentType {
  ASSISTANT,
  DEVELOPER,
  DESIGNER,
  ADVISOR,
  ARCHITECT,
  DATA_ENGINEER,
  DEVOPS
}

interface Task {
  id: string;
  description: string;
  requirements: string[];
  priority: Priority;
  assignedAgents: SpecializedAgent[];
  dependencies: Task[];
  status: TaskStatus;
}

// Main coordination system implementation
class AgentCoordinationSystem implements AgentCoordination {
  private agents: Map<string, SpecializedAgent> = new Map();
  private taskQueue: Task[] = [];
  
  registerAgent(agent: SpecializedAgent): void {
    this.agents.set(agent.id, agent);
    console.log(\`Agent \${agent.id} of type \${agent.type} registered\`);
  }
  
  async delegateTask(task: Task): Promise<TaskResult> {
    // Implement task delegation logic
    // Find most suitable agent based on task requirements and agent capabilities
    // ...
  }
  
  // Additional implementation details...
}`
    }
  ]
};

const LiveChat: React.FC<LiveChatProps> = ({
  activeAgent,
}) => {
  const [messages, setMessages] = useState<MessageType[]>([
    {
      id: '1',
      type: 'system',
      content: 'Welcome to ADE Platform. How can I help you build your application today?',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isSending, setIsSending] = useState(false);
  const [responseLoading, setResponseLoading] = useState(false);
  const [copyState, setCopyState] = useState<{[key: string]: boolean}>({});
  const chatEndRef = useRef<HTMLDivElement>(null);

  // Handle agent change
  useEffect(() => {
    // Add a system message when active agent changes
    if (messages.length > 1) {
      const systemMessage: MessageType = {
        id: Date.now().toString(),
        type: 'system',
        content: `Switched to ${activeAgent.charAt(0).toUpperCase() + activeAgent.slice(1)} Agent`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, systemMessage]);
      
      // Add welcome message from new agent
      setTimeout(() => {
        const welcomeMessage: MessageType = {
          id: (Date.now() + 1).toString(),
          type: 'agent',
          agent: activeAgent,
          content: agentResponses[activeAgent][0],
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, welcomeMessage]);
      }, 800);
    }
  }, [activeAgent]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleInputChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    setInput(event.target.value);
  };

  const handleCopyCode = (code: string, blockId: string) => {
    navigator.clipboard.writeText(code)
      .then(() => {
        // Visual feedback for copy
        setCopyState({...copyState, [blockId]: true});
        setTimeout(() => {
          setCopyState({...copyState, [blockId]: false});
        }, 2000);
      })
      .catch(err => {
        // Log error to our error logging system
        logError('FRONTEND', 'ERROR', 'Failed to copy code to clipboard', {
          error: err.toString(),
          component: 'LiveChat',
          blockId
        });
      });
  };

  // Integration with error logging system
  const logError = (category: string, severity: string, message: string, context: any) => {
    // In a real implementation, this would call the error logging API
    console.error(`[${category}][${severity}] ${message}`, context);
    
    // Simulate sending error to backend error logging system
    fetch('/api/error-logs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        timestamp: new Date().toISOString(),
        error_type: context.error || 'User Interface Error',
        message,
        category,
        severity,
        component: context.component || 'LiveChat',
        context
      })
    }).catch(err => {
      console.error('Failed to log error:', err);
    });
  };

  const simulateAgentResponse = (userInput: string) => {
    setResponseLoading(true);
    
    // Simulate API call delay
    setTimeout(() => {
      try {
        // Randomly select a response from the agent
        const responseIndex = Math.floor(Math.random() * agentResponses[activeAgent].length);
        const responseContent = agentResponses[activeAgent][responseIndex];
        
        // Determine if we should include a code snippet (50% chance for developer and architect)
        const includeCode = (activeAgent === 'developer' || activeAgent === 'architect') && Math.random() > 0.5;
        
        // Create agent response
        const agentResponse: MessageType = {
          id: Date.now().toString(),
          type: 'agent',
          agent: activeAgent,
          content: responseContent,
          timestamp: new Date(),
          codeBlocks: includeCode ? agentCodeSnippets[activeAgent] : undefined
        };
        
        setMessages(prev => [...prev, agentResponse]);
        setResponseLoading(false);
      } catch (error) {
        // Log error to our error logging system
        logError('AGENT', 'ERROR', 'Failed to generate agent response', {
          error: error.toString(),
          agent: activeAgent,
          userInput
        });
        
        // Send error message to user
        const errorResponse: MessageType = {
          id: Date.now().toString(),
          type: 'agent',
          agent: activeAgent,
          content: 'Sorry, I encountered an error while processing your request. This has been logged and our team will investigate.',
          timestamp: new Date(),
          error: true
        };
        
        setMessages(prev => [...prev, errorResponse]);
        setResponseLoading(false);
      }
    }, 1500 + Math.random() * 1000); // Random delay between 1.5-2.5 seconds
  };

  const handleSend = () => {
    if (input.trim() === '') return;
    
    setIsSending(true);
    
    // Add user message
    const userMessage: MessageType = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };
    
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    
    // Simulate sending message to backend and wait for response
    setTimeout(() => {
      setIsSending(false);
      simulateAgentResponse(input);
    }, 300);
  };

  const getAgentIcon = (agent?: string) => {
    switch(agent) {
      case 'designer':
        return <DesignIcon />;
      case 'developer':
        return <DevIcon />;
      case 'advisor':
        return <AdvisorIcon />;
      case 'assistant':
      default:
        return <AIIcon />;
    }
  };

  const getAgentColor = (agent?: string) => {
    switch(agent) {
      case 'designer':
        return '#9c27b0'; // Purple
      case 'developer':
        return '#2196f3'; // Blue
      case 'advisor':
        return '#ff9800'; // Orange
      case 'assistant':
      default:
        return '#4caf50'; // Green
    }
  };

  return (
    <Root>
      <ChatContainer>
        {messages.map((message) => (
          <Message key={message.id}>
            {message.type === 'user' ? (
              <UserMessage>
                <Typography variant="body1" sx={{ wordBreak: 'break-word' }}>
                  {message.content}
                </Typography>
                <Typography variant="caption" sx={{ display: 'block', textAlign: 'right', mt: 1, opacity: 0.7 }}>
                  {message.timestamp.toLocaleTimeString()}
                </Typography>
              </UserMessage>
            ) : message.type === 'system' ? (
              <SystemMessage>
                <Typography variant="body2">
                  {message.content}
                </Typography>
              </SystemMessage>
            ) : (
              <AgentMessage>
                <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                  <Avatar 
                    sx={{ 
                      width: 28, 
                      height: 28, 
                      mr: 1,
                      bgcolor: getAgentColor(message.agent)
                    }}
                  >
                    {getAgentIcon(message.agent)}
                  </Avatar>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    {message.agent ? `${message.agent.charAt(0).toUpperCase() + message.agent.slice(1)} Agent` : 'System'}
                  </Typography>
                </Box>
                <Typography variant="body1" sx={{ wordBreak: 'break-word' }}>
                  {message.content}
                </Typography>
                
                {message.codeBlocks && message.codeBlocks.map((codeBlock, index) => (
                  <Box key={index} sx={{ mt: 2, position: 'relative' }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Chip 
                        size="small" 
                        label={codeBlock.language} 
                        icon={<CodeIcon />} 
                      />
                      <Tooltip title={copyState[`${message.id}-${index}`] ? 'Copied!' : 'Copy code'}>
                        <IconButton 
                          size="small" 
                          onClick={() => handleCopyCode(codeBlock.code, `${message.id}-${index}`)}
                        >
                          {copyState[`${message.id}-${index}`] ? <DoneIcon color="success" /> : <CopyIcon />}
                        </IconButton>
                      </Tooltip>
                    </Box>
                    <SyntaxHighlighter 
                      code={codeBlock.code}
                      language={codeBlock.language}
                    />
                  </Box>
                ))}
                
                <Typography variant="caption" sx={{ display: 'block', mt: 1, opacity: 0.7 }}>
                  {message.timestamp.toLocaleTimeString()}
                </Typography>
              </AgentMessage>
            )}
          </Message>
        ))}

        {responseLoading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
        
        <div ref={chatEndRef} />
      </ChatContainer>

      <InputContainer>
        <TextField
          fullWidth
          variant="outlined"
          placeholder="Ask anything..."
          value={input}
          onChange={(e) => handleInputChange(e)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              handleSend();
            }
          }}
          disabled={isSending}
          size="small"
          multiline
          maxRows={4}
          sx={{ mr: 1 }}
        />
        {isSending ? (
          <IconButton color="error" onClick={() => setIsSending(false)}>
            <StopIcon />
          </IconButton>
        ) : (
          <IconButton
            color="primary"
            onClick={handleSend}
            disabled={!input.trim()}
          >
            <SendIcon />
          </IconButton>
        )}
      </InputContainer>
    </Root>
  );
};

export default LiveChat;