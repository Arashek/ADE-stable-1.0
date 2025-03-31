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
  Divider
} from '@mui/material';
import {
  Add as AddIcon,
  Delete as DeleteIcon,
  Edit as EditIcon,
  PriorityHigh as PriorityHighIcon,
  Schedule as ScheduleIcon,
  Assignment as AssignmentIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon
} from '@mui/icons-material';

interface Task {
  id: string;
  title: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  status: 'pending' | 'in_progress' | 'completed' | 'blocked';
  subtasks: Task[];
  estimatedTime: number;
  dependencies: string[];
  aiSuggestions: {
    complexity: number;
    risks: string[];
    optimizations: string[];
  };
}

interface TaskManagerProps {
  projectId: string;
}

const TaskManager: React.FC<TaskManagerProps> = ({ projectId }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [newTask, setNewTask] = useState<Partial<Task>>({
    title: '',
    description: '',
    priority: 'medium',
    status: 'pending',
    subtasks: [],
    estimatedTime: 0,
    dependencies: [],
    aiSuggestions: {
      complexity: 0,
      risks: [],
      optimizations: []
    }
  });

  useEffect(() => {
    fetchTasks();
  }, [projectId]);

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
      // First, get AI analysis of the task
      const analysisResponse = await fetch('/api/tasks/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          title: newTask.title,
          description: newTask.description
        }),
      });
      const analysis = await analysisResponse.json();

      // Create task with AI analysis
      const response = await fetch('/api/tasks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...newTask,
          projectId,
          aiSuggestions: analysis
        }),
      });

      if (response.ok) {
        const createdTask = await response.json();
        setTasks(prev => [...prev, createdTask]);
        setOpenDialog(false);
        setNewTask({
          title: '',
          description: '',
          priority: 'medium',
          status: 'pending',
          subtasks: [],
          estimatedTime: 0,
          dependencies: [],
          aiSuggestions: {
            complexity: 0,
            risks: [],
            optimizations: []
          }
        });
      } else {
        throw new Error('Failed to create task');
      }
    } catch (err) {
      setError('Failed to create task');
    }
  };

  const handleBreakdownTask = async (taskId: string) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}/breakdown`, {
        method: 'POST',
      });
      if (response.ok) {
        const breakdown = await response.json();
        setTasks(prev => prev.map(task => 
          task.id === taskId 
            ? { ...task, subtasks: breakdown.subtasks }
            : task
        ));
      } else {
        throw new Error('Failed to break down task');
      }
    } catch (err) {
      setError('Failed to break down task');
    }
  };

  const handleOptimizeTask = async (taskId: string) => {
    try {
      const response = await fetch(`/api/tasks/${taskId}/optimize`, {
        method: 'POST',
      });
      if (response.ok) {
        const optimization = await response.json();
        setTasks(prev => prev.map(task => 
          task.id === taskId 
            ? { ...task, aiSuggestions: { ...task.aiSuggestions, optimizations: optimization.suggestions } }
            : task
        ));
      } else {
        throw new Error('Failed to optimize task');
      }
    } catch (err) {
      setError('Failed to optimize task');
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

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed':
        return <CheckCircleIcon color="success" />;
      case 'blocked':
        return <ErrorIcon color="error" />;
      case 'in_progress':
        return <InfoIcon color="info" />;
      default:
        return <WarningIcon color="warning" />;
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
            <Typography variant="h4">Task Management</Typography>
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

        {/* Task List */}
        <Grid item xs={12}>
          <Paper>
            <List>
              {tasks.map((task) => (
                <React.Fragment key={task.id}>
                  <ListItem>
                    <ListItemIcon>
                      {getStatusIcon(task.status)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          {task.title}
                          <Chip
                            size="small"
                            label={task.priority}
                            color={getPriorityColor(task.priority)}
                            icon={<PriorityHighIcon />}
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
                              label={`${task.estimatedTime}h`}
                              icon={<ScheduleIcon />}
                            />
                            {task.dependencies.length > 0 && (
                              <Chip
                                size="small"
                                label={`${task.dependencies.length} dependencies`}
                                icon={<AssignmentIcon />}
                              />
                            )}
                          </Box>
                        </Box>
                      }
                    />
                    <ListItemSecondaryAction>
                      <Tooltip title="Break Down Task">
                        <IconButton
                          edge="end"
                          onClick={() => handleBreakdownTask(task.id)}
                          sx={{ mr: 1 }}
                        >
                          <AssignmentIcon />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Optimize Task">
                        <IconButton
                          edge="end"
                          onClick={() => handleOptimizeTask(task.id)}
                          sx={{ mr: 1 }}
                        >
                          <InfoIcon />
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
                  {task.subtasks.length > 0 && (
                    <List component="div" disablePadding>
                      {task.subtasks.map((subtask) => (
                        <ListItem key={subtask.id} sx={{ pl: 4 }}>
                          <ListItemIcon>
                            <AssignmentIcon fontSize="small" />
                          </ListItemIcon>
                          <ListItemText
                            primary={subtask.title}
                            secondary={subtask.description}
                          />
                        </ListItem>
                      ))}
                    </List>
                  )}
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
          {selectedTask ? 'Edit Task' : 'Create New Task'}
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
                label="Description"
                multiline
                rows={4}
                value={newTask.description}
                onChange={(e) => setNewTask({ ...newTask, description: e.target.value })}
              />
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={newTask.priority}
                  label="Priority"
                  onChange={(e) => setNewTask({ ...newTask, priority: e.target.value as Task['priority'] })}
                >
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel>Status</InputLabel>
                <Select
                  value={newTask.status}
                  label="Status"
                  onChange={(e) => setNewTask({ ...newTask, status: e.target.value as Task['status'] })}
                >
                  <MenuItem value="pending">Pending</MenuItem>
                  <MenuItem value="in_progress">In Progress</MenuItem>
                  <MenuItem value="completed">Completed</MenuItem>
                  <MenuItem value="blocked">Blocked</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Estimated Time (hours)"
                type="number"
                value={newTask.estimatedTime}
                onChange={(e) => setNewTask({ ...newTask, estimatedTime: Number(e.target.value) })}
              />
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

export default TaskManager; 