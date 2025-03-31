import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ListItemButton,
  Divider,
  Chip,
  IconButton,
  Tooltip,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  CircularProgress,
  Badge,
  Alert,
  Card,
  CardContent,
  Grid,
  LinearProgress,
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  PlayArrow,
  Stop,
  Build,
  BugReport,
  Code,
  Storage,
  Terminal,
  Refresh,
  Settings,
  ExpandMore,
  Psychology,
  Group,
  Sync,
  CheckCircle,
  Error as ErrorIcon,
  Warning,
  Info,
} from '@mui/icons-material';

const CommandHubContainer = styled(Paper)(({ theme }) => ({
  height: '100%',
  display: 'flex',
  flexDirection: 'column',
  backgroundColor: theme.palette.background.paper,
  borderRadius: theme.shape.borderRadius,
}));

const CommandSection = styled(Box)(({ theme }) => ({
  padding: theme.spacing(2),
}));

const AgentStatusIndicator = styled(Badge)(({ theme }) => ({
  '& .MuiBadge-badge': {
    backgroundColor: '#44b700',
    color: '#44b700',
    boxShadow: `0 0 0 2px ${theme.palette.background.paper}`,
    '&::after': {
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      borderRadius: '50%',
      animation: 'ripple 1.2s infinite ease-in-out',
      border: '1px solid currentColor',
      content: '""',
    },
  },
  '@keyframes ripple': {
    '0%': {
      transform: 'scale(.8)',
      opacity: 1,
    },
    '100%': {
      transform: 'scale(2.4)',
      opacity: 0,
    },
  },
}));

interface Command {
  id: string;
  name: string;
  description: string;
  category: string;
  framework?: string;
  icon: React.ReactNode;
  action: () => void;
}

interface Agent {
  id: string;
  type: string;
  status: 'active' | 'inactive' | 'busy';
  capabilities: string[];
  lastActivity?: string;
}

interface ConflictResolution {
  attribute: string;
  values: Record<string, any>;
  selectedValue: any;
  selectedAgent: string;
  confidence: number;
}

interface ConsensusDecision {
  id: string;
  key: string;
  description: string;
  options: any[];
  selectedOption: any;
  votes: {
    agent: string;
    option: any;
    confidence: number;
    reasoning: string;
  }[];
  confidence: number;
  status: 'pending' | 'in_progress' | 'resolved';
}

interface CommandHubProps {
  projectType: string;
  onCommandExecute: (command: string) => void;
}

const CommandHub: React.FC<CommandHubProps> = ({ projectType, onCommandExecute }) => {
  const [commands, setCommands] = useState<Command[]>([]);
  const [activeCommand, setActiveCommand] = useState<string | null>(null);
  const [boundariesConfig, setBoundariesConfig] = useState<any>(null);
  const [agents, setAgents] = useState<Agent[]>([]);
  const [conflicts, setConflicts] = useState<ConflictResolution[]>([]);
  const [consensusDecisions, setConsensusDecisions] = useState<ConsensusDecision[]>([]);
  const [agentCoordinationActive, setAgentCoordinationActive] = useState<boolean>(false);

  useEffect(() => {
    // Load Boundaries configuration
    const loadBoundariesConfig = async () => {
      try {
        const response = await fetch('/.boundaries/commands.json');
        const config = await response.json();
        setBoundariesConfig(config);
        
        // Generate commands based on project type and configuration
        const frameworkCommands = generateFrameworkCommands(config, projectType);
        setCommands(frameworkCommands);
      } catch (error) {
        console.error('Failed to load Boundaries configuration:', error);
      }
    };

    loadBoundariesConfig();
    
    // Load agent information
    const loadAgentInfo = async () => {
      try {
        const response = await fetch('/api/agents');
        const agentData = await response.json();
        setAgents(agentData);
      } catch (error) {
        console.error('Failed to load agent information:', error);
        // Set some mock data for development
        setAgents([
          { id: 'security-1', type: 'security', status: 'active', capabilities: ['security_analysis', 'vulnerability_detection'] },
          { id: 'architecture-1', type: 'architecture', status: 'active', capabilities: ['system_design', 'component_modeling'] },
          { id: 'design-1', type: 'design', status: 'active', capabilities: ['ui_design', 'ux_optimization'] },
          { id: 'validation-1', type: 'validation', status: 'inactive', capabilities: ['code_validation', 'test_generation'] },
          { id: 'performance-1', type: 'performance', status: 'busy', capabilities: ['performance_analysis', 'optimization'] },
        ]);
      }
    };
    
    loadAgentInfo();
    
    // Set up polling for agent coordination status
    const pollAgentCoordination = setInterval(() => {
      fetchAgentCoordinationStatus();
    }, 5000);
    
    return () => {
      clearInterval(pollAgentCoordination);
    };
  }, [projectType]);
  
  const fetchAgentCoordinationStatus = async () => {
    try {
      const response = await fetch('/api/coordination/status');
      const data = await response.json();
      
      if (data.active) {
        setAgentCoordinationActive(true);
        setConflicts(data.conflicts || []);
        setConsensusDecisions(data.consensusDecisions || []);
      } else {
        setAgentCoordinationActive(false);
      }
    } catch (error) {
      console.error('Failed to fetch agent coordination status:', error);
    }
  };

  const generateFrameworkCommands = (config: any, framework: string): Command[] => {
    const baseCommands: Command[] = [
      {
        id: 'preview',
        name: 'Start Preview',
        description: 'Start the development preview server',
        category: 'Development',
        icon: <PlayArrow />,
        action: () => executeCommand('preview'),
      },
      {
        id: 'build',
        name: 'Build Project',
        description: 'Build the project for production',
        category: 'Build',
        icon: <Build />,
        action: () => executeCommand('build'),
      },
      {
        id: 'test',
        name: 'Run Tests',
        description: 'Execute test suite',
        category: 'Testing',
        icon: <BugReport />,
        action: () => executeCommand('test'),
      },
      {
        id: 'docker',
        name: 'Docker Operations',
        description: 'Manage Docker containers',
        category: 'Docker',
        icon: <Storage />,
        action: () => executeCommand('docker'),
      },
    ];
    
    // Add agent coordination commands
    const agentCommands: Command[] = [
      {
        id: 'start_coordination',
        name: 'Start Agent Coordination',
        description: 'Activate the agent coordination system',
        category: 'Agents',
        icon: <Group />,
        action: () => executeCommand('start_coordination'),
      },
      {
        id: 'stop_coordination',
        name: 'Stop Agent Coordination',
        description: 'Deactivate the agent coordination system',
        category: 'Agents',
        icon: <Stop />,
        action: () => executeCommand('stop_coordination'),
      },
      {
        id: 'run_consensus',
        name: 'Run Consensus Process',
        description: 'Trigger a consensus building process among agents',
        category: 'Agents',
        icon: <Psychology />,
        action: () => executeCommand('run_consensus'),
      },
    ];

    // Add framework-specific commands
    if (config?.commands?.[framework]) {
      const frameworkSpecific = Object.entries(config.commands[framework]).map(
        ([id, cmd]: [string, any]) => ({
          id,
          name: cmd.name || id,
          description: cmd.description || '',
          category: cmd.category || 'Framework',
          framework,
          icon: <Code />,
          action: () => executeCommand(id),
        })
      );
      return [...baseCommands, ...agentCommands, ...frameworkSpecific];
    }

    return [...baseCommands, ...agentCommands];
  };

  const executeCommand = (commandId: string) => {
    setActiveCommand(commandId);
    onCommandExecute(commandId);
  };

  const stopCommand = () => {
    if (activeCommand) {
      onCommandExecute(`stop:${activeCommand}`);
      setActiveCommand(null);
    }
  };

  const renderCommandList = (category: string) => {
    const categoryCommands = commands.filter((cmd) => cmd.category === category);
    
    if (categoryCommands.length === 0) return null;

    return (
      <Box key={category}>
        <Typography variant="subtitle2" sx={{ px: 2, py: 1, color: 'text.secondary' }}>
          {category}
        </Typography>
        <List dense>
          {categoryCommands.map((command) => (
            <ListItem
              key={command.id}
              disablePadding
              secondaryAction={
                command.framework && (
                  <Chip
                    label={command.framework}
                    size="small"
                    color="primary"
                    variant="outlined"
                  />
                )
              }
            >
              <ListItemButton
                selected={activeCommand === command.id}
                onClick={() => command.action()}
              >
                <ListItemIcon>{command.icon}</ListItemIcon>
                <ListItemText
                  primary={command.name}
                  secondary={command.description}
                  primaryTypographyProps={{ variant: 'body2' }}
                  secondaryTypographyProps={{ variant: 'caption' }}
                />
              </ListItemButton>
            </ListItem>
          ))}
        </List>
        <Divider />
      </Box>
    );
  };
  
  const renderAgentStatus = () => {
    return (
      <Accordion defaultExpanded>
        <AccordionSummary expandIcon={<ExpandMore />}>
          <Typography variant="subtitle1">Agent Status</Typography>
        </AccordionSummary>
        <AccordionDetails>
          <List dense>
            {agents.map((agent) => (
              <ListItem key={agent.id}>
                <ListItemIcon>
                  <AgentStatusIndicator
                    overlap="circular"
                    anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
                    variant="dot"
                    color={
                      agent.status === 'active' 
                        ? 'success' 
                        : agent.status === 'busy' 
                          ? 'warning' 
                          : 'error'
                    }
                  >
                    <Psychology color="primary" />
                  </AgentStatusIndicator>
                </ListItemIcon>
                <ListItemText
                  primary={`${agent.type} (${agent.id})`}
                  secondary={agent.capabilities.join(', ')}
                  primaryTypographyProps={{ variant: 'body2' }}
                  secondaryTypographyProps={{ variant: 'caption' }}
                />
                <Chip 
                  label={agent.status} 
                  size="small" 
                  color={
                    agent.status === 'active' 
                      ? 'success' 
                      : agent.status === 'busy' 
                        ? 'warning' 
                        : 'error'
                  }
                />
              </ListItem>
            ))}
          </List>
        </AccordionDetails>
      </Accordion>
    );
  };
  
  const renderConflictResolutions = () => {
    if (conflicts.length === 0) {
      return (
        <Alert severity="info" sx={{ mt: 1 }}>
          No active conflicts detected
        </Alert>
      );
    }
    
    return (
      <Box>
        {conflicts.map((conflict, index) => (
          <Card key={index} variant="outlined" sx={{ mb: 1 }}>
            <CardContent>
              <Typography variant="subtitle2" color="text.secondary">
                Conflict: {conflict.attribute}
              </Typography>
              <Box sx={{ mt: 1 }}>
                <Typography variant="body2">
                  <strong>Resolution:</strong> {conflict.selectedValue} (from {conflict.selectedAgent})
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  <Typography variant="caption" sx={{ mr: 1 }}>
                    Confidence:
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={conflict.confidence * 100}
                    sx={{ flexGrow: 1, mr: 1 }}
                  />
                  <Typography variant="caption">
                    {Math.round(conflict.confidence * 100)}%
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ mt: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  Conflicting values:
                </Typography>
                <Grid container spacing={1} sx={{ mt: 0.5 }}>
                  {Object.entries(conflict.values).map(([agent, value]) => (
                    <Grid item key={agent}>
                      <Chip
                        size="small"
                        label={`${agent}: ${value}`}
                        color={agent === conflict.selectedAgent ? 'primary' : 'default'}
                        variant={agent === conflict.selectedAgent ? 'filled' : 'outlined'}
                      />
                    </Grid>
                  ))}
                </Grid>
              </Box>
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  };
  
  const renderConsensusDecisions = () => {
    if (consensusDecisions.length === 0) {
      return (
        <Alert severity="info" sx={{ mt: 1 }}>
          No consensus decisions in progress
        </Alert>
      );
    }
    
    return (
      <Box>
        {consensusDecisions.map((decision) => (
          <Card key={decision.id} variant="outlined" sx={{ mb: 1 }}>
            <CardContent>
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Typography variant="subtitle2" color="text.secondary">
                  {decision.description}
                </Typography>
                <Chip
                  size="small"
                  label={decision.status}
                  color={
                    decision.status === 'resolved' 
                      ? 'success' 
                      : decision.status === 'in_progress' 
                        ? 'warning' 
                        : 'default'
                  }
                />
              </Box>
              
              {decision.status === 'resolved' ? (
                <Box sx={{ mt: 1 }}>
                  <Typography variant="body2">
                    <strong>Decision:</strong> {decision.selectedOption}
                  </Typography>
                  <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                    <Typography variant="caption" sx={{ mr: 1 }}>
                      Confidence:
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={decision.confidence * 100}
                      sx={{ flexGrow: 1, mr: 1 }}
                    />
                    <Typography variant="caption">
                      {Math.round(decision.confidence * 100)}%
                    </Typography>
                  </Box>
                </Box>
              ) : (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                  <CircularProgress size={24} />
                </Box>
              )}
              
              {decision.votes && decision.votes.length > 0 && (
                <Accordion sx={{ mt: 1 }} elevation={0}>
                  <AccordionSummary expandIcon={<ExpandMore />}>
                    <Typography variant="caption">Agent Votes ({decision.votes.length})</Typography>
                  </AccordionSummary>
                  <AccordionDetails>
                    <List dense disablePadding>
                      {decision.votes.map((vote, index) => (
                        <ListItem key={index} disablePadding>
                          <ListItemText
                            primary={`${vote.agent}: ${vote.option} (${Math.round(vote.confidence * 100)}%)`}
                            secondary={vote.reasoning}
                            primaryTypographyProps={{ variant: 'caption' }}
                            secondaryTypographyProps={{ variant: 'caption', color: 'text.secondary' }}
                          />
                        </ListItem>
                      ))}
                    </List>
                  </AccordionDetails>
                </Accordion>
              )}
            </CardContent>
          </Card>
        ))}
      </Box>
    );
  };

  const categories = Array.from(new Set(commands.map((cmd) => cmd.category)));

  return (
    <CommandHubContainer>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Command Hub</Typography>
          <Box>
            <Tooltip title="Stop Active Command">
              <span>
                <IconButton
                  size="small"
                  color="error"
                  disabled={!activeCommand}
                  onClick={stopCommand}
                >
                  <Stop />
                </IconButton>
              </span>
            </Tooltip>
            <Tooltip title="Refresh Commands">
              <IconButton size="small" onClick={() => window.location.reload()}>
                <Refresh />
              </IconButton>
            </Tooltip>
            <Tooltip title="Settings">
              <IconButton size="small">
                <Settings />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        {agentCoordinationActive && (
          <Alert severity="success" icon={<Sync />} sx={{ mt: 1 }}>
            Agent Coordination System Active
          </Alert>
        )}
      </Box>

      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <CommandSection>
          {categories.map((category) => renderCommandList(category))}
        </CommandSection>
        
        {/* Agent Status Section */}
        <CommandSection>
          {renderAgentStatus()}
        </CommandSection>
        
        {/* Consensus Building Section */}
        <CommandSection>
          <Accordion defaultExpanded={consensusDecisions.length > 0}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="subtitle1">
                Consensus Building
                {consensusDecisions.length > 0 && (
                  <Badge 
                    badgeContent={consensusDecisions.length} 
                    color="primary" 
                    sx={{ ml: 1 }}
                  />
                )}
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              {renderConsensusDecisions()}
            </AccordionDetails>
          </Accordion>
        </CommandSection>
        
        {/* Conflict Resolution Section */}
        <CommandSection>
          <Accordion defaultExpanded={conflicts.length > 0}>
            <AccordionSummary expandIcon={<ExpandMore />}>
              <Typography variant="subtitle1">
                Conflict Resolution
                {conflicts.length > 0 && (
                  <Badge 
                    badgeContent={conflicts.length} 
                    color="error" 
                    sx={{ ml: 1 }}
                  />
                )}
              </Typography>
            </AccordionSummary>
            <AccordionDetails>
              {renderConflictResolutions()}
            </AccordionDetails>
          </Accordion>
        </CommandSection>
      </Box>
      
      <Box sx={{ p: 2, borderTop: 1, borderColor: 'divider' }}>
        <Typography variant="caption" color="text.secondary">
          ADE Platform v1.0 - Agent Development Environment
        </Typography>
      </Box>
    </CommandHubContainer>
  );
};

export default CommandHub;