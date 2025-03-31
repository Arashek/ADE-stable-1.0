import { Server, Socket } from 'socket.io';
import { DatabaseService } from '../DatabaseService';
import { FileService } from '../FileService';
import {
  DesignCanvas,
  DesignElement,
  DesignStyle,
  DesignCollaboration,
  DesignTool,
} from '../../../frontend/src/services/InteractiveDesignService';

interface Session {
  socket: Socket;
  projectId: string;
  sessionId: string;
  userId: string;
  role: 'viewer' | 'editor' | 'admin';
}

export class InteractiveDesignService {
  private sessions: Map<string, Session> = new Map();
  private projectSessions: Map<string, Set<string>> = new Map();
  private canvasSessions: Map<string, Set<string>> = new Map();
  private undoStacks: Map<string, DesignCanvas[]> = new Map();
  private redoStacks: Map<string, DesignCanvas[]> = new Map();

  constructor(
    private io: Server,
    private db: DatabaseService,
    private fileService: FileService
  ) {
    this.setupEventListeners();
  }

  private setupEventListeners() {
    this.io.on('connection', (socket: Socket) => {
      socket.on('design:connect', this.handleConnect.bind(this, socket));
      socket.on('design:disconnect', this.handleDisconnect.bind(this, socket));
      socket.on('design:create-canvas', this.handleCreateCanvas.bind(this, socket));
      socket.on('design:add-element', this.handleAddElement.bind(this, socket));
      socket.on('design:update-element', this.handleUpdateElement.bind(this, socket));
      socket.on('design:update-style', this.handleUpdateStyle.bind(this, socket));
      socket.on('design:group-elements', this.handleGroupElements.bind(this, socket));
      socket.on('design:ungroup-elements', this.handleUngroupElements.bind(this, socket));
      socket.on('design:update-canvas-settings', this.handleUpdateCanvasSettings.bind(this, socket));
      socket.on('design:chat-message', this.handleChatMessage.bind(this, socket));
      socket.on('design:update-cursor', this.handleUpdateCursor.bind(this, socket));
      socket.on('design:undo', this.handleUndo.bind(this, socket));
      socket.on('design:redo', this.handleRedo.bind(this, socket));
    });
  }

  private async handleConnect(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    userId: string;
    role: 'viewer' | 'editor' | 'admin';
  }) {
    const { projectId, sessionId, userId, role } = data;
    this.sessions.set(sessionId, { socket, projectId, sessionId, userId, role });

    if (!this.projectSessions.has(projectId)) {
      this.projectSessions.set(projectId, new Set());
    }
    this.projectSessions.get(projectId)?.add(sessionId);

    // Load existing canvas and collaboration data
    const canvas = await this.db.getCanvas(projectId);
    if (canvas) {
      socket.emit('design:update', { canvas });
    }

    const collaboration = await this.db.getCollaboration(projectId);
    if (collaboration) {
      socket.emit('design:collaboration', { collaboration });
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

  private async handleCreateCanvas(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    name: string;
  }) {
    try {
      const { projectId, name } = data;
      const session = this.sessions.get(data.sessionId);

      if (!session || session.role === 'viewer') {
        socket.emit('design:error', { error: 'Insufficient permissions' });
        return;
      }

      const canvas: DesignCanvas = {
        id: Date.now().toString(),
        name,
        elements: [],
        style: {
          fill: '#ffffff',
          stroke: '#000000',
          strokeWidth: 1,
        },
        grid: {
          enabled: true,
          size: 20,
          color: '#e0e0e0',
        },
        snap: {
          enabled: true,
          threshold: 10,
        },
        zoom: 1,
        pan: { x: 0, y: 0 },
      };

      await this.db.saveCanvas(projectId, canvas);
      this.broadcastToProject(projectId, 'design:update', { canvas });
    } catch (error) {
      socket.emit('design:error', { error: error.message });
    }
  }

  private async handleAddElement(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    canvasId: string;
    element: Omit<DesignElement, 'id'>;
  }) {
    try {
      const { projectId, canvasId, element } = data;
      const session = this.sessions.get(data.sessionId);

      if (!session || session.role === 'viewer') {
        socket.emit('design:error', { error: 'Insufficient permissions' });
        return;
      }

      const canvas = await this.db.getCanvas(projectId);
      if (!canvas) {
        socket.emit('design:error', { error: 'Canvas not found' });
        return;
      }

      const newElement: DesignElement = {
        ...element,
        id: Date.now().toString(),
      };

      canvas.elements.push(newElement);
      await this.saveCanvasState(projectId, canvas);
      this.broadcastToProject(projectId, 'design:update', { canvas });
    } catch (error) {
      socket.emit('design:error', { error: error.message });
    }
  }

  private async handleUpdateElement(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    canvasId: string;
    elementId: string;
    updates: Partial<DesignElement>;
  }) {
    try {
      const { projectId, elementId, updates } = data;
      const session = this.sessions.get(data.sessionId);

      if (!session || session.role === 'viewer') {
        socket.emit('design:error', { error: 'Insufficient permissions' });
        return;
      }

      const canvas = await this.db.getCanvas(projectId);
      if (!canvas) {
        socket.emit('design:error', { error: 'Canvas not found' });
        return;
      }

      const elementIndex = canvas.elements.findIndex(e => e.id === elementId);
      if (elementIndex === -1) {
        socket.emit('design:error', { error: 'Element not found' });
        return;
      }

      canvas.elements[elementIndex] = {
        ...canvas.elements[elementIndex],
        ...updates,
      };

      await this.saveCanvasState(projectId, canvas);
      this.broadcastToProject(projectId, 'design:update', { canvas });
    } catch (error) {
      socket.emit('design:error', { error: error.message });
    }
  }

  private async handleUpdateStyle(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    canvasId: string;
    elementId: string;
    style: DesignStyle;
  }) {
    try {
      const { projectId, elementId, style } = data;
      const session = this.sessions.get(data.sessionId);

      if (!session || session.role === 'viewer') {
        socket.emit('design:error', { error: 'Insufficient permissions' });
        return;
      }

      const canvas = await this.db.getCanvas(projectId);
      if (!canvas) {
        socket.emit('design:error', { error: 'Canvas not found' });
        return;
      }

      const elementIndex = canvas.elements.findIndex(e => e.id === elementId);
      if (elementIndex === -1) {
        socket.emit('design:error', { error: 'Element not found' });
        return;
      }

      canvas.elements[elementIndex].style = {
        ...canvas.elements[elementIndex].style,
        ...style,
      };

      await this.saveCanvasState(projectId, canvas);
      this.broadcastToProject(projectId, 'design:update', { canvas });
    } catch (error) {
      socket.emit('design:error', { error: error.message });
    }
  }

  private async handleGroupElements(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    canvasId: string;
    elementIds: string[];
  }) {
    try {
      const { projectId, elementIds } = data;
      const session = this.sessions.get(data.sessionId);

      if (!session || session.role === 'viewer') {
        socket.emit('design:error', { error: 'Insufficient permissions' });
        return;
      }

      const canvas = await this.db.getCanvas(projectId);
      if (!canvas) {
        socket.emit('design:error', { error: 'Canvas not found' });
        return;
      }

      const groupId = Date.now().toString();
      elementIds.forEach(elementId => {
        const element = canvas.elements.find(e => e.id === elementId);
        if (element) {
          element.groupId = groupId;
        }
      });

      await this.saveCanvasState(projectId, canvas);
      this.broadcastToProject(projectId, 'design:update', { canvas });
    } catch (error) {
      socket.emit('design:error', { error: error.message });
    }
  }

  private async handleUngroupElements(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    canvasId: string;
    groupId: string;
  }) {
    try {
      const { projectId, groupId } = data;
      const session = this.sessions.get(data.sessionId);

      if (!session || session.role === 'viewer') {
        socket.emit('design:error', { error: 'Insufficient permissions' });
        return;
      }

      const canvas = await this.db.getCanvas(projectId);
      if (!canvas) {
        socket.emit('design:error', { error: 'Canvas not found' });
        return;
      }

      canvas.elements.forEach(element => {
        if (element.groupId === groupId) {
          delete element.groupId;
        }
      });

      await this.saveCanvasState(projectId, canvas);
      this.broadcastToProject(projectId, 'design:update', { canvas });
    } catch (error) {
      socket.emit('design:error', { error: error.message });
    }
  }

  private async handleUpdateCanvasSettings(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    canvasId: string;
    settings: Partial<DesignCanvas>;
  }) {
    try {
      const { projectId, settings } = data;
      const session = this.sessions.get(data.sessionId);

      if (!session || session.role === 'viewer') {
        socket.emit('design:error', { error: 'Insufficient permissions' });
        return;
      }

      const canvas = await this.db.getCanvas(projectId);
      if (!canvas) {
        socket.emit('design:error', { error: 'Canvas not found' });
        return;
      }

      Object.assign(canvas, settings);
      await this.saveCanvasState(projectId, canvas);
      this.broadcastToProject(projectId, 'design:update', { canvas });
    } catch (error) {
      socket.emit('design:error', { error: error.message });
    }
  }

  private async handleChatMessage(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    canvasId: string;
    message: string;
    type: 'text' | 'command' | 'suggestion';
  }) {
    try {
      const { projectId, message, type } = data;
      const session = this.sessions.get(data.sessionId);

      if (!session) {
        socket.emit('design:error', { error: 'Session not found' });
        return;
      }

      const collaboration = await this.db.getCollaboration(projectId);
      if (!collaboration) {
        socket.emit('design:error', { error: 'Collaboration not found' });
        return;
      }

      const chatMessage = {
        id: Date.now().toString(),
        userId: session.userId,
        message,
        timestamp: new Date(),
        type,
      };

      collaboration.chat.push(chatMessage);
      await this.db.saveCollaboration(projectId, collaboration);
      this.broadcastToProject(projectId, 'design:chat', { message: chatMessage });
    } catch (error) {
      socket.emit('design:error', { error: error.message });
    }
  }

  private async handleUpdateCursor(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    canvasId: string;
    position: { x: number; y: number };
  }) {
    try {
      const { projectId, position } = data;
      const session = this.sessions.get(data.sessionId);

      if (!session) {
        socket.emit('design:error', { error: 'Session not found' });
        return;
      }

      const collaboration = await this.db.getCollaboration(projectId);
      if (!collaboration) {
        socket.emit('design:error', { error: 'Collaboration not found' });
        return;
      }

      const participant = collaboration.participants.find(p => p.id === session.userId);
      if (participant) {
        participant.cursor = {
          ...position,
          color: this.getUserColor(session.userId),
        };
        await this.db.saveCollaboration(projectId, collaboration);
        this.broadcastToProject(projectId, 'design:collaboration', { collaboration });
      }
    } catch (error) {
      socket.emit('design:error', { error: error.message });
    }
  }

  private async handleUndo(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    canvasId: string;
  }) {
    try {
      const { projectId } = data;
      const session = this.sessions.get(data.sessionId);

      if (!session || session.role === 'viewer') {
        socket.emit('design:error', { error: 'Insufficient permissions' });
        return;
      }

      const undoStack = this.undoStacks.get(projectId);
      if (!undoStack || undoStack.length === 0) {
        socket.emit('design:error', { error: 'Nothing to undo' });
        return;
      }

      const currentCanvas = await this.db.getCanvas(projectId);
      if (!currentCanvas) {
        socket.emit('design:error', { error: 'Canvas not found' });
        return;
      }

      const previousState = undoStack.pop();
      if (previousState) {
        const redoStack = this.redoStacks.get(projectId) || [];
        redoStack.push(currentCanvas);
        this.redoStacks.set(projectId, redoStack);
        await this.db.saveCanvas(projectId, previousState);
        this.broadcastToProject(projectId, 'design:update', { canvas: previousState });
      }
    } catch (error) {
      socket.emit('design:error', { error: error.message });
    }
  }

  private async handleRedo(socket: Socket, data: {
    projectId: string;
    sessionId: string;
    canvasId: string;
  }) {
    try {
      const { projectId } = data;
      const session = this.sessions.get(data.sessionId);

      if (!session || session.role === 'viewer') {
        socket.emit('design:error', { error: 'Insufficient permissions' });
        return;
      }

      const redoStack = this.redoStacks.get(projectId);
      if (!redoStack || redoStack.length === 0) {
        socket.emit('design:error', { error: 'Nothing to redo' });
        return;
      }

      const currentCanvas = await this.db.getCanvas(projectId);
      if (!currentCanvas) {
        socket.emit('design:error', { error: 'Canvas not found' });
        return;
      }

      const nextState = redoStack.pop();
      if (nextState) {
        const undoStack = this.undoStacks.get(projectId) || [];
        undoStack.push(currentCanvas);
        this.undoStacks.set(projectId, undoStack);
        await this.db.saveCanvas(projectId, nextState);
        this.broadcastToProject(projectId, 'design:update', { canvas: nextState });
      }
    } catch (error) {
      socket.emit('design:error', { error: error.message });
    }
  }

  private async saveCanvasState(projectId: string, canvas: DesignCanvas): Promise<void> {
    const undoStack = this.undoStacks.get(projectId) || [];
    undoStack.push(JSON.parse(JSON.stringify(canvas)));
    this.undoStacks.set(projectId, undoStack);
    this.redoStacks.delete(projectId);
    await this.db.saveCanvas(projectId, canvas);
  }

  private getUserColor(userId: string): string {
    // Generate a consistent color based on user ID
    const colors = [
      '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD',
      '#D4A5A5', '#9B59B6', '#3498DB', '#E67E22', '#2ECC71',
    ];
    const index = userId.split('').reduce((acc, char) => acc + char.charCodeAt(0), 0) % colors.length;
    return colors[index];
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