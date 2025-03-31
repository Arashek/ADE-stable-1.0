import React, { useState } from 'react';
import { Box, Grid, Container, Typography } from '@mui/material';
import { ModelSelectionPanel } from './panels/ModelSelectionPanel';
import { TaskConfigurationPanel } from './panels/TaskConfigurationPanel';
import { AgentControlPanel } from './panels/AgentControlPanel';
import { ResultsPanel } from './panels/ResultsPanel';

interface AgentDashboardProps {
  projectId: string;
}

export const AgentDashboard: React.FC<AgentDashboardProps> = ({ projectId }) => {
  const [modelConfig, setModelConfig] = useState<any>(null);
  const [taskConfig, setTaskConfig] = useState<any>(null);
  const [agentConfig, setAgentConfig] = useState<any>(null);

  const handleModelConfigChange = (config: any) => {
    setModelConfig(config);
    // TODO: Implement API call to update model configuration
  };

  const handleTaskConfigChange = (config: any) => {
    setTaskConfig(config);
    // TODO: Implement API call to update task configuration
  };

  const handleAgentConfigChange = (config: any) => {
    setAgentConfig(config);
    // TODO: Implement API call to update agent configuration
  };

  const handleResultsRefresh = () => {
    // TODO: Implement API call to refresh results
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ py: 4 }}>
        <Typography variant="h4" gutterBottom>
          Agent Dashboard
        </Typography>
        <Typography variant="subtitle1" color="text.secondary" gutterBottom>
          Project ID: {projectId}
        </Typography>

        <Grid container spacing={3}>
          {/* Left Column - Configuration Panels */}
          <Grid item xs={12} md={4}>
            <Grid container spacing={3}>
              <Grid item xs={12}>
                <ModelSelectionPanel onModelConfigChange={handleModelConfigChange} />
              </Grid>
              <Grid item xs={12}>
                <TaskConfigurationPanel onTaskConfigChange={handleTaskConfigChange} />
              </Grid>
            </Grid>
          </Grid>

          {/* Middle Column - Agent Control */}
          <Grid item xs={12} md={4}>
            <AgentControlPanel onAgentConfigChange={handleAgentConfigChange} />
          </Grid>

          {/* Right Column - Results */}
          <Grid item xs={12} md={4}>
            <ResultsPanel onRefresh={handleResultsRefresh} />
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
}; 