import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Paper,
  Typography,
  Card,
  CardContent,
  LinearProgress,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Alert,
  Tabs,
  Tab,
} from '@mui/material';
import {
  Code as CodeIcon,
  Storage as StorageIcon,
  Group as GroupIcon,
  Timeline as TimelineIcon,
  BugReport as BugIcon,
  Build as BuildIcon,
} from '@mui/icons-material';

const ProjectDashboard = ({ projectId }) => {
  const [project, setProject] = useState(null);
  const [usage, setUsage] = useState({});
  const [team, setTeam] = useState([]);
  const [deployments, setDeployments] = useState([]);
  const [issues, setIssues] = useState([]);
  const [activeTab, setActiveTab] = useState(0);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchProjectData();
  }, [projectId]);

  const fetchProjectData = async () => {
    try {
      const [projectData, usageData, teamData, deploymentsData, issuesData] = await Promise.all([
        fetch(`/api/projects/${projectId}`),
        fetch(`/api/projects/${projectId}/usage`),
        fetch(`/api/projects/${projectId}/team`),
        fetch(`/api/projects/${projectId}/deployments`),
        fetch(`/api/projects/${projectId}/issues`),
      ]);

      const project = await projectData.json();
      const usage = await usageData.json();
      const team = await teamData.json();
      const deployments = await deploymentsData.json();
      const issues = await issuesData.json();

      setProject(project);
      setUsage(usage);
      setTeam(team);
      setDeployments(deployments);
      setIssues(issues);
    } catch (err) {
      setError('Failed to fetch project data');
    }
  };

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const renderOverview = () => (
    <Grid container spacing={3}>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Resource Usage
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Compute Hours
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(usage.compute_hours?.current / usage.compute_hours?.limit) * 100}
                sx={{ height: 8, borderRadius: 4 }}
              />
              <Typography variant="caption">
                {usage.compute_hours?.current} / {usage.compute_hours?.limit} hours
              </Typography>
            </Box>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Storage
              </Typography>
              <LinearProgress
                variant="determinate"
                value={(usage.storage_gb?.current / usage.storage_gb?.limit) * 100}
                sx={{ height: 8, borderRadius: 4 }}
              />
              <Typography variant="caption">
                {usage.storage_gb?.current} / {usage.storage_gb?.limit} GB
              </Typography>
            </Box>
          </CardContent>
        </Card>
      </Grid>
      <Grid item xs={12} md={6}>
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Recent Activity
            </Typography>
            <List>
              {deployments.slice(0, 5).map((deployment) => (
                <ListItem key={deployment.id}>
                  <ListItemIcon>
                    <BuildIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={`Deployment ${deployment.version}`}
                    secondary={`${new Date(deployment.timestamp).toLocaleString()} - ${deployment.status}`}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      </Grid>
    </Grid>
  );

  const renderTeam = () => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">Team Members</Typography>
          <Button variant="contained" size="small">
            Add Member
          </Button>
        </Box>
        <List>
          {team.map((member) => (
            <ListItem key={member.id}>
              <ListItemIcon>
                <GroupIcon />
              </ListItemIcon>
              <ListItemText
                primary={member.name}
                secondary={`${member.role} - ${member.email}`}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );

  const renderIssues = () => (
    <Card>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">Issues</Typography>
          <Button variant="contained" size="small">
            New Issue
          </Button>
        </Box>
        <List>
          {issues.map((issue) => (
            <ListItem key={issue.id}>
              <ListItemIcon>
                <BugIcon />
              </ListItemIcon>
              <ListItemText
                primary={issue.title}
                secondary={`${issue.status} - ${issue.priority}`}
              />
            </ListItem>
          ))}
        </List>
      </CardContent>
    </Card>
  );

  return (
    <Box sx={{ p: 3 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {success && (
        <Alert severity="success" sx={{ mb: 2 }}>
          {success}
        </Alert>
      )}

      <Typography variant="h4" gutterBottom>
        {project?.name}
      </Typography>

      <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 3 }}>
        <Tab label="Overview" icon={<TimelineIcon />} />
        <Tab label="Team" icon={<GroupIcon />} />
        <Tab label="Issues" icon={<BugIcon />} />
        <Tab label="Deployments" icon={<BuildIcon />} />
      </Tabs>

      {activeTab === 0 && renderOverview()}
      {activeTab === 1 && renderTeam()}
      {activeTab === 2 && renderIssues()}
      {activeTab === 3 && (
        <Card>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Deployment History
            </Typography>
            <List>
              {deployments.map((deployment) => (
                <ListItem key={deployment.id}>
                  <ListItemIcon>
                    <BuildIcon />
                  </ListItemIcon>
                  <ListItemText
                    primary={`Version ${deployment.version}`}
                    secondary={`${new Date(deployment.timestamp).toLocaleString()} - ${deployment.status}`}
                  />
                </ListItem>
              ))}
            </List>
          </CardContent>
        </Card>
      )}
    </Box>
  );
};

export default ProjectDashboard; 