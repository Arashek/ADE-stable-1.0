import React, { useState } from 'react';
import {
  Grid,
  Typography,
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
  Code as CodeIcon,
  Terminal as TerminalIcon,
  Build as BuildIcon,
  BugReport as BugIcon,
  Description as DocIcon,
} from '@mui/icons-material';
import Card from '../common/Card';
import Button from '../common/Button';
import { dashboardService } from '../../services/dashboardService';

interface DialogState {
  open: boolean;
  type: 'project' | 'codeReview' | 'terminal' | 'build' | 'bug' | 'documentation';
}

const QuickActions: React.FC = () => {
  const [dialog, setDialog] = useState<DialogState>({ open: false, type: 'project' });
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    repositoryUrl: '',
    prNumber: '',
    environment: 'development',
    severity: 'medium',
    docType: 'api',
    docFormat: 'markdown',
  });

  const handleClose = () => {
    setDialog({ ...dialog, open: false });
    setFormData({
      name: '',
      description: '',
      repositoryUrl: '',
      prNumber: '',
      environment: 'development',
      severity: 'medium',
      docType: 'api',
      docFormat: 'markdown',
    });
  };

  const handleSubmit = async () => {
    try {
      switch (dialog.type) {
        case 'project':
          await dashboardService.createProject({
            name: formData.name,
            description: formData.description,
            status: 'active',
            progress: 0,
            lastUpdated: new Date().toISOString(),
            tasksCompleted: 0,
            totalTasks: 0,
          });
          break;
        case 'codeReview':
          await dashboardService.startCodeReview(
            formData.repositoryUrl,
            formData.prNumber ? parseInt(formData.prNumber) : undefined
          );
          break;
        case 'terminal':
          await dashboardService.openTerminal(formData.name);
          break;
        case 'build':
          await dashboardService.startBuild(
            formData.name,
            formData.environment as 'development' | 'staging' | 'production'
          );
          break;
        case 'bug':
          await dashboardService.reportBug({
            title: formData.name,
            description: formData.description,
            severity: formData.severity as 'low' | 'medium' | 'high',
            reproducible: true,
          });
          break;
        case 'documentation':
          await dashboardService.generateDocumentation(formData.name, {
            type: formData.docType as 'api' | 'code' | 'user',
            format: formData.docFormat as 'markdown' | 'html' | 'pdf',
          });
          break;
      }
      handleClose();
    } catch (error) {
      console.error('Failed to execute action:', error);
    }
  };

  const actions = [
    {
      id: 'new-project',
      label: 'New Project',
      icon: <AddIcon />,
      color: 'primary',
      onClick: () => setDialog({ open: true, type: 'project' }),
    },
    {
      id: 'code-review',
      label: 'Code Review',
      icon: <CodeIcon />,
      color: 'secondary',
      onClick: () => setDialog({ open: true, type: 'codeReview' }),
    },
    {
      id: 'terminal',
      label: 'Terminal',
      icon: <TerminalIcon />,
      color: 'success',
      onClick: () => setDialog({ open: true, type: 'terminal' }),
    },
    {
      id: 'build',
      label: 'Build',
      icon: <BuildIcon />,
      color: 'warning',
      onClick: () => setDialog({ open: true, type: 'build' }),
    },
    {
      id: 'report-bug',
      label: 'Report Bug',
      icon: <BugIcon />,
      color: 'error',
      onClick: () => setDialog({ open: true, type: 'bug' }),
    },
    {
      id: 'documentation',
      label: 'Documentation',
      icon: <DocIcon />,
      color: 'primary',
      onClick: () => setDialog({ open: true, type: 'documentation' }),
    },
  ] as const;

  const renderDialogContent = () => {
    switch (dialog.type) {
      case 'project':
        return (
          <>
            <TextField
              fullWidth
              label="Project Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              margin="normal"
              multiline
              rows={3}
            />
          </>
        );
      case 'codeReview':
        return (
          <>
            <TextField
              fullWidth
              label="Repository URL"
              value={formData.repositoryUrl}
              onChange={(e) => setFormData({ ...formData, repositoryUrl: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label="PR Number (optional)"
              value={formData.prNumber}
              onChange={(e) => setFormData({ ...formData, prNumber: e.target.value })}
              margin="normal"
              type="number"
            />
          </>
        );
      case 'terminal':
      case 'build':
        return (
          <>
            <TextField
              fullWidth
              label="Project Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              margin="normal"
            />
            {dialog.type === 'build' && (
              <FormControl fullWidth margin="normal">
                <InputLabel>Environment</InputLabel>
                <Select
                  value={formData.environment}
                  onChange={(e) => setFormData({ ...formData, environment: e.target.value })}
                >
                  <MenuItem value="development">Development</MenuItem>
                  <MenuItem value="staging">Staging</MenuItem>
                  <MenuItem value="production">Production</MenuItem>
                </Select>
              </FormControl>
            )}
          </>
        );
      case 'bug':
        return (
          <>
            <TextField
              fullWidth
              label="Bug Title"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              margin="normal"
            />
            <TextField
              fullWidth
              label="Description"
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              margin="normal"
              multiline
              rows={3}
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Severity</InputLabel>
              <Select
                value={formData.severity}
                onChange={(e) => setFormData({ ...formData, severity: e.target.value })}
              >
                <MenuItem value="low">Low</MenuItem>
                <MenuItem value="medium">Medium</MenuItem>
                <MenuItem value="high">High</MenuItem>
              </Select>
            </FormControl>
          </>
        );
      case 'documentation':
        return (
          <>
            <TextField
              fullWidth
              label="Project Name"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              margin="normal"
            />
            <FormControl fullWidth margin="normal">
              <InputLabel>Documentation Type</InputLabel>
              <Select
                value={formData.docType}
                onChange={(e) => setFormData({ ...formData, docType: e.target.value })}
              >
                <MenuItem value="api">API Documentation</MenuItem>
                <MenuItem value="code">Code Documentation</MenuItem>
                <MenuItem value="user">User Guide</MenuItem>
              </Select>
            </FormControl>
            <FormControl fullWidth margin="normal">
              <InputLabel>Format</InputLabel>
              <Select
                value={formData.docFormat}
                onChange={(e) => setFormData({ ...formData, docFormat: e.target.value })}
              >
                <MenuItem value="markdown">Markdown</MenuItem>
                <MenuItem value="html">HTML</MenuItem>
                <MenuItem value="pdf">PDF</MenuItem>
              </Select>
            </FormControl>
          </>
        );
      default:
        return null;
    }
  };

  return (
    <>
      <Card title="Quick Actions" subtitle="Common development tasks">
        <Grid container spacing={2}>
          {actions.map((action) => (
            <Grid item xs={6} key={action.id}>
              <Button
                variant="outline"
                color={action.color}
                onClick={action.onClick}
                startIcon={action.icon}
                fullWidth
                sx={{
                  justifyContent: 'flex-start',
                  py: 1.5,
                  px: 2,
                  borderRadius: 2,
                  '& .MuiButton-startIcon': {
                    mr: 1.5,
                  },
                }}
              >
                <Typography
                  variant="body2"
                  sx={{
                    fontWeight: 500,
                    textAlign: 'left',
                    lineHeight: 1.2,
                  }}
                >
                  {action.label}
                </Typography>
              </Button>
            </Grid>
          ))}
        </Grid>
      </Card>

      <Dialog open={dialog.open} onClose={handleClose} maxWidth="sm" fullWidth>
        <DialogTitle>
          {actions.find((a) => a.id === `${dialog.type}`)?.label || 'Action'}
        </DialogTitle>
        <DialogContent>{renderDialogContent()}</DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="inherit">
            Cancel
          </Button>
          <Button onClick={handleSubmit} color="primary" variant="contained">
            Submit
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
};

export default QuickActions; 