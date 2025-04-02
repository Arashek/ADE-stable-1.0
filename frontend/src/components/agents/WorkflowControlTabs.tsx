import React, { useState } from 'react';
import {
  Box,
  Paper,
  Tabs,
  Tab,
  Typography,
  useTheme,
  alpha
} from '@mui/material';
import {
  Queue as QueueIcon,
  Storage as StorageIcon,
  Group as GroupIcon,
  Error as ErrorIcon,
  Speed as SpeedIcon
} from '@mui/icons-material';
import { Agent } from './AgentListPanel';
import TaskQueuePanel from './workflow/TaskQueuePanel';
import ResourceMonitorPanel from './workflow/ResourceMonitorPanel';
import ConsensusBuilderPanel from './workflow/ConsensusBuilderPanel';
import ErrorAnalyticsPanel from './workflow/ErrorAnalyticsPanel';
import PerformanceMetricsPanel from './workflow/PerformanceMetricsPanel';

// Interface for tab panel props
interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

// Tab Panel component
const TabPanel = (props: TabPanelProps) => {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`workflow-tabpanel-${index}`}
      aria-labelledby={`workflow-tab-${index}`}
      style={{ height: '100%' }}
      {...other}
    >
      {value === index && (
        <Box sx={{ height: '100%', pt: 2 }}>
          {children}
        </Box>
      )}
    </div>
  );
};

// Helper function for a11y props
const a11yProps = (index: number) => {
  return {
    id: `workflow-tab-${index}`,
    'aria-controls': `workflow-tabpanel-${index}`,
  };
};

interface WorkflowControlTabsProps {
  agents: Agent[];
  selectedAgentId?: string;
}

/**
 * WorkflowControlTabs Component - Provides tabbed interface for different workflow views
 */
const WorkflowControlTabs: React.FC<WorkflowControlTabsProps> = ({
  agents,
  selectedAgentId
}) => {
  const theme = useTheme();
  const [tabValue, setTabValue] = useState(0);

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    setTabValue(newValue);
  };

  return (
    <Box sx={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Paper 
        elevation={0}
        sx={{ 
          borderBottom: 1, 
          borderColor: 'divider',
          backgroundColor: alpha(theme.palette.background.paper, 0.8)
        }}
      >
        <Tabs 
          value={tabValue} 
          onChange={handleTabChange} 
          aria-label="workflow control tabs"
          variant="scrollable"
          scrollButtons="auto"
        >
          <Tab 
            icon={<QueueIcon />} 
            label="Task Queue" 
            {...a11yProps(0)} 
            sx={{ minWidth: 120 }} 
          />
          <Tab 
            icon={<StorageIcon />} 
            label="Resource Monitor" 
            {...a11yProps(1)} 
            sx={{ minWidth: 140 }} 
          />
          <Tab 
            icon={<GroupIcon />} 
            label="Consensus Builder" 
            {...a11yProps(2)} 
            sx={{ minWidth: 140 }} 
          />
          <Tab 
            icon={<ErrorIcon />} 
            label="Error Analytics" 
            {...a11yProps(3)} 
            sx={{ minWidth: 140 }} 
          />
          <Tab 
            icon={<SpeedIcon />} 
            label="Performance Metrics" 
            {...a11yProps(4)} 
            sx={{ minWidth: 140 }} 
          />
        </Tabs>
      </Paper>
      
      <Box sx={{ flexGrow: 1, overflow: 'auto' }}>
        <TabPanel value={tabValue} index={0}>
          <TaskQueuePanel agents={agents} selectedAgentId={selectedAgentId} />
        </TabPanel>
        
        <TabPanel value={tabValue} index={1}>
          <ResourceMonitorPanel agents={agents} selectedAgentId={selectedAgentId} />
        </TabPanel>
        
        <TabPanel value={tabValue} index={2}>
          <ConsensusBuilderPanel agents={agents} selectedAgentId={selectedAgentId} />
        </TabPanel>
        
        <TabPanel value={tabValue} index={3}>
          <ErrorAnalyticsPanel agents={agents} selectedAgentId={selectedAgentId} />
        </TabPanel>
        
        <TabPanel value={tabValue} index={4}>
          <PerformanceMetricsPanel agents={agents} selectedAgentId={selectedAgentId} />
        </TabPanel>
      </Box>
    </Box>
  );
};

export default WorkflowControlTabs;
