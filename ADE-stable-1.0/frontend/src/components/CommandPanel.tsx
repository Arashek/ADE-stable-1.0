import React, { KeyboardEvent } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  IconButton,
  useTheme,
  useMediaQuery,
  Tooltip,
  VisuallyHidden,
} from '@mui/material';
import {
  Send as SendIcon,
  Code as CodeIcon,
  BugReport as BugReportIcon,
  Description as DescriptionIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';

interface CommandPanelProps {
  className?: string;
}

export const CommandPanel: React.FC<CommandPanelProps> = ({ className }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [command, setCommand] = React.useState('');
  const commandInputRef = React.useRef<HTMLInputElement>(null);

  const handleCommandSubmit = (event: React.FormEvent) => {
    event.preventDefault();
    if (command.trim()) {
      // Handle command submission
      console.log('Command submitted:', command);
      setCommand('');
    }
  };

  const handleKeyDown = (event: KeyboardEvent) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault();
      handleCommandSubmit(event);
    }
  };

  const handleToolbarKeyDown = (event: KeyboardEvent, action: string) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      console.log(`Toolbar action: ${action}`);
    }
  };

  return (
    <Box
      className={className}
      role="region"
      aria-label="Command Center"
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
        <Typography variant="h6" component="h1" sx={{ flexGrow: 1 }}>
          Command Center
        </Typography>
        {!isMobile && (
          <Box role="toolbar" aria-label="Command tools">
            <Tooltip title="Code Generation">
              <IconButton
                color="primary"
                aria-label="Generate code"
                tabIndex={0}
                onKeyDown={(e) => handleToolbarKeyDown(e, 'generate-code')}
                sx={{
                  '&:focus': {
                    outline: `2px solid ${theme.palette.primary.main}`,
                    outlineOffset: 2,
                  },
                }}
              >
                <CodeIcon />
                <VisuallyHidden>Generate code</VisuallyHidden>
              </IconButton>
            </Tooltip>
            <Tooltip title="Debug">
              <IconButton
                color="primary"
                aria-label="Debug code"
                tabIndex={0}
                onKeyDown={(e) => handleToolbarKeyDown(e, 'debug')}
                sx={{
                  '&:focus': {
                    outline: `2px solid ${theme.palette.primary.main}`,
                    outlineOffset: 2,
                  },
                }}
              >
                <BugReportIcon />
                <VisuallyHidden>Debug code</VisuallyHidden>
              </IconButton>
            </Tooltip>
            <Tooltip title="Documentation">
              <IconButton
                color="primary"
                aria-label="Generate documentation"
                tabIndex={0}
                onKeyDown={(e) => handleToolbarKeyDown(e, 'documentation')}
                sx={{
                  '&:focus': {
                    outline: `2px solid ${theme.palette.primary.main}`,
                    outlineOffset: 2,
                  },
                }}
              >
                <DescriptionIcon />
                <VisuallyHidden>Generate documentation</VisuallyHidden>
              </IconButton>
            </Tooltip>
            <Tooltip title="Settings">
              <IconButton
                aria-label="Open settings"
                tabIndex={0}
                onKeyDown={(e) => handleToolbarKeyDown(e, 'settings')}
                sx={{
                  '&:focus': {
                    outline: `2px solid ${theme.palette.primary.main}`,
                    outlineOffset: 2,
                  },
                }}
              >
                <SettingsIcon />
                <VisuallyHidden>Open settings</VisuallyHidden>
              </IconButton>
            </Tooltip>
          </Box>
        )}
      </Paper>

      <Box
        role="log"
        aria-label="Command history"
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
        {/* Command history and results will be rendered here */}
      </Box>

      <Paper
        component="form"
        onSubmit={handleCommandSubmit}
        role="group"
        aria-label="Command input"
        sx={{
          p: 2,
          borderTop: 1,
          borderColor: 'divider',
          display: 'flex',
          gap: 1,
          backgroundColor: theme.palette.mode === 'dark' 
            ? theme.palette.grey[900] 
            : theme.palette.background.paper,
        }}
      >
        <TextField
          fullWidth
          inputRef={commandInputRef}
          placeholder="Enter a command..."
          value={command}
          onChange={(e) => setCommand(e.target.value)}
          onKeyDown={handleKeyDown}
          size="small"
          multiline
          maxRows={4}
          aria-label="Command input"
          InputProps={{
            'aria-describedby': 'command-help-text',
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
        <IconButton
          color="primary"
          type="submit"
          disabled={!command.trim()}
          aria-label="Submit command"
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
          <VisuallyHidden>Submit command</VisuallyHidden>
        </IconButton>
      </Paper>
      <VisuallyHidden id="command-help-text">
        Press Enter to submit the command. Use Shift + Enter for a new line.
      </VisuallyHidden>
    </Box>
  );
}; 