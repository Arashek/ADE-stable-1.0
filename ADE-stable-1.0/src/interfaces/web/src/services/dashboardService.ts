import axios from 'axios';
import { Activity } from '../components/dashboard/ActivitySummary';
import { Project } from '../components/dashboard/ProjectsOverview';
import { Agent } from '../components/dashboard/AgentStatusCard';
import { Task } from '../components/dashboard/RecentTasks';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

export const dashboardService = {
  // Activities
  getActivities: async (): Promise<Activity[]> => {
    const response = await axios.get(`${API_BASE_URL}/activities`);
    return response.data;
  },

  // Projects
  getProjects: async (): Promise<Project[]> => {
    const response = await axios.get(`${API_BASE_URL}/projects`);
    return response.data;
  },

  updateProjectStatus: async (projectId: string, status: Project['status']) => {
    const response = await axios.patch(`${API_BASE_URL}/projects/${projectId}/status`, { status });
    return response.data;
  },

  // Agents
  getAgents: async (): Promise<Agent[]> => {
    const response = await axios.get(`${API_BASE_URL}/agents`);
    return response.data;
  },

  updateAgentStatus: async (agentId: string, action: 'start' | 'stop' | 'restart') => {
    const response = await axios.post(`${API_BASE_URL}/agents/${agentId}/${action}`);
    return response.data;
  },

  // Tasks
  getTasks: async (): Promise<Task[]> => {
    const response = await axios.get(`${API_BASE_URL}/tasks`);
    return response.data;
  },

  updateTaskStatus: async (taskId: string, status: Task['status']) => {
    const response = await axios.patch(`${API_BASE_URL}/tasks/${taskId}/status`, { status });
    return response.data;
  },

  deleteTask: async (taskId: string) => {
    await axios.delete(`${API_BASE_URL}/tasks/${taskId}`);
  },

  // Quick Actions
  createProject: async (projectData: Partial<Project>) => {
    const response = await axios.post(`${API_BASE_URL}/projects`, projectData);
    return response.data;
  },

  startCodeReview: async (repositoryUrl: string, prNumber?: number) => {
    const response = await axios.post(`${API_BASE_URL}/code-review`, {
      repositoryUrl,
      prNumber,
    });
    return response.data;
  },

  openTerminal: async (projectId: string) => {
    const response = await axios.post(`${API_BASE_URL}/terminal/open`, { projectId });
    return response.data;
  },

  startBuild: async (projectId: string, environment: 'development' | 'staging' | 'production') => {
    const response = await axios.post(`${API_BASE_URL}/build`, {
      projectId,
      environment,
    });
    return response.data;
  },

  reportBug: async (bugReport: {
    title: string;
    description: string;
    severity: 'low' | 'medium' | 'high';
    reproducible: boolean;
    steps?: string[];
  }) => {
    const response = await axios.post(`${API_BASE_URL}/bugs`, bugReport);
    return response.data;
  },

  generateDocumentation: async (projectId: string, options: {
    type: 'api' | 'code' | 'user';
    format: 'markdown' | 'html' | 'pdf';
    sections?: string[];
  }) => {
    const response = await axios.post(`${API_BASE_URL}/documentation/generate`, {
      projectId,
      ...options,
    });
    return response.data;
  },
}; 