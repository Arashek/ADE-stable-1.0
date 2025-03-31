import { Socket } from 'socket.io-client';
import { v4 as uuidv4 } from 'uuid';

export interface DesignTool {
  id: string;
  name: string;
  type: 'shape' | 'text' | 'image' | 'connection' | 'style';
  icon: string;
  description: string;
  properties: DesignToolProperty[];
}

export interface DesignToolProperty {
  id: string;
  name: string;
  type: 'color' | 'number' | 'text' | 'select' | 'boolean' | 'slider';
  label: string;
  defaultValue: any;
  options?: { label: string; value: any }[];
  min?: number;
  max?: number;
  step?: number;
}

export interface DesignStyle {
  fill?: string;
  stroke?: string;
  strokeWidth?: number;
  opacity?: number;
  borderRadius?: number;
  shadow?: {
    color: string;
    blur: number;
    offsetX: number;
    offsetY: number;
  };
  font?: {
    family: string;
    size: number;
    weight: string;
    style: string;
    color: string;
  };
}

export interface DesignElement {
  id: string;
  type: 'component' | 'connection' | 'text' | 'image';
  content: string;
  position: {
    x: number;
    y: number;
  };
  size: {
    width: number;
    height: number;
  };
  style: DesignStyle;
  properties: Record<string, any>;
  selected?: boolean;
  locked?: boolean;
  groupId?: string;
}

export interface DesignCanvas {
  id: string;
  name: string;
  elements: DesignElement[];
  style: DesignStyle;
  grid: {
    enabled: boolean;
    size: number;
    color: string;
  };
  snap: {
    enabled: boolean;
    threshold: number;
  };
  zoom: number;
  pan: {
    x: number;
    y: number;
  };
}

export interface DesignCollaboration {
  id: string;
  projectId: string;
  canvasId: string;
  participants: Array<{
    id: string;
    name: string;
    role: 'viewer' | 'editor' | 'admin';
    cursor?: {
      x: number;
      y: number;
      color: string;
    };
  }>;
  history: Array<{
    id: string;
    type: 'add' | 'remove' | 'modify' | 'style' | 'group' | 'ungroup';
    elementId: string;
    timestamp: Date;
    userId: string;
    changes: any;
  }>;
  chat: Array<{
    id: string;
    userId: string;
    message: string;
    timestamp: Date;
    type: 'text' | 'command' | 'suggestion';
  }>;
}

export class InteractiveDesignService {
  private socket: Socket;
  private projectId: string;
  private sessionId: string;
  private currentCanvas: DesignCanvas | null = null;
  private collaboration: DesignCollaboration | null = null;

  constructor(socket: Socket) {
    this.socket = socket;
    this.projectId = '';
    this.sessionId = uuidv4();
    this.setupEventListeners();
  }

  private setupEventListeners() {
    this.socket.on('design:update', this.handleUpdate.bind(this));
    this.socket.on('design:collaboration', this.handleCollaboration.bind(this));
    this.socket.on('design:chat', this.handleChat.bind(this));
    this.socket.on('design:error', this.handleError.bind(this));
  }

  private handleUpdate(data: { canvas: DesignCanvas }) {
    this.currentCanvas = data.canvas;
    this.socket.emit('design:update', data);
  }

  private handleCollaboration(data: { collaboration: DesignCollaboration }) {
    this.collaboration = data.collaboration;
    this.socket.emit('design:collaboration', data);
  }

  private handleChat(data: { message: any }) {
    this.socket.emit('design:chat', data);
  }

  private handleError(data: { error: string }) {
    this.socket.emit('design:error', data);
  }

  async initialize(projectId: string): Promise<void> {
    this.projectId = projectId;
    this.socket.emit('design:connect', {
      projectId: this.projectId,
      sessionId: this.sessionId,
    });
  }

  async createCanvas(name: string): Promise<DesignCanvas> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:create-canvas', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        name,
      });

      this.socket.once('design:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('design:update', (data: { canvas: DesignCanvas }) => {
        resolve(data.canvas);
      });
    });
  }

  async addElement(element: Omit<DesignElement, 'id'>): Promise<DesignElement> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:add-element', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        canvasId: this.currentCanvas?.id,
        element,
      });

      this.socket.once('design:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('design:update', (data: { canvas: DesignCanvas }) => {
        const newElement = data.canvas.elements.find(e => e.id === element.id);
        if (newElement) {
          resolve(newElement);
        } else {
          reject(new Error('Element not found in update'));
        }
      });
    });
  }

  async updateElement(elementId: string, updates: Partial<DesignElement>): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:update-element', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        canvasId: this.currentCanvas?.id,
        elementId,
        updates,
      });

      this.socket.once('design:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('design:update', () => {
        resolve();
      });
    });
  }

  async updateStyle(elementId: string, style: DesignStyle): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:update-style', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        canvasId: this.currentCanvas?.id,
        elementId,
        style,
      });

      this.socket.once('design:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('design:update', () => {
        resolve();
      });
    });
  }

  async groupElements(elementIds: string[]): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:group-elements', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        canvasId: this.currentCanvas?.id,
        elementIds,
      });

      this.socket.once('design:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('design:update', () => {
        resolve();
      });
    });
  }

  async ungroupElements(groupId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:ungroup-elements', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        canvasId: this.currentCanvas?.id,
        groupId,
      });

      this.socket.once('design:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('design:update', () => {
        resolve();
      });
    });
  }

  async updateCanvasSettings(settings: Partial<DesignCanvas>): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:update-canvas-settings', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        canvasId: this.currentCanvas?.id,
        settings,
      });

      this.socket.once('design:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('design:update', () => {
        resolve();
      });
    });
  }

  async sendChatMessage(message: string, type: 'text' | 'command' | 'suggestion' = 'text'): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:chat-message', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        canvasId: this.currentCanvas?.id,
        message,
        type,
      });

      this.socket.once('design:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('design:chat', () => {
        resolve();
      });
    });
  }

  public async updateCursor(position: { x: number; y: number }): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:cursor:update', {
        sessionId: this.sessionId,
        projectId: this.projectId,
        position
      }, (response: { error?: string }) => {
        if (response.error) {
          reject(new Error(response.error));
        } else {
          resolve();
        }
      });
    });
  }

  public async connectSession(projectId: string, userId: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:connect', {
        sessionId: this.sessionId,
        projectId,
        userId
      }, (response: { success: boolean; session?: any; error?: string }) => {
        if (response.error) {
          reject(new Error(response.error));
        } else {
          resolve(response.session);
        }
      });
    });
  }

  public async disconnectSession(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:disconnect', {
        sessionId: this.sessionId,
        projectId: this.projectId
      }, (response: { success: boolean; error?: string }) => {
        if (response.error) {
          reject(new Error(response.error));
        } else {
          resolve();
        }
      });
    });
  }

  public async saveDesign(design: any): Promise<any> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:save', {
        sessionId: this.sessionId,
        projectId: this.projectId,
        design
      }, (response: { success: boolean; savedDesign?: any; error?: string }) => {
        if (response.error) {
          reject(new Error(response.error));
        } else {
          resolve(response.savedDesign);
        }
      });
    });
  }

  public async updateDesign(designId: string, updates: any): Promise<any> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:update', {
        sessionId: this.sessionId,
        projectId: this.projectId,
        designId,
        updates
      }, (response: { success: boolean; updatedDesign?: any; error?: string }) => {
        if (response.error) {
          reject(new Error(response.error));
        } else {
          resolve(response.updatedDesign);
        }
      });
    });
  }

  public async getDesignById(designId: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:get', {
        sessionId: this.sessionId,
        projectId: this.projectId,
        designId
      }, (response: { success: boolean; design?: any; error?: string }) => {
        if (response.error) {
          reject(new Error(response.error));
        } else {
          resolve(response.design);
        }
      });
    });
  }

  public async exportDesign(designId: string, format: 'react' | 'vue' | 'angular' | 'html' = 'react'): Promise<any> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:export', {
        sessionId: this.sessionId,
        projectId: this.projectId,
        designId,
        format
      }, (response: { success: boolean; exportedCode?: any; error?: string }) => {
        if (response.error) {
          reject(new Error(response.error));
        } else {
          resolve(response.exportedCode);
        }
      });
    });
  }

  async undo(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:undo', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        canvasId: this.currentCanvas?.id,
      });

      this.socket.once('design:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('design:update', () => {
        resolve();
      });
    });
  }

  async redo(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.emit('design:redo', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        canvasId: this.currentCanvas?.id,
      });

      this.socket.once('design:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('design:update', () => {
        resolve();
      });
    });
  }

  dispose(): void {
    this.socket.emit('design:disconnect', {
      projectId: this.projectId,
      sessionId: this.sessionId,
    });
  }
}