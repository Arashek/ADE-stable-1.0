import { EventEmitter } from 'events';

interface WebSocketOptions {
  onMessage?: (data: any) => void;
  onError?: (error: any) => void;
}

export class WebSocketService extends EventEmitter {
  private static instance: WebSocketService;
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectTimeout = 1000;
  private isConnecting = false;
  private options: WebSocketOptions = {};
  private url: string;

  private constructor() {
    super();
    this.url = process.env.REACT_APP_WS_URL || 'ws://localhost:8000';
  }

  static getInstance(): WebSocketService {
    if (!WebSocketService.instance) {
      WebSocketService.instance = new WebSocketService();
    }
    return WebSocketService.instance;
  }

  connect(channel: string, options: WebSocketOptions = {}) {
    if (this.isConnecting || this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.options = options;
    this.isConnecting = true;
    this.ws = new WebSocket(this.url);

    this.ws.onopen = () => {
      this.isConnecting = false;
      this.reconnectAttempts = 0;
      this.emit('connected');
      // Subscribe to the channel
      this.send({ type: 'subscribe', channel });
    };

    this.ws.onclose = () => {
      this.isConnecting = false;
      this.emit('disconnected');
      this.handleReconnect();
    };

    this.ws.onerror = (error) => {
      this.isConnecting = false;
      this.emit('error', error);
      if (this.options.onError) {
        this.options.onError(error);
      }
    };

    this.ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        this.emit('message', data);
        if (this.options.onMessage) {
          this.options.onMessage(data);
        }
      } catch (error) {
        console.error('Error parsing WebSocket message:', error);
      }
    };
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      setTimeout(() => {
        this.connect('', this.options);
      }, this.reconnectTimeout * this.reconnectAttempts);
    } else {
      this.emit('reconnect_failed');
    }
  }

  send(data: any) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data));
    } else {
      console.warn('WebSocket is not connected');
    }
  }

  disconnect() {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
      this.emit('disconnected');
    }
  }

  isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }
} 