import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemSecondaryAction,
  IconButton,
  Divider,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Assignment as TaskIcon,
  Timeline as SprintIcon,
  Assessment as MetricsIcon,
} from '@mui/icons-material';
import { useAuth } from '../../hooks/useAuth';
import { api } from '../../services/api';

interface Project {
  id: string;
  name: string;
  description: string;
  status: string;
  tasks: Task[];
  sprints: Sprint[];
  metrics: ProjectMetrics;
}

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

interface ProjectMetrics {
  total_tasks: number;
  completed_tasks: number;
  total_sprints: number;
  completed_sprints: number;
  total_story_points: number;
  completed_story_points: number;
  average_velocity: number;
}

const ProjectDashboard: React.FC = () => {
  const { user } = useAuth();
  const [projects, setProjects] = useState<Project[]>([]);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [openDialog, setOpenDialog] = useState(false);
  const [dialogType, setDialogType] = useState<'project' | 'task' | 'sprint'>('project');
  const [formData, setFormData] = useState<any>({});

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      const response = await api.get('/api/project-management/projects');
      setProjects(response.data);
    } catch (error) {
      console.error('Error fetching projects:', error);
    }
  };

  const handleOpenDialog = (type: 'project' | 'task' | 'sprint') => {
    setDialogType(type);
    setOpenDialog(true);
  };

  const handleCloseDialog = () => {
    setOpenDialog(false);
    setFormData({});
  };

  const handleSubmit = async () => {
    try {
      if (dialogType === 'project') {
        await api.post('/api/project-management/projects', formData);
      } else if (dialogType === 'task' && selectedProject) {
        await api.post(`/api/project-management/projects/${selectedProject.id}/tasks`, formData);
      } else if (dialogType === 'sprint' && selectedProject) {
        await api.post(`/api/project-management/projects/${selectedProject.id}/sprints`, formData);
      }
      handleCloseDialog();
      fetchProjects();
    } catch (error) {
      console.error('Error submitting form:', error);
    }
  };

  const renderProjectCard = (project: Project) => (
    <Paper key={project.id} sx={{ p: 2, mb: 2 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center">
        <Typography variant="h6">{project.name}</Typography>
        <Box>
          <IconButton onClick={() => setSelectedProject(project)}>
            <EditIcon />
          </IconButton>
          <IconButton>
            <DeleteIcon />
          </IconButton>
        </Box>
      </Box>
      <Typography color="textSecondary">{project.description}</Typography>
      <Box mt={2}>
        <Chip label={project.status} color="primary" size="small" />
      </Box>
      <Box mt={2} display="flex" gap={1}>
        <Button
          startIcon={<TaskIcon />}
          size="small"
          onClick={() => {
            setSelectedProject(project);
            handleOpenDialog('task');
          }}
        >
          Tasks
        </Button>
        <Button
          startIcon={<SprintIcon />}
          size="small"
          onClick={() => {
            setSelectedProject(project);
            handleOpenDialog('sprint');
          }}
        >
          Sprints
        </Button>
        <Button
          startIcon={<MetricsIcon />}
          size="small"
          onClick={() => {
            setSelectedProject(project);
            // Show metrics dialog
          }}
        >
          Metrics
        </Button>
      </Box>
    </Paper>
  );

  const renderDialogContent = () => {
    switch (dialogType) {
      case 'project':
        return (
          <>
            <TextField
              fullWidth
              label="Project Name"
              margin="normal"
              value={formData.name || ''}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
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
          </>
        );
      case 'task':
        return (
          <>
            <TextField
              fullWidth
              label="Task Title"
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
              label="Estimated Hours"
              type="number"
              margin="normal"
              value={formData.estimated_hours || ''}
              onChange={(e) => setFormData({ ...formData, estimated_hours: parseFloat(e.target.value) })}
            />
          </>
        );
      case 'sprint':
        return (
          <>
            <TextField
              fullWidth
              label="Sprint Name"
              margin="normal"
              value={formData.name || ''}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
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
            <TextField
              fullWidth
              label="Start Date"
              type="date"
              margin="normal"
              InputLabelProps={{ shrink: true }}
              value={formData.start_date || ''}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
            />
            <TextField
              fullWidth
              label="End Date"
              type="date"
              margin="normal"
              InputLabelProps={{ shrink: true }}
              value={formData.end_date || ''}
              onChange={(e) => setFormData({ ...formData, end_date: e.target.value })}
            />
          </>
        );
      default:
        return null;
    }
  };

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
        <Typography variant="h4">Project Management</Typography>
        <Button
          variant="contained"
          color="primary"
          startIcon={<AddIcon />}
          onClick={() => handleOpenDialog('project')}
        >
          New Project
        </Button>
      </Box>

      <Grid container spacing={3}>
        <Grid item xs={12}>
          {projects.map(renderProjectCard)}
        </Grid>
      </Grid>

      <Dialog open={openDialog} onClose={handleCloseDialog} maxWidth="sm" fullWidth>
        <DialogTitle>
          {dialogType === 'project' && 'Create New Project'}
          {dialogType === 'task' && 'Create New Task'}
          {dialogType === 'sprint' && 'Create New Sprint'}
        </DialogTitle>
        <DialogContent>
          {renderDialogContent()}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleCloseDialog}>Cancel</Button>
          <Button onClick={handleSubmit} variant="contained" color="primary">
            Create
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default ProjectDashboard; 