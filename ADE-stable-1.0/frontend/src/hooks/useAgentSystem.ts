import { useCallback } from 'react';
import { Socket } from 'socket.io-client';

interface AgentConfig {
  type: string;
  capabilities: string[];
}

interface AgentActivity {
  id: string;
  type: string;
  timestamp: string;
  details: any;
}

export const useAgentSystem = (socket: Socket | null) => {
  const registerAgent = useCallback((config: AgentConfig) => {
    if (!socket) return;
    
    socket.emit('agent:register', {
      type: config.type,
      capabilities: config.capabilities,
      timestamp: new Date().toISOString()
    });
  }, [socket]);

  const subscribeToActivities = useCallback((callback: (activities: AgentActivity[]) => void) => {
    if (!socket) return () => {};

    const handleActivity = (activity: AgentActivity) => {
      callback([activity]);
    };

    socket.on('agent:activity', handleActivity);

    return () => {
      socket.off('agent:activity', handleActivity);
    };
  }, [socket]);

  const sendAgentMessage = useCallback((message: any) => {
    if (!socket) return;

    socket.emit('agent:message', {
      ...message,
      timestamp: new Date().toISOString()
    });
  }, [socket]);

  const requestAgentCollaboration = useCallback((targetAgentId: string, context: any) => {
    if (!socket) return;

    socket.emit('collaboration:request', {
      targetAgentId,
      context,
      timestamp: new Date().toISOString()
    });
  }, [socket]);

  return {
    registerAgent,
    subscribeToActivities,
    sendAgentMessage,
    requestAgentCollaboration
  };
}; 