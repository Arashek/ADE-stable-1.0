import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardActions,
  Button,
  IconButton,
  TextField,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Chip,
  LinearProgress,
  Menu,
  MenuItem,
  Alert,
  Drawer,
} from '@mui/material';
import {
  Add as AddIcon,
  MoreVert as MoreVertIcon,
  GitHub as GitHubIcon,
  Code as CodeIcon,
  Schedule as ScheduleIcon,
  Group as GroupIcon,
  Chat as ChatIcon,
} from '@mui/icons-material';
import UnifiedChat from '../components/shared/UnifiedChat';

interface Project {
  id: string;
  name: string;
  description: string;
  repository?: string;
  status: 'active' | 'completed' | 'archived';
  progress: number;
  language: string;
  teamSize: number;
  lastUpdated: string;
}

const Projects: React.FC = () => {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [openNewProject, setOpenNewProject] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);
  const [newProject, setNewProject] = useState({
    name: '',
    description: '',
    repository: '',
  });
  const [chatOpen, setChatOpen] = useState(false);
  const [selectedProjectForChat, setSelectedProjectForChat] = useState<Project | null>(null);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      // TODO: Fetch projects from API
      const mockData: Project[] = [
        {
          id: '1',
          name: 'ADE Platform',
          description: 'Autonomous Development Environment Platform',
          repository: 'org/ade-platform',
          status: 'active',
          progress: 65,
          language: 'TypeScript',
          teamSize: 4,
          lastUpdated: '2024-03-24',
        },
        {
          id: '2',
          name: 'Test Project',
          description: 'Test project for development',
          status: 'completed',
          progress: 100,
          language: 'Python',
          teamSize: 2,
          lastUpdated: '2024-03-23',
        },
      ];
      setProjects(mockData);
    } catch (err) {
      setError('Failed to fetch projects');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateProject = async () => {
    try {
      // TODO: Create project via API
      const project: Project = {
        id: Date.now().toString(),
        ...newProject,
        status: 'active',
        progress: 0,
        language: 'Unknown',
        teamSize: 1,
        lastUpdated: new Date().toISOString().split('T')[0],
      };
      setProjects((prev) => [...prev, project]);
      setOpenNewProject(false);
      setNewProject({ name: '', description: '', repository: '' });
    } catch (err) {
      setError('Failed to create project');
    }
  };

  const handleProjectAction = (action: string) => {
    if (!selectedProject) return;

    switch (action) {
      case 'archive':
        setProjects((prev) =>
          prev.map((p) =>
            p.id === selectedProject.id ? { ...p, status: 'archived' } : p
          )
        );
        break;
      case 'delete':
        setProjects((prev) => prev.filter((p) => p.id !== selectedProject.id));
        break;
    }
    setAnchorEl(null);
    setSelectedProject(null);
  };

  const getStatusColor = (status: Project['status']) => {
    switch (status) {
      case 'active':
        return 'success';
      case 'completed':
        return 'primary';
      case 'archived':
        return 'default';
    }
  };

  const handleChatOpen = (project: Project) => {
    setSelectedProjectForChat(project);
    setChatOpen(true);
  };

  const handleSendMessage = (message: string, threadId?: string) => {
    // TODO: Implement message sending to backend
    console.log('Sending message:', message, 'to thread:', threadId);
  };

  const handleCreateThread = (title: string, type: string) => {
    // TODO: Implement thread creation
    console.log('Creating thread:', title, 'of type:', type);
  };

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 4 }}>
        <Typography variant="h4">Projects</Typography>
        <Button
          variant="contained"
          startIcon={<AddIcon />}
          onClick={() => setOpenNewProject(true)}
        >
          New Project
        </Button>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={3}>
        {projects.map((project) => (
          <Grid item xs={12} md={6} lg={4} key={project.id}>
            <Card>
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
                  <Typography variant="h6" gutterBottom>
                    {project.name}
                  </Typography>
                  <IconButton
                    onClick={(e) => {
                      setAnchorEl(e.currentTarget);
                      setSelectedProject(project);
                    }}
                  >
                    <MoreVertIcon />
                  </IconButton>
                </Box>

                <Typography
                  variant="body2"
                  color="text.secondary"
                  sx={{ mb: 2, height: 40, overflow: 'hidden' }}
                >
                  {project.description}
                </Typography>

                <Box sx={{ mb: 2 }}>
                  <Chip
                    label={project.status}
                    color={getStatusColor(project.status)}
                    size="small"
                    sx={{ mr: 1 }}
                  />
                  <Chip
                    label={project.language}
                    variant="outlined"
                    size="small"
                  />
                </Box>

                <Box sx={{ mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">
                    Progress
                  </Typography>
                  <LinearProgress
                    variant="determinate"
                    value={project.progress}
                    sx={{ mt: 1 }}
                  />
                </Box>

                <Grid container spacing={2} sx={{ mt: 2 }}>
                  <Grid item xs={4}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <GitHubIcon fontSize="small" />
                      <Typography variant="body2">
                        {project.repository || 'No repo'}
                      </Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={4}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <GroupIcon fontSize="small" />
                      <Typography variant="body2">{project.teamSize}</Typography>
                    </Box>
                  </Grid>
                  <Grid item xs={4}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      <ScheduleIcon fontSize="small" />
                      <Typography variant="body2">{project.lastUpdated}</Typography>
                    </Box>
                  </Grid>
                </Grid>
              </CardContent>
              <CardActions>
                <Button size="small" startIcon={<CodeIcon />}>
                  Open IDE
                </Button>
                <Button size="small">View Details</Button>
                <Button
                  size="small"
                  startIcon={<ChatIcon />}
                  onClick={() => handleChatOpen(project)}
                >
                  Chat
                </Button>
              </CardActions>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Chat Drawer */}
      <Drawer
        anchor="right"
        open={chatOpen}
        onClose={() => setChatOpen(false)}
        sx={{
          '& .MuiDrawer-paper': {
            width: '40%',
            minWidth: 400,
          },
        }}
      >
        <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
          {selectedProjectForChat && (
            <>
              <Box sx={{ p: 2, borderBottom: 1, borderColor: 'divider' }}>
                <Typography variant="h6">{selectedProjectForChat.name}</Typography>
                <Typography variant="body2" color="text.secondary">
                  Project Chat
                </Typography>
              </Box>
              <Box sx={{ flex: 1 }}>
                <UnifiedChat
                  onSendMessage={handleSendMessage}
                  onCreateThread={handleCreateThread}
                  showThreads
                  currentAgent={{
                    id: 'project-assistant',
                    name: 'Project Assistant',
                    type: 'agent',
                    capabilities: ['code', 'planning', 'review'],
                  }}
                />
              </Box>
            </>
          )}
        </Box>
      </Drawer>

      {/* New Project Dialog */}
      <Dialog open={openNewProject} onClose={() => setOpenNewProject(false)}>
        <DialogTitle>Create New Project</DialogTitle>
        <DialogContent>
          <TextField
            fullWidth
            label="Project Name"
            value={newProject.name}
            onChange={(e) =>
              setNewProject((prev) => ({ ...prev, name: e.target.value }))
            }
            margin="normal"
            required
          />
          <TextField
            fullWidth
            label="Description"
            value={newProject.description}
            onChange={(e) =>
              setNewProject((prev) => ({ ...prev, description: e.target.value }))
            }
            margin="normal"
            multiline
            rows={3}
          />
          <TextField
            fullWidth
            label="GitHub Repository (optional)"
            value={newProject.repository}
            onChange={(e) =>
              setNewProject((prev) => ({ ...prev, repository: e.target.value }))
            }
            margin="normal"
            placeholder="org/repo-name"
          />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenNewProject(false)}>Cancel</Button>
          <Button
            variant="contained"
            onClick={handleCreateProject}
            disabled={!newProject.name}
          >
            Create Project
          </Button>
        </DialogActions>
      </Dialog>

      {/* Project Actions Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={() => {
          setAnchorEl(null);
          setSelectedProject(null);
        }}
      >
        <MenuItem onClick={() => handleProjectAction('archive')}>
          Archive Project
        </MenuItem>
        <MenuItem
          onClick={() => handleProjectAction('delete')}
          sx={{ color: 'error.main' }}
        >
          Delete Project
        </MenuItem>
      </Menu>
    </Container>
  );
};

export default Projects; 