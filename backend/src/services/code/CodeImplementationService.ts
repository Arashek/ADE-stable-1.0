import { Server, Socket } from 'socket.io';
import { DatabaseService } from '../DatabaseService';
import { FileService } from '../FileService';
import { CodeAnalyzer } from './CodeAnalyzer';
import { CodeCompiler } from './CodeCompiler';
import { CodeValidator } from './CodeValidator';
import { CodeImplementation, CodeFile, CodeAnalysis } from '../../../frontend/src/services/CodeImplementationService';

interface Session {
  socket: Socket;
  projectId: string;
  sessionId: string;
}

export class CodeImplementationService {
  private sessions: Map<string, Session> = new Map();
  private projectSessions: Map<string, Set<string>> = new Map();

  constructor(
    private io: Server,
    private db: DatabaseService,
    private fileService: FileService,
    private analyzer: CodeAnalyzer,
    private compiler: CodeCompiler,
    private validator: CodeValidator
  ) {
    this.setupEventListeners();
  }

  private setupEventListeners() {
    this.io.on('connection', (socket: Socket) => {
      socket.on('code:connect', this.handleConnect.bind(this, socket));
      socket.on('code:disconnect', this.handleDisconnect.bind(this, socket));
      socket.on('code:save', this.handleSave.bind(this, socket));
      socket.on('code:update-file', this.handleUpdateFile.bind(this, socket));
      socket.on('code:analyze', this.handleAnalyze.bind(this, socket));
      socket.on('code:compile', this.handleCompile.bind(this, socket));
      socket.on('code:add-feedback', this.handleAddFeedback.bind(this, socket));
    });
  }

  private async handleConnect(socket: Socket, data: { projectId: string; sessionId: string }) {
    const { projectId, sessionId } = data;
    this.sessions.set(sessionId, { socket, projectId, sessionId });

    if (!this.projectSessions.has(projectId)) {
      this.projectSessions.set(projectId, new Set());
    }
    this.projectSessions.get(projectId)?.add(sessionId);

    // Load existing implementations
    const implementations = await this.db.getCodeImplementations(projectId);
    socket.emit('code:update', { implementation: implementations[0] });
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
    implementation: CodeImplementation;
  }) {
    try {
      const { projectId, implementation } = data;

      // Validate implementation
      const validationResult = await this.validator.validateImplementation(implementation);
      if (!validationResult.isValid) {
        socket.emit('code:error', { error: validationResult.errors.join(', ') });
        return;
      }

      // Save implementation to database
      await this.db.saveCodeImplementation(projectId, implementation);

      // Save files to storage
      for (const file of implementation.files) {
        await this.fileService.saveFile(file.path, file.content);
      }

      // Analyze code
      for (const file of implementation.files) {
        const analysis = await this.analyzer.analyzeFile(file);
        socket.emit('code:analysis', { fileId: file.id, analysis });
      }

      // Broadcast update to all project sessions
      this.broadcastToProject(projectId, 'code:update', { implementation });
    } catch (error) {
      socket.emit('code:error', { error: error.message });
    }
  }

  private async handleUpdateFile(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    fileId: string;
    updates: Partial<CodeFile>;
  }) {
    try {
      const { projectId, fileId, updates } = data;

      // Get current implementation
      const implementation = await this.db.getCodeImplementation(projectId);
      if (!implementation) {
        socket.emit('code:error', { error: 'Implementation not found' });
        return;
      }

      // Find and update file
      const fileIndex = implementation.files.findIndex(f => f.id === fileId);
      if (fileIndex === -1) {
        socket.emit('code:error', { error: 'File not found' });
        return;
      }

      const updatedFile = {
        ...implementation.files[fileIndex],
        ...updates,
        lastModified: new Date(),
      };

      implementation.files[fileIndex] = updatedFile;

      // Validate implementation
      const validationResult = await this.validator.validateImplementation(implementation);
      if (!validationResult.isValid) {
        socket.emit('code:error', { error: validationResult.errors.join(', ') });
        return;
      }

      // Save implementation to database
      await this.db.saveCodeImplementation(projectId, implementation);

      // Save file to storage
      await this.fileService.saveFile(updatedFile.path, updatedFile.content);

      // Analyze updated file
      const analysis = await this.analyzer.analyzeFile(updatedFile);
      socket.emit('code:analysis', { fileId, analysis });

      // Broadcast update to all project sessions
      this.broadcastToProject(projectId, 'code:update', { implementation });
    } catch (error) {
      socket.emit('code:error', { error: error.message });
    }
  }

  private async handleAnalyze(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    fileId: string;
  }) {
    try {
      const { projectId, fileId } = data;

      // Get implementation and file
      const implementation = await this.db.getCodeImplementation(projectId);
      if (!implementation) {
        socket.emit('code:error', { error: 'Implementation not found' });
        return;
      }

      const file = implementation.files.find(f => f.id === fileId);
      if (!file) {
        socket.emit('code:error', { error: 'File not found' });
        return;
      }

      // Analyze file
      const analysis = await this.analyzer.analyzeFile(file);
      socket.emit('code:analysis', { fileId, analysis });
    } catch (error) {
      socket.emit('code:error', { error: error.message });
    }
  }

  private async handleCompile(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    implementationId: string;
  }) {
    try {
      const { projectId, implementationId } = data;

      // Get implementation
      const implementation = await this.db.getCodeImplementation(projectId);
      if (!implementation) {
        socket.emit('code:error', { error: 'Implementation not found' });
        return;
      }

      // Compile implementation
      const result = await this.compiler.compileImplementation(implementation);
      socket.emit('code:compilation', result);

      if (result.success) {
        // Update implementation status
        implementation.status = 'implemented';
        await this.db.saveCodeImplementation(projectId, implementation);

        // Broadcast update to all project sessions
        this.broadcastToProject(projectId, 'code:update', { implementation });
      }
    } catch (error) {
      socket.emit('code:error', { error: error.message });
    }
  }

  private async handleAddFeedback(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    implementationId: string;
    feedback: {
      from: string;
      comment: string;
    };
  }) {
    try {
      const { projectId, implementationId, feedback } = data;

      // Get implementation
      const implementation = await this.db.getCodeImplementation(projectId);
      if (!implementation) {
        socket.emit('code:error', { error: 'Implementation not found' });
        return;
      }

      // Add feedback
      const newFeedback = {
        id: Date.now().toString(),
        ...feedback,
        timestamp: new Date(),
        status: 'pending' as const,
      };

      if (!implementation.feedback) {
        implementation.feedback = [];
      }
      implementation.feedback.push(newFeedback);

      // Save implementation to database
      await this.db.saveCodeImplementation(projectId, implementation);

      // Broadcast update to all project sessions
      this.broadcastToProject(projectId, 'code:update', { implementation });
    } catch (error) {
      socket.emit('code:error', { error: error.message });
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