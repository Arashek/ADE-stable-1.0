import { Server } from 'socket.io';
import { Server as HttpServer } from 'http';
import { AgentRegistry } from '../agent/AgentRegistry';
import { Logger } from '../logger/Logger';
import { ConfigService } from '../config/ConfigService';
import { authenticateSocket } from '../../middleware/auth';

export class AgentWebSocketServer {
  private io: Server;
  private agentRegistry: AgentRegistry;
  private logger: Logger;

  constructor(
    httpServer: HttpServer,
    agentRegistry: AgentRegistry,
    logger: Logger,
    config: ConfigService
  ) {
    this.agentRegistry = agentRegistry;
    this.logger = logger;

    this.io = new Server(httpServer, {
      cors: {
        origin: config.get('CORS_ORIGIN'),
        methods: ['GET', 'POST'],
        credentials: true
      }
    });

    this.setupMiddleware();
    this.setupEventHandlers();
  }

  private setupMiddleware(): void {
    this.io.use(authenticateSocket);
  }

  private setupEventHandlers(): void {
    this.io.on('connection', (socket) => {
      this.logger.info(`Client connected: ${socket.id}`);

      // Handle agent preview subscriptions
      socket.on('subscribe:agent-preview', async (agentId: string) => {
        try {
          const registration = this.agentRegistry.getRegistration(agentId);
          if (!registration) {
            socket.emit('error', { message: `Agent ${agentId} not found` });
            return;
          }

          // Join agent-specific room
          socket.join(`agent:${agentId}`);
          this.agentRegistry.registerPreviewSocket(agentId, socket as any);

          // Send initial state
          socket.emit('agent-preview:state', {
            agentId,
            status: registration.status,
            lastActivity: registration.lastActivity,
            collaborators: registration.collaborators
          });

          this.logger.info(`Client ${socket.id} subscribed to agent ${agentId} preview`);
        } catch (error) {
          this.logger.error(`Failed to subscribe to agent preview: ${error}`);
          socket.emit('error', { message: 'Failed to subscribe to agent preview' });
        }
      });

      // Handle agent collaboration requests
      socket.on('collaboration:request', async (data: {
        sourceAgentId: string;
        targetAgentId: string;
        action: 'start' | 'end';
        context?: any;
      }) => {
        try {
          await this.agentRegistry.startCollaboration(data);
          this.io.to(`agent:${data.sourceAgentId}`).to(`agent:${data.targetAgentId}`)
            .emit('collaboration:update', {
              ...data,
              timestamp: new Date()
            });
        } catch (error) {
          this.logger.error(`Failed to handle collaboration request: ${error}`);
          socket.emit('error', { message: 'Failed to process collaboration request' });
        }
      });

      // Handle disconnection
      socket.on('disconnect', () => {
        this.logger.info(`Client disconnected: ${socket.id}`);
      });
    });

    // Subscribe to agent registry events
    this.agentRegistry.subscribeToActivity().subscribe(activity => {
      this.io.to(`agent:${activity.agentId}`).emit('agent:activity', activity);
    });

    this.agentRegistry.subscribeToCollaboration().subscribe(collaboration => {
      this.io.to(`agent:${collaboration.sourceAgentId}`)
        .to(`agent:${collaboration.targetAgentId}`)
        .emit('collaboration:update', {
          ...collaboration,
          timestamp: new Date()
        });
    });
  }

  public broadcastAgentUpdate(agentId: string, data: any): void {
    this.io.to(`agent:${agentId}`).emit('agent:update', {
      agentId,
      data,
      timestamp: new Date()
    });
  }

  public broadcastCapabilityUpdate(agentId: string, capabilityId: string, data: any): void {
    this.io.to(`agent:${agentId}`).emit('capability:update', {
      agentId,
      capabilityId,
      data,
      timestamp: new Date()
    });
  }

  public broadcastLLMUpdate(llmId: string, data: any): void {
    this.io.emit('llm:update', {
      llmId,
      data,
      timestamp: new Date()
    });
  }

  public close(): void {
    this.io.close();
  }
} 