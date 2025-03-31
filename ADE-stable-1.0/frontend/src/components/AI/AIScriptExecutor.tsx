import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  TextField,
  Button,
  CircularProgress,
  Alert,
  IconButton,
  Tooltip,
  Divider,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Clear as ClearIcon,
  Refresh as RefreshIcon,
  History as HistoryIcon,
  Settings as SettingsIcon,
  Save as SaveIcon,
  Delete as DeleteIcon,
} from '@mui/icons-material';

export interface ExecutionResult {
  stdout: string;
  stderr: string;
  exitCode: number;
  executionTime: number;
  resourceUsage: {
    cpu: number;
    memory: number;
  };
}

export interface ExecutionTemplate {
  name: string;
  command: string;
  description: string;
  env: Record<string, string>;
}

export interface AIScriptExecutorProps {
  onExecutionStart: (command: string) => void;
  onExecutionComplete: (result: ExecutionResult) => void;
  onExecutionError: (error: Error) => void;
  initialCommand?: string;
  disabled?: boolean;
}

const AIScriptExecutor: React.FC<AIScriptExecutorProps> = ({
  onExecutionStart,
  onExecutionComplete,
  onExecutionError,
  initialCommand = '',
  disabled = false,
}) => {
  const [command, setCommand] = useState(initialCommand);
  const [isExecuting, setIsExecuting] = useState(false);
  const [output, setOutput] = useState<ExecutionResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [history, setHistory] = useState<ExecutionResult[]>([]);
  const [templates, setTemplates] = useState<ExecutionTemplate[]>([]);
  const [selectedTemplate, setSelectedTemplate] = useState<string>('');
  const [showHistory, setShowHistory] = useState(false);
  const [showTemplates, setShowTemplates] = useState(false);
  const [envVars, setEnvVars] = useState<Record<string, string>>({});
  const [showEnvDialog, setShowEnvDialog] = useState(false);
  const [newEnvKey, setNewEnvKey] = useState('');
  const [newEnvValue, setNewEnvValue] = useState('');

  // Load templates from localStorage on mount
  useEffect(() => {
    const savedTemplates = localStorage.getItem('executionTemplates');
    if (savedTemplates) {
      setTemplates(JSON.parse(savedTemplates));
    }
  }, []);

  const handleExecute = async () => {
    if (!command.trim()) {
      setError('Please enter a command to execute');
      return;
    }

    setIsExecuting(true);
    setError(null);
    setOutput(null);
    onExecutionStart(command);

    try {
      const response = await fetch('/api/ai/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          command,
          env: envVars,
        }),
      });

      if (!response.ok) {
        throw new Error(`Execution failed: ${response.statusText}`);
      }

      const result: ExecutionResult = await response.json();
      setOutput(result);
      setHistory(prev => [result, ...prev].slice(0, 10)); // Keep last 10 executions
      onExecutionComplete(result);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('Unknown error occurred');
      setError(error.message);
      onExecutionError(error);
    } finally {
      setIsExecuting(false);
    }
  };

  const handleStop = () => {
    setIsExecuting(false);
    // TODO: Implement stop functionality
  };

  const handleClear = () => {
    setCommand('');
    setOutput(null);
    setError(null);
  };

  const handleRefresh = () => {
    if (command.trim()) {
      handleExecute();
    }
  };

  const handleSaveTemplate = () => {
    const newTemplate: ExecutionTemplate = {
      name: `Template ${templates.length + 1}`,
      command,
      description: 'Custom execution template',
      env: envVars,
    };
    const updatedTemplates = [...templates, newTemplate];
    setTemplates(updatedTemplates);
    localStorage.setItem('executionTemplates', JSON.stringify(updatedTemplates));
  };

  const handleDeleteTemplate = (index: number) => {
    const updatedTemplates = templates.filter((_, i) => i !== index);
    setTemplates(updatedTemplates);
    localStorage.setItem('executionTemplates', JSON.stringify(updatedTemplates));
  };

  const handleTemplateSelect = (template: ExecutionTemplate) => {
    setCommand(template.command);
    setEnvVars(template.env);
    setShowTemplates(false);
  };

  const handleAddEnvVar = () => {
    if (newEnvKey && newEnvValue) {
      setEnvVars(prev => ({
        ...prev,
        [newEnvKey]: newEnvValue,
      }));
      setNewEnvKey('');
      setNewEnvValue('');
    }
  };

  const handleRemoveEnvVar = (key: string) => {
    setEnvVars(prev => {
      const newEnv = { ...prev };
      delete newEnv[key];
      return newEnv;
    });
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="h6">AI Script Executor</Typography>
        <Box>
          <Tooltip title="History">
            <IconButton onClick={() => setShowHistory(true)}>
              <HistoryIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Templates">
            <IconButton onClick={() => setShowTemplates(true)}>
              <SettingsIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Environment Variables">
            <IconButton onClick={() => setShowEnvDialog(true)}>
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Command Input */}
      <Box sx={{ p: 2 }}>
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          <TextField
            fullWidth
            multiline
            rows={2}
            variant="outlined"
            placeholder="Enter command to execute..."
            value={command}
            onChange={(e) => setCommand(e.target.value)}
            disabled={isExecuting || disabled}
            error={!!error}
            helperText={error}
          />
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
            <Tooltip title="Execute">
              <IconButton
                onClick={handleExecute}
                disabled={isExecuting || disabled}
                color="primary"
              >
                <PlayIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Stop">
              <IconButton
                onClick={handleStop}
                disabled={!isExecuting || disabled}
                color="error"
              >
                <StopIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Clear">
              <IconButton
                onClick={handleClear}
                disabled={isExecuting || disabled}
              >
                <ClearIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Refresh">
              <IconButton
                onClick={handleRefresh}
                disabled={isExecuting || disabled}
              >
                <RefreshIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Save as Template">
              <IconButton
                onClick={handleSaveTemplate}
                disabled={isExecuting || disabled}
              >
                <SaveIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>

        {/* Environment Variables Display */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
          {Object.entries(envVars).map(([key, value]) => (
            <Chip
              key={key}
              label={`${key}=${value}`}
              onDelete={() => handleRemoveEnvVar(key)}
            />
          ))}
        </Box>

        {isExecuting && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <CircularProgress size={20} />
            <Typography variant="body2">Executing command...</Typography>
          </Box>
        )}
      </Box>

      {/* Output Display */}
      {output && (
        <Box sx={{ flex: 1, p: 2, overflow: 'auto' }}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="subtitle2" gutterBottom>
              Execution Results
            </Typography>
            <Divider sx={{ mb: 2 }} />
            
            {/* Standard Output */}
            {output.stdout && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Standard Output
                </Typography>
                <Paper
                  variant="outlined"
                  sx={{
                    p: 1,
                    bgcolor: 'background.default',
                    fontFamily: 'monospace',
                    whiteSpace: 'pre-wrap',
                    maxHeight: '200px',
                    overflow: 'auto',
                  }}
                >
                  {output.stdout}
                </Paper>
              </Box>
            )}

            {/* Standard Error */}
            {output.stderr && (
              <Box sx={{ mb: 2 }}>
                <Typography variant="caption" color="text.secondary">
                  Standard Error
                </Typography>
                <Paper
                  variant="outlined"
                  sx={{
                    p: 1,
                    bgcolor: 'background.default',
                    fontFamily: 'monospace',
                    whiteSpace: 'pre-wrap',
                    maxHeight: '200px',
                    overflow: 'auto',
                  }}
                >
                  {output.stderr}
                </Paper>
              </Box>
            )}

            {/* Execution Details */}
            <Box sx={{ mt: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Execution Details
              </Typography>
              <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
                <Typography variant="body2">
                  Exit Code: {output.exitCode}
                </Typography>
                <Typography variant="body2">
                  Time: {output.executionTime.toFixed(2)}s
                </Typography>
                <Typography variant="body2">
                  CPU: {output.resourceUsage.cpu.toFixed(2)}%
                </Typography>
                <Typography variant="body2">
                  Memory: {output.resourceUsage.memory.toFixed(2)}%
                </Typography>
              </Box>
            </Box>
          </Paper>
        </Box>
      )}

      {/* History Dialog */}
      <Dialog open={showHistory} onClose={() => setShowHistory(false)} maxWidth="md" fullWidth>
        <DialogTitle>Execution History</DialogTitle>
        <DialogContent>
          <List>
            {history.map((result, index) => (
              <ListItem key={index}>
                <ListItemText
                  primary={`Execution ${index + 1}`}
                  secondary={
                    <>
                      <Typography variant="body2">
                        Exit Code: {result.exitCode}
                      </Typography>
                      <Typography variant="body2">
                        Time: {result.executionTime.toFixed(2)}s
                      </Typography>
                      <Typography variant="body2">
                        CPU: {result.resourceUsage.cpu.toFixed(2)}%
                      </Typography>
                      <Typography variant="body2">
                        Memory: {result.resourceUsage.memory.toFixed(2)}%
                      </Typography>
                    </>
                  }
                />
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowHistory(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Templates Dialog */}
      <Dialog open={showTemplates} onClose={() => setShowTemplates(false)} maxWidth="md" fullWidth>
        <DialogTitle>Execution Templates</DialogTitle>
        <DialogContent>
          <List>
            {templates.map((template, index) => (
              <ListItem key={index}>
                <ListItemText
                  primary={template.name}
                  secondary={template.description}
                />
                <ListItemSecondaryAction>
                  <IconButton onClick={() => handleTemplateSelect(template)}>
                    <PlayIcon />
                  </IconButton>
                  <IconButton onClick={() => handleDeleteTemplate(index)}>
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowTemplates(false)}>Close</Button>
        </DialogActions>
      </Dialog>

      {/* Environment Variables Dialog */}
      <Dialog open={showEnvDialog} onClose={() => setShowEnvDialog(false)}>
        <DialogTitle>Environment Variables</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField
              label="Key"
              value={newEnvKey}
              onChange={(e) => setNewEnvKey(e.target.value)}
            />
            <TextField
              label="Value"
              value={newEnvValue}
              onChange={(e) => setNewEnvValue(e.target.value)}
            />
            <Button onClick={handleAddEnvVar}>Add</Button>
          </Box>
          <List>
            {Object.entries(envVars).map(([key, value]) => (
              <ListItem key={key}>
                <ListItemText
                  primary={key}
                  secondary={value}
                />
                <ListItemSecondaryAction>
                  <IconButton onClick={() => handleRemoveEnvVar(key)}>
                    <DeleteIcon />
                  </IconButton>
                </ListItemSecondaryAction>
              </ListItem>
            ))}
          </List>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowEnvDialog(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default AIScriptExecutor; 