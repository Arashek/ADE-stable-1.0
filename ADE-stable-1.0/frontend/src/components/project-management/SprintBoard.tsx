import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Assignment as TaskIcon,
} from '@mui/icons-material';

interface Task {
  id: string;
  title: string;
  description: string;
  status: string;
  priority: string;
  assignee: string;
  estimated_hours: number;
  actual_hours: number;
  due_date: string;
  tags: string[];
}

interface Sprint {
  id: string;
  name: string;
  description: string;
  status: string;
  start_date: string;
  end_date: string;
  goals: string[];
  tasks: string[];
}

interface SprintBoardProps {
  sprint: Sprint;
  tasks: Task[];
  onUpdateTask: (taskId: string, updates: Partial<Task>) => void;
  onAddTask: (task: Omit<Task, 'id'>) => void;
  onDeleteTask: (taskId: string) => void;
}

const SprintBoard: React.FC<SprintBoardProps> = ({
  sprint,
  tasks,
  onUpdateTask,
  onAddTask,
  onDeleteTask,
}) => {
  const [openDialog, setOpenDialog] = useState(false);
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [formData, setFormData] = useState<Partial<Task>>({});

  const handleOpenDialog = (task?: Task) => {
    if (task) {
      setSelectedTask(task);
      setFormData(task);
    } else {
      setSelectedTask(null);
      setFormData({});
    }
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setSelectedTask(null);
    setFormData({});
  };

  const handleSubmit = () => {
    if (selectedTask) {
      onUpdateTask(selectedTask.id, formData);
    } else {
      onAddTask(formData as Omit<Task, 'id'>);
    }
    handleCloseDialog();
  };

  const handleDragStart = (e: React.DragEvent, taskId: string) => {
    e.dataTransfer.setData('taskId', taskId);
  };

  const handleDrop = (e: React.DragEvent, status: string) => {
    e.preventDefault();
    const taskId = e.dataTransfer.getData('taskId');
    onUpdateTask(taskId, { status });
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
  };

  const renderTaskCard = (task: Task) => (
    <Card key={task.id} sx={{ mb: 2 }}>
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start">
          <Typography variant="h6">{task.title}</Typography>
          <IconButton size="small" onClick={() => handleOpenDialog(task)}>
            <EditIcon />
          </IconButton>
        </Box>
        <Typography color="textSecondary" gutterBottom>
          {task.description}
        </Typography>
        <Box display="flex" gap={1} mb={2}>
          <Chip
            label={task.priority}
            color={
              task.priority === 'urgent'
                ? 'error'
                : task.priority === 'high'
                ? 'warning'
                : 'default'
            }
            size="small"
          />
          <Chip label={`${task.estimated_hours}h`} size="small" />
        </Box>
        <Typography variant="caption" color="textSecondary">
          Assigned to: {task.assignee}
        </Typography>
      </CardContent>
      <CardActions>
        <Button size="small" color="error" onClick={() => onDeleteTask(task.id)}>
          Delete
        </Button>
      </CardActions>
    </Card>
  );

  const renderColumn = (title: string, status: string) => {
    const columnTasks = tasks.filter((task) => task.status === status);
    return (
      <Grid item xs={12} md={4}>
        <Paper
          sx={{
            p: 2,
            height: '100%',
            minHeight: 500,
            backgroundColor: 'grey.50',
          }}
        >
          <Typography variant="h6" gutterBottom>
            {title} ({columnTasks.length})
          </Typography>
          <Box
            onDrop={(e) => handleDrop(e, status)}
            onDragOver={handleDragOver}
            sx={{ minHeight: 400 }}
          >
            {columnTasks.map((task) => (
              <div
                key={task.id}
                draggable
                onDragStart={(e) => handleDragStart(e, task.id)}
              >
                {renderTaskCard(task)}
              </div>
            ))}
          </Box>
        </Paper>
      </Grid>
    );
  };

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h5">{sprint.name}</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog()}
        >
          Add Task
        </Button>
      </Box>

      <Grid container spacing={2}>
        {renderColumn('To Do', 'todo')}
        {renderColumn('In Progress', 'in_progress')}
        {renderColumn('Review', 'review')}
        {renderColumn('Done', 'done')}
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {selectedTask ? 'Edit Task' : 'Create New Task'}
        </DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Title"
            margin="normal"
            value={formData.title || ''}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
          />
          <TextField
            fullWidth
            label="Description"
            margin="normal"
            multiline
            rows={4}
            value={formData.description || ''}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
          <FormControl fullWidth margin="normal">
            <InputLabel>Priority</InputLabel>
            <Select
              value={formData.priority || 'medium'}
              onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
            >
              <MenuItem value="low">Low</MenuItem>
              <MenuItem value="medium">Medium</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="urgent">Urgent</MenuItem>
            </Select>
          </FormControl>
          <TextField
            fullWidth
            label="Assignee"
            margin="normal"
            value={formData.assignee || ''}
            onChange={(e) => setFormData({ ...formData, assignee: e.target.value })}
          />
          <TextField
            fullWidth
            label="Estimated Hours"
            type="number"
            margin="normal"
            value={formData.estimated_hours || ''}
            onChange={(e) =>
              setFormData({ ...formData, estimated_hours: parseFloat(e.target.value) })
            }
          />
          <TextField
            fullWidth
            label="Due Date"
            type="date"
            margin="normal"
            InputLabelProps={{ shrink: true }}
            value={formData.due_date || ''}
            onChange={(e) => setFormData({ ...formData, due_date: e.target.value })}
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            {selectedTask ? 'Update' : 'Create'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default SprintBoard; 