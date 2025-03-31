import { Message, Agent, PipelineStep, ResourceData } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

// Chat API
export const chatApi = {
  sendMessage: async (message: string): Promise<Message> => {
    const response = await fetch(`${API_BASE_URL}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ message }),
    });
    return response.json();
  },

  getMessages: async (): Promise<Message[]> => {
    const response = await fetch(`${API_BASE_URL}/chat/messages`);
    return response.json();
  },
};

// Agent API
export const agentApi = {
  getAgents: async (): Promise<Agent[]> => {
    const response = await fetch(`${API_BASE_URL}/agents`);
    return response.json();
  },

  updateAgentStatus: async (id: number, status: 'active' | 'inactive'): Promise<Agent> => {
    const response = await fetch(`${API_BASE_URL}/agents/${id}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status }),
    });
    return response.json();
  },
};

// Pipeline API
export const pipelineApi = {
  getPipelineSteps: async (): Promise<PipelineStep[]> => {
    const response = await fetch(`${API_BASE_URL}/pipeline/steps`);
    return response.json();
  },

  updateStepStatus: async (label: string, status: 'completed' | 'active' | 'pending'): Promise<PipelineStep> => {
    const response = await fetch(`${API_BASE_URL}/pipeline/steps/${label}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status }),
    });
    return response.json();
  },
};

// Resource Monitoring API
export const resourceApi = {
  getResourceData: async (): Promise<ResourceData[]> => {
    const response = await fetch(`${API_BASE_URL}/resources/data`);
    return response.json();
  },

  subscribeToResourceUpdates: (callback: (data: ResourceData) => void): () => void => {
    const ws = new WebSocket('ws://localhost:8000/ws/resources');
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data) as ResourceData;
      callback(data);
    };

    return () => {
      ws.close();
    };
  },
}; 