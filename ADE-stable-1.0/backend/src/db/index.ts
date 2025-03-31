import { PrismaClient } from '@prisma/client';

export const db = new PrismaClient();

// Database schema types
export interface ModelInteraction {
  id: string;
  projectId: string;
  timestamp: Date;
  startTime: Date;
  endTime: Date;
  status: 'success' | 'error';
  tokenUsage: number;
  cost: number;
}

export interface AgentActivity {
  id: string;
  projectId: string;
  timestamp: Date;
  type: 'task' | 'error' | 'coordination';
  status: 'completed' | 'recovered' | 'success' | 'failed';
  resourceUsage?: number;
}

export interface ApiCall {
  id: string;
  projectId: string;
  timestamp: Date;
  startTime: Date;
  endTime: Date;
  cost: number;
}

export interface SystemResource {
  id: string;
  projectId: string;
  timestamp: Date;
  cpuUsage: number;
  memoryUsage: number;
  diskUsage: number;
}

export interface TaskQueue {
  id: string;
  projectId: string;
  timestamp: Date;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

export interface CodeAssessment {
  id: string;
  projectId: string;
  timestamp: Date;
  complexityScore: number;
  maintainabilityScore: number;
  reliabilityScore: number;
  testCoverage: number;
  apiDocsScore: number;
  codeCommentsScore: number;
  readmeScore: number;
  potentialIssues: number;
  preventedIssues: number;
} 