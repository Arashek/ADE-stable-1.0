import { performanceMonitor } from './performance';

interface CollaborationConfig {
  wsUrl: string;
  reconnectAttempts?: number;
  reconnectDelay?: number;
  heartbeatInterval?: number;
}

interface CollaborationMessage {
  type: string;
  payload: any;
  timestamp: number;
  sender: string;
}

type MessageHandler = (message: CollaborationMessage) => void;

export class CollaborationService {
  private ws: WebSocket | null = null;
  private readonly config: Required<CollaborationConfig>;
  private reconnectCount = 0;
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private messageHandlers: Map<string, Set<MessageHandler>> = new Map();
  private pendingMessages: CollaborationMessage[] = [];

  constructor(config: CollaborationConfig) {
    this.config = {
      wsUrl: config.wsUrl,
      reconnectAttempts: config.reconnectAttempts || 5,
      reconnectDelay: config.reconnectDelay || 1000,
      heartbeatInterval: config.heartbeatInterval || 30000,
    };
  }

  /**
   * Connect to the WebSocket server
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      const startTime = performance.now();

      try {
        this.ws = new WebSocket(this.config.wsUrl);

        this.ws.onopen = () => {
          this.reconnectCount = 0;
          this.startHeartbeat();
          this.processPendingMessages();
          performanceMonitor.recordMetric('ws-connect', performance.now() - startTime);
          resolve();
        };

        this.ws.onclose = () => {
          this.handleDisconnect();
        };

        this.ws.onerror = (error) => {
          performanceMonitor.recordMetric('ws-error', 1);
          reject(error);
        };

        this.ws.onmessage = (event) => {
          this.handleMessage(event);
        };
      } catch (error) {
        performanceMonitor.recordMetric('ws-error', 1);
        reject(error);
      }
    });
  }

  /**
   * Subscribe to a specific message type
   */
  subscribe(type: string, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, new Set());
    }

    const handlers = this.messageHandlers.get(type)!;
    handlers.add(handler);

    return () => {
      handlers.delete(handler);
      if (handlers.size === 0) {
        this.messageHandlers.delete(type);
      }
    };
  }

  /**
   * Send a message through WebSocket
   */
  send(type: string, payload: any): void {
    const message: CollaborationMessage = {
      type,
      payload,
      timestamp: Date.now(),
      sender: 'user', // This should be replaced with actual user ID
    };

    if (this.ws?.readyState === WebSocket.OPEN) {
      const startTime = performance.now();
      try {
        this.ws.send(JSON.stringify(message));
        performanceMonitor.recordMetric('ws-send', performance.now() - startTime);
      } catch (error) {
        performanceMonitor.recordMetric('ws-send-error', 1);
        this.pendingMessages.push(message);
        throw error;
      }
    } else {
      this.pendingMessages.push(message);
      this.reconnect();
    }
  }

  /**
   * Disconnect from the WebSocket server
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.stopHeartbeat();
  }

  /**
   * Handle incoming messages
   */
  private handleMessage(event: MessageEvent): void {
    const startTime = performance.now();

    try {
      const message: CollaborationMessage = JSON.parse(event.data);
      const handlers = this.messageHandlers.get(message.type);

      if (handlers) {
        handlers.forEach(handler => handler(message));
      }

      performanceMonitor.recordMetric('ws-message-processed', performance.now() - startTime);
    } catch (error) {
      performanceMonitor.recordMetric('ws-message-error', 1);
      throw error;
    }
  }

  /**
   * Handle disconnection and reconnection
   */
  private handleDisconnect(): void {
    this.stopHeartbeat();
    performanceMonitor.recordMetric('ws-disconnect', 1);

    if (this.reconnectCount < this.config.reconnectAttempts) {
      this.reconnect();
    } else {
      performanceMonitor.recordMetric('ws-reconnect-failed', 1);
    }
  }

  /**
   * Attempt to reconnect
   */
  private reconnect(): void {
    this.reconnectCount++;
    performanceMonitor.recordMetric('ws-reconnect-attempt', this.reconnectCount);

    setTimeout(() => {
      this.connect().catch(() => {
        performanceMonitor.recordMetric('ws-reconnect-error', 1);
      });
    }, this.config.reconnectDelay * this.reconnectCount);
  }

  /**
   * Start heartbeat to keep connection alive
   */
  private startHeartbeat(): void {
    this.heartbeatInterval = setInterval(() => {
      if (this.ws?.readyState === WebSocket.OPEN) {
        this.send('heartbeat', { timestamp: Date.now() });
      }
    }, this.config.heartbeatInterval);
  }

  /**
   * Stop heartbeat
   */
  private stopHeartbeat(): void {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  /**
   * Process any pending messages
   */
  private processPendingMessages(): void {
    while (this.pendingMessages.length > 0) {
      const message = this.pendingMessages.shift();
      if (message) {
        this.send(message.type, message.payload);
      }
    }
  }
}

// Create a singleton instance with default config
export const collaborationService = new CollaborationService({
  wsUrl: process.env.REACT_APP_WS_URL || 'ws://localhost:8080',
}); 