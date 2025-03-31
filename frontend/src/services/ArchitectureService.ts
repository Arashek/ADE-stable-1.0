import { Socket } from 'socket.io-client';
import { v4 as uuidv4 } from 'uuid';

export interface ArchitectureComponent {
  id: string;
  name: string;
  type: string;
  description: string;
  position: {
    x: number;
    y: number;
  };
  size: {
    width: number;
    height: number;
  };
  style?: {
    color?: string;
    borderColor?: string;
    borderWidth?: number;
    textColor?: string;
  };
  properties?: Record<string, any>;
}

export interface ArchitectureConnection {
  id: string;
  sourceId: string;
  targetId: string;
  type: 'dependency' | 'composition' | 'aggregation' | 'inheritance';
  style?: {
    color?: string;
    borderWidth?: number;
    textColor?: string;
  };
}

export interface ArchitectureSpec {
  id: string;
  projectId: string;
  name: string;
  description: string;
  components: ArchitectureComponent[];
  connections: ArchitectureConnection[];
  createdAt: Date;
  updatedAt: Date;
  status: 'draft' | 'review' | 'approved' | 'implemented';
  feedback?: Array<{
    id: string;
    from: string;
    comment: string;
    timestamp: Date;
    status: 'pending' | 'resolved' | 'rejected';
  }>;
}

export interface ArchitectureAnalysis {
  metrics: {
    complexity: number;
    coupling: number;
    cohesion: number;
    scalability: number;
    maintainability: number;
  };
  insights: string[];
  recommendations: string[];
  issues: string[];
}

export class ArchitectureService {
  private socket: Socket;
  private projectId: string;
  private sessionId: string;

  constructor(socket: Socket) {
    this.socket = socket;
    this.projectId = '';
    this.sessionId = uuidv4();
    this.setupEventListeners();
  }

  private setupEventListeners() {
    this.socket.on('architecture:update', this.handleUpdate.bind(this));
    this.socket.on('architecture:analysis', this.handleAnalysis.bind(this));
    this.socket.on('architecture:validation', this.handleValidation.bind(this));
    this.socket.on('architecture:error', this.handleError.bind(this));
  }

  private handleUpdate(data: { architecture: ArchitectureSpec }) {
    // Emit event for UI update
    this.socket.emit('architecture:update', data);
  }

  private handleAnalysis(data: { analysis: ArchitectureAnalysis }) {
    // Emit event for UI update
    this.socket.emit('architecture:analysis', data);
  }

  private handleValidation(data: { isValid: boolean; errors: string[] }) {
    // Emit event for UI update
    this.socket.emit('architecture:validation', data);
  }

  private handleError(data: { error: string }) {
    // Emit event for UI update
    this.socket.emit('architecture:error', data);
  }

  async initialize(projectId: string): Promise<void> {
    this.projectId = projectId;
    this.socket.emit('architecture:connect', {
      projectId: this.projectId,
      sessionId: this.sessionId,
    });
  }

  async saveArchitecture(architecture: ArchitectureSpec): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.emit('architecture:save', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        architecture,
      });

      this.socket.once('architecture:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('architecture:update', () => {
        resolve();
      });
    });
  }

  async updateComponent(
    componentId: string,
    updates: Partial<ArchitectureComponent>
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.emit('architecture:update-component', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        componentId,
        updates,
      });

      this.socket.once('architecture:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('architecture:update', () => {
        resolve();
      });
    });
  }

  async updateConnection(
    connectionId: string,
    updates: Partial<ArchitectureConnection>
  ): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.emit('architecture:update-connection', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        connectionId,
        updates,
      });

      this.socket.once('architecture:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('architecture:update', () => {
        resolve();
      });
    });
  }

  async analyzeArchitecture(): Promise<ArchitectureAnalysis> {
    return new Promise((resolve, reject) => {
      this.socket.emit('architecture:analyze', {
        projectId: this.projectId,
        sessionId: this.sessionId,
      });

      this.socket.once('architecture:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('architecture:analysis', (data: { analysis: ArchitectureAnalysis }) => {
        resolve(data.analysis);
      });
    });
  }

  async validateArchitecture(): Promise<{ isValid: boolean; errors: string[] }> {
    return new Promise((resolve, reject) => {
      this.socket.emit('architecture:validate', {
        projectId: this.projectId,
        sessionId: this.sessionId,
      });

      this.socket.once('architecture:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('architecture:validation', (data: { isValid: boolean; errors: string[] }) => {
        resolve(data);
      });
    });
  }

  async addFeedback(feedback: { from: string; comment: string }): Promise<void> {
    return new Promise((resolve, reject) => {
      this.socket.emit('architecture:add-feedback', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        architectureId: this.projectId, // Using projectId as architectureId for now
        feedback,
      });

      this.socket.once('architecture:error', (data: { error: string }) => {
        reject(new Error(data.error));
      });

      this.socket.once('architecture:update', () => {
        resolve();
      });
    });
  }

  dispose(): void {
    this.socket.emit('architecture:disconnect', {
      projectId: this.projectId,
      sessionId: this.sessionId,
    });
  }
} 