import { Server, Socket } from 'socket.io';
import { DatabaseService } from '../DatabaseService';
import { FileService } from '../FileService';
import { ArchitectureAnalyzer } from './ArchitectureAnalyzer';
import { ArchitectureValidator } from './ArchitectureValidator';
import { ArchitectureRenderer } from './ArchitectureRenderer';
import { ArchitectureSpec, ArchitectureComponent, ArchitectureConnection, ArchitectureAnalysis } from '../../../frontend/src/services/ArchitectureService';

interface Session {
  socket: Socket;
  projectId: string;
  sessionId: string;
}

export class ArchitectureService {
  private sessions: Map<string, Session> = new Map();
  private projectSessions: Map<string, Set<string>> = new Map();

  constructor(
    private io: Server,
    private db: DatabaseService,
    private fileService: FileService,
    private analyzer: ArchitectureAnalyzer,
    private validator: ArchitectureValidator,
    private renderer: ArchitectureRenderer
  ) {
    this.setupEventListeners();
  }

  private setupEventListeners() {
    this.io.on('connection', (socket: Socket) => {
      socket.on('architecture:connect', this.handleConnect.bind(this, socket));
      socket.on('architecture:disconnect', this.handleDisconnect.bind(this, socket));
      socket.on('architecture:save', this.handleSave.bind(this, socket));
      socket.on('architecture:update-component', this.handleUpdateComponent.bind(this, socket));
      socket.on('architecture:update-connection', this.handleUpdateConnection.bind(this, socket));
      socket.on('architecture:analyze', this.handleAnalyze.bind(this, socket));
      socket.on('architecture:validate', this.handleValidate.bind(this, socket));
      socket.on('architecture:add-feedback', this.handleAddFeedback.bind(this, socket));
    });
  }

  private async handleConnect(socket: Socket, data: { projectId: string; sessionId: string }) {
    const { projectId, sessionId } = data;
    this.sessions.set(sessionId, { socket, projectId, sessionId });

    if (!this.projectSessions.has(projectId)) {
      this.projectSessions.set(projectId, new Set());
    }
    this.projectSessions.get(projectId)?.add(sessionId);

    // Load existing architecture
    const architecture = await this.db.getArchitecture(projectId);
    if (architecture) {
      socket.emit('architecture:update', { architecture });
    }
  }

  private handleDisconnect(socket: Socket, data: { projectId: string; sessionId: string }) {
    const { projectId, sessionId } = data;
    this.sessions.delete(sessionId);
    this.projectSessions.get(projectId)?.delete(sessionId);

    if (this.projectSessions.get(projectId)?.size === 0) {
      this.projectSessions.delete(projectId);
    }
  }

  private async handleSave(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    architecture: ArchitectureSpec;
  }) {
    try {
      const { projectId, architecture } = data;

      // Validate architecture
      const validationResult = await this.validator.validateArchitecture(architecture);
      if (!validationResult.isValid) {
        socket.emit('architecture:error', { error: validationResult.errors.join(', ') });
        return;
      }

      // Save architecture to database
      await this.db.saveArchitecture(projectId, architecture);

      // Analyze architecture
      const analysis = await this.analyzer.analyzeArchitecture(architecture);
      socket.emit('architecture:analysis', { analysis });

      // Broadcast update to all project sessions
      this.broadcastToProject(projectId, 'architecture:update', { architecture });
    } catch (error) {
      socket.emit('architecture:error', { error: error.message });
    }
  }

  private async handleUpdateComponent(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    componentId: string;
    updates: Partial<ArchitectureComponent>;
  }) {
    try {
      const { projectId, componentId, updates } = data;

      // Get current architecture
      const architecture = await this.db.getArchitecture(projectId);
      if (!architecture) {
        socket.emit('architecture:error', { error: 'Architecture not found' });
        return;
      }

      // Find and update component
      const componentIndex = architecture.components.findIndex(c => c.id === componentId);
      if (componentIndex === -1) {
        socket.emit('architecture:error', { error: 'Component not found' });
        return;
      }

      architecture.components[componentIndex] = {
        ...architecture.components[componentIndex],
        ...updates,
      };

      // Validate architecture
      const validationResult = await this.validator.validateArchitecture(architecture);
      if (!validationResult.isValid) {
        socket.emit('architecture:error', { error: validationResult.errors.join(', ') });
        return;
      }

      // Save architecture to database
      await this.db.saveArchitecture(projectId, architecture);

      // Analyze architecture
      const analysis = await this.analyzer.analyzeArchitecture(architecture);
      socket.emit('architecture:analysis', { analysis });

      // Broadcast update to all project sessions
      this.broadcastToProject(projectId, 'architecture:update', { architecture });
    } catch (error) {
      socket.emit('architecture:error', { error: error.message });
    }
  }

  private async handleUpdateConnection(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    connectionId: string;
    updates: Partial<ArchitectureConnection>;
  }) {
    try {
      const { projectId, connectionId, updates } = data;

      // Get current architecture
      const architecture = await this.db.getArchitecture(projectId);
      if (!architecture) {
        socket.emit('architecture:error', { error: 'Architecture not found' });
        return;
      }

      // Find and update connection
      const connectionIndex = architecture.connections.findIndex(c => c.id === connectionId);
      if (connectionIndex === -1) {
        socket.emit('architecture:error', { error: 'Connection not found' });
        return;
      }

      architecture.connections[connectionIndex] = {
        ...architecture.connections[connectionIndex],
        ...updates,
      };

      // Validate architecture
      const validationResult = await this.validator.validateArchitecture(architecture);
      if (!validationResult.isValid) {
        socket.emit('architecture:error', { error: validationResult.errors.join(', ') });
        return;
      }

      // Save architecture to database
      await this.db.saveArchitecture(projectId, architecture);

      // Analyze architecture
      const analysis = await this.analyzer.analyzeArchitecture(architecture);
      socket.emit('architecture:analysis', { analysis });

      // Broadcast update to all project sessions
      this.broadcastToProject(projectId, 'architecture:update', { architecture });
    } catch (error) {
      socket.emit('architecture:error', { error: error.message });
    }
  }

  private async handleAnalyze(socket: Socket, data: {
    projectId: string;
    sessionId: string;
  }) {
    try {
      const { projectId } = data;

      // Get architecture
      const architecture = await this.db.getArchitecture(projectId);
      if (!architecture) {
        socket.emit('architecture:error', { error: 'Architecture not found' });
        return;
      }

      // Analyze architecture
      const analysis = await this.analyzer.analyzeArchitecture(architecture);
      socket.emit('architecture:analysis', { analysis });
    } catch (error) {
      socket.emit('architecture:error', { error: error.message });
    }
  }

  private async handleValidate(socket: Socket, data: {
    projectId: string;
    sessionId: string;
  }) {
    try {
      const { projectId } = data;

      // Get architecture
      const architecture = await this.db.getArchitecture(projectId);
      if (!architecture) {
        socket.emit('architecture:error', { error: 'Architecture not found' });
        return;
      }

      // Validate architecture
      const validationResult = await this.validator.validateArchitecture(architecture);
      socket.emit('architecture:validation', validationResult);
    } catch (error) {
      socket.emit('architecture:error', { error: error.message });
    }
  }

  private async handleAddFeedback(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    architectureId: string;
    feedback: {
      from: string;
      comment: string;
    };
  }) {
    try {
      const { projectId, architectureId, feedback } = data;

      // Get architecture
      const architecture = await this.db.getArchitecture(projectId);
      if (!architecture) {
        socket.emit('architecture:error', { error: 'Architecture not found' });
        return;
      }

      // Add feedback
      const newFeedback = {
        id: Date.now().toString(),
        ...feedback,
        timestamp: new Date(),
        status: 'pending' as const,
      };

      if (!architecture.feedback) {
        architecture.feedback = [];
      }
      architecture.feedback.push(newFeedback);

      // Save architecture to database
      await this.db.saveArchitecture(projectId, architecture);

      // Broadcast update to all project sessions
      this.broadcastToProject(projectId, 'architecture:update', { architecture });
    } catch (error) {
      socket.emit('architecture:error', { error: error.message });
    }
  }

  private broadcastToProject(projectId: string, event: string, data: any) {
    const sessions = this.projectSessions.get(projectId);
    if (sessions) {
      sessions.forEach(sessionId => {
        const session = this.sessions.get(sessionId);
        if (session) {
          session.socket.emit(event, data);
        }
      });
    }
  }
} 