import { Server, Socket } from 'socket.io';
import { v4 as uuidv4 } from 'uuid';
import { DesignSpec, DesignComponent, DesignSystem } from '../../../frontend/src/services/DesignAgentService';
import { DatabaseService } from '../database/DatabaseService';
import { FileService } from '../file/FileService';
import { PreviewGenerator } from './PreviewGenerator';
import { DesignValidator } from './DesignValidator';
import { DesignRenderer } from './DesignRenderer';

export class DesignService {
  private io: Server;
  private db: DatabaseService;
  private fileService: FileService;
  private previewGenerator: PreviewGenerator;
  private validator: DesignValidator;
  private renderer: DesignRenderer;
  private sessions: Map<string, { socket: Socket; projectId: string }> = new Map();

  constructor(
    io: Server,
    db: DatabaseService,
    fileService: FileService
  ) {
    this.io = io;
    this.db = db;
    this.fileService = fileService;
    this.previewGenerator = new PreviewGenerator();
    this.validator = new DesignValidator();
    this.renderer = new DesignRenderer();
  }

  public initialize() {
    this.setupEventListeners();
  }

  private setupEventListeners() {
    this.io.on('connection', (socket: Socket) => {
      socket.on('design:connect', this.handleConnect.bind(this, socket));
      socket.on('design:disconnect', this.handleDisconnect.bind(this, socket));
      socket.on('design:save', this.handleSave.bind(this, socket));
      socket.on('design:update', this.handleUpdate.bind(this, socket));
      socket.on('design:add-feedback', this.handleAddFeedback.bind(this, socket));
      socket.on('design:generate-preview', this.handleGeneratePreview.bind(this, socket));
      socket.on('design:implement', this.handleImplement.bind(this, socket));
    });
  }

  private async handleConnect(socket: Socket, data: { projectId: string; sessionId: string }) {
    const { projectId, sessionId } = data;
    this.sessions.set(sessionId, { socket, projectId });

    // Load existing design for the project
    const design = await this.db.getDesign(projectId);
    if (design) {
      socket.emit('design:update', { design });
    }

    // Load design system
    const system = await this.db.getDesignSystem(projectId);
    if (system) {
      socket.emit('design:system-update', { system });
    }
  }

  private handleDisconnect(socket: Socket, data: { projectId: string; sessionId: string }) {
    const { sessionId } = data;
    this.sessions.delete(sessionId);
  }

  private async handleSave(socket: Socket, data: { projectId: string; sessionId: string; design: DesignSpec }, callback: (response: any) => void) {
    try {
      const { projectId, design } = data;

      // Validate design
      const validationResult = await this.validator.validateDesign(design);
      if (!validationResult.isValid) {
        callback({ success: false, error: validationResult.errors.join(', ') });
        return;
      }

      // Save design to database
      await this.db.saveDesign(design);

      // Generate preview
      const preview = await this.previewGenerator.generatePreview(design);
      await this.fileService.savePreview(design.id, preview);

      // Notify other clients
      this.broadcastToProject(projectId, 'design:update', { design });
      this.broadcastToProject(projectId, 'design:preview-update', { designId: design.id, preview });

      callback({ success: true });
    } catch (error) {
      callback({ success: false, error: error.message });
    }
  }

  private async handleUpdate(socket: Socket, data: { projectId: string; designId: string; updates: Partial<DesignSpec> }, callback: (response: any) => void) {
    try {
      const { projectId, designId, updates } = data;

      // Get current design
      const currentDesign = await this.db.getDesign(designId);
      if (!currentDesign) {
        callback({ success: false, error: 'Design not found' });
        return;
      }

      // Merge updates
      const updatedDesign = { ...currentDesign, ...updates, updatedAt: new Date() };

      // Validate updated design
      const validationResult = await this.validator.validateDesign(updatedDesign);
      if (!validationResult.isValid) {
        callback({ success: false, error: validationResult.errors.join(', ') });
        return;
      }

      // Save updated design
      await this.db.updateDesign(designId, updatedDesign);

      // Generate new preview
      const preview = await this.previewGenerator.generatePreview(updatedDesign);
      await this.fileService.savePreview(designId, preview);

      // Notify other clients
      this.broadcastToProject(projectId, 'design:update', { design: updatedDesign });
      this.broadcastToProject(projectId, 'design:preview-update', { designId, preview });

      callback({ success: true });
    } catch (error) {
      callback({ success: false, error: error.message });
    }
  }

  private async handleAddFeedback(socket: Socket, data: { projectId: string; designId: string; feedback: any }, callback: (response: any) => void) {
    try {
      const { projectId, designId, feedback } = data;

      // Add feedback to design
      const updatedDesign = await this.db.addFeedback(designId, {
        ...feedback,
        id: uuidv4(),
        timestamp: new Date(),
        status: 'pending'
      });

      // Notify other clients
      this.broadcastToProject(projectId, 'design:update', { design: updatedDesign });

      callback({ success: true });
    } catch (error) {
      callback({ success: false, error: error.message });
    }
  }

  private async handleGeneratePreview(socket: Socket, data: { projectId: string; designId: string }, callback: (response: any) => void) {
    try {
      const { projectId, designId } = data;

      // Get design
      const design = await this.db.getDesign(designId);
      if (!design) {
        callback({ success: false, error: 'Design not found' });
        return;
      }

      // Generate preview
      const preview = await this.previewGenerator.generatePreview(design);
      await this.fileService.savePreview(designId, preview);

      // Send preview to client
      socket.emit('design:preview-update', { designId, preview });

      callback({ success: true, preview });
    } catch (error) {
      callback({ success: false, error: error.message });
    }
  }

  private async handleImplement(socket: Socket, data: { projectId: string; designId: string }, callback: (response: any) => void) {
    try {
      const { projectId, designId } = data;

      // Get design
      const design = await this.db.getDesign(designId);
      if (!design) {
        callback({ success: false, error: 'Design not found' });
        return;
      }

      // Generate implementation code
      const implementation = await this.renderer.generateImplementation(design);

      // Save implementation
      await this.fileService.saveImplementation(designId, implementation);

      // Update design status
      await this.db.updateDesign(designId, { status: 'implemented' });

      // Notify other clients
      this.broadcastToProject(projectId, 'design:update', { design: { ...design, status: 'implemented' } });

      callback({ success: true });
    } catch (error) {
      callback({ success: false, error: error.message });
    }
  }

  private broadcastToProject(projectId: string, event: string, data: any) {
    this.sessions.forEach((session, sessionId) => {
      if (session.projectId === projectId) {
        session.socket.emit(event, data);
      }
    });
  }
} 