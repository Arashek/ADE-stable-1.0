import React from 'react';
import { Grid } from '@mui/material';
import { AppProvider } from './context/AppContext';
import Layout from './components/Layout';
import SystemArchitecture from './components/SystemArchitecture';
import DecisionTree from './components/DecisionTree';
import ResourceMonitor from './components/ResourceMonitor';
import AgentCollaboration from './components/AgentCollaboration';
import DeploymentPipeline from './components/DeploymentPipeline';
import ChatPanel from './components/ChatPanel';

const App: React.FC = () => {
  return (
    <AppProvider>
      <Layout>
        <Grid container spacing={2} sx={{ height: '100%' }}>
          {/* Main Content Area */}
          <Grid item xs={12} md={8} sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <SystemArchitecture />
            <DecisionTree />
            <ResourceMonitor />
            <AgentCollaboration />
            <DeploymentPipeline />
          </Grid>
          
          {/* Chat Panel */}
          <Grid item xs={12} md={4}>
            <ChatPanel />
          </Grid>
        </Grid>
      </Layout>
    </AppProvider>
  );
};

export default App; 