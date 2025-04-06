import { Socket as IOSocket } from 'socket.io-client';

// Client to server events
export interface ClientToServerEvents {
  'agent:register': (data: { projectId: string; agent: any }) => void;
  'codebase:initialize': (data: any) => void;
  'agent:notification': (data: any) => void;
  'agent:status-updated': (data: { projectId: string; agentId: string; status: string }) => void;
  'task:created': (data: { projectId: string; task: any }) => void;
  'task:status-updated': (data: { projectId: string; taskId: string; status: string }) => void;
  'agent:message': (data: { projectId: string; from: string; to: string; message: any }) => void;
  'agent:dispose': (data: { projectId: string; sessionId: string }) => void;
  'agent:request': (data: { id: string; projectId: string; message: string }) => void;
}

// Server to client events
export interface ServerToClientEvents {
  'agent:status-update': (data: { agentId: string; status: string }) => void;
  'task:update': (data: { taskId: string; updates: any }) => void;
  'codebase:change': (data: { componentId: string; changes: any }) => void;
  'agent:message': (data: { from: string; to: string; message: any }) => void;
  'agent:response': (data: { id: string; response: string }) => void;
}

// Socket.io with typed events
export type Socket = IOSocket<ServerToClientEvents, ClientToServerEvents>;
