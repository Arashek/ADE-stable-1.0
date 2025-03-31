import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
  Divider,
  Button,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Grid,
  Chip
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Pause as PauseIcon,
  Stop as StopIcon,
  SkipNext as StepOverIcon,
  SkipPrevious as StepBackIcon,
  BugReport as BreakpointIcon,
  Visibility as WatchIcon,
  Memory as VariablesIcon,
  CallSplit as CallStackIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';

interface Breakpoint {
  id: string;
  line: number;
  file: string;
  condition?: string;
  enabled: boolean;
}

interface WatchVariable {
  id: string;
  name: string;
  value: string;
  type: string;
}

interface CallStackFrame {
  id: string;
  function: string;
  file: string;
  line: number;
}

interface DebuggerState {
  isRunning: boolean;
  isPaused: boolean;
  currentLine: number;
  currentFile: string;
  breakpoints: Breakpoint[];
  watchVariables: WatchVariable[];
  callStack: CallStackFrame[];
  variables: Record<string, any>;
  errors: Array<{
    type: 'error' | 'warning' | 'info';
    message: string;
    line: number;
    file: string;
  }>;
}

interface DebuggerPanelProps {
  onBreakpointToggle: (line: number, file: string) => void;
  onStepOver: () => void;
  onStepBack: () => void;
  onContinue: () => void;
  onStop: () => void;
  onAddWatch: (variable: string) => void;
  onRemoveWatch: (id: string) => void;
  onEvaluateExpression: (expression: string) => void;
}

const DebuggerPanel: React.FC<DebuggerPanelProps> = ({
  onBreakpointToggle,
  onStepOver,
  onStepBack,
  onContinue,
  onStop,
  onAddWatch,
  onRemoveWatch,
  onEvaluateExpression
}) => {
  const [debuggerState, setDebuggerState] = useState<DebuggerState>({
    isRunning: false,
    isPaused: false,
    currentLine: 0,
    currentFile: '',
    breakpoints: [],
    watchVariables: [],
    callStack: [],
    variables: {},
    errors: []
  });

  const [expression, setExpression] = useState('');
  const [selectedTab, setSelectedTab] = useState('variables');

  const handleBreakpointToggle = (line: number, file: string) => {
    onBreakpointToggle(line, file);
    setDebuggerState(prev => ({
      ...prev,
      breakpoints: prev.breakpoints.map(bp =>
        bp.line === line && bp.file === file
          ? { ...bp, enabled: !bp.enabled }
          : bp
      )
    }));
  };

  const handleAddWatch = () => {
    if (expression.trim()) {
      onAddWatch(expression.trim());
      setExpression('');
    }
  };

  const handleRemoveWatch = (id: string) => {
    onRemoveWatch(id);
    setDebuggerState(prev => ({
      ...prev,
      watchVariables: prev.watchVariables.filter(v => v.id !== id)
    }));
  };

  const handleEvaluateExpression = () => {
    if (expression.trim()) {
      onEvaluateExpression(expression.trim());
      setExpression('');
    }
  };

  return (
    <Paper elevation={3} sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', alignItems: 'center', gap: 1 }}>
        <Typography variant="h6" sx={{ flex: 1 }}>Debugger</Typography>
        <Tooltip title="Continue">
          <IconButton onClick={onContinue} disabled={!debuggerState.isPaused}>
            <PlayIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Pause">
          <IconButton onClick={() => setDebuggerState(prev => ({ ...prev, isPaused: true }))} disabled={!debuggerState.isRunning || debuggerState.isPaused}>
            <PauseIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Stop">
          <IconButton onClick={onStop} disabled={!debuggerState.isRunning}>
            <StopIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Step Over">
          <IconButton onClick={onStepOver} disabled={!debuggerState.isPaused}>
            <StepOverIcon />
          </IconButton>
        </Tooltip>
        <Tooltip title="Step Back">
          <IconButton onClick={onStepBack} disabled={!debuggerState.isPaused}>
            <StepBackIcon />
          </IconButton>
        </Tooltip>
      </Box>

      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <TextField
              fullWidth
              size="small"
              placeholder="Evaluate expression or add watch variable"
              value={expression}
              onChange={(e) => setExpression(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleEvaluateExpression()}
            />
          </Grid>
          <Grid item xs={6}>
            <Button
              fullWidth
              variant="outlined"
              onClick={handleAddWatch}
              disabled={!expression.trim()}
            >
              Add Watch
            </Button>
          </Grid>
          <Grid item xs={6}>
            <Button
              fullWidth
              variant="outlined"
              onClick={handleEvaluateExpression}
              disabled={!expression.trim()}
            >
              Evaluate
            </Button>
          </Grid>
        </Grid>
      </Box>

      <Box sx={{ flex: 1, overflow: 'auto' }}>
        <List>
          <ListItem>
            <ListItemIcon>
              <VariablesIcon />
            </ListItemIcon>
            <ListItemText primary="Variables" />
          </ListItem>
          {Object.entries(debuggerState.variables).map(([name, value]) => (
            <ListItem key={name}>
              <ListItemText
                primary={name}
                secondary={typeof value === 'object' ? JSON.stringify(value) : String(value)}
              />
            </ListItem>
          ))}

          <Divider />

          <ListItem>
            <ListItemIcon>
              <WatchIcon />
            </ListItemIcon>
            <ListItemText primary="Watch Variables" />
          </ListItem>
          {debuggerState.watchVariables.map(variable => (
            <ListItem
              key={variable.id}
              secondaryAction={
                <IconButton edge="end" onClick={() => handleRemoveWatch(variable.id)}>
                  <StopIcon />
                </IconButton>
              }
            >
              <ListItemText
                primary={variable.name}
                secondary={`${variable.type}: ${variable.value}`}
              />
            </ListItem>
          ))}

          <Divider />

          <ListItem>
            <ListItemIcon>
              <CallStackIcon />
            </ListItemIcon>
            <ListItemText primary="Call Stack" />
          </ListItem>
          {debuggerState.callStack.map(frame => (
            <ListItem key={frame.id}>
              <ListItemText
                primary={frame.function}
                secondary={`${frame.file}:${frame.line}`}
              />
            </ListItem>
          ))}

          <Divider />

          <ListItem>
            <ListItemIcon>
              <BreakpointIcon />
            </ListItemIcon>
            <ListItemText primary="Breakpoints" />
          </ListItem>
          {debuggerState.breakpoints.map(breakpoint => (
            <ListItem
              key={`${breakpoint.file}:${breakpoint.line}`}
              secondaryAction={
                <IconButton
                  edge="end"
                  onClick={() => handleBreakpointToggle(breakpoint.line, breakpoint.file)}
                >
                  <BreakpointIcon color={breakpoint.enabled ? 'error' : 'disabled'} />
                </IconButton>
              }
            >
              <ListItemText
                primary={`${breakpoint.file}:${breakpoint.line}`}
                secondary={breakpoint.condition || 'No condition'}
              />
            </ListItem>
          ))}

          <Divider />

          <ListItem>
            <ListItemIcon>
              <ErrorIcon />
            </ListItemIcon>
            <ListItemText primary="Errors and Warnings" />
          </ListItem>
          {debuggerState.errors.map((error, index) => (
            <ListItem key={index}>
              <ListItemIcon>
                {error.type === 'error' ? <ErrorIcon color="error" /> :
                 error.type === 'warning' ? <WarningIcon color="warning" /> :
                 <InfoIcon color="info" />}
              </ListItemIcon>
              <ListItemText
                primary={error.message}
                secondary={`${error.file}:${error.line}`}
              />
            </ListItem>
          ))}
        </List>
      </Box>
    </Paper>
  );
};

export default DebuggerPanel; 