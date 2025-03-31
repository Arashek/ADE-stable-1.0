import React, { useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Button,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Chip,
  Alert,
  LinearProgress,
} from '@mui/material';
import {
  PlayArrow as PlayIcon,
  Stop as StopIcon,
  Save as SaveIcon,
  Timeline as TimelineIcon,
  Settings as SettingsIcon,
  Code as CodeIcon,
  BugReport as BugIcon,
  Description as DocIcon,
  RateReview as ReviewIcon,
  Assignment as TaskIcon,
  Psychology as AIIcon,
  Palette as DesignIcon,
  Build as ToolsIcon,
  CheckCircle as CheckCircleIcon,
  Error as ErrorIcon,
} from '@mui/icons-material';

interface CommandHubProps {
  onSave: (design: any) => void;
  onGenerateCode: (design: any) => void;
  isGenerating: boolean;
  activeAgent: string;
}

const CommandHub: React.FC<CommandHubProps> = ({
  onSave,
  onGenerateCode,
  isGenerating,
  activeAgent,
}) => {
  const [openCoordinationDialog, setOpenCoordinationDialog] = useState(false);
  const [selectedFlow, setSelectedFlow] = useState<string | null>(null);
  const [coordinationStatus, setCoordinationStatus] = useState<'idle' | 'running' | 'completed' | 'error'>('idle');

  const handleStartCoordination = async () => {
    try {
      setCoordinationStatus('running');
      const response = await fetch('/api/coordination/start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          flowId: selectedFlow,
          agent: activeAgent,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to start coordination flow');
      }

      const result = await response.json();
      setCoordinationStatus('completed');
      
      // Trigger appropriate actions based on the flow result
      if (result.actions) {
        for (const action of result.actions) {
          switch (action.type) {
            case 'save':
              onSave(action.data);
              break;
            case 'generate_code':
              onGenerateCode(action.data);
              break;
            // Add more action types as needed
          }
        }
      }
    } catch (error) {
      console.error('Error in coordination flow:', error);
      setCoordinationStatus('error');
    }
  };

  const handleStopCoordination = async () => {
    try {
      const response = await fetch('/api/coordination/stop', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          flowId: selectedFlow,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to stop coordination flow');
      }

      setCoordinationStatus('idle');
    } catch (error) {
      console.error('Error stopping coordination flow:', error);
      setCoordinationStatus('error');
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      <Grid container spacing={3}>
        {/* Header */}
        <Grid item xs={12}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
            <Typography variant="h4">Command Hub</Typography>
            <Box>
              <Tooltip title="Start Coordination Flow">
                <IconButton
                  color="primary"
                  onClick={() => setOpenCoordinationDialog(true)}
                  disabled={coordinationStatus === 'running'}
                >
                  <TimelineIcon />
                </IconButton>
              </Tooltip>
              <Tooltip title="Stop Coordination Flow">
                <IconButton
                  color="error"
                  onClick={handleStopCoordination}
                  disabled={coordinationStatus !== 'running'}
                >
                  <StopIcon />
                </IconButton>
              </Tooltip>
            </Box>
          </Box>
        </Grid>

        {/* Status Indicators */}
        <Grid item xs={12}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Active Agent
                </Typography>
                <Chip
                  icon={activeAgent === 'design' ? <DesignIcon /> :
                         activeAgent === 'code' ? <CodeIcon /> :
                         activeAgent === 'ai' ? <AIIcon /> : <ToolsIcon />}
                  label={activeAgent.charAt(0).toUpperCase() + activeAgent.slice(1)}
                  color="primary"
                />
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Coordination Status
                </Typography>
                <Chip
                  icon={coordinationStatus === 'running' ? <PlayIcon /> :
                         coordinationStatus === 'completed' ? <CheckCircleIcon /> :
                         coordinationStatus === 'error' ? <ErrorIcon /> : <TimelineIcon />}
                  label={coordinationStatus.charAt(0).toUpperCase() + coordinationStatus.slice(1)}
                  color={coordinationStatus === 'running' ? 'primary' :
                         coordinationStatus === 'completed' ? 'success' :
                         coordinationStatus === 'error' ? 'error' : 'default'}
                />
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="subtitle2" gutterBottom>
                  Generation Status
                </Typography>
                <Chip
                  icon={isGenerating ? <PlayIcon /> : <StopIcon />}
                  label={isGenerating ? 'Generating' : 'Idle'}
                  color={isGenerating ? 'primary' : 'default'}
                />
              </Paper>
            </Grid>
          </Grid>
        </Grid>

        {/* Action Buttons */}
        <Grid item xs={12}>
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<SaveIcon />}
                onClick={() => onSave({})}
                disabled={isGenerating || coordinationStatus === 'running'}
              >
                Save Design
              </Button>
            </Grid>
            <Grid item xs={12} md={6}>
              <Button
                fullWidth
                variant="contained"
                startIcon={<CodeIcon />}
                onClick={() => onGenerateCode({})}
                disabled={isGenerating || coordinationStatus === 'running'}
              >
                Generate Code
              </Button>
            </Grid>
          </Grid>
        </Grid>
      </Grid>

      {/* Coordination Flow Dialog */}
      <Dialog
        open={openCoordinationDialog}
        onClose={() => setOpenCoordinationDialog(false)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>Select Coordination Flow</DialogTitle>
        <DialogContent>
          <Grid container spacing={2} sx={{ mt: 1 }}>
            <Grid item xs={12}>
              <FormControl fullWidth>
                <InputLabel>Flow Template</InputLabel>
                <Select
                  value={selectedFlow || ''}
                  onChange={(e) => setSelectedFlow(e.target.value as string)}
                  label="Flow Template"
                >
                  <MenuItem value="web_dev">Web Development Flow</MenuItem>
                  <MenuItem value="mobile_dev">Mobile Development Flow</MenuItem>
                  <MenuItem value="ai_dev">AI Development Flow</MenuItem>
                  <MenuItem value="custom">Custom Flow</MenuItem>
                </Select>
              </FormControl>
            </Grid>
          </Grid>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setOpenCoordinationDialog(false)}>Cancel</Button>
          <Button
            variant="contained"
            startIcon={<PlayIcon />}
            onClick={() => {
              handleStartCoordination();
              setOpenCoordinationDialog(false);
            }}
            disabled={!selectedFlow}
          >
            Start Flow
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default CommandHub; 