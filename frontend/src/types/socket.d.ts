import { Socket as BaseSocket } from 'socket.io-client';
import { Agent, AgentTask } from '../services/AgentCollaborationService';

interface ServerToClientEvents {
  'agent:status-update': (data: { agentId: string; status: Agent['status'] }) => void;
  'task:update': (data: { taskId: string; updates: Partial<AgentTask> }) => void;
  'codebase:change': (data: { componentId: string; changes: any }) => void;
  'agent:message': (data: { from: string; to: string; message: any }) => void;
}

interface ClientToServerEvents {
  'agent:register': (data: { projectId: string; agent: Agent }) => void;
  'codebase:initialize': (data: { projectId: string; sessionId: string }, callback: (data: any) => void) => void;
  'agent:notification': (data: { projectId: string; agentId: string; type: string; data: any }) => void;
}

export type Socket = BaseSocket<ServerToClientEvents, ClientToServerEvents>; 