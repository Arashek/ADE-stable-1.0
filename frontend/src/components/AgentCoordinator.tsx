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
  CardActions,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  StepContent,
  Accordion,
  AccordionSummary,
  AccordionDetails
} from '@mui/material';
import {
  SmartToy as AgentIcon,
  Assignment as TaskIcon,
  Group as GroupIcon,
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
  Timeline as TimelineIcon
} from '@mui/icons-material';

interface Agent {
  id: string;
  name: string;
  type: string;
  status: 'idle' | 'busy' | 'error';
  capabilities: string[];
  currentTask?: string;
  performance: {
    successRate: number;
    avgCompletionTime: number;
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
  coordinationFlow?: string;
}

interface AgentCoordinatorProps {
  projectId: string;
}

const AgentCoordinator: React.FC<AgentCoordinatorProps> = ({ projectId }) => {
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
  const [activeStep, setActiveStep] = useState(0);
  const [expandedTask, setExpandedTask] = useState<string | false>(false);

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
    } catch (err: any) {
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
    } catch (err: any) {
      setError('Failed to fetch tasks');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateTask = async () => {
    try {
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newTask,
          projectId,
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
    } catch (err: any) {
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
    } catch (err: any) {
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
    } catch (err: any) {
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
    } catch (err: any) {
      setError('Failed to assign agent');
    }
  };

  const handleStartCoordinationFlow = async (taskId: string, flowId: string) => {
    try {
      const response = await fetch('/api/coordination/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          taskId,
          flowId,
          projectId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start coordination flow');
      }

      const result = await response.json();
      setTasks(prev => prev.map(task =>
        task.id === taskId
          ? { ...task, coordinationFlow: flowId, status: 'in_progress' }
          : task
      ));
    } catch (error: any) {
      console.error('Error starting coordination flow:', error);
      setError('Failed to start coordination flow');
    }
  };

  const handleStopCoordinationFlow = async (taskId: string) => {
    try {
      const response = await fetch('/api/coordination/stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          taskId,
          projectId,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to stop coordination flow');
      }

      setTasks(prev => prev.map(task =>
        task.id === taskId
          ? { ...task, coordinationFlow: undefined, status: 'pending' }
          : task
      ));
    } catch (error: any) {
      console.error('Error stopping coordination flow:', error);
      setError('Failed to stop coordination flow');
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

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">Agent Coordination</Typography>
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
                    <AgentIcon color={getAgentStatusColor(agent.status)} />
                  </ListItemIcon>
                  <ListItemText
                    primary={agent.name}
                    secondary={
                      <Box>
                        <Typography variant="body2">
                          Type: {agent.type}
                        </Typography>
                        <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
                          <Chip
                            size="small"
                            label={`Success: ${agent.performance.successRate}%`}
                            color={agent.performance.successRate >= 80 ? 'success' : 'warning'}
                          />
                          <Chip
                            size="small"
                            label={`Avg Time: ${agent.performance.avgCompletionTime}s`}
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
                                    icon={<AgentIcon />}
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
                                        {agent.name} ({agent.type})
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

export default AgentCoordinator; 