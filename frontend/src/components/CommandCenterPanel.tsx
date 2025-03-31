import React from 'react';
import {
  Box,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Paper,
  Divider,
  LinearProgress,
  Chip
} from '@mui/material';
import {
  PlayArrow as StartIcon,
  Pause as PauseIcon,
  Check as CompleteIcon,
  Delete as DeleteIcon,
  Error as FailIcon
} from '@mui/icons-material';
import { Task, TaskUpdate } from '../hooks/useCommandCenter';

interface CommandCenterPanelProps {
  tasks: Task[];
  onTaskUpdate: (taskId: string, update: TaskUpdate) => void;
}

const getStatusColor = (status: Task['status']) => {
  switch (status) {
    case 'completed':
      return 'success';
    case 'failed':
      return 'error';
    case 'in_progress':
      return 'primary';
    default:
      return 'default';
  }
};

const getPriorityColor = (priority: Task['priority']) => {
  switch (priority) {
    case 'high':
      return 'error';
    case 'medium':
      return 'warning';
    default:
      return 'default';
  }
};

export const CommandCenterPanel: React.FC<CommandCenterPanelProps> = ({
  tasks,
  onTaskUpdate
}) => {
  return (
    <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
      <Typography variant="h6" gutterBottom>
        Command Center
      </Typography>
      <List>
        {tasks.map((task) => (
          <React.Fragment key={task.id}>
            <ListItem>
              <ListItemText
                primary={
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Typography variant="subtitle2">
                      {task.title}
                    </Typography>
                    <Chip
                      label={task.status}
                      size="small"
                      color={getStatusColor(task.status)}
                    />
                    <Chip
                      label={task.priority}
                      size="small"
                      color={getPriorityColor(task.priority)}
                    />
                  </Box>
                }
                secondary={
                  <Box sx={{ mt: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      {task.assignedAgent ? `Assigned to: ${task.assignedAgent}` : 'Unassigned'}
                    </Typography>
                    <LinearProgress
                      variant="determinate"
                      value={task.progress}
                      sx={{ mt: 1 }}
                    />
                  </Box>
                }
              />
              <ListItemSecondaryAction>
                {task.status === 'pending' && (
                  <IconButton
                    edge="end"
                    onClick={() => onTaskUpdate(task.id, { status: 'in_progress' })}
                  >
                    <StartIcon />
                  </IconButton>
                )}
                {task.status === 'in_progress' && (
                  <>
                    <IconButton
                      edge="end"
                      onClick={() => onTaskUpdate(task.id, { status: 'completed' })}
                    >
                      <CompleteIcon />
                    </IconButton>
                    <IconButton
                      edge="end"
                      onClick={() => onTaskUpdate(task.id, { status: 'failed' })}
                    >
                      <FailIcon />
                    </IconButton>
                  </>
                )}
              </ListItemSecondaryAction>
            </ListItem>
            <Divider />
          </React.Fragment>
        ))}
      </List>
    </Paper>
  );
}; 