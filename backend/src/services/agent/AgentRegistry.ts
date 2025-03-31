import { singleton } from 'tsyringe';
import { Logger } from '../logger/Logger';
import { AgentService, AgentConfig, AgentCapability } from './AgentService';
import { Subject, Observable } from 'rxjs';
import { WebSocket } from 'ws';

export interface AgentRegistration {
  agentId: string;
  timestamp: Date;
  status: 'active' | 'inactive' | 'error';
  error?: string;
  previewUrl?: string;
  collaborators?: string[];
  lastActivity?: Date;
}

export interface AgentActivity {
  agentId: string;
  action: string;
  timestamp: Date;
  data?: any;
}

export interface CollaborationRequest {
  sourceAgentId: string;
  targetAgentId: string;
  action: 'start' | 'end';
  context?: any;
}

@singleton()
export class AgentRegistry {
  private static instance: AgentRegistry;
  private registrations: Map<string, AgentRegistration>;
  private logger: Logger;
  private agentService: AgentService;
  private activitySubject: Subject<AgentActivity>;
  private collaborationSubject: Subject<CollaborationRequest>;
  private previewSockets: Map<string, Set<WebSocket>>;

  constructor(logger: Logger, agentService: AgentService) {
    this.logger = logger;
    this.agentService = agentService;
    this.registrations = new Map();
    this.activitySubject = new Subject();
    this.collaborationSubject = new Subject();
    this.previewSockets = new Map();
  }

  public static getInstance(logger: Logger, agentService: AgentService): AgentRegistry {
    if (!AgentRegistry.instance) {
      AgentRegistry.instance = new AgentRegistry(logger, agentService);
    }
    return AgentRegistry.instance;
  }

  public async registerAgent(config: AgentConfig): Promise<AgentRegistration> {
    try {
      await this.agentService.registerAgent(config);
      
      const registration: AgentRegistration = {
        agentId: config.id,
        timestamp: new Date(),
        status: 'active',
        collaborators: [],
        lastActivity: new Date()
      };
      
      this.registrations.set(config.id, registration);
      this.logger.info(`Agent ${config.id} registered successfully in registry`);
      
      // Initialize preview socket set for this agent
      this.previewSockets.set(config.id, new Set());
      
      // Emit registration activity
      this.emitActivity({
        agentId: config.id,
        action: 'register',
        timestamp: new Date(),
        data: { config }
      });
      
      return registration;
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Unknown error';
      const registration: AgentRegistration = {
        agentId: config.id,
        timestamp: new Date(),
        status: 'error',
        error: errorMsg
      };
      
      this.registrations.set(config.id, registration);
      this.logger.error(`Failed to register agent ${config.id}:`, error);
      
      return registration;
    }
  }

  public async unregisterAgent(agentId: string): Promise<void> {
    try {
      await this.agentService.unregisterAgent(agentId);
      this.registrations.delete(agentId);
      
      // Close and clear all preview sockets
      const sockets = this.previewSockets.get(agentId);
      if (sockets) {
        sockets.forEach(socket => socket.close());
        this.previewSockets.delete(agentId);
      }
      
      // Emit unregister activity
      this.emitActivity({
        agentId,
        action: 'unregister',
        timestamp: new Date()
      });
      
      this.logger.info(`Agent ${agentId} unregistered successfully from registry`);
    } catch (error) {
      this.logger.error(`Failed to unregister agent ${agentId}:`, error);
      throw error;
    }
  }

  public getRegistration(agentId: string): AgentRegistration | undefined {
    return this.registrations.get(agentId);
  }

  public getAllRegistrations(): AgentRegistration[] {
    return Array.from(this.registrations.values());
  }

  public async getActiveAgents(): Promise<AgentConfig[]> {
    const activeAgents: AgentConfig[] = [];
    
    for (const [agentId, registration] of this.registrations) {
      if (registration.status === 'active') {
        const agent = this.agentService.getAgent(agentId);
        if (agent && agent.isActive) {
          activeAgents.push(agent);
        }
      }
    }
    
    return activeAgents;
  }

  public async findAgentsByCapability(capability: string): Promise<AgentConfig[]> {
    const agents = await this.getActiveAgents();
    return agents.filter(agent => 
      agent.capabilities.some(cap => cap.supportedActions.includes(capability))
    );
  }

  public async updateAgentStatus(
    agentId: string,
    status: 'active' | 'inactive' | 'error',
    error?: string
  ): Promise<void> {
    const registration = this.registrations.get(agentId);
    if (!registration) {
      throw new Error(`Agent ${agentId} not found in registry`);
    }

    registration.status = status;
    registration.error = error;
    registration.lastActivity = new Date();
    
    this.emitActivity({
      agentId,
      action: 'status_update',
      timestamp: new Date(),
      data: { status, error }
    });
    
    this.logger.info(`Updated status for agent ${agentId} to ${status}`);
  }

  public subscribeToActivity(): Observable<AgentActivity> {
    return this.activitySubject.asObservable();
  }

  public subscribeToCollaboration(): Observable<CollaborationRequest> {
    return this.collaborationSubject.asObservable();
  }

  public async startCollaboration(request: CollaborationRequest): Promise<void> {
    const sourceReg = this.registrations.get(request.sourceAgentId);
    const targetReg = this.registrations.get(request.targetAgentId);

    if (!sourceReg || !targetReg) {
      throw new Error('One or both agents not found');
    }

    if (!sourceReg.collaborators) sourceReg.collaborators = [];
    if (!targetReg.collaborators) targetReg.collaborators = [];

    sourceReg.collaborators.push(request.targetAgentId);
    targetReg.collaborators.push(request.sourceAgentId);

    this.collaborationSubject.next(request);
    
    this.logger.info(`Started collaboration between agents ${request.sourceAgentId} and ${request.targetAgentId}`);
  }

  public async endCollaboration(request: CollaborationRequest): Promise<void> {
    const sourceReg = this.registrations.get(request.sourceAgentId);
    const targetReg = this.registrations.get(request.targetAgentId);

    if (!sourceReg || !targetReg) {
      throw new Error('One or both agents not found');
    }

    if (sourceReg.collaborators) {
      sourceReg.collaborators = sourceReg.collaborators.filter(id => id !== request.targetAgentId);
    }
    if (targetReg.collaborators) {
      targetReg.collaborators = targetReg.collaborators.filter(id => id !== request.sourceAgentId);
    }

    this.collaborationSubject.next(request);
    
    this.logger.info(`Ended collaboration between agents ${request.sourceAgentId} and ${request.targetAgentId}`);
  }

  public registerPreviewSocket(agentId: string, socket: WebSocket): void {
    let sockets = this.previewSockets.get(agentId);
    if (!sockets) {
      sockets = new Set();
      this.previewSockets.set(agentId, sockets);
    }
    sockets.add(socket);

    // Handle socket closure
    socket.on('close', () => {
      this.unregisterPreviewSocket(agentId, socket);
    });
  }

  public unregisterPreviewSocket(agentId: string, socket: WebSocket): void {
    const sockets = this.previewSockets.get(agentId);
    if (sockets) {
      sockets.delete(socket);
      if (sockets.size === 0) {
        this.previewSockets.delete(agentId);
      }
    }
  }

  public broadcastPreviewUpdate(agentId: string, data: any): void {
    const sockets = this.previewSockets.get(agentId);
    if (sockets) {
      const message = JSON.stringify({
        type: 'preview_update',
        agentId,
        data,
        timestamp: new Date()
      });

      sockets.forEach(socket => {
        if (socket.readyState === WebSocket.OPEN) {
          socket.send(message);
        }
      });
    }
  }

  private emitActivity(activity: AgentActivity): void {
    this.activitySubject.next(activity);
  }
} 