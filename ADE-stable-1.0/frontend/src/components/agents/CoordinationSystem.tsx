import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Tabs,
  Tab,
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Tooltip,
  Chip,
} from '@mui/material';
import {
  Timeline as TimelineIcon,
  Group as GroupIcon,
  Assessment as AssessmentIcon,
  Settings as SettingsIcon,
  PlayArrow as StartIcon,
  Stop as StopIcon,
  Refresh as RefreshIcon,
} from '@mui/icons-material';
import { AgentControlPanel } from './panels/AgentControlPanel';
import { TaskConfigurationPanel } from './panels/TaskConfigurationPanel';
import { ResultsPanel } from './panels/ResultsPanel';

interface CoordinationSystemProps {
  projectId: string;
}

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;
  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`coordination-tabpanel-${index}`}
      aria-labelledby={`coordination-tab-${index}`}
      {...other}
    >
      {value === index && <Box sx={{ p: 3 }}>{children}</Box>}
    </div>
  );
}

export const CoordinationSystem: React.FC<CoordinationSystemProps> = ({ projectId }) => {
  const [tabValue, setTabValue] = useState(0);
  const [activeFlows, setActiveFlows] = useState<string[]>([]);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  const handleFlowToggle = (flowId: string) => {
    setActiveFlows(prev =>
      prev.includes(flowId)
        ? prev.filter(id => id !== flowId)
        : [...prev, flowId]
    );
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Agent Coordination System
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Project ID: {projectId}
        </Typography>

        <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tabs value={tabValue} onChange={handleTabChange}>
            <Tab
              icon={<TimelineIcon />}
              label="Workflows"
              id="coordination-tab-0"
              aria-controls="coordination-tabpanel-0"
            />
            <Tab
              icon={<GroupIcon />}
              label="Agents"
              id="coordination-tab-1"
              aria-controls="coordination-tabpanel-1"
            />
            <Tab
              icon={<AssessmentIcon />}
              label="Performance"
              id="coordination-tab-2"
              aria-controls="coordination-tabpanel-2"
            />
            <Tab
              icon={<SettingsIcon />}
              label="Settings"
              id="coordination-tab-3"
              aria-controls="coordination-tabpanel-3"
            />
          </Tabs>
        </Box>

        <TabPanel value={tabValue} index={0}>
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Active Workflows
                  </Typography>
                  <List>
                    {['Web Development', 'Mobile Development', 'AI Development'].map((flow) => (
                      <ListItem
                        key={flow}
                        secondaryAction={
                          <Box>
                            <Tooltip title={activeFlows.includes(flow) ? 'Stop' : 'Start'}>
                              <IconButton
                                edge="end"
                                onClick={() => handleFlowToggle(flow)}
                                color={activeFlows.includes(flow) ? 'error' : 'primary'}
                              >
                                {activeFlows.includes(flow) ? <StopIcon /> : <StartIcon />}
                              </IconButton>
                            </Tooltip>
                            <Tooltip title="Refresh">
                              <IconButton edge="end">
                                <RefreshIcon />
                              </IconButton>
                            </Tooltip>
                          </Box>
                        }
                      >
                        <ListItemIcon>
                          <TimelineIcon />
                        </ListItemIcon>
                        <ListItemText
                          primary={flow}
                          secondary="Click to view details"
                        />
                      </ListItem>
                    ))}
                  </List>
                </CardContent>
              </Card>
            </Grid>
            <Grid item xs={12} md={4}>
              <TaskConfigurationPanel onTaskConfigChange={() => {}} />
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={1}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <AgentControlPanel onAgentConfigChange={() => {}} />
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={2}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <ResultsPanel onRefresh={() => {}} />
            </Grid>
          </Grid>
        </TabPanel>

        <TabPanel value={tabValue} index={3}>
          <Grid container spacing={3}>
            <Grid item xs={12}>
              <Card>
                <CardContent>
                  <Typography variant="h6" gutterBottom>
                    Coordination Settings
                  </Typography>
                  <List>
                    <ListItem>
                      <ListItemText
                        primary="Default Coordination Mode"
                        secondary="Set the default mode for agent coordination"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Resource Allocation"
                        secondary="Configure default resource limits"
                      />
                    </ListItem>
                    <ListItem>
                      <ListItemText
                        primary="Error Handling"
                        secondary="Set default error handling strategies"
                      />
                    </ListItem>
                  </List>
                </CardContent>
              </Card>
            </Grid>
          </Grid>
        </TabPanel>
      </Box>
    </Container>
  );
}; 