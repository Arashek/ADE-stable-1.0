import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  LinearProgress,
  Tooltip,
  Divider,
  Card,
  CardContent,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Stepper,
  Step,
  StepLabel,
  StepContent
} from '@mui/material';
import {
  Assignment as TaskIcon,
  Code as CodeIcon,
  RateReview as ReviewIcon,
  BugReport as TestIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Timeline as TimelineIcon,
  Description as DocIcon,
  BugReport as BugIcon
} from '@mui/icons-material';

interface Agent {
  id: string;
  name: string;
  type: 'task_planner' | 'code_generator' | 'reviewer' | 'tester' | 'documentation' | 'error_handler';
  status: 'idle' | 'busy' | 'error';
  capabilities: string[];
  currentTask?: Task;
  performance: {
    successRate: number;
    averageTime: number;
    lastActive: string;
  };
}

interface Task {
  id: string;
  title: string;
  description: string;
  type: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  assignedAgent?: string;
  dependencies: string[];
  progress: number;
  results?: any;
  error?: string;
  startTime?: string;
  endTime?: string;
  subtasks?: Task[];
}

interface SpecializedAgentsProps {
  projectId: string;
}

const SpecializedAgents: React.FC<SpecializedAgentsProps> = ({ projectId }) => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [newTask, setNewTask] = useState<Partial<Task>>({
    title: '',
    description: '',
    type: '',
    priority: 'medium',
    status: 'pending',
    dependencies: [],
    progress: 0
  });
  const [expandedTask, setExpandedTask] = useState<string | false>(false);
  const [activeStep, setActiveStep] = useState(0);

  useEffect(() => {
    fetchAgents();
    fetchTasks();
  }, [projectId]);

  const fetchAgents = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/agents?projectId=${projectId}`);
      const data = await response.json();
      setAgents(data.agents);
    } catch (err) {
      setError('Failed to fetch agents');
    } finally {
      setLoading(false);
    }
  };

  const fetchTasks = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/tasks?projectId=${projectId}`);
      const data = await response.json();
      setTasks(data.tasks);
    } catch (err) {
      setError('Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async () => {
    try {
      // First, get task planning from the Task Planner Agent
      const planningResponse = await fetch('/api/agents/task-planner/plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: newTask.title,
          description: newTask.description,
          type: newTask.type
        }),
      });
      const planning = await planningResponse.json();

      // Create task with planned subtasks
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newTask,
          projectId,
          subtasks: planning.subtasks
        }),
      });

      if (response.ok) {
        const createdTask = await response.json();
        setTasks(prev => [...prev, createdTask]);
        setOpenDialog(false);
        setNewTask({
          title: '',
          description: '',
          type: '',
          priority: 'medium',
          status: 'pending',
          dependencies: [],
          progress: 0
        });
      } else {
        throw new Error('Failed to create task');
      }
    } catch (err) {
      setError('Failed to create task');
    }
  };

  const handleStartTask = async (taskId: string) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}/start`, {
        method: 'POST',
      });
      if (response.ok) {
        const updatedTask = await response.json();
        setTasks(prev => prev.map(task => 
          task.id === taskId ? updatedTask : task
        ));
      } else {
        throw new Error('Failed to start task');
      }
    } catch (err) {
      setError('Failed to start task');
    }
  };

  const handleStopTask = async (taskId: string) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}/stop`, {
        method: 'POST',
      });
      if (response.ok) {
        const updatedTask = await response.json();
        setTasks(prev => prev.map(task => 
          task.id === taskId ? updatedTask : task
        ));
      } else {
        throw new Error('Failed to stop task');
      }
    } catch (err) {
      setError('Failed to stop task');
    }
  };

  const handleAssignAgent = async (taskId: string, agentId: string) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}/assign`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ agentId }),
      });
      if (response.ok) {
        const updatedTask = await response.json();
        setTasks(prev => prev.map(task => 
          task.id === taskId ? updatedTask : task
        ));
      } else {
        throw new Error('Failed to assign agent');
      }
    } catch (err) {
      setError('Failed to assign agent');
    }
  };

  const handleCodeGeneration = async (taskId: string) => {
    try {
      const response = await fetch(`/api/agents/code-generator/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ taskId }),
      });
      if (response.ok) {
        const result = await response.json();
        setTasks(prev => prev.map(task => 
          task.id === taskId 
            ? { ...task, results: result }
            : task
        ));
      } else {
        throw new Error('Failed to generate code');
      }
    } catch (err) {
      setError('Failed to generate code');
    }
  };

  const handleCodeReview = async (taskId: string) => {
    try {
      const response = await fetch(`/api/agents/reviewer/review`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ taskId }),
      });
      if (response.ok) {
        const review = await response.json();
        setTasks(prev => prev.map(task => 
          task.id === taskId 
            ? { ...task, results: { ...task.results, review } }
            : task
        ));
      } else {
        throw new Error('Failed to review code');
      }
    } catch (err) {
      setError('Failed to review code');
    }
  };

  const handleRunTests = async (taskId: string) => {
    try {
      const response = await fetch(`/api/agents/tester/test`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ taskId }),
      });
      if (response.ok) {
        const testResults = await response.json();
        setTasks(prev => prev.map(task => 
          task.id === taskId 
            ? { ...task, results: { ...task.results, testResults } }
            : task
        ));
      } else {
        throw new Error('Failed to run tests');
      }
    } catch (err) {
      setError('Failed to run tests');
    }
  };

  const handleDocumentation = async (taskId: string) => {
    try {
      const response = await fetch(`/api/agents/documentation/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ taskId }),
      });
      if (response.ok) {
        const result = await response.json();
        setTasks(prev => prev.map(task => 
          task.id === taskId 
            ? { ...task, results: { ...task.results, documentation: result } }
            : task
        ));
      } else {
        throw new Error('Failed to generate documentation');
      }
    } catch (err) {
      setError('Failed to generate documentation');
    }
  };

  const handleErrorDiagnosis = async (taskId: string) => {
    try {
      const response = await fetch(`/api/agents/error-handler/diagnose`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ taskId }),
      });
      if (response.ok) {
        const result = await response.json();
        setTasks(prev => prev.map(task => 
          task.id === taskId 
            ? { ...task, results: { ...task.results, errorDiagnosis: result } }
            : task
        ));
      } else {
        throw new Error('Failed to diagnose error');
      }
    } catch (err) {
      setError('Failed to diagnose error');
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in_progress':
        return 'primary';
      case 'failed':
        return 'error';
      case 'pending':
        return 'warning';
      default:
        return 'default';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getAgentStatusColor = (status: string) => {
    switch (status) {
      case 'idle':
        return 'success';
      case 'busy':
        return 'primary';
      case 'error':
        return 'error';
      default:
        return 'default';
    }
  };

  const getAgentIcon = (type: string) => {
    switch (type) {
      case 'task_planner':
        return <TaskIcon />;
      case 'code_generator':
        return <CodeIcon />;
      case 'reviewer':
        return <ReviewIcon />;
      case 'tester':
        return <TestIcon />;
      case 'documentation':
        return <DocIcon />;
      case 'error_handler':
        return <BugIcon />;
      default:
        return <InfoIcon />;
    }
  };

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">Specialized Agents</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => setOpenDialog(true)}
            >
              New Task
            </Button>
          </Box>
        </Grid>

        {/* Error Alert */}
        {error && (
          <Grid item xs={12}>
            <Alert severity="error" onClose={() => setError(null)}>
              {error}
            </Alert>
          </Grid>
        )}

        {/* Agents Overview */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Available Agents
            </Typography>
            <List>
              {agents.map((agent) => (
                <ListItem key={agent.id}>
                  <ListItemIcon>
                    {getAgentIcon(agent.type)}
                  </ListItemIcon>
                  <ListItemText
                    primary={agent.name}
                    secondary={
                      <Box>
                        <Typography variant="body2">
                          Type: {agent.type.replace('_', ' ')}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                          <Chip
                            size="small"
                            label={`Success: ${agent.performance.successRate}%`}
                            color={agent.performance.successRate >= 80 ? 'success' : 'warning'}
                          />
                          <Chip
                            size="small"
                            label={`Avg Time: ${agent.performance.averageTime}s`}
                            color="primary"
                          />
                        </Box>
                      </Box>
                    }
                  />
                </ListItem>
              ))}
            </List>
          </Paper>
        </Grid>

        {/* Tasks List */}
        <Grid item xs={12} md={8}>
          <Paper>
            <List>
              {tasks.map((task) => (
                <React.Fragment key={task.id}>
                  <Accordion
                    expanded={expandedTask === task.id}
                    onChange={() => setExpandedTask(expandedTask === task.id ? false : task.id)}
                  >
                    <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                      <ListItem>
                        <ListItemIcon>
                          <TaskIcon color={getStatusColor(task.status)} />
                        </ListItemIcon>
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {task.title}
                              <Chip
                                size="small"
                                label={task.status}
                                color={getStatusColor(task.status)}
                              />
                              <Chip
                                size="small"
                                label={task.priority}
                                color={getPriorityColor(task.priority)}
                              />
                            </Box>
                          }
                          secondary={
                            <Box>
                              <Typography variant="body2" color="text.secondary">
                                {task.description}
                              </Typography>
                              <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                                <Chip
                                  size="small"
                                  label={`Progress: ${task.progress}%`}
                                  color="primary"
                                />
                                {task.assignedAgent && (
                                  <Chip
                                    size="small"
                                    label={`Assigned: ${task.assignedAgent}`}
                                    icon={<InfoIcon />}
                                  />
                                )}
                              </Box>
                            </Box>
                          }
                        />
                        <ListItemSecondaryAction>
                          {task.status === 'pending' && (
                            <Tooltip title="Start Task">
                              <IconButton
                                edge="end"
                                onClick={() => handleStartTask(task.id)}
                                sx={{ mr: 1 }}
                              >
                                <StartIcon />
                              </IconButton>
                            </Tooltip>
                          )}
                          {task.status === 'in_progress' && (
                            <Tooltip title="Stop Task">
                              <IconButton
                                edge="end"
                                onClick={() => handleStopTask(task.id)}
                                sx={{ mr: 1 }}
                              >
                                <StopIcon />
                              </IconButton>
                            </Tooltip>
                          )}
                          <Tooltip title="Generate Code">
                            <IconButton
                              edge="end"
                              onClick={() => handleCodeGeneration(task.id)}
                              sx={{ mr: 1 }}
                            >
                              <CodeIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Review Code">
                            <IconButton
                              edge="end"
                              onClick={() => handleCodeReview(task.id)}
                              sx={{ mr: 1 }}
                            >
                              <ReviewIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Run Tests">
                            <IconButton
                              edge="end"
                              onClick={() => handleRunTests(task.id)}
                              sx={{ mr: 1 }}
                            >
                              <TestIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Generate Documentation">
                            <IconButton
                              edge="end"
                              onClick={() => handleDocumentation(task.id)}
                              sx={{ mr: 1 }}
                            >
                              <DocIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Diagnose Error">
                            <IconButton
                              edge="end"
                              onClick={() => handleErrorDiagnosis(task.id)}
                              sx={{ mr: 1 }}
                            >
                              <BugIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Edit Task">
                            <IconButton
                              edge="end"
                              onClick={() => {
                                setSelectedTask(task);
                                setOpenDialog(true);
                              }}
                              sx={{ mr: 1 }}
                            >
                              <EditIcon />
                            </IconButton>
                          </Tooltip>
                          <Tooltip title="Delete Task">
                            <IconButton
                              edge="end"
                              onClick={() => {
                                // Implement delete functionality
                              }}
                            >
                              <DeleteIcon />
                            </IconButton>
                          </Tooltip>
                        </ListItemSecondaryAction>
                      </ListItem>
                    </AccordionSummary>
                    <AccordionDetails>
                      <Box sx={{ pl: 4 }}>
                        {/* Task Details */}
                        <Grid container spacing={2}>
                          <Grid item xs={12}>
                            <Typography variant="subtitle1" gutterBottom>
                              Task Details
                            </Typography>
                            <List>
                              <ListItem>
                                <ListItemText
                                  primary="Type"
                                  secondary={task.type}
                                />
                              </ListItem>
                              <ListItem>
                                <ListItemText
                                  primary="Dependencies"
                                  secondary={task.dependencies.join(', ') || 'None'}
                                />
                              </ListItem>
                              {task.startTime && (
                                <ListItem>
                                  <ListItemText
                                    primary="Start Time"
                                    secondary={new Date(task.startTime).toLocaleString()}
                                  />
                                </ListItem>
                              )}
                              {task.endTime && (
                                <ListItem>
                                  <ListItemText
                                    primary="End Time"
                                    secondary={new Date(task.endTime).toLocaleString()}
                                  />
                                </ListItem>
                              )}
                            </List>
                          </Grid>

                          {/* Subtasks */}
                          {task.subtasks && task.subtasks.length > 0 && (
                            <Grid item xs={12}>
                              <Typography variant="subtitle1" gutterBottom>
                                Subtasks
                              </Typography>
                              <List>
                                {task.subtasks.map((subtask, index) => (
                                  <ListItem key={index}>
                                    <ListItemIcon>
                                      <TaskIcon color={getStatusColor(subtask.status)} />
                                    </ListItemIcon>
                                    <ListItemText
                                      primary={subtask.title}
                                      secondary={
                                        <Box>
                                          <Typography variant="body2">
                                            {subtask.description}
                                          </Typography>
                                          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                                            <Chip
                                              size="small"
                                              label={`Progress: ${subtask.progress}%`}
                                              color="primary"
                                            />
                                          </Box>
                                        </Box>
                                      }
                                    />
                                  </ListItem>
                                ))}
                              </List>
                            </Grid>
                          )}

                          {/* Results or Error */}
                          {(task.results || task.error) && (
                            <Grid item xs={12}>
                              <Typography variant="subtitle1" gutterBottom>
                                {task.error ? 'Error' : 'Results'}
                              </Typography>
                              <Alert severity={task.error ? 'error' : 'success'}>
                                {task.error || JSON.stringify(task.results, null, 2)}
                              </Alert>
                            </Grid>
                          )}

                          {/* Agent Assignment */}
                          {!task.assignedAgent && (
                            <Grid item xs={12}>
                              <FormControl fullWidth>
                                <InputLabel>Assign Agent</InputLabel>
                                <Select
                                  value=""
                                  label="Assign Agent"
                                  onChange={(e) => handleAssignAgent(task.id, e.target.value)}
                                >
                                  {agents
                                    .filter(agent => agent.status === 'idle')
                                    .map(agent => (
                                      <MenuItem key={agent.id} value={agent.id}>
                                        {agent.name} ({agent.type.replace('_', ' ')})
                                      </MenuItem>
                                    ))}
                                </Select>
                              </FormControl>
                            </Grid>
                          )}
                        </Grid>
                      </Box>
                    </AccordionDetails>
                  </Accordion>
                  <Divider />
                </React.Fragment>
              ))}
            </List>
          </Paper>
        </Grid>
      </Grid>

      {/* Task Dialog */}
      <Dialog open={openDialog} onClose={() => setOpenDialog(false)} maxWidth="md" fullWidth>
        <DialogTitle>
          {selectedTask ? 'Edit Task' : 'New Task'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Title"
                value={newTask.title}
                onChange={(e) => setNewTask({ ...newTask, title: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={4}
                label="Description"
                value={newTask.description}
                onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Type</InputLabel>
                <Select
                  value={newTask.type}
                  label="Type"
                  onChange={(e) => setNewTask({ ...newTask, type: e.target.value })}
                >
                  <MenuItem value="code_analysis">Code Analysis</MenuItem>
                  <MenuItem value="testing">Testing</MenuItem>
                  <MenuItem value="optimization">Optimization</MenuItem>
                  <MenuItem value="documentation">Documentation</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={newTask.priority}
                  label="Priority"
                  onChange={(e) => setNewTask({ ...newTask, priority: e.target.value })}
                >
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenDialog(false)}>Cancel</Button>
          <Button onClick={handleCreateTask} variant="contained" color="primary">
            {selectedTask ? 'Save Changes' : 'Create Task'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SpecializedAgents; 