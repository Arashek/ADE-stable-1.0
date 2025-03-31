import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { v4 as uuidv4 } from 'uuid';

interface Agent {
  id: string;
  name: string;
  role: string;
  status: 'idle' | 'active' | 'busy' | 'error';
  currentTask?: string;
  lastActive: Date;
}

interface Message {
  id: string;
  agentId: string;
  content: string;
  timestamp: Date;
  read: boolean;
  type: 'info' | 'warning' | 'error' | 'success';
}

interface Task {
  id: string;
  title: string;
  description: string;
  assignedTo: string[];
  status: 'pending' | 'in_progress' | 'completed' | 'blocked';
  priority: 'low' | 'medium' | 'high';
  dependencies: string[];
  createdAt: Date;
  updatedAt: Date;
}

interface AgentState {
  agents: Agent[];
  messages: Message[];
  tasks: Task[];
  activeAgent?: string;
  settings: AgentSettings;
}

type AgentSettings = {
  notifications: boolean;
  autoFocus: boolean;
  theme: 'light' | 'dark';
};

type AgentAction =
  | { type: 'ADD_AGENT'; payload: Omit<Agent, 'id'> }
  | { type: 'UPDATE_AGENT'; payload: Partial<Agent> & { id: string } }
  | { type: 'ADD_MESSAGE'; payload: Omit<Message, 'id' | 'timestamp'> }
  | { type: 'MARK_MESSAGE_READ'; payload: string }
  | { type: 'ADD_TASK'; payload: Omit<Task, 'id' | 'createdAt' | 'updatedAt'> }
  | { type: 'UPDATE_TASK'; payload: Partial<Task> & { id: string } }
  | { type: 'SET_ACTIVE_AGENT'; payload: string }
  | { type: 'UPDATE_SETTINGS'; payload: Partial<AgentSettings> };

const initialState: AgentState = {
  agents: [],
  messages: [],
  tasks: [],
  settings: {
    notifications: true,
    autoFocus: true,
    theme: 'dark'
  }
};

const agentReducer = (state: AgentState, action: AgentAction): AgentState => {
  switch (action.type) {
    case 'ADD_AGENT':
      return {
        ...state,
        agents: [...state.agents, { ...action.payload, id: uuidv4() }]
      };
    case 'UPDATE_AGENT':
      return {
        ...state,
        agents: state.agents.map(agent =>
          agent.id === action.payload.id ? { ...agent, ...action.payload } : agent
        )
      };
    case 'ADD_MESSAGE':
      return {
        ...state,
        messages: [
          ...state.messages,
          {
            ...action.payload,
            id: uuidv4(),
            timestamp: new Date(),
            read: false
          }
        ]
      };
    case 'MARK_MESSAGE_READ':
      return {
        ...state,
        messages: state.messages.map(message =>
          message.id === action.payload ? { ...message, read: true } : message
        )
      };
    case 'ADD_TASK':
      return {
        ...state,
        tasks: [
          ...state.tasks,
          {
            ...action.payload,
            id: uuidv4(),
            createdAt: new Date(),
            updatedAt: new Date()
          }
        ]
      };
    case 'UPDATE_TASK':
      return {
        ...state,
        tasks: state.tasks.map(task =>
          task.id === action.payload.id
            ? { ...task, ...action.payload, updatedAt: new Date() }
            : task
        )
      };
    case 'SET_ACTIVE_AGENT':
      return {
        ...state,
        activeAgent: action.payload
      };
    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: { ...state.settings, ...action.payload }
      };
    default:
      return state;
  }
};

interface AgentContextType {
  state: AgentState;
  actions: {
    addAgent: (agent: Omit<Agent, 'id'>) => void;
    updateAgent: (agent: Partial<Agent> & { id: string }) => void;
    addMessage: (message: Omit<Message, 'id' | 'timestamp'>) => void;
    markMessageRead: (messageId: string) => void;
    addTask: (task: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) => void;
    updateTask: (task: Partial<Task> & { id: string }) => void;
    setActiveAgent: (agentId: string) => void;
    updateSettings: (settings: Partial<AgentSettings>) => void;
    subscribeToMessages: (callback: (message: Message) => void) => () => void;
  };
}

const AgentContext = createContext<AgentContextType | undefined>(undefined);

export const AgentProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(agentReducer, initialState);
  const messageSubscribers = React.useRef<((message: Message) => void)[]>([]);

  const addAgent = useCallback((agent: Omit<Agent, 'id'>) => {
    dispatch({ type: 'ADD_AGENT', payload: agent });
  }, []);

  const updateAgent = useCallback((agent: Partial<Agent> & { id: string }) => {
    dispatch({ type: 'UPDATE_AGENT', payload: agent });
  }, []);

  const addMessage = useCallback((message: Omit<Message, 'id' | 'timestamp'>) => {
    dispatch({ type: 'ADD_MESSAGE', payload: message });
    messageSubscribers.current.forEach(callback => callback(message as Message));
  }, []);

  const markMessageRead = useCallback((messageId: string) => {
    dispatch({ type: 'MARK_MESSAGE_READ', payload: messageId });
  }, []);

  const addTask = useCallback((task: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) => {
    dispatch({ type: 'ADD_TASK', payload: task });
  }, []);

  const updateTask = useCallback((task: Partial<Task> & { id: string }) => {
    dispatch({ type: 'UPDATE_TASK', payload: task });
  }, []);

  const setActiveAgent = useCallback((agentId: string) => {
    dispatch({ type: 'SET_ACTIVE_AGENT', payload: agentId });
  }, []);

  const updateSettings = useCallback((settings: Partial<AgentSettings>) => {
    dispatch({ type: 'UPDATE_SETTINGS', payload: settings });
  }, []);

  const subscribeToMessages = useCallback((callback: (message: Message) => void) => {
    messageSubscribers.current.push(callback);
    return () => {
      messageSubscribers.current = messageSubscribers.current.filter(cb => cb !== callback);
    };
  }, []);

  const value = {
    state,
    actions: {
      addAgent,
      updateAgent,
      addMessage,
      markMessageRead,
      addTask,
      updateTask,
      setActiveAgent,
      updateSettings,
      subscribeToMessages
    }
  };

  return <AgentContext.Provider value={value}>{children}</AgentContext.Provider>;
};

export const useAgentContext = () => {
  const context = useContext(AgentContext);
  if (context === undefined) {
    throw new Error('useAgentContext must be used within an AgentProvider');
  }
  return context;
}; 