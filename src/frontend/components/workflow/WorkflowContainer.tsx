import React, { useEffect, useState } from 'react';
import { Box, Alert, Snackbar } from '@mui/material';
import { WorkflowVisualizer } from './WorkflowVisualizer';
import { WorkflowStatus, WorkflowResult, WorkflowConfig } from '../../../core/models/project/DevelopmentWorkflowManager';

interface WorkflowContainerProps {
  containerId: string;
}

interface ApiError {
  message: string;
  code?: string;
}

export const WorkflowContainer: React.FC<WorkflowContainerProps> = ({ containerId }) => {
  const [status, setStatus] = useState<WorkflowStatus>({
    status: 'idle',
    progress: 0,
    lastUpdated: new Date(),
    currentStage: undefined,
    activeStages: []
  });
  const [result, setResult] = useState<WorkflowResult | null>(null);
  const [config, setConfig] = useState<WorkflowConfig | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [loading, setLoading] = useState(false);

  const fetchStatus = async () => {
    try {
      const response = await fetch(`/api/workflow/${containerId}/status`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!response.ok) throw new Error('Failed to fetch status');
      const data = await response.json();
      setStatus(data);
    } catch (err) {
      setError({ message: 'Failed to fetch workflow status' });
    }
  };

  const fetchResult = async () => {
    try {
      const response = await fetch(`/api/workflow/${containerId}/result`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!response.ok) throw new Error('Failed to fetch result');
      const data = await response.json();
      setResult(data);
    } catch (err) {
      setError({ message: 'Failed to fetch workflow result' });
    }
  };

  const fetchConfig = async () => {
    try {
      const response = await fetch(`/api/workflow/${containerId}/config`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!response.ok) throw new Error('Failed to fetch config');
      const data = await response.json();
      setConfig(data);
    } catch (err) {
      setError({ message: 'Failed to fetch workflow configuration' });
    }
  };

  const startWorkflow = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/workflow/${containerId}/start`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!response.ok) throw new Error('Failed to start workflow');
      await fetchStatus();
    } catch (err) {
      setError({ message: 'Failed to start workflow' });
    } finally {
      setLoading(false);
    }
  };

  const stopWorkflow = async () => {
    setLoading(true);
    try {
      const response = await fetch(`/api/workflow/${containerId}/stop`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });
      if (!response.ok) throw new Error('Failed to stop workflow');
      await fetchStatus();
    } catch (err) {
      setError({ message: 'Failed to stop workflow' });
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchConfig();
    fetchStatus();
    fetchResult();

    // Set up polling for status and result when workflow is running
    const pollInterval = setInterval(() => {
      if (status.status === 'running') {
        fetchStatus();
        fetchResult();
      }
    }, 5000);

    return () => clearInterval(pollInterval);
  }, [containerId, status.status]);

  const handleErrorClose = () => {
    setError(null);
  };

  return (
    <Box>
      {error && (
        <Snackbar
          open={!!error}
          autoHideDuration={6000}
          onClose={handleErrorClose}
          anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
        >
          <Alert onClose={handleErrorClose} severity="error" sx={{ width: '100%' }}>
            {error.message}
          </Alert>
        </Snackbar>
      )}

      <WorkflowVisualizer
        containerId={containerId}
        status={status}
        result={result}
        onStart={startWorkflow}
        onStop={stopWorkflow}
      />
    </Box>
  );
}; 