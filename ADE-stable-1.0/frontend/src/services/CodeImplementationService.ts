import { Socket } from 'socket.io-client';
import { v4 as uuidv4 } from 'uuid';

export interface CodeFile {
  id: string;
  path: string;
  content: string;
  language: string;
  dependencies: string[];
  lastModified: Date;
}

export interface CodeImplementation {
  id: string;
  projectId: string;
  name: string;
  description: string;
  files: CodeFile[];
  status: 'draft' | 'review' | 'approved' | 'implemented';
  feedback?: Array<{
    id: string;
    from: string;
    comment: string;
    timestamp: Date;
    status: 'pending' | 'resolved';
  }>;
}

export interface CodeAnalysis {
  complexity: number;
  maintainability: number;
  testCoverage: number;
  issues: Array<{
    type: 'error' | 'warning' | 'info';
    message: string;
    line: number;
    column: number;
  }>;
}

export class CodeImplementationService {
  private ws: Socket;
  private projectId: string;
  private sessionId: string;

  constructor(config: { ws: Socket; projectId: string }) {
    this.ws = config.ws;
    this.projectId = config.projectId;
    this.sessionId = uuidv4();
  }

  public async initialize() {
    this.setupEventListeners();
    await this.establishConnection();
  }

  private setupEventListeners() {
    this.ws.on('code:update', (data: { implementation: CodeImplementation }) => {
      this.handleImplementationUpdate(data);
    });

    this.ws.on('code:analysis', (data: { fileId: string; analysis: CodeAnalysis }) => {
      this.handleCodeAnalysis(data);
    });

    this.ws.on('code:feedback', (data: { implementationId: string; feedback: any }) => {
      this.handleFeedback(data);
    });

    this.ws.on('code:compilation', (data: { success: boolean; output: string }) => {
      this.handleCompilation(data);
    });
  }

  private async establishConnection() {
    this.ws.emit('code:connect', {
      projectId: this.projectId,
      sessionId: this.sessionId,
    });
  }

  private handleImplementationUpdate(data: { implementation: CodeImplementation }) {
    window.dispatchEvent(
      new CustomEvent('code:update', { detail: data.implementation })
    );
  }

  private handleCodeAnalysis(data: { fileId: string; analysis: CodeAnalysis }) {
    window.dispatchEvent(
      new CustomEvent('code:analysis', { detail: data })
    );
  }

  private handleFeedback(data: { implementationId: string; feedback: any }) {
    window.dispatchEvent(
      new CustomEvent('code:feedback', { detail: data })
    );
  }

  private handleCompilation(data: { success: boolean; output: string }) {
    window.dispatchEvent(
      new CustomEvent('code:compilation', { detail: data })
    );
  }

  public async saveImplementation(implementation: CodeImplementation) {
    return new Promise((resolve, reject) => {
      this.ws.emit('code:save', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        implementation,
      }, (response: { success: boolean; error?: string }) => {
        if (response.success) {
          resolve(response);
        } else {
          reject(new Error(response.error));
        }
      });
    });
  }

  public async updateFile(fileId: string, updates: Partial<CodeFile>) {
    return new Promise((resolve, reject) => {
      this.ws.emit('code:update-file', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        fileId,
        updates,
      }, (response: { success: boolean; error?: string }) => {
        if (response.success) {
          resolve(response);
        } else {
          reject(new Error(response.error));
        }
      });
    });
  }

  public async analyzeCode(fileId: string) {
    return new Promise((resolve, reject) => {
      this.ws.emit('code:analyze', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        fileId,
      }, (response: { success: boolean; error?: string; analysis?: CodeAnalysis }) => {
        if (response.success) {
          resolve(response.analysis);
        } else {
          reject(new Error(response.error));
        }
      });
    });
  }

  public async compileCode(implementationId: string) {
    return new Promise((resolve, reject) => {
      this.ws.emit('code:compile', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        implementationId,
      }, (response: { success: boolean; error?: string; output?: string }) => {
        if (response.success) {
          resolve(response.output);
        } else {
          reject(new Error(response.error));
        }
      });
    });
  }

  public async addFeedback(implementationId: string, feedback: {
    from: string;
    comment: string;
  }) {
    return new Promise((resolve, reject) => {
      this.ws.emit('code:add-feedback', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        implementationId,
        feedback,
      }, (response: { success: boolean; error?: string }) => {
        if (response.success) {
          resolve(response);
        } else {
          reject(new Error(response.error));
        }
      });
    });
  }

  public dispose() {
    this.ws.emit('code:disconnect', {
      projectId: this.projectId,
      sessionId: this.sessionId,
    });
  }
} 