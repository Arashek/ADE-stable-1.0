import { Socket } from 'socket.io-client';
import { v4 as uuidv4 } from 'uuid';
import { AgentCollaborationService, AgentType } from './AgentCollaborationService';

export interface AgentIntegrationConfig {
  ws: Socket;
  projectId: string;
  codeEditingService: any; // Replace with actual type
  ideCommunicationService: any; // Replace with actual type
  collaborativeEditingService: any; // Replace with actual type
  codeNavigationService: any; // Replace with actual type
}

export class AgentIntegrationService {
  private ws: Socket;
  private projectId: string;
  private agentCollaboration: AgentCollaborationService;
  private codeEditingService: any;
  private ideCommunicationService: any;
  private collaborativeEditingService: any;
  private codeNavigationService: any;
  private sessionId: string;

  constructor(config: AgentIntegrationConfig) {
    this.ws = config.ws;
    this.projectId = config.projectId;
    this.sessionId = uuidv4();
    this.codeEditingService = config.codeEditingService;
    this.ideCommunicationService = config.ideCommunicationService;
    this.collaborativeEditingService = config.collaborativeEditingService;
    this.codeNavigationService = config.codeNavigationService;

    this.agentCollaboration = new AgentCollaborationService({
      ws: this.ws,
      projectId: this.projectId
    });
  }

  public async initialize() {
    await this.agentCollaboration.initialize();
    this.setupEventListeners();
  }

  private setupEventListeners() {
    // Code editing events
    this.ws.on('code:edit', (data: any) => {
      this.handleCodeEdit(data);
    });

    // IDE communication events
    this.ws.on('ide:message', (data: any) => {
      this.handleIDEMessage(data);
    });

    // Collaborative editing events
    this.ws.on('collab:edit', (data: any) => {
      this.handleCollaborativeEdit(data);
    });

    // Code navigation events
    this.ws.on('code:navigate', (data: any) => {
      this.handleCodeNavigation(data);
    });
  }

  private handleCodeEdit(data: any) {
    this.codeEditingService.applyEdit(data);
  }

  private handleIDEMessage(data: any) {
    this.ideCommunicationService.processMessage(data);
  }

  private handleCollaborativeEdit(data: any) {
    this.collaborativeEditingService.processEdit(data);
  }

  private handleCodeNavigation(data: any) {
    this.codeNavigationService.navigate(data);
  }

  public async sendMessageToAgent(message: string): Promise<string> {
    return this.agentCollaboration.sendMessage(message);
  }

  public dispose() {
    this.agentCollaboration.dispose();
  }
}