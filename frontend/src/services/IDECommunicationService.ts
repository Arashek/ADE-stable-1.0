import { Socket } from 'socket.io-client';
import { v4 as uuidv4 } from 'uuid';

export interface IDEConfig {
  type: 'vscode' | 'jetbrains' | 'web';
  version: string;
  capabilities: string[];
  extensions?: string[];
}

export interface IDEMessage {
  type: string;
  payload: any;
  metadata: {
    timestamp: Date;
    source: string;
    target: string;
  };
}

export class IDECommunicationService {
  private ws: Socket;
  private projectId: string;
  private sessionId: string;
  private ideConfig: IDEConfig;
  private messageQueue: IDEMessage[] = [];
  private isConnected: boolean = false;

  constructor(config: { ws: Socket; projectId: string; ideConfig: IDEConfig }) {
    this.ws = config.ws;
    this.projectId = config.projectId;
    this.sessionId = uuidv4();
    this.ideConfig = config.ideConfig;
  }

  public async initialize() {
    this.setupEventListeners();
    await this.establishConnection();
    this.setupCapabilities();
  }

  private setupEventListeners() {
    // Connection events
    this.ws.on('ide:connected', () => {
      this.handleConnection();
    });

    this.ws.on('ide:disconnected', () => {
      this.handleDisconnection();
    });

    // Message events
    this.ws.on('ide:message', (data: IDEMessage) => {
      this.handleMessage(data);
    });

    // Capability events
    this.ws.on('ide:capability-update', (data: { capabilities: string[] }) => {
      this.handleCapabilityUpdate(data);
    });

    // Extension events
    this.ws.on('ide:extension-update', (data: { extensions: string[] }) => {
      this.handleExtensionUpdate(data);
    });
  }

  private async establishConnection() {
    this.ws.emit('ide:connect', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      config: this.ideConfig
    });
  }

  private handleConnection() {
    this.isConnected = true;
    this.processMessageQueue();
  }

  private handleDisconnection() {
    this.isConnected = false;
  }

  private handleMessage(message: IDEMessage) {
    switch (message.type) {
      case 'file:open':
        this.handleFileOpen(message.payload);
        break;
      case 'file:save':
        this.handleFileSave(message.payload);
        break;
      case 'file:close':
        this.handleFileClose(message.payload);
        break;
      case 'command:execute':
        this.handleCommandExecution(message.payload);
        break;
      case 'debug:start':
        this.handleDebugStart(message.payload);
        break;
      case 'debug:stop':
        this.handleDebugStop(message.payload);
        break;
      default:
        console.warn(`Unknown message type: ${message.type}`);
    }
  }

  private handleCapabilityUpdate(data: { capabilities: string[] }) {
    this.ideConfig.capabilities = data.capabilities;
    this.ws.emit('ide:capability-acknowledged', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      capabilities: this.ideConfig.capabilities
    });
  }

  private handleExtensionUpdate(data: { extensions: string[] }) {
    if (this.ideConfig.extensions) {
      this.ideConfig.extensions = data.extensions;
      this.ws.emit('ide:extension-acknowledged', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        extensions: this.ideConfig.extensions
      });
    }
  }

  private handleFileOpen(payload: any) {
    // Handle file open request
    this.ws.emit('file:open', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      ...payload
    });
  }

  private handleFileSave(payload: any) {
    // Handle file save request
    this.ws.emit('file:save', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      ...payload
    });
  }

  private handleFileClose(payload: any) {
    // Handle file close request
    this.ws.emit('file:close', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      ...payload
    });
  }

  private handleCommandExecution(payload: any) {
    // Handle command execution request
    this.ws.emit('command:execute', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      ...payload
    });
  }

  private handleDebugStart(payload: any) {
    // Handle debug start request
    this.ws.emit('debug:start', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      ...payload
    });
  }

  private handleDebugStop(payload: any) {
    // Handle debug stop request
    this.ws.emit('debug:stop', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      ...payload
    });
  }

  private setupCapabilities() {
    // Set up IDE-specific capabilities
    switch (this.ideConfig.type) {
      case 'vscode':
        this.setupVSCodeCapabilities();
        break;
      case 'jetbrains':
        this.setupJetBrainsCapabilities();
        break;
      case 'web':
        this.setupWebIDECapabilities();
        break;
    }
  }

  private setupVSCodeCapabilities() {
    // Set up VSCode-specific capabilities
    this.ws.emit('ide:capability-setup', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      capabilities: [
        'file:open',
        'file:save',
        'file:close',
        'command:execute',
        'debug:start',
        'debug:stop',
        'completion:provide',
        'hover:provide',
        'definition:provide',
        'reference:provide'
      ]
    });
  }

  private setupJetBrainsCapabilities() {
    // Set up JetBrains-specific capabilities
    this.ws.emit('ide:capability-setup', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      capabilities: [
        'file:open',
        'file:save',
        'file:close',
        'command:execute',
        'debug:start',
        'debug:stop',
        'completion:provide',
        'hover:provide',
        'definition:provide',
        'reference:provide',
        'refactoring:provide',
        'intention:provide',
        'quickfix:provide'
      ]
    });
  }

  private setupWebIDECapabilities() {
    // Set up web IDE-specific capabilities
    this.ws.emit('ide:capability-setup', {
      projectId: this.projectId,
      sessionId: this.sessionId,
      capabilities: [
        'file:open',
        'file:save',
        'file:close',
        'command:execute',
        'debug:start',
        'debug:stop',
        'completion:provide',
        'hover:provide',
        'definition:provide',
        'reference:provide',
        'collaboration:provide',
        'preview:provide'
      ]
    });
  }

  public async sendMessage(message: IDEMessage) {
    if (!this.isConnected) {
      this.messageQueue.push(message);
    } else {
      this.ws.emit('ide:message', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        ...message
      });
    }
  }

  private processMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      if (message) {
        this.sendMessage(message);
      }
    }
  }

  public dispose() {
    this.ws.emit('ide:disconnect', {
      projectId: this.projectId,
      sessionId: this.sessionId
    });
    this.messageQueue = [];
    this.isConnected = false;
  }
} 