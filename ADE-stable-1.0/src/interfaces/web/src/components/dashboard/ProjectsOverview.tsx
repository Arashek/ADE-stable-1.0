import React from 'react';
import { useQuery, useQueryClient } from '@tanstack/react-query';
import {
  Box,
  Grid,
  Typography,
  CircularProgress,
  Alert,
  LinearProgress,
  Chip,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  MoreVert as MoreIcon,
  CheckCircle as CheckCircleIcon,
  Warning as WarningIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';
import Card from '../common/Card';
import { dashboardService } from '../../services/dashboardService';
import { useWebSocket } from '../../hooks/useWebSocket';

export interface Project {
  id: string;
  name: string;
  description: string;
  status: 'active' | 'paused' | 'completed' | 'failed';
  progress: number;
  lastUpdated: string;
  tasksCompleted: number;
  totalTasks: number;
}

const mockProjects: Project[] = [
  {
    id: '1',
    name: 'ADE Platform',
    description: 'Main development platform',
    status: 'active',
    progress: 75,
    lastUpdated: '2024-03-20T10:30:00Z',
    tasksCompleted: 15,
    totalTasks: 20,
  },
  {
    id: '2',
    name: 'API Integration',
    description: 'External services integration',
    status: 'active',
    progress: 45,
    lastUpdated: '2024-03-20T09:45:00Z',
    tasksCompleted: 9,
    totalTasks: 20,
  },
  {
    id: '3',
    name: 'Documentation',
    description: 'Platform documentation',
    status: 'paused',
    progress: 30,
    lastUpdated: '2024-03-20T08:15:00Z',
    tasksCompleted: 3,
    totalTasks: 10,
  },
];

const getStatusIcon = (status: Project['status']) => {
  switch (status) {
    case 'completed':
      return <CheckCircleIcon color="success" />;
    case 'active':
      return <CheckCircleIcon color="primary" />;
    case 'paused':
      return <WarningIcon color="warning" />;
    case 'failed':
      return <ErrorIcon color="error" />;
    default:
      return null;
  }
};

const getStatusColor = (status: Project['status']) => {
  switch (status) {
    case 'completed':
      return 'success';
    case 'active':
      return 'primary';
    case 'paused':
      return 'warning';
    case 'failed':
      return 'error';
    default:
      return 'default';
  }
};

const ProjectCard: React.FC<{ project: Project }> = ({ project }) => {
  const queryClient = useQueryClient();

  const handleStatusChange = async (newStatus: Project['status']) => {
    try {
      await dashboardService.updateProjectStatus(project.id, newStatus);
      queryClient.invalidateQueries({ queryKey: ['projects'] });
    } catch (error) {
      console.error('Failed to update project status:', error);
    }
  };

  return (
    <Card>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
        <Box>
          <Typography variant="h6" gutterBottom>
            {project.name}
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {project.description}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', alignItems: 'start', gap: 1 }}>
          <Chip
            size="small"
            label={project.status}
            color={getStatusColor(project.status)}
            icon={getStatusIcon(project.status)}
          />
          <Tooltip title="More actions">
            <IconButton size="small">
              <MoreIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
          <Typography variant="body2" color="text.secondary">
            Progress
          </Typography>
          <Typography variant="body2" color="text.secondary">
            {project.progress}%
          </Typography>
        </Box>
        <LinearProgress
          variant="determinate"
          value={project.progress}
          sx={{ height: 8, borderRadius: 4 }}
        />
      </Box>

      <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
        <Typography variant="caption" color="text.secondary">
          Tasks: {project.tasksCompleted}/{project.totalTasks}
        </Typography>
        <Typography variant="caption" color="text.secondary">
          Updated: {new Date(project.lastUpdated).toLocaleString()}
        </Typography>
      </Box>
    </Card>
  );
};

const ProjectsOverview: React.FC = () => {
  // Add WebSocket subscription
  useWebSocket('project');

  const { data: projects, isLoading, error } = useQuery<Project[]>({
    queryKey: ['projects'],
    queryFn: dashboardService.getProjects,
  });

  if (isLoading) {
    return (
      <Card title="Projects Overview">
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 3 }}>
          <CircularProgress />
        </Box>
      </Card>
    );
  }

  if (error) {
    return (
      <Card title="Projects Overview">
        <Alert severity="error">Failed to load projects</Alert>
      </Card>
    );
  }

  return (
    <Card
      title="Projects Overview"
      subtitle="Status of active development projects"
    >
      <Grid container spacing={3}>
        {projects?.map((project) => (
          <Grid item xs={12} md={6} lg={4} key={project.id}>
            <ProjectCard project={project} />
          </Grid>
        ))}
      </Grid>
    </Card>
  );
};

export default ProjectsOverview; 