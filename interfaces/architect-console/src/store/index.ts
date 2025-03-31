import { create } from 'zustand';
import { Message, Agent, PipelineStep, ResourceData } from '../types';

interface AppState {
  // Chat state
  messages: Message[];
  addMessage: (message: Message) => void;
  clearMessages: () => void;

  // Agent state
  agents: Agent[];
  updateAgentStatus: (id: number, status: 'active' | 'inactive') => void;
  updateAgentActivity: (id: number, activity: string) => void;

  // Pipeline state
  pipelineSteps: PipelineStep[];
  updateStepStatus: (label: string, status: 'completed' | 'active' | 'pending') => void;

  // Resource monitoring state
  resourceData: ResourceData[];
  addResourceData: (data: ResourceData) => void;
  clearResourceData: () => void;
}

const useStore = create<AppState>((set) => ({
  // Chat state
  messages: [],
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),
  clearMessages: () => set({ messages: [] }),

  // Agent state
  agents: [],
  updateAgentStatus: (id, status) =>
    set((state) => ({
      agents: state.agents.map((agent) =>
        agent.id === id ? { ...agent, status } : agent
      ),
    })),
  updateAgentActivity: (id, activity) =>
    set((state) => ({
      agents: state.agents.map((agent) =>
        agent.id === id ? { ...agent, lastActivity: activity } : agent
      ),
    })),

  // Pipeline state
  pipelineSteps: [],
  updateStepStatus: (label, status) =>
    set((state) => ({
      pipelineSteps: state.pipelineSteps.map((step) =>
        step.label === label ? { ...step, status } : step
      ),
    })),

  // Resource monitoring state
  resourceData: [],
  addResourceData: (data) =>
    set((state) => ({
      resourceData: [...state.resourceData, data],
    })),
  clearResourceData: () => set({ resourceData: [] }),
}));

export default useStore; 