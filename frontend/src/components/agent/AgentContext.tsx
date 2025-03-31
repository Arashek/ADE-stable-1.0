import React, { createContext, useContext, useState, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';

interface Agent {
  id: string;
  name: string;
  role: string;
  status: 'active' | 'idle' | 'busy' | 'error';
  capabilities: string[];
  currentTask?: string;
  lastActive: Date;
  focusArea?: string;
  performance: {
    tasksCompleted: number;
    successRate: number;
    averageResponseTime: number;
  };
}

interface Task {
  id: string;
  title: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  priority: 'low' | 'medium' | 'high';
  assignedTo?: string;
  createdBy: string;
  createdAt: Date;
  updatedAt: Date;
  dependencies?: string[];
  progress: number;
  tags: string[];
}

interface AgentContextType {
  agents: Agent[];
  tasks: Task[];
  addTask: (task: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) => void;
  updateTask: (taskId: string, updates: Partial<Task>) => void;
  deleteTask: (taskId: string) => void;
  assignTask: (taskId: string, agentId: string) => void;
  updateAgentStatus: (agentId: string, status: Agent['status']) => void;
  updateAgentFocus: (agentId: string, focusArea: string) => void;
  getAgentById: (agentId: string) => Agent | undefined;
  getTasksByAgent: (agentId: string) => Task[];
  getTasksByStatus: (status: Task['status']) => Task[];
  getTasksByPriority: (priority: Task['priority']) => Task[];
}

const AgentContext = createContext<AgentContextType | undefined>(undefined);

export const useAgentContext = () => {
  const context = useContext(AgentContext);
  if (!context) {
    throw new Error('useAgentContext must be used within an AgentProvider');
  }
  return context;
};

interface AgentProviderProps {
  children: React.ReactNode;
  projectId: string;
}

export const AgentProvider: React.FC<AgentProviderProps> = ({ children, projectId }) => {
  const [agents, setAgents] = useState<Agent[]>([
    {
      id: uuidv4(),
      name: 'Project Manager',
      role: 'project_manager',
      status: 'active',
      capabilities: ['task_management', 'resource_allocation', 'progress_tracking'],
      lastActive: new Date(),
      performance: {
        tasksCompleted: 0,
        successRate: 100,
        averageResponseTime: 0,
      },
    },
    {
      id: uuidv4(),
      name: 'Architect',
      role: 'architect',
      status: 'active',
      capabilities: ['system_design', 'architecture_review', 'technical_decisions'],
      lastActive: new Date(),
      performance: {
        tasksCompleted: 0,
        successRate: 100,
        averageResponseTime: 0,
      },
    },
    {
      id: uuidv4(),
      name: 'Developer',
      role: 'developer',
      status: 'active',
      capabilities: ['code_implementation', 'code_review', 'bug_fixing'],
      lastActive: new Date(),
      performance: {
        tasksCompleted: 0,
        successRate: 100,
        averageResponseTime: 0,
      },
    },
  ]);

  const [tasks, setTasks] = useState<Task[]>([]);

  const addTask = (task: Omit<Task, 'id' | 'createdAt' | 'updatedAt'>) => {
    const newTask: Task = {
      ...task,
      id: uuidv4(),
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setTasks((prev) => [...prev, newTask]);
  };

  const updateTask = (taskId: string, updates: Partial<Task>) => {
    setTasks((prev) =>
      prev.map((task) =>
        task.id === taskId
          ? { ...task, ...updates, updatedAt: new Date() }
          : task
      )
    );
  };

  const deleteTask = (taskId: string) => {
    setTasks((prev) => prev.filter((task) => task.id !== taskId));
  };

  const assignTask = (taskId: string, agentId: string) => {
    updateTask(taskId, {
      assignedTo: agentId,
      status: 'in_progress',
    });
    updateAgentStatus(agentId, 'busy');
  };

  const updateAgentStatus = (agentId: string, status: Agent['status']) => {
    setAgents((prev) =>
      prev.map((agent) =>
        agent.id === agentId
          ? { ...agent, status, lastActive: new Date() }
          : agent
      )
    );
  };

  const updateAgentFocus = (agentId: string, focusArea: string) => {
    setAgents((prev) =>
      prev.map((agent) =>
        agent.id === agentId
          ? { ...agent, focusArea, lastActive: new Date() }
          : agent
      )
    );
  };

  const getAgentById = (agentId: string) => {
    return agents.find((agent) => agent.id === agentId);
  };

  const getTasksByAgent = (agentId: string) => {
    return tasks.filter((task) => task.assignedTo === agentId);
  };

  const getTasksByStatus = (status: Task['status']) => {
    return tasks.filter((task) => task.status === status);
  };

  const getTasksByPriority = (priority: Task['priority']) => {
    return tasks.filter((task) => task.priority === priority);
  };

  // Simulate agent activities
  useEffect(() => {
    const interval = setInterval(() => {
      setAgents((prev) =>
        prev.map((agent) => ({
          ...agent,
          lastActive: new Date(),
          performance: {
            ...agent.performance,
            tasksCompleted: agent.performance.tasksCompleted + Math.floor(Math.random() * 2),
            averageResponseTime: Math.random() * 1000,
          },
        }))
      );
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const value = {
    agents,
    tasks,
    addTask,
    updateTask,
    deleteTask,
    assignTask,
    updateAgentStatus,
    updateAgentFocus,
    getAgentById,
    getTasksByAgent,
    getTasksByStatus,
    getTasksByPriority,
  };

  return (
    <AgentContext.Provider value={value}>
      {children}
    </AgentContext.Provider>
  );
}; 