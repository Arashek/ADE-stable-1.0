import { useState, useEffect } from 'react';
import useStore from '../store';
import { agentApi } from '../services/api';
import { Agent } from '../types';

export const useAgents = () => {
  const { agents, updateAgentStatus, updateAgentActivity } = useStore();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const loadAgents = async () => {
      try {
        setIsLoading(true);
        const fetchedAgents = await agentApi.getAgents();
        // Update store with fetched agents
        fetchedAgents.forEach((agent) => {
          updateAgentStatus(agent.id, agent.status);
          updateAgentActivity(agent.id, agent.lastActivity);
        });
      } catch (err) {
        setError('Failed to load agents');
        console.error('Error loading agents:', err);
      } finally {
        setIsLoading(false);
      }
    };

    loadAgents();
  }, [updateAgentStatus, updateAgentActivity]);

  const toggleAgentStatus = async (id: number, currentStatus: 'active' | 'inactive') => {
    try {
      setIsLoading(true);
      const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
      await agentApi.updateAgentStatus(id, newStatus);
      updateAgentStatus(id, newStatus);
      updateAgentActivity(id, `Status changed to ${newStatus}`);
    } catch (err) {
      setError('Failed to update agent status');
      console.error('Error updating agent status:', err);
    } finally {
      setIsLoading(false);
    }
  };

  return {
    agents,
    isLoading,
    error,
    toggleAgentStatus,
  };
}; 