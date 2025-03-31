import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Grid,
  Paper,
  Typography,
  CircularProgress,
  Button,
  TextField,
  Card,
  CardContent,
} from '@mui/material';
import { ProjectStatus, AgentActivity, CodeMetrics } from '../types';
import { useProject } from '../hooks/useProject';
import { MetricsChart } from './MetricsChart';
import { AgentList } from './AgentList';
import { CodeEditor } from './CodeEditor';

interface ProjectDashboardProps {
  projectId: string;
}

export const ProjectDashboard: React.FC<ProjectDashboardProps> = ({ projectId }) => {
  const { project, metrics, agents, loading, error } = useProject(projectId);
  const [selectedFile, setSelectedFile] = useState<string | null>(null);

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="80vh">
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  return (
    <Container maxWidth="xl">
      <Grid container spacing={3}>
        {/* Project Overview */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Typography variant="h4">{project.name}</Typography>
            <Typography variant="body1" color="textSecondary">
              Status: {project.status}
            </Typography>
          </Paper>
        </Grid>

        {/* Agent Activities */}
        <Grid item xs={12} md={4}>
          <Paper sx={{ p: 2, height: '100%' }}>
            <Typography variant="h6" gutterBottom>
              Active Agents
            </Typography>
            <AgentList agents={agents} />
          </Paper>
        </Grid>

        {/* Code Metrics */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Code Metrics
            </Typography>
            <MetricsChart metrics={metrics} />
          </Paper>
        </Grid>

        {/* Code Editor */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Code Editor
            </Typography>
            <CodeEditor
              file={selectedFile}
              onFileChange={setSelectedFile}
              projectFiles={project.files}
            />
          </Paper>
        </Grid>

        {/* Agent Controls */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>
              Agent Controls
            </Typography>
            <Grid container spacing={2}>
              <Grid item>
                <Button
                  variant="contained"
                  color="primary"
                  onClick={() => {/* Implement agent control */}}
                >
                  Generate Code
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="contained"
                  color="secondary"
                  onClick={() => {/* Implement test generation */}}
                >
                  Generate Tests
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="contained"
                  color="info"
                  onClick={() => {/* Implement code review */}}
                >
                  Review Code
                </Button>
              </Grid>
              <Grid item>
                <Button
                  variant="contained"
                  color="success"
                  onClick={() => {/* Implement deployment */}}
                >
                  Deploy
                </Button>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
};
