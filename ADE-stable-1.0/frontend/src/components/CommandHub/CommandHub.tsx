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

interface Command {
  id: string;
  name: string;
  description: string;
  category: string;
  framework?: string;
  icon: React.ReactNode;
  action: () => void;
}

interface CommandHubProps {
  projectType: string;
  onCommandExecute: (command: string) => void;
}

const CommandHub: React.FC<CommandHubProps> = ({ projectType, onCommandExecute }) => {
  const [commands, setCommands] = useState<Command[]>([]);
  const [activeCommand, setActiveCommand] = useState<string | null>(null);
  const [boundariesConfig, setBoundariesConfig] = useState<any>(null);

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
  }, [projectType]);

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
      return [...baseCommands, ...frameworkSpecific];
    }

    return baseCommands;
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

  const categories = Array.from(new Set(commands.map((cmd) => cmd.category)));

  return (
    <CommandHubContainer>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Typography variant="h6">Command Hub</Typography>
          <Box>
            <Tooltip title="Stop Active Command">
              <IconButton
                size="small"
                onClick={stopCommand}
                disabled={!activeCommand}
                color={activeCommand ? 'error' : 'default'}
              >
                <Stop />
              </IconButton>
            </Tooltip>
            <Tooltip title="Refresh Commands">
              <IconButton
                size="small"
                onClick={() => {
                  if (boundariesConfig) {
                    const frameworkCommands = generateFrameworkCommands(boundariesConfig, projectType);
                    setCommands(frameworkCommands);
                  }
                }}
              >
                <Refresh />
              </IconButton>
            </Tooltip>
            <Tooltip title="Command Settings">
              <IconButton size="small">
                <Settings />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
      </Box>

      <Box sx={{ flex: 1, overflow: 'auto' }}>
        {categories.map((category) => renderCommandList(category))}
      </Box>

      {activeCommand && (
        <CommandSection>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Terminal fontSize="small" />
            <Typography variant="body2">
              Running: {commands.find((cmd) => cmd.id === activeCommand)?.name}
            </Typography>
    </Box>
        </CommandSection>
      )}
    </CommandHubContainer>
  );
};

export default CommandHub; 