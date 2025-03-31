import { useState, useEffect } from 'react';
import useStore from '../store';
import { pipelineApi } from '../services/api';
import { PipelineStep } from '../types';

export const usePipeline = () => {
  const { pipelineSteps, updateStepStatus } = useStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadPipelineSteps = async () => {
      try {
        setIsLoading(true);
        const fetchedSteps = await pipelineApi.getPipelineSteps();
        // Update store with fetched steps
        fetchedSteps.forEach((step) => {
          updateStepStatus(step.label, step.status);
        });
      } catch (err) {
        setError('Failed to load pipeline steps');
        console.error('Error loading pipeline steps:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadPipelineSteps();
  }, [updateStepStatus]);

  const executeStep = async (label: string) => {
    try {
      setIsLoading(true);
      await pipelineApi.updateStepStatus(label, 'active');
      updateStepStatus(label, 'active');

      // Simulate step execution
      await new Promise((resolve) => setTimeout(resolve, 2000));

      await pipelineApi.updateStepStatus(label, 'completed');
      updateStepStatus(label, 'completed');
    } catch (err) {
      setError('Failed to execute pipeline step');
      console.error('Error executing pipeline step:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const rerunStep = async (label: string) => {
    try {
      setIsLoading(true);
      await pipelineApi.updateStepStatus(label, 'active');
      updateStepStatus(label, 'active');

      // Simulate step execution
      await new Promise((resolve) => setTimeout(resolve, 2000));

      await pipelineApi.updateStepStatus(label, 'completed');
      updateStepStatus(label, 'completed');
    } catch (err) {
      setError('Failed to rerun pipeline step');
      console.error('Error rerunning pipeline step:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    pipelineSteps,
    isLoading,
    error,
    executeStep,
    rerunStep,
  };
}; 