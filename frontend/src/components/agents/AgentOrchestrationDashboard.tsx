import React, { useState } from 'react';
import { 
  Box,
  Paper, 
  Grid, 
  Typography, 
  Tabs, 
  Tab, 
  Divider,
  useTheme,
  alpha
} from '@mui/material';
import AgentListPanel, { Agent, AgentStatus, AgentType, generateMockAgents } from './AgentListPanel';
import AgentNetworkVisualization from './AgentNetworkVisualization';

// Interface for tab panel props
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

// Tab panel component for the workflow control panel
function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`workflow-tabpanel-${index}`}
      aria-labelledby={`workflow-tab-${index}`}
      style={{ height: '100%', overflow: 'auto' }}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 2, height: '100%' }}>
          {children}
        </Box>
      )}
    </div>
  );
}

// Helper function for tab accessibility properties
function a11yProps(index: number) {
  return {
    id: `workflow-tab-${index}`,
    'aria-controls': `workflow-tabpanel-${index}`,
  };
}

/**
 * AgentOrchestrationDashboard - A comprehensive visual interface for monitoring and managing 
 * agent relationships, workflows, and performance in the ADE platform.
 */
const AgentOrchestrationDashboard: React.FC = () => {
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);
  const [agents, setAgents] = useState<Agent[]>(generateMockAgents(10));
  const [selectedAgentId, setSelectedAgentId] = useState<string | undefined>(undefined);

  // Handle tab change
  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  // Handle agent selection
  const handleAgentSelect = (agentId: string) => {
    setSelectedAgentId(agentId);
  };

  return (
    <Box sx={{ 
      display: 'flex', 
      flexDirection: 'column', 
      height: '100%',
      overflow: 'hidden',
      bgcolor: theme.palette.background.default
    }}>
      {/* Dashboard Header */}
      <Paper 
        elevation={2} 
        sx={{ 
          p: 2, 
          mb: 2, 
          borderRadius: 1,
          bgcolor: alpha(theme.palette.primary.main, 0.05)
        }}
      >
        <Typography variant="h5" component="h1" gutterBottom>
          Intelligent Agent Orchestration Dashboard
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Monitor and manage agent relationships, workflows, and performance
        </Typography>
      </Paper>

      {/* Main Dashboard Content */}
      <Grid container spacing={2} sx={{ flexGrow: 1, overflow: 'hidden' }}>
        {/* Agent List Panel */}
        <Grid item xs={2} sx={{ height: '70vh' }}>
          <Paper 
            elevation={1} 
            sx={{ 
              p: 2, 
              height: '100%',
              borderRadius: 1,
              overflow: 'auto'
            }}
          >
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Agent List
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <AgentListPanel
              agents={agents}
              selectedAgentId={selectedAgentId}
              onAgentSelect={handleAgentSelect}
            />
          </Paper>
        </Grid>

        {/* Agent Network Visualization */}
        <Grid item xs={6} sx={{ height: '70vh' }}>
          <Paper 
            elevation={1} 
            sx={{ 
              p: 2, 
              height: '100%',
              borderRadius: 1
            }}
          >
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Agent Network Visualization
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Box 
              sx={{ 
                height: 'calc(100% - 50px)', 
                bgcolor: alpha(theme.palette.background.paper, 0.6),
                borderRadius: 1,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
              }}
            >
              <AgentNetworkVisualization 
                agents={agents}
                selectedAgentId={selectedAgentId}
                onNodeClick={handleAgentSelect}
              />
            </Box>
          </Paper>
        </Grid>

        {/* Agent Activity Timeline */}
        <Grid item xs={3} sx={{ height: '70vh' }}>
          <Paper 
            elevation={1} 
            sx={{ 
              p: 2, 
              height: '100%',
              borderRadius: 1,
              overflow: 'auto'
            }}
          >
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom>
              Agent Activity Timeline
            </Typography>
            <Divider sx={{ mb: 2 }} />
            <Typography variant="body2" color="textSecondary">
              Real-time activity stream will be displayed here
            </Typography>
            {/* Activity timeline component will be added here */}
          </Paper>
        </Grid>

        {/* Control Panel */}
        <Grid item xs={1} sx={{ height: '70vh' }}>
          <Paper 
            elevation={1} 
            sx={{ 
              p: 2, 
              height: '100%',
              borderRadius: 1,
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'flex-start'
            }}
          >
            <Typography variant="subtitle1" fontWeight="bold" gutterBottom sx={{ textAlign: 'center' }}>
              Controls
            </Typography>
            <Divider sx={{ mb: 2, width: '100%' }} />
            <Typography variant="body2" color="textSecondary" sx={{ textAlign: 'center' }}>
              Control actions will be displayed here
            </Typography>
            {/* Control buttons will be added here */}
          </Paper>
        </Grid>

        {/* Workflow Control Panel */}
        <Grid item xs={12} sx={{ height: '25vh' }}>
          <Paper 
            elevation={1} 
            sx={{ 
              height: '100%',
              borderRadius: 1,
              display: 'flex',
              flexDirection: 'column'
            }}
          >
            <Tabs 
              value={tabValue} 
              onChange={handleTabChange} 
              aria-label="workflow control tabs"
              variant="scrollable"
              scrollButtons="auto"
              sx={{ 
                borderBottom: 1, 
                borderColor: 'divider',
                bgcolor: alpha(theme.palette.primary.main, 0.05)
              }}
            >
              <Tab label="Task Queue" {...a11yProps(0)} />
              <Tab label="Resource Monitor" {...a11yProps(1)} />
              <Tab label="Consensus Builder" {...a11yProps(2)} />
              <Tab label="Error Analytics" {...a11yProps(3)} />
              <Tab label="Performance Metrics" {...a11yProps(4)} />
            </Tabs>
            
            <TabPanel value={tabValue} index={0}>
              <Typography variant="body2" color="textSecondary">
                Task Queue interface will be displayed here
              </Typography>
              {/* Task Queue component will be added here */}
            </TabPanel>
            
            <TabPanel value={tabValue} index={1}>
              <Typography variant="body2" color="textSecondary">
                Resource Monitor interface will be displayed here
              </Typography>
              {/* Resource Monitor component will be added here */}
            </TabPanel>
            
            <TabPanel value={tabValue} index={2}>
              <Typography variant="body2" color="textSecondary">
                Consensus Builder interface will be displayed here
              </Typography>
              {/* Consensus Builder component will be added here */}
            </TabPanel>
            
            <TabPanel value={tabValue} index={3}>
              <Typography variant="body2" color="textSecondary">
                Error Analytics interface will be displayed here
              </Typography>
              {/* Error Analytics component will be added here */}
            </TabPanel>
            
            <TabPanel value={tabValue} index={4}>
              <Typography variant="body2" color="textSecondary">
                Performance Metrics interface will be displayed here
              </Typography>
              {/* Performance Metrics component will be added here */}
            </TabPanel>
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};

export default AgentOrchestrationDashboard;
