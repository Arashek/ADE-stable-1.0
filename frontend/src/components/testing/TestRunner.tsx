import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  Typography,
  Button,
  CircularProgress,
  Stepper,
  Step,
  StepLabel,
  Grid,
  Chip,
  IconButton,
  Tooltip,
  TextField,
} from '@mui/material';
import {
  PlayArrow,
  Stop,
  Refresh,
  Save,
  BugReport,
  Speed,
  Security,
  Timeline,
} from '@mui/icons-material';
import { styled } from '@mui/material/styles';
import { TestResults } from './TestResults';
import { LoadTestVisualizer } from './LoadTestVisualizer';
import { SecurityTestDashboard } from './SecurityTestDashboard';
import { MonitoringService } from '../../services/monitoring.service';

const StyledPaper = styled(Paper)(({ theme }) => ({
  padding: theme.spacing(3),
  marginBottom: theme.spacing(2),
}));

const TestControls = styled(Box)(({ theme }) => ({
  display: 'flex',
  gap: theme.spacing(2),
  marginBottom: theme.spacing(3),
}));

interface TestConfig {
  type: 'unit' | 'integration' | 'load' | 'security';
  target?: string;
  concurrent_users?: number;
  duration?: number;
  security_checks?: string[];
}

export const TestRunner: React.FC = () => {
  const [activeTest, setActiveTest] = useState<TestConfig | null>(null);
  const [isRunning, setIsRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [results, setResults] = useState<any>(null);
  const [activeStep, setActiveStep] = useState(0);
  const [savedConfigs, setSavedConfigs] = useState<TestConfig[]>([]);
  
  const monitoring = MonitoringService.getInstance();

  const steps = ['Configure', 'Run', 'Analyze'];

  useEffect(() => {
    // Load saved configurations
    const loadSavedConfigs = async () => {
      try {
        const configs = localStorage.getItem('testConfigs');
        if (configs) {
          setSavedConfigs(JSON.parse(configs));
        }
      } catch (error) {
        monitoring.recordError('load_test_configs_failed', error);
      }
    };
    loadSavedConfigs();
  }, []);

  const handleStartTest = async () => {
    if (!activeTest) return;

    setIsRunning(true);
    setProgress(0);
    setResults(null);

    try {
      monitoring.recordMetric({
        category: 'testing',
        name: 'test_started',
        value: 1,
        tags: { type: activeTest.type }
      });

      // Simulate test progress
      const interval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 100) {
            clearInterval(interval);
            return 100;
          }
          return prev + 1;
        });
      }, 100);

      // Mock test execution
      const mockResults = await simulateTestRun(activeTest);
      setResults(mockResults);
      setActiveStep(2);

      monitoring.recordMetric({
        category: 'testing',
        name: 'test_completed',
        value: 1,
        tags: { 
          type: activeTest.type,
          success: mockResults.success
        }
      });
    } catch (error) {
      monitoring.recordError('test_execution_failed', error);
    } finally {
      setIsRunning(false);
    }
  };

  const handleStopTest = () => {
    setIsRunning(false);
    monitoring.recordMetric({
      category: 'testing',
      name: 'test_stopped',
      value: 1,
      tags: { type: activeTest?.type }
    });
  };

  const handleSaveConfig = () => {
    if (!activeTest) return;

    const newConfigs = [...savedConfigs, activeTest];
    setSavedConfigs(newConfigs);
    localStorage.setItem('testConfigs', JSON.stringify(newConfigs));

    monitoring.recordMetric({
      category: 'testing',
      name: 'config_saved',
      value: 1,
      tags: { type: activeTest.type }
    });
  };

  const simulateTestRun = async (config: TestConfig): Promise<any> => {
    // Mock test execution
    await new Promise(resolve => setTimeout(resolve, 2000));

    switch (config.type) {
      case 'unit':
        return {
          success: true,
          total: 10,
          passed: 9,
          failed: 1,
          coverage: 85,
          duration: 1.5,
          tests: [
            { name: 'Test 1', status: 'passed', duration: 0.1 },
            { name: 'Test 2', status: 'failed', duration: 0.2, error: 'Assertion failed' },
            // ... more test results
          ]
        };
      case 'load':
        return {
          success: true,
          requests: 1000,
          rps: 50,
          latency: {
            p50: 100,
            p90: 200,
            p99: 300
          },
          errors: 5,
          timeline: [
            // ... performance timeline data
          ]
        };
      case 'security':
        return {
          success: true,
          vulnerabilities: [
            { severity: 'high', type: 'sql_injection', location: '/api/users' },
            { severity: 'medium', type: 'xss', location: '/api/comments' },
          ],
          passed_checks: 15,
          total_checks: 20
        };
      default:
        return { success: false, error: 'Unknown test type' };
    }
  };

  const renderTestConfig = () => {
    if (!activeTest) return null;

    switch (activeTest.type) {
      case 'load':
        return (
          <Grid container spacing={2}>
            <Grid item xs={6}>
              <TextField
                fullWidth
                label="Target URL"
                value={activeTest.target}
                onChange={(e) => setActiveTest({
                  ...activeTest,
                  target: e.target.value
                })}
              />
            </Grid>
            <Grid item xs={3}>
              <TextField
                fullWidth
                type="number"
                label="Concurrent Users"
                value={activeTest.concurrent_users}
                onChange={(e) => setActiveTest({
                  ...activeTest,
                  concurrent_users: parseInt(e.target.value)
                })}
              />
            </Grid>
            <Grid item xs={3}>
              <TextField
                fullWidth
                type="number"
                label="Duration (seconds)"
                value={activeTest.duration}
                onChange={(e) => setActiveTest({
                  ...activeTest,
                  duration: parseInt(e.target.value)
                })}
              />
            </Grid>
          </Grid>
        );
      // Add more test type configurations
      default:
        return null;
    }
  };

  const renderResults = () => {
    if (!results) return null;

    switch (activeTest?.type) {
      case 'unit':
      case 'integration':
        return <TestResults results={results} />;
      case 'load':
        return <LoadTestVisualizer results={results} />;
      case 'security':
        return <SecurityTestDashboard results={results} />;
      default:
        return null;
    }
  };

  return (
    <Box>
      <Typography variant="h5" sx={{ mb: 3 }}>
        Test Runner
      </Typography>
      <StyledPaper>
        <Stepper activeStep={activeStep} sx={{ mb: 4 }}>
          {steps.map((label) => (
            <Step key={label}>
              <StepLabel>{label}</StepLabel>
            </Step>
          ))}
        </Stepper>
        {activeStep === 0 && (
          <Grid container spacing={2}>
            <Grid item xs={12}>
              <Typography variant="subtitle1" sx={{ mb: 2 }}>
                Select Test Type
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Button
                  variant={activeTest?.type === 'unit' ? 'contained' : 'outlined'}
                  startIcon={<BugReport />}
                  onClick={() => setActiveTest({ type: 'unit' })}
                >
                  Unit Tests
                </Button>
                <Button
                  variant={activeTest?.type === 'load' ? 'contained' : 'outlined'}
                  startIcon={<Speed />}
                  onClick={() => setActiveTest({ type: 'load' })}
                >
                  Load Tests
                </Button>
                <Button
                  variant={activeTest?.type === 'security' ? 'contained' : 'outlined'}
                  startIcon={<Security />}
                  onClick={() => setActiveTest({ type: 'security' })}
                >
                  Security Tests
                </Button>
              </Box>
            </Grid>
            <Grid item xs={12}>
              {renderTestConfig()}
            </Grid>
          </Grid>
        )}
        <TestControls>
          {!isRunning ? (
            <>
              <Button
                variant="contained"
                color="primary"
                startIcon={<PlayArrow />}
                onClick={handleStartTest}
                disabled={!activeTest}
              >
                Start Test
              </Button>
              <Button
                variant="outlined"
                startIcon={<Save />}
                onClick={handleSaveConfig}
                disabled={!activeTest}
              >
                Save Configuration
              </Button>
            </>
          ) : (
            <Button
              variant="contained"
              color="error"
              startIcon={<Stop />}
              onClick={handleStopTest}
            >
              Stop Test
            </Button>
          )}
          <Button
            variant="outlined"
            startIcon={<Refresh />}
            onClick={() => {
              setActiveTest(null);
              setResults(null);
              setActiveStep(0);
            }}
          >
            Reset
          </Button>
        </TestControls>
        {isRunning && (
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <CircularProgress variant="determinate" value={progress} />
            <Typography variant="body2" color="textSecondary">
              {progress}% Complete
            </Typography>
          </Box>
        )}
        {results && renderResults()}
      </StyledPaper>
    </Box>
  );
};
