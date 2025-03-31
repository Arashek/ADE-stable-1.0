import { DesignSystem, DesignComponent, DesignStyle, DesignValidationResult, DesignImplementation, DesignModification } from '../types/design';
import { WebSocketService } from './WebSocketService';

interface ToolAction {
  type: string;
  target: string;
  value: any;
}

interface AgentResponse {
  message: string;
  metadata?: {
    component?: DesignComponent;
    style?: DesignStyle;
    preview?: string;
    modification?: DesignModification;
    suggestedTool?: {
      name: string;
      type: string;
      target: string;
      value: any;
    };
  };
  designUpdate?: Partial<DesignSystem>;
}

interface ToolActionResult {
  success: boolean;
  designUpdate?: Partial<DesignSystem>;
  error?: string;
}

interface DesignSuggestion {
  id: string;
  type: 'component' | 'style' | 'layout' | 'page' | 'system';
  target: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  preview?: string;
  changes?: Partial<DesignSystem>;
  status: 'pending' | 'reviewed' | 'applied' | 'rejected';
  timestamp: Date;
}

interface DesignNotification {
  id: string;
  type: 'suggestion' | 'review' | 'update' | 'finalize';
  title: string;
  message: string;
  priority: 'high' | 'medium' | 'low';
  timestamp: Date;
  action?: {
    type: string;
    data: any;
  };
}

export class DesignAgent {
  private ws: WebSocketService;
  private currentDesign: Partial<DesignSystem> = {};
  private socket: WebSocket;
  private suggestions: DesignSuggestion[] = [];
  private notifications: DesignNotification[] = [];
  private listeners: Map<string, Set<Function>> = new Map();

  constructor(socket: WebSocket, initialDesign: Partial<DesignSystem>) {
    this.ws = new WebSocketService('ws://localhost:3001/design');
    this.socket = socket;
    this.currentDesign = initialDesign;
    this.setupWebSocketHandlers();
  }

  private setupWebSocketHandlers() {
    this.ws.on('design:update', (data: Partial<DesignSystem>) => {
      this.currentDesign = { ...this.currentDesign, ...data };
      this.notifyListeners('design:update', data);
    });

    this.ws.on('design:preview', (data: { componentId: string; preview: string }) => {
      this.notifyListeners('design:preview', data);
    });

    this.ws.on('design:validation', (data: DesignValidationResult) => {
      this.notifyListeners('design:validation', data);
    });

    this.ws.on('design:suggestion', (data: DesignSuggestion) => {
      this.suggestions.push(data);
      this.notifyListeners('design:suggestion', data);
    });

    this.ws.on('design:notification', (data: DesignNotification) => {
      this.notifications.push(data);
      this.notifyListeners('design:notification', data);
    });
  }

  private notifyListeners(event: string, data: any) {
    const eventListeners = this.listeners.get(event);
    if (eventListeners) {
      eventListeners.forEach(listener => listener(data));
    }
  }

  on(event: string, listener: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)?.add(listener);
  }

  off(event: string, listener: Function) {
    this.listeners.get(event)?.delete(listener);
  }

  async analyzeDesignContext(context: {
    type: string;
    target: string;
    properties?: Record<string, any>;
  }): Promise<DesignSuggestion[]> {
    return new Promise((resolve, reject) => {
      const messageId = Date.now().toString();
      
      const handleResponse = (event: MessageEvent) => {
        const response = JSON.parse(event.data);
        if (response.messageId === messageId) {
          this.socket.removeEventListener('message', handleResponse);
          resolve(response.data.suggestions);
        }
      };

      this.socket.addEventListener('message', handleResponse);

      this.socket.send(JSON.stringify({
        type: 'analyze_design_context',
        messageId,
        data: {
          context,
          currentDesign: this.currentDesign,
        },
      }));
    });
  }

  async generateDesignSuggestions(): Promise<DesignSuggestion[]> {
    return new Promise((resolve, reject) => {
      const messageId = Date.now().toString();
      
      const handleResponse = (event: MessageEvent) => {
        const response = JSON.parse(event.data);
        if (response.messageId === messageId) {
          this.socket.removeEventListener('message', handleResponse);
          resolve(response.data.suggestions);
        }
      };

      this.socket.addEventListener('message', handleResponse);

      this.socket.send(JSON.stringify({
        type: 'generate_design_suggestions',
        messageId,
        data: {
          currentDesign: this.currentDesign,
        },
      }));
    });
  }

  async applySuggestion(suggestionId: string): Promise<boolean> {
    return new Promise((resolve, reject) => {
      const messageId = Date.now().toString();
      
      const handleResponse = (event: MessageEvent) => {
        const response = JSON.parse(event.data);
        if (response.messageId === messageId) {
          this.socket.removeEventListener('message', handleResponse);
          resolve(response.data.success);
        }
      };

      this.socket.addEventListener('message', handleResponse);

      this.socket.send(JSON.stringify({
        type: 'apply_suggestion',
        messageId,
        data: {
          suggestionId,
          currentDesign: this.currentDesign,
        },
      }));
    });
  }

  async rejectSuggestion(suggestionId: string): Promise<void> {
    return new Promise((resolve, reject) => {
      const messageId = Date.now().toString();
      
      const handleResponse = (event: MessageEvent) => {
        const response = JSON.parse(event.data);
        if (response.messageId === messageId) {
          this.socket.removeEventListener('message', handleResponse);
          resolve();
        }
      };

      this.socket.addEventListener('message', handleResponse);

      this.socket.send(JSON.stringify({
        type: 'reject_suggestion',
        messageId,
        data: {
          suggestionId,
          currentDesign: this.currentDesign,
        },
      }));
    });
  }

  getSuggestions(): DesignSuggestion[] {
    return this.suggestions;
  }

  getNotifications(): DesignNotification[] {
    return this.notifications;
  }

  clearNotifications(): void {
    this.notifications = [];
  }

  async handleComponentAddition(component: any): Promise<void> {
    // Send component to backend for processing
    await this.ws.emit('design:add-component', {
      component,
      currentDesign: this.currentDesign,
    });
  }

  async handleStyleAddition(style: any): Promise<void> {
    // Send style to backend for processing
    await this.ws.emit('design:add-style', {
      style,
      currentDesign: this.currentDesign,
    });
  }

  async validateDesign(design: Partial<DesignSystem>): Promise<DesignValidationResult> {
    // Send design to backend for validation
    const response = await this.ws.emit('design:validate', design);
    return response as DesignValidationResult;
  }

  async generateImplementation(design: Partial<DesignSystem>): Promise<DesignImplementation> {
    // Send design to backend for implementation generation
    const response = await this.ws.emit('design:generate-implementation', design);
    return response as DesignImplementation;
  }

  async getComponentPreview(componentId: string): Promise<string> {
    // Request component preview from backend
    const response = await this.ws.emit('design:get-preview', { componentId });
    return response as string;
  }

  async updateComponent(componentId: string, updates: Partial<DesignComponent>): Promise<void> {
    // Send component updates to backend
    await this.ws.emit('design:update-component', {
      componentId,
      updates,
      currentDesign: this.currentDesign,
    });
  }

  async updateStyle(styleId: string, updates: Partial<DesignStyle>): Promise<void> {
    // Send style updates to backend
    await this.ws.emit('design:update-style', {
      styleId,
      updates,
      currentDesign: this.currentDesign,
    });
  }

  async finalizeDesign(design: DesignSystem): Promise<void> {
    // Send finalized design to backend for processing
    await this.ws.emit('design:finalize', design);
  }

  disconnect() {
    this.ws.disconnect();
  }

  async processMessage(message: string, currentDesign: Partial<DesignSystem>): Promise<AgentResponse> {
    this.currentDesign = currentDesign;
    
    return new Promise((resolve, reject) => {
      const messageId = Date.now().toString();
      
      const handleResponse = (event: MessageEvent) => {
        const response = JSON.parse(event.data);
        if (response.messageId === messageId) {
          this.socket.removeEventListener('message', handleResponse);
          resolve(response.data);
        }
      };

      this.socket.addEventListener('message', handleResponse);

      this.socket.send(JSON.stringify({
        type: 'process_message',
        messageId,
        data: {
          message,
          currentDesign,
        },
      }));
    });
  }

  async applyToolAction(action: ToolAction): Promise<ToolActionResult> {
    return new Promise((resolve, reject) => {
      const messageId = Date.now().toString();
      
      const handleResponse = (event: MessageEvent) => {
        const response = JSON.parse(event.data);
        if (response.messageId === messageId) {
          this.socket.removeEventListener('message', handleResponse);
          resolve(response.data);
        }
      };

      this.socket.addEventListener('message', handleResponse);

      this.socket.send(JSON.stringify({
        type: 'apply_tool_action',
        messageId,
        data: {
          action,
          currentDesign: this.currentDesign,
        },
      }));
    });
  }

  updateDesign(design: Partial<DesignSystem>) {
    this.currentDesign = design;
  }
} 