import React, { useState, useEffect } from 'react';
import {
  Box, 
  Container,
  Divider,
  Grid,
  Paper,
  Tab,
  Tabs,
  Typography
} from '@mui/material';
import ErrorLogsViewer from './admin/ErrorLogsViewer';
import TestApi from '../TestApi';
import PromptProcessor from './PromptProcessor';
import ErrorBoundary from '../components/common/ErrorBoundary';
import { logError, ErrorCategory, ErrorSeverity } from '../services/errorHandling';

interface TabPanelProps {
  children?: React.ReactNode;
  index: number;
  value: number;
}

/**
 * TabPanel component displays content for the selected tab
 */
function TabPanel(props: TabPanelProps) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`error-monitoring-tabpanel-${index}`}
      aria-labelledby={`error-monitoring-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box sx={{ p: 3 }}>
          {children}
        </Box>
      )}
    </div>
  );
}

/**
 * A comprehensive error monitoring dashboard component for the ADE platform
 * Provides UI for viewing errors, testing API, and processing prompts
 */
const ErrorMonitoringDashboard: React.FC = () => {
  const [value, setValue] = useState(0);
  const [testCount, setTestCount] = useState(0);

  const handleChange = (event: React.SyntheticEvent, newValue: number) => {
    setValue(newValue);
  };

  // Generate a test error
  const generateTestError = () => {
    try {
      // Simulate an error
      setTestCount(prev => prev + 1);
      if (testCount % 3 === 0) {
        throw new Error(`Manually triggered test error #${testCount}`);
      }
    } catch (error) {
      if (error instanceof Error) {
        logError(
          error.message,
          ErrorCategory.FRONTEND,
          ErrorSeverity.ERROR,
          'ErrorMonitoringDashboard',
          { source: 'Test Button', count: testCount },
          error.stack
        );
      }
    }
  };

  // Generate various test errors on first load
  useEffect(() => {
    const generateInitialErrors = async () => {
      // Log info message
      await logError(
        'ErrorMonitoringDashboard initialized',
        ErrorCategory.FRONTEND,
        ErrorSeverity.INFO,
        'ErrorMonitoringDashboard',
        { initialLoad: true }
      );

      // Log warning
      await logError(
        'System resources running low',
        ErrorCategory.SYSTEM,
        ErrorSeverity.WARNING,
        'SystemMonitor',
        { 
          memory: { used: '80%', available: '20%' }, 
          cpu: { usage: '75%' }
        }
      );
    };

    generateInitialErrors();
  }, []);

  return (
    <Container maxWidth="xl">
      <Paper elevation={3} sx={{ mt: 4, mb: 4 }}>
        <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
          <Tabs 
            value={value} 
            onChange={handleChange}
            aria-label="Error monitoring dashboard tabs"
            variant="fullWidth"
          >
            <Tab label="Error Logs" />
            <Tab label="API Testing" />
            <Tab label="Prompt Processing" />
          </Tabs>
        </Box>

        {/* Error Logs Panel */}
        <TabPanel value={value} index={0}>
          <ErrorBoundary componentName="ErrorLogsViewer">
            <ErrorLogsViewer />
          </ErrorBoundary>
        </TabPanel>

        {/* API Testing Panel */}
        <TabPanel value={value} index={1}>
          <ErrorBoundary componentName="TestApi">
            <TestApi />
          </ErrorBoundary>
        </TabPanel>

        {/* Prompt Processing Panel */}
        <TabPanel value={value} index={2}>
          <ErrorBoundary componentName="PromptProcessor">
            <PromptProcessor />
          </ErrorBoundary>
        </TabPanel>
      </Paper>

      {/* Error Simulation Controls */}
      <Paper elevation={2} sx={{ p: 2, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Error Simulation Tools
        </Typography>
        <Typography variant="body2" paragraph>
          Use these tools to test error logging and monitoring functionality in the ADE platform.
        </Typography>
        
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <Box sx={{ p: 2, border: '1px dashed grey', borderRadius: 1 }}>
              <Typography variant="subtitle2" gutterBottom>
                Manual Error Generation
              </Typography>
              <button onClick={generateTestError}>
                Generate Test Error
              </button>
              <Typography variant="caption" display="block" sx={{ mt: 1 }}>
                Clicking this button will generate an error every third click.
              </Typography>
            </Box>
          </Grid>
        </Grid>
      </Paper>
    </Container>
  );
};

export default ErrorMonitoringDashboard;
