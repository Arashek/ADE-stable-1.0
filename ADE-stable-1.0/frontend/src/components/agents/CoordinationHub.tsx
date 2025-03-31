import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Tabs,
  Tab,
  Button,
  Card,
  CardContent,
  CardActions,
  IconButton,
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
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  ListItemSecondaryAction,
  Switch,
  Slider,
  FormControlLabel,
  Accordion,
  AccordionSummary,
  AccordionDetails,
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Save as SaveIcon,
  Share as ShareIcon,
  Timeline as TimelineIcon,
  Settings as SettingsIcon,
  Code as CodeIcon,
  BugReport as BugIcon,
  Description as DocIcon,
  RateReview as ReviewIcon,
  Assignment as TaskIcon,
  ExpandMore as ExpandMoreIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  Speed as SpeedIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Cloud as CloudIcon,
  Devices as DevicesIcon,
  Psychology as AIIcon,
} from '@mui/icons-material';

interface CoordinationHubProps {
  projectId: string;
}

interface FlowTemplate {
  id: string;
  name: string;
  description: string;
  context: string[];
  steps: FlowStep[];
  priority: 'high' | 'medium' | 'low';
  performance: {
    successRate: number;
    avgCompletionTime: number;
    resourceUsage: number;
  };
  tags: string[];
  isCustom: boolean;
}

interface FlowStep {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  agentType: string;
  dependencies: string[];
  estimatedTime: number;
  resources: string[];
  validationRules: string[];
  results?: any;
  error?: string;
  startTime?: string;
  endTime?: string;
}

const CoordinationHub: React.FC<CoordinationHubProps> = ({ projectId }) => {
  const [activeTab, setActiveTab] = useState(0);
  const [templates, setTemplates] = useState<FlowTemplate[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [openTemplateDialog, setOpenTemplateDialog] = useState(false);
  const [selectedTemplate, setSelectedTemplate] = useState<FlowTemplate | null>(null);
  const [expandedTemplate, setExpandedTemplate] = useState<string | false>(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterContext, setFilterContext] = useState<string[]>([]);
  const [sortBy, setSortBy] = useState<'name' | 'priority' | 'performance'>('name');

  // Predefined templates for different contexts
  const predefinedTemplates: FlowTemplate[] = [
    {
      id: 'web_dev',
      name: 'Web Development Flow',
      description: 'Standard web application development workflow',
      context: ['web', 'frontend', 'fullstack'],
      steps: [
        {
          id: 'planning',
          title: 'Project Planning',
          description: 'Define requirements and architecture',
          status: 'pending',
          agentType: 'task_planner',
          dependencies: [],
          estimatedTime: 2,
          resources: ['task_planner', 'documentation'],
          validationRules: ['requirements_complete', 'architecture_valid'],
        },
        // ... other steps
      ],
      priority: 'high',
      performance: {
        successRate: 95,
        avgCompletionTime: 24,
        resourceUsage: 85,
      },
      tags: ['web', 'frontend', 'backend', 'fullstack'],
      isCustom: false,
    },
    // ... other predefined templates
  ];

  useEffect(() => {
    // Load templates from API
    const loadTemplates = async () => {
      try {
        setLoading(true);
        const response = await fetch(`/api/coordination/templates?projectId=${projectId}`);
        if (response.ok) {
          const data = await response.json();
          setTemplates([...predefinedTemplates, ...data]);
        } else {
          throw new Error('Failed to load templates');
        }
      } catch (err) {
        setError('Failed to load templates');
      } finally {
        setLoading(false);
      }
    };

    loadTemplates();
  }, [projectId]);

  const handleCreateTemplate = async (template: FlowTemplate) => {
    try {
      const response = await fetch('/api/coordination/templates', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ ...template, projectId }),
      });

      if (response.ok) {
        const newTemplate = await response.json();
        setTemplates(prev => [...prev, newTemplate]);
      } else {
        throw new Error('Failed to create template');
      }
    } catch (err) {
      setError('Failed to create template');
    }
  };

  const handleUpdateTemplate = async (template: FlowTemplate) => {
    try {
      const response = await fetch(`/api/coordination/templates/${template.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(template),
      });

      if (response.ok) {
        const updatedTemplate = await response.json();
        setTemplates(prev => prev.map(t =>
          t.id === template.id ? updatedTemplate : t
        ));
      } else {
        throw new Error('Failed to update template');
      }
    } catch (err) {
      setError('Failed to update template');
    }
  };

  const handleDeleteTemplate = async (templateId: string) => {
    try {
      const response = await fetch(`/api/coordination/templates/${templateId}`, {
        method: 'DELETE',
      });

      if (response.ok) {
        setTemplates(prev => prev.filter(t => t.id !== templateId));
      } else {
        throw new Error('Failed to delete template');
      }
    } catch (err) {
      setError('Failed to delete template');
    }
  };

  const filteredTemplates = templates.filter(template => {
    const matchesSearch = template.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                         template.description.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesContext = filterContext.length === 0 || 
                          filterContext.some(context => template.context.includes(context));
    return matchesSearch && matchesContext;
  });

  const sortedTemplates = [...filteredTemplates].sort((a, b) => {
    switch (sortBy) {
      case 'priority':
        return b.priority.localeCompare(a.priority);
      case 'performance':
        return b.performance.successRate - a.performance.successRate;
      default:
        return a.name.localeCompare(b.name);
    }
  });

  const renderTemplateCard = (template: FlowTemplate) => (
    <Card key={template.id} sx={{ mb: 2 }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Typography variant="h6">{template.name}</Typography>
          <Box>
            <Tooltip title="Edit Template">
              <IconButton onClick={() => {
                setSelectedTemplate(template);
                setOpenTemplateDialog(true);
              }}>
                <EditIcon />
              </IconButton>
            </Tooltip>
            <Tooltip title="Delete Template">
              <IconButton onClick={() => handleDeleteTemplate(template.id)}>
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          </Box>
        </Box>
        <Typography variant="body2" color="text.secondary" paragraph>
          {template.description}
        </Typography>
        <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
          {template.tags.map(tag => (
            <Chip key={tag} label={tag} size="small" />
          ))}
        </Box>
        <Box sx={{ display: 'flex', gap: 2 }}>
          <Chip
            icon={<CheckCircleIcon />}
            label={`${template.performance.successRate}% Success`}
            color="success"
            size="small"
          />
          <Chip
            icon={<TimelineIcon />}
            label={`${template.performance.avgCompletionTime}h Avg`}
            color="primary"
            size="small"
          />
          <Chip
            icon={<SpeedIcon />}
            label={`${template.performance.resourceUsage}% Resources`}
            color="warning"
            size="small"
          />
        </Box>
      </CardContent>
      <CardActions>
        <Button
          startIcon={<PlayIcon />}
          variant="contained"
          color="primary"
          onClick={() => {/* Start flow */}}
        >
          Start Flow
        </Button>
        <Button
          startIcon={<ShareIcon />}
          variant="outlined"
          onClick={() => {/* Share template */}}
        >
          Share
        </Button>
      </CardActions>
    </Card>
  );

  if (loading) {
    return <LinearProgress />;
  }

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">Coordination Hub</Typography>
            <Button
              variant="contained"
              startIcon={<AddIcon />}
              onClick={() => {
                setSelectedTemplate(null);
                setOpenTemplateDialog(true);
              }}
            >
              Create Template
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

        {/* Filters and Search */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Grid container spacing={2} alignItems="center">
              <Grid item xs={12} md={4}>
                <TextField
                  fullWidth
                  label="Search Templates"
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                />
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Filter by Context</InputLabel>
                  <Select
                    multiple
                    value={filterContext}
                    onChange={(e) => setFilterContext(typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value)}
                    label="Filter by Context"
                  >
                    <MenuItem value="web">Web</MenuItem>
                    <MenuItem value="mobile">Mobile</MenuItem>
                    <MenuItem value="desktop">Desktop</MenuItem>
                    <MenuItem value="backend">Backend</MenuItem>
                    <MenuItem value="frontend">Frontend</MenuItem>
                    <MenuItem value="fullstack">Fullstack</MenuItem>
                    <MenuItem value="ai">AI/ML</MenuItem>
                    <MenuItem value="iot">IoT</MenuItem>
                    <MenuItem value="embedded">Embedded</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
              <Grid item xs={12} md={4}>
                <FormControl fullWidth>
                  <InputLabel>Sort By</InputLabel>
                  <Select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as 'name' | 'priority' | 'performance')}
                    label="Sort By"
                  >
                    <MenuItem value="name">Name</MenuItem>
                    <MenuItem value="priority">Priority</MenuItem>
                    <MenuItem value="performance">Performance</MenuItem>
                  </Select>
                </FormControl>
              </Grid>
            </Grid>
          </Paper>
        </Grid>

        {/* Templates Grid */}
        <Grid item xs={12}>
          <Grid container spacing={2}>
            {sortedTemplates.map(template => (
              <Grid item xs={12} md={6} lg={4} key={template.id}>
                {renderTemplateCard(template)}
              </Grid>
            ))}
          </Grid>
        </Grid>
      </Grid>

      {/* Template Dialog */}
      <Dialog
        open={openTemplateDialog}
        onClose={() => setOpenTemplateDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          {selectedTemplate ? 'Edit Template' : 'Create New Template'}
        </DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <TextField
                fullWidth
                label="Template Name"
                value={selectedTemplate?.name || ''}
                onChange={(e) => setSelectedTemplate(prev => prev ? { ...prev, name: e.target.value } : null)}
              />
            </Grid>
            <Grid item xs={12}>
              <TextField
                fullWidth
                multiline
                rows={3}
                label="Description"
                value={selectedTemplate?.description || ''}
                onChange={(e) => setSelectedTemplate(prev => prev ? { ...prev, description: e.target.value } : null)}
              />
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Context</InputLabel>
                <Select
                  multiple
                  value={selectedTemplate?.context || []}
                  onChange={(e) => setSelectedTemplate(prev => prev ? { ...prev, context: typeof e.target.value === 'string' ? e.target.value.split(',') : e.target.value } : null)}
                  label="Context"
                >
                  <MenuItem value="web">Web</MenuItem>
                  <MenuItem value="mobile">Mobile</MenuItem>
                  <MenuItem value="desktop">Desktop</MenuItem>
                  <MenuItem value="backend">Backend</MenuItem>
                  <MenuItem value="frontend">Frontend</MenuItem>
                  <MenuItem value="fullstack">Fullstack</MenuItem>
                  <MenuItem value="ai">AI/ML</MenuItem>
                  <MenuItem value="iot">IoT</MenuItem>
                  <MenuItem value="embedded">Embedded</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Priority</InputLabel>
                <Select
                  value={selectedTemplate?.priority || 'medium'}
                  onChange={(e) => setSelectedTemplate(prev => prev ? { ...prev, priority: e.target.value as 'high' | 'medium' | 'low' } : null)}
                  label="Priority"
                >
                  <MenuItem value="high">High</MenuItem>
                  <MenuItem value="medium">Medium</MenuItem>
                  <MenuItem value="low">Low</MenuItem>
                </Select>
              </FormControl>
            </Grid>
            {/* Add more fields for template customization */}
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenTemplateDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            startIcon={<SaveIcon />}
            onClick={() => {
              if (selectedTemplate) {
                handleUpdateTemplate(selectedTemplate);
              } else {
                handleCreateTemplate(selectedTemplate as FlowTemplate);
              }
              setOpenTemplateDialog(false);
            }}
          >
            Save
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CoordinationHub; 