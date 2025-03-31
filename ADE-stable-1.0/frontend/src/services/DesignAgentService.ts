import { Socket } from 'socket.io-client';
import { v4 as uuidv4 } from 'uuid';

export interface DesignComponent {
  id: string;
  type: 'container' | 'button' | 'input' | 'text' | 'image' | 'card';
  content: string;
  style: React.CSSProperties;
  position: { x: number; y: number };
  size: { width: number; height: number };
  children?: DesignComponent[];
}

export interface DesignSpec {
  id: string;
  projectId: string;
  name: string;
  description: string;
  components: DesignComponent[];
  createdAt: Date;
  updatedAt: Date;
  status: 'draft' | 'review' | 'approved' | 'implemented';
  feedback?: Array<{
    id: string;
    from: string;
    comment: string;
    timestamp: Date;
    status: 'pending' | 'resolved';
  }>;
}

export interface DesignSystem {
  colors: {
    primary: string;
    secondary: string;
    background: string;
    text: string;
    error: string;
    success: string;
    warning: string;
    info: string;
  };
  typography: {
    fontFamily: string;
    fontSize: {
      small: string;
      medium: string;
      large: string;
    };
    fontWeight: {
      light: number;
      regular: number;
      bold: number;
    };
  };
  spacing: {
    small: string;
    medium: string;
    large: string;
  };
  components: {
    [key: string]: {
      defaultProps: any;
      variants: {
        [key: string]: any;
      };
    };
  };
}

export class DesignAgentService {
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
    this.ws.on('design:update', (data: { design: DesignSpec }) => {
      this.handleDesignUpdate(data);
    });

    this.ws.on('design:feedback', (data: { designId: string; feedback: any }) => {
      this.handleDesignFeedback(data);
    });

    this.ws.on('design:system-update', (data: { system: DesignSystem }) => {
      this.handleDesignSystemUpdate(data);
    });

    this.ws.on('design:preview-update', (data: { designId: string; preview: string }) => {
      this.handlePreviewUpdate(data);
    });
  }

  private async establishConnection() {
    this.ws.emit('design:connect', {
      projectId: this.projectId,
      sessionId: this.sessionId,
    });
  }

  private handleDesignUpdate(data: { design: DesignSpec }) {
    // Emit event for UI update
    window.dispatchEvent(
      new CustomEvent('design:update', { detail: data.design })
    );
  }

  private handleDesignFeedback(data: { designId: string; feedback: any }) {
    // Emit event for feedback update
    window.dispatchEvent(
      new CustomEvent('design:feedback', { detail: data })
    );
  }

  private handleDesignSystemUpdate(data: { system: DesignSystem }) {
    // Emit event for design system update
    window.dispatchEvent(
      new CustomEvent('design:system-update', { detail: data.system })
    );
  }

  private handlePreviewUpdate(data: { designId: string; preview: string }) {
    // Emit event for preview update
    window.dispatchEvent(
      new CustomEvent('design:preview-update', { detail: data })
    );
  }

  public async saveDesign(design: DesignSpec) {
    return new Promise((resolve, reject) => {
      this.ws.emit('design:save', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        design,
      }, (response: { success: boolean; error?: string }) => {
        if (response.success) {
          resolve(response);
        } else {
          reject(new Error(response.error));
        }
      });
    });
  }

  public async updateDesign(designId: string, updates: Partial<DesignSpec>) {
    return new Promise((resolve, reject) => {
      this.ws.emit('design:update', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        designId,
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

  public async addFeedback(designId: string, feedback: {
    from: string;
    comment: string;
  }) {
    return new Promise((resolve, reject) => {
      this.ws.emit('design:add-feedback', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        designId,
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

  public async generatePreview(designId: string) {
    return new Promise((resolve, reject) => {
      this.ws.emit('design:generate-preview', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        designId,
      }, (response: { success: boolean; error?: string; preview?: string }) => {
        if (response.success) {
          resolve(response.preview);
        } else {
          reject(new Error(response.error));
        }
      });
    });
  }

  public async implementDesign(designId: string) {
    return new Promise((resolve, reject) => {
      this.ws.emit('design:implement', {
        projectId: this.projectId,
        sessionId: this.sessionId,
        designId,
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
    this.ws.emit('design:disconnect', {
      projectId: this.projectId,
      sessionId: this.sessionId,
    });
  }
} 