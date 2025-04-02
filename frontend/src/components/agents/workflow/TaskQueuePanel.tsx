import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  IconButton,
  Chip,
  Divider,
  Badge,
  Button,
  CircularProgress,
  Menu,
  MenuItem,
  TextField,
  InputAdornment,
  useTheme,
  alpha
} from '@mui/material';
import {
  Assignment as AssignmentIcon,
  Done as DoneIcon,
  Cancel as CancelIcon,
  MoreVert as MoreVertIcon,
  PlayArrow as PlayArrowIcon,
  Pause as PauseIcon,
  ArrowUpward as ArrowUpwardIcon,
  ArrowDownward as ArrowDownwardIcon,
  Search as SearchIcon,
  FilterList as FilterListIcon,
  AssignmentLate as AssignmentLateIcon,
  AssignmentTurnedIn as AssignmentTurnedInIcon,
  AccessTime as AccessTimeIcon
} from '@mui/icons-material';
import { Agent } from '../AgentListPanel';

// Task status enum
export enum TaskStatus {
  PENDING = 'PENDING',
  IN_PROGRESS = 'IN_PROGRESS',
  COMPLETED = 'COMPLETED',
  FAILED = 'FAILED',
  CANCELED = 'CANCELED'
}

// Task priority enum
export enum TaskPriority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
  CRITICAL = 'CRITICAL'
}

// Task interface
export interface Task {
  id: string;
  title: string;
  description: string;
  status: TaskStatus;
  priority: TaskPriority;
  agentId: string;
  createdAt: Date;
  updatedAt: Date;
  completedAt?: Date;
  estimatedDuration?: number; // in minutes
  progress?: number; // 0-100
  dependencies?: string[]; // IDs of dependent tasks
}

interface TaskQueuePanelProps {
  agents: Agent[];
  selectedAgentId?: string;
}

/**
 * Helper function to generate mock tasks for development and testing
 */
export const generateMockTasks = (agents: Agent[], count: number = 15): Task[] => {
  const tasks: Task[] = [];
  const statuses = Object.values(TaskStatus);
  const priorities = Object.values(TaskPriority);
  
  // Task titles
  const taskTitles = [
    'Code Review',
    'Requirement Analysis',
    'Security Assessment',
    'Performance Optimization',
    'Architecture Review',
    'Dependency Resolution',
    'Test Case Generation',
    'Documentation',
    'API Integration',
    'Database Schema Validation'
  ];
  
  // Generate random tasks
  for (let i = 0; i < count; i++) {
    const createdAt = new Date(Date.now() - Math.floor(Math.random() * 7 * 24 * 60 * 60 * 1000)); // Within last week
    const updatedAt = new Date(createdAt.getTime() + Math.floor(Math.random() * 24 * 60 * 60 * 1000)); // After created
    
    const status = statuses[Math.floor(Math.random() * statuses.length)];
    const priority = priorities[Math.floor(Math.random() * priorities.length)];
    const agent = agents[Math.floor(Math.random() * agents.length)];
    
    // Select a random task title
    const titleIndex = Math.floor(Math.random() * taskTitles.length);
    const title = `${taskTitles[titleIndex]} #${i + 1}`;
    
    // Generate a description based on the title
    const description = `${agent.name} will ${taskTitles[titleIndex].toLowerCase()} for the current project component`;
    
    // Randomize progress for in-progress tasks
    let progress;
    if (status === TaskStatus.IN_PROGRESS) {
      progress = Math.floor(Math.random() * 100);
    }
    
    // Set completedAt for completed or failed tasks
    let completedAt;
    if (status === TaskStatus.COMPLETED || status === TaskStatus.FAILED) {
      completedAt = new Date(updatedAt.getTime() + Math.floor(Math.random() * 24 * 60 * 60 * 1000));
    }
    
    tasks.push({
      id: `task-${i}`,
      title,
      description,
      status,
      priority,
      agentId: agent.id,
      createdAt,
      updatedAt,
      completedAt,
      estimatedDuration: Math.floor(Math.random() * 120) + 10, // 10-130 minutes
      progress
    });
  }
  
  // Add some task dependencies
  tasks.forEach((task, index) => {
    // 30% chance to have dependencies
    if (Math.random() > 0.7 && index > 0) {
      // Add 1-2 dependencies to previous tasks
      const dependencies: string[] = [];
      const numDependencies = Math.floor(Math.random() * 2) + 1;
      
      for (let j = 0; j < numDependencies; j++) {
        // Only select from tasks that come before this one
        const dependencyIndex = Math.floor(Math.random() * index);
        dependencies.push(tasks[dependencyIndex].id);
      }
      
      task.dependencies = dependencies;
    }
  });
  
  return tasks;
};

/**
 * TaskQueuePanel Component - Displays and manages the agent task queue
 */
const TaskQueuePanel: React.FC<TaskQueuePanelProps> = ({
  agents,
  selectedAgentId
}) => {
  const theme = useTheme();
  
  // State for tasks
  const [tasks, setTasks] = useState<Task[]>(generateMockTasks(agents));
  
  // State for search and filtering
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<TaskStatus | ''>('');
  const [priorityFilter, setPriorityFilter] = useState<TaskPriority | ''>('');
  const [sortBy, setSortBy] = useState<'priority' | 'date' | 'status'>('priority');
  const [sortDirection, setSortDirection] = useState<'asc' | 'desc'>('desc');
  
  // State for task menu
  const [menuAnchorEl, setMenuAnchorEl] = useState<HTMLElement | null>(null);
  const [selectedTaskId, setSelectedTaskId] = useState<string | null>(null);
  
  // Get selected task
  const selectedTask = selectedTaskId ? tasks.find(task => task.id === selectedTaskId) : null;

  // Filter and sort tasks
  const filteredTasks = tasks
    .filter(task => 
      // Filter by selected agent if any
      (selectedAgentId ? task.agentId === selectedAgentId : true) &&
      // Search term in title or description
      (searchTerm === '' || 
        task.title.toLowerCase().includes(searchTerm.toLowerCase()) || 
        task.description.toLowerCase().includes(searchTerm.toLowerCase())) &&
      // Filter by status if selected
      (statusFilter === '' || task.status === statusFilter) &&
      // Filter by priority if selected
      (priorityFilter === '' || task.priority === priorityFilter)
    )
    .sort((a, b) => {
      // Sort by chosen field
      if (sortBy === 'priority') {
        const priorityOrder = { 
          [TaskPriority.CRITICAL]: 0, 
          [TaskPriority.HIGH]: 1, 
          [TaskPriority.MEDIUM]: 2, 
          [TaskPriority.LOW]: 3 
        };
        return sortDirection === 'asc' 
          ? priorityOrder[a.priority] - priorityOrder[b.priority]
          : priorityOrder[b.priority] - priorityOrder[a.priority];
      } else if (sortBy === 'date') {
        return sortDirection === 'asc'
          ? a.createdAt.getTime() - b.createdAt.getTime()
          : b.createdAt.getTime() - a.createdAt.getTime();
      } else if (sortBy === 'status') {
        const statusOrder = {
          [TaskStatus.IN_PROGRESS]: 0,
          [TaskStatus.PENDING]: 1,
          [TaskStatus.COMPLETED]: 2,
          [TaskStatus.FAILED]: 3,
          [TaskStatus.CANCELED]: 4
        };
        return sortDirection === 'asc'
          ? statusOrder[a.status] - statusOrder[b.status]
          : statusOrder[b.status] - statusOrder[a.status];
      }
      return 0;
    });
  
  // Format date to readable string
  const formatDate = (date: Date): string => {
    return date.toLocaleString(undefined, { 
      month: 'short', 
      day: 'numeric', 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };
  
  // Get agent by ID
  const getAgentById = (id: string) => {
    return agents.find(agent => agent.id === id);
  };
  
  // Handle menu open
  const handleMenuOpen = (event: React.MouseEvent<HTMLElement>, taskId: string) => {
    setMenuAnchorEl(event.currentTarget);
    setSelectedTaskId(taskId);
  };
  
  // Handle menu close
  const handleMenuClose = () => {
    setMenuAnchorEl(null);
  };
  
  // Handle task actions
  const updateTaskStatus = (taskId: string, status: TaskStatus) => {
    setTasks(prevTasks => 
      prevTasks.map(task => 
        task.id === taskId 
          ? { 
              ...task, 
              status, 
              updatedAt: new Date(),
              completedAt: (status === TaskStatus.COMPLETED || status === TaskStatus.FAILED) 
                ? new Date() 
                : task.completedAt
            } 
          : task
      )
    );
    handleMenuClose();
  };
  
  // Handle sorting change
  const handleSortChange = (field: 'priority' | 'date' | 'status') => {
    if (sortBy === field) {
      // Toggle direction if same field
      setSortDirection(prev => prev === 'asc' ? 'desc' : 'asc');
    } else {
      // Set new field with default direction
      setSortBy(field);
      setSortDirection('desc');
    }
  };
  
  // Get status color
  const getStatusColor = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.PENDING:
        return theme.palette.info.main;
      case TaskStatus.IN_PROGRESS:
        return theme.palette.primary.main;
      case TaskStatus.COMPLETED:
        return theme.palette.success.main;
      case TaskStatus.FAILED:
        return theme.palette.error.main;
      case TaskStatus.CANCELED:
        return theme.palette.grey[500];
      default:
        return theme.palette.grey[500];
    }
  };
  
  // Get priority color
  const getPriorityColor = (priority: TaskPriority) => {
    switch (priority) {
      case TaskPriority.CRITICAL:
        return theme.palette.error.main;
      case TaskPriority.HIGH:
        return theme.palette.warning.main;
      case TaskPriority.MEDIUM:
        return theme.palette.info.main;
      case TaskPriority.LOW:
        return theme.palette.success.main;
      default:
        return theme.palette.grey[500];
    }
  };
  
  // Get status icon
  const getStatusIcon = (status: TaskStatus) => {
    switch (status) {
      case TaskStatus.PENDING:
        return <AccessTimeIcon />;
      case TaskStatus.IN_PROGRESS:
        return <CircularProgress size={24} />;
      case TaskStatus.COMPLETED:
        return <DoneIcon />;
      case TaskStatus.FAILED:
        return <CancelIcon color="error" />;
      case TaskStatus.CANCELED:
        return <CancelIcon color="disabled" />;
      default:
        return <AssignmentIcon />;
    }
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {/* Task header with search and filters */}
      <Box sx={{ p: 2, bgcolor: alpha(theme.palette.background.paper, 0.7) }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6" component="h2">
            Task Queue
          </Typography>
          
          <Box>
            <Button 
              size="small" 
              startIcon={sortBy === 'priority' ? (sortDirection === 'asc' ? <ArrowUpwardIcon fontSize="small" /> : <ArrowDownwardIcon fontSize="small" />) : undefined}
              onClick={() => handleSortChange('priority')}
              color={sortBy === 'priority' ? 'primary' : 'inherit'}
              sx={{ mr: 1 }}
            >
              Priority
            </Button>
            
            <Button 
              size="small" 
              startIcon={sortBy === 'date' ? (sortDirection === 'asc' ? <ArrowUpwardIcon fontSize="small" /> : <ArrowDownwardIcon fontSize="small" />) : undefined}
              onClick={() => handleSortChange('date')}
              color={sortBy === 'date' ? 'primary' : 'inherit'}
              sx={{ mr: 1 }}
            >
              Date
            </Button>
            
            <Button 
              size="small" 
              startIcon={sortBy === 'status' ? (sortDirection === 'asc' ? <ArrowUpwardIcon fontSize="small" /> : <ArrowDownwardIcon fontSize="small" />) : undefined}
              onClick={() => handleSortChange('status')}
              color={sortBy === 'status' ? 'primary' : 'inherit'}
            >
              Status
            </Button>
          </Box>
        </Box>
        
        <Box sx={{ display: 'flex', gap: 2 }}>
          <TextField
            variant="outlined"
            size="small"
            placeholder="Search tasks..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon fontSize="small" />
                </InputAdornment>
              ),
            }}
            sx={{ flexGrow: 1 }}
          />
          
          <Button
            variant="outlined"
            size="small"
            startIcon={<FilterListIcon />}
            onClick={() => {
              // Reset all filters
              setStatusFilter('');
              setPriorityFilter('');
            }}
          >
            {statusFilter || priorityFilter ? 'Clear Filters' : 'Filter'}
          </Button>
        </Box>
        
        {/* Status filters */}
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mt: 2 }}>
          {Object.values(TaskStatus).map(status => (
            <Chip
              key={status}
              label={status.replace('_', ' ')}
              size="small"
              variant={statusFilter === status ? 'filled' : 'outlined'}
              onClick={() => setStatusFilter(prev => prev === status ? '' : status)}
              sx={{ 
                color: statusFilter === status ? theme.palette.getContrastText(getStatusColor(status)) : getStatusColor(status),
                bgcolor: statusFilter === status ? getStatusColor(status) : 'transparent',
                borderColor: getStatusColor(status)
              }}
            />
          ))}
        </Box>
      </Box>
      
      <Divider />
      
      {/* Task list */}
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        {filteredTasks.length === 0 ? (
          <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
            <Typography variant="body2" color="textSecondary">
              No tasks found matching your filters
            </Typography>
          </Box>
        ) : (
          <List sx={{ width: '100%' }}>
            {filteredTasks.map((task, index) => {
              const agent = getAgentById(task.agentId);
              
              return (
                <React.Fragment key={task.id}>
                  <ListItem
                    alignItems="flex-start"
                    sx={{ 
                      cursor: 'pointer',
                      '&:hover': { bgcolor: alpha(theme.palette.primary.main, 0.05) },
                      bgcolor: selectedTaskId === task.id ? alpha(theme.palette.primary.main, 0.1) : 'transparent'
                    }}
                  >
                    <ListItemIcon>
                      {getStatusIcon(task.status)}
                    </ListItemIcon>
                    <ListItemText
                      primary={
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                          <Typography variant="subtitle1">
                            {task.title}
                          </Typography>
                          <Chip
                            label={task.priority}
                            size="small"
                            sx={{ 
                              bgcolor: alpha(getPriorityColor(task.priority), 0.1),
                              color: getPriorityColor(task.priority),
                              borderColor: getPriorityColor(task.priority),
                              fontWeight: 'medium'
                            }}
                            variant="outlined"
                          />
                        </Box>
                      }
                      secondary={
                        <React.Fragment>
                          <Typography variant="body2" color="textSecondary" component="span">
                            {task.description}
                          </Typography>
                          <Box sx={{ mt: 1, display: 'flex', gap: 1, flexWrap: 'wrap', alignItems: 'center' }}>
                            <Chip
                              label={`Assigned: ${agent?.name || 'Unknown'}`}
                              size="small"
                              variant="outlined"
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                            
                            <Chip
                              label={`Created: ${formatDate(task.createdAt)}`}
                              size="small"
                              variant="outlined"
                              sx={{ height: 20, fontSize: '0.7rem' }}
                            />
                            
                            {task.status === TaskStatus.IN_PROGRESS && task.progress !== undefined && (
                              <Chip
                                label={`Progress: ${task.progress}%`}
                                size="small"
                                variant="outlined"
                                sx={{ height: 20, fontSize: '0.7rem' }}
                              />
                            )}
                            
                            {task.completedAt && (
                              <Chip
                                label={`Completed: ${formatDate(task.completedAt)}`}
                                size="small"
                                variant="outlined"
                                sx={{ height: 20, fontSize: '0.7rem' }}
                              />
                            )}
                            
                            {task.dependencies && task.dependencies.length > 0 && (
                              <Chip
                                label={`Dependencies: ${task.dependencies.length}`}
                                size="small"
                                variant="outlined"
                                sx={{ height: 20, fontSize: '0.7rem' }}
                              />
                            )}
                          </Box>
                        </React.Fragment>
                      }
                    />
                    <ListItemSecondaryAction>
                      <IconButton 
                        edge="end" 
                        onClick={(e) => handleMenuOpen(e, task.id)}
                        size="small"
                      >
                        <MoreVertIcon />
                      </IconButton>
                    </ListItemSecondaryAction>
                  </ListItem>
                  {index < filteredTasks.length - 1 && <Divider variant="inset" component="li" />}
                </React.Fragment>
              );
            })}
          </List>
        )}
      </Box>
      
      {/* Task action menu */}
      <Menu
        anchorEl={menuAnchorEl}
        open={Boolean(menuAnchorEl)}
        onClose={handleMenuClose}
        MenuListProps={{
          'aria-labelledby': 'task-menu-button',
        }}
      >
        {selectedTask && (
          <>
            {selectedTask.status === TaskStatus.PENDING && (
              <MenuItem onClick={() => updateTaskStatus(selectedTask.id, TaskStatus.IN_PROGRESS)}>
                <ListItemIcon>
                  <PlayArrowIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText>Start Task</ListItemText>
              </MenuItem>
            )}
            
            {selectedTask.status === TaskStatus.IN_PROGRESS && (
              <MenuItem onClick={() => updateTaskStatus(selectedTask.id, TaskStatus.COMPLETED)}>
                <ListItemIcon>
                  <DoneIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText>Complete Task</ListItemText>
              </MenuItem>
            )}
            
            {selectedTask.status === TaskStatus.IN_PROGRESS && (
              <MenuItem onClick={() => updateTaskStatus(selectedTask.id, TaskStatus.PENDING)}>
                <ListItemIcon>
                  <PauseIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText>Pause Task</ListItemText>
              </MenuItem>
            )}
            
            {(selectedTask.status === TaskStatus.PENDING || selectedTask.status === TaskStatus.IN_PROGRESS) && (
              <MenuItem onClick={() => updateTaskStatus(selectedTask.id, TaskStatus.CANCELED)}>
                <ListItemIcon>
                  <CancelIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText>Cancel Task</ListItemText>
              </MenuItem>
            )}
            
            {selectedTask.status === TaskStatus.FAILED && (
              <MenuItem onClick={() => updateTaskStatus(selectedTask.id, TaskStatus.PENDING)}>
                <ListItemIcon>
                  <AssignmentLateIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText>Retry Task</ListItemText>
              </MenuItem>
            )}
            
            {selectedTask.status === TaskStatus.COMPLETED && (
              <MenuItem onClick={() => updateTaskStatus(selectedTask.id, TaskStatus.PENDING)}>
                <ListItemIcon>
                  <AssignmentTurnedInIcon fontSize="small" />
                </ListItemIcon>
                <ListItemText>Reopen Task</ListItemText>
              </MenuItem>
            )}
          </>
        )}
      </Menu>
    </Box>
  );
};

export default TaskQueuePanel;
