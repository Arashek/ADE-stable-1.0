import { Activity } from '../components/dashboard/ActivitySummary';
import { Project } from '../components/dashboard/ProjectsOverview';
import { Agent } from '../components/dashboard/AgentStatusCard';
import { Task } from '../components/dashboard/RecentTasks';
import { notificationService } from './notificationService';

type WebSocketMessage = {
  type: 'activity' | 'project' | 'agent' | 'task';
  action: 'create' | 'update' | 'delete';
  data: Activity | Project | Agent | Task;
};

type MessageHandler = (message: WebSocketMessage) => void;

interface QueuedMessage {
  message: Partial<WebSocketMessage>;
  timestamp: number;
  retries: number;
}

class WebSocketService {
  private socket: WebSocket | null = null;
  private messageHandlers: Set<MessageHandler> = new Set();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private messageQueue: QueuedMessage[] = [];
  private maxQueueSize = 1000;
  private maxRetries = 3;
  private isAuthenticated = false;
  private authToken: string | null = null;

  constructor() {
    this.loadQueueFromStorage();
    window.addEventListener('online', this.handleOnline.bind(this));
    window.addEventListener('offline', this.handleOffline.bind(this));
  }

  public setAuthToken(token: string) {
    this.authToken = token;
    this.connect();
  }

  private loadQueueFromStorage() {
    try {
      const savedQueue = localStorage.getItem('wsMessageQueue');
      if (savedQueue) {
        this.messageQueue = JSON.parse(savedQueue);
        // Clean up old messages (older than 24 hours)
        const yesterday = Date.now() - 24 * 60 * 60 * 1000;
        this.messageQueue = this.messageQueue.filter(msg => msg.timestamp > yesterday);
        this.saveQueueToStorage();
      }
    } catch (error) {
      console.error('Failed to load message queue from storage:', error);
    }
  }

  private saveQueueToStorage() {
    try {
      localStorage.setItem('wsMessageQueue', JSON.stringify(this.messageQueue));
    } catch (error) {
      console.error('Failed to save message queue to storage:', error);
    }
  }

  private connect() {
    if (!this.authToken) {
      notificationService.error('WebSocket authentication token not provided');
      return;
    }

    const wsUrl = process.env.REACT_APP_WS_URL || 'ws://localhost:3001/ws';
    
    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        this.authenticate();
      };

      this.socket.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          
          if (message.type === 'auth') {
            this.handleAuthResponse(message);
            return;
          }

          if (!this.isAuthenticated) {
            this.queueMessage(message);
            return;
          }

          this.messageHandlers.forEach(handler => handler(message));
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
          notificationService.error('Failed to process server message');
        }
      };

      this.socket.onclose = (event) => {
        this.isAuthenticated = false;
        if (event.wasClean) {
          notificationService.info('WebSocket connection closed');
        } else {
          notificationService.warning('WebSocket connection lost');
        }
        this.handleReconnect();
      };

      this.socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        notificationService.error('WebSocket connection error');
      };
    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      notificationService.error('Failed to establish WebSocket connection');
      this.handleReconnect();
    }
  }

  private authenticate() {
    if (!this.socket || !this.authToken) return;

    this.socket.send(JSON.stringify({
      type: 'auth',
      token: this.authToken
    }));
  }

  private handleAuthResponse(message: any) {
    if (message.success) {
      this.isAuthenticated = true;
      this.reconnectAttempts = 0;
      this.reconnectDelay = 1000;
      notificationService.success('WebSocket connected');
      this.processMessageQueue();
    } else {
      this.isAuthenticated = false;
      notificationService.error('WebSocket authentication failed');
      this.socket?.close();
    }
  }

  private handleReconnect() {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      notificationService.info(
        `Attempting to reconnect (${this.reconnectAttempts}/${this.maxReconnectAttempts})...`
      );
      
      setTimeout(() => {
        this.connect();
      }, this.reconnectDelay);
      
      this.reconnectDelay *= 2;
    } else {
      notificationService.error('Max reconnection attempts reached');
    }
  }

  private handleOnline() {
    notificationService.info('Network connection restored');
    this.connect();
  }

  private handleOffline() {
    notificationService.warning('Network connection lost');
    this.isAuthenticated = false;
  }

  private queueMessage(message: Partial<WebSocketMessage>) {
    if (this.messageQueue.length >= this.maxQueueSize) {
      // Remove oldest message if queue is full
      this.messageQueue.shift();
    }

    this.messageQueue.push({
      message,
      timestamp: Date.now(),
      retries: 0
    });

    this.saveQueueToStorage();
  }

  private async processMessageQueue() {
    if (!this.isAuthenticated || this.messageQueue.length === 0) return;

    const processedMessages: QueuedMessage[] = [];
    const failedMessages: QueuedMessage[] = [];

    for (const queuedMessage of this.messageQueue) {
      if (queuedMessage.retries >= this.maxRetries) {
        notificationService.error(
          `Message delivery failed after ${this.maxRetries} attempts`
        );
        continue;
      }

      try {
        await this.send(queuedMessage.message);
        processedMessages.push(queuedMessage);
      } catch (error) {
        queuedMessage.retries++;
        failedMessages.push(queuedMessage);
      }
    }

    // Remove processed messages from queue
    this.messageQueue = this.messageQueue.filter(
      msg => !processedMessages.includes(msg)
    );

    // Update queue in storage
    this.saveQueueToStorage();

    if (failedMessages.length > 0) {
      notificationService.warning(
        `${failedMessages.length} messages failed to send and will be retried`
      );
    }
  }

  public subscribe(handler: MessageHandler): () => void {
    this.messageHandlers.add(handler);
    return () => {
      this.messageHandlers.delete(handler);
    };
  }

  public async send(message: Partial<WebSocketMessage>): Promise<void> {
    if (!navigator.onLine) {
      this.queueMessage(message);
      notificationService.info('Message queued for delivery when online');
      return;
    }

    if (!this.isAuthenticated || !this.socket || this.socket.readyState !== WebSocket.OPEN) {
      this.queueMessage(message);
      return;
    }

    return new Promise((resolve, reject) => {
      try {
        this.socket!.send(JSON.stringify(message));
        resolve();
      } catch (error) {
        this.queueMessage(message);
        reject(error);
      }
    });
  }

  public disconnect() {
    window.removeEventListener('online', this.handleOnline.bind(this));
    window.removeEventListener('offline', this.handleOffline.bind(this));
    
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
    
    this.isAuthenticated = false;
  }
}

export const websocketService = new WebSocketService(); 