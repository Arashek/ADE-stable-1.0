import WebSocket from 'ws';
import http from 'http';
import jwt from 'jsonwebtoken';
import { EventEmitter } from 'events';
import { config } from '../config';
import { redisService } from '../services/redisService';
import { metricsService } from '../services/metricsService';
import { IncomingMessage } from 'http';

interface AuthenticatedClient extends WebSocket {
  isAuthenticated: boolean;
  userId?: string;
  pongReceived?: boolean;
}

interface WebSocketMessage {
  type: string;
  action?: string;
  data?: any;
  token?: string;
}

class WebSocketServer extends EventEmitter {
  private wss: WebSocket.Server;
  private clients: Set<AuthenticatedClient> = new Set();
  private jwtSecret: string;
  private pingInterval: NodeJS.Timeout | null = null;

  constructor(server: http.Server, jwtSecret: string) {
    super();
    this.jwtSecret = jwtSecret;
    this.wss = new WebSocket.Server({
      server,
      path: config.wsPath,
      maxPayload: config.ws.maxPayloadSize,
    });
    this.init();
  }

  private init() {
    this.wss.on('connection', this.handleConnection.bind(this));
    this.startPingInterval();
  }

  private startPingInterval() {
    this.pingInterval = setInterval(() => {
      this.clients.forEach(client => {
        if (!client.isAuthenticated) return;

        if (client.pongReceived === false) {
          console.log(`Client ${client.userId} failed to respond to ping, closing connection`);
          client.terminate();
          return;
        }

        client.pongReceived = false;
        client.ping();
      });
    }, config.ws.pingInterval);
  }

  private async handleConnection(socket: WebSocket, request: IncomingMessage): Promise<void> {
    const startTime = Date.now();
    try {
      const client = socket as AuthenticatedClient;
      client.isAuthenticated = false;
      client.pongReceived = true;
      this.clients.add(client);

      await metricsService.incrementCounter('connections.total');
      await metricsService.updateGauge('connections.active', this.clients.size);
      
      if (this.clients.size > (await this.getMetricValue('connections.peak', 0))) {
        await metricsService.updateGauge('connections.peak', this.clients.size);
      }

      socket.on('message', async (data: WebSocket.Data) => {
        try {
          await this.handleMessage(client, data);
        } catch (error) {
          console.error('Failed to parse message:', error);
          this.sendError(client, 'Invalid message format');
        }
      });

      socket.on('close', () => {
        this.clients.delete(client);
        await this.handleClose(client);
      });

      socket.on('error', (error) => {
        console.error('WebSocket error:', error);
        this.clients.delete(client);
      });

      socket.on('pong', () => {
        client.pongReceived = true;
      });
    } catch (error) {
      await metricsService.incrementCounter('connections.errors');
      throw error;
    } finally {
      const duration = Date.now() - startTime;
      await metricsService.recordTiming('connections.handshake_duration', duration);
    }
  }

  private async handleMessage(client: AuthenticatedClient, rawMessage: WebSocket.Data): Promise<void> {
    const startTime = Date.now();
    try {
      await metricsService.incrementCounter('messages.received');
      
      const message = await this.parseMessage(rawMessage);
      const messageSize = this.getMessageSize(rawMessage);
      await metricsService.recordTiming('messages.size', messageSize);

      if (message.compressed) {
        await metricsService.incrementCounter('messages.compressed');
      }

      if (message.type === 'auth') {
        await this.handleAuth(client, message.token);
        return;
      }

      if (!client.isAuthenticated) {
        this.sendError(client, 'Not authenticated');
        return;
      }

      switch (message.type) {
        case 'activity':
        case 'project':
        case 'agent':
        case 'task':
          await this.handleEntityMessage(client, message);
          break;
        default:
          this.sendError(client, 'Unknown message type');
      }

      await metricsService.incrementCounter('messages.sent');
    } catch (error) {
      await metricsService.incrementCounter('messages.errors');
      throw error;
    } finally {
      const duration = Date.now() - startTime;
      await metricsService.recordTiming('messages.processing_time', duration);
    }
  }

  private async handleAuth(client: AuthenticatedClient, token?: string) {
    if (!token) {
      this.sendError(client, 'No authentication token provided');
      return;
    }

    try {
      const decoded = jwt.verify(token, this.jwtSecret) as { userId: string };
      client.isAuthenticated = true;
      client.userId = decoded.userId;
      
      client.send(JSON.stringify({
        type: 'auth',
        success: true
      }));

      // Send queued messages
      const queuedMessages = await redisService.getQueuedMessages(decoded.userId);
      for (const message of queuedMessages) {
        client.send(JSON.stringify(message));
      }
    } catch (error) {
      console.error('Authentication failed:', error);
      this.sendError(client, 'Authentication failed');
      client.close();
    }
  }

  private async handleEntityMessage(client: AuthenticatedClient, message: WebSocketMessage) {
    if (!message.action || !message.data) {
      this.sendError(client, 'Invalid message format');
      return;
    }

    // Emit event for external handlers
    this.emit(`${message.type}:${message.action}`, {
      userId: client.userId,
      data: message.data
    });

    // Broadcast to all authenticated clients
    await this.broadcast(message, [client]);
  }

  private sendError(client: WebSocket, message: string) {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify({
        type: 'error',
        message
      }));
    }
  }

  public async broadcast(message: WebSocketMessage, excludeClients: WebSocket[] = []) {
    const offlineUsers = new Set<string>();

    // Send to connected clients
    this.clients.forEach(client => {
      if (client.isAuthenticated && !excludeClients.includes(client)) {
        if (client.readyState === WebSocket.OPEN) {
          client.send(JSON.stringify(message));
        } else if (client.userId) {
          offlineUsers.add(client.userId);
        }
      }
    });

    // Queue messages for offline users
    for (const userId of offlineUsers) {
      await redisService.queueMessage(userId, message);
    }
  }

  public async sendToUser(userId: string, message: WebSocketMessage) {
    let delivered = false;

    // Try to send to connected client
    this.clients.forEach(client => {
      if (client.isAuthenticated && client.userId === userId && client.readyState === WebSocket.OPEN) {
        client.send(JSON.stringify(message));
        delivered = true;
      }
    });

    // Queue message if user is offline
    if (!delivered) {
      await redisService.queueMessage(userId, message);
    }
  }

  private async handleClose(client: AuthenticatedClient): Promise<void> {
    await metricsService.updateGauge('connections.active', this.clients.size);
  }

  private getMessageSize(message: WebSocket.Data): number {
    if (typeof message === 'string') {
      return Buffer.from(message).length;
    } else if (message instanceof Buffer) {
      return message.length;
    } else if (Array.isArray(message)) {
      return message.reduce((sum, part) => sum + this.getMessageSize(part), 0);
    }
    return 0;
  }

  public async getServerMetrics(): Promise<Record<string, any>> {
    const metrics = {
      connections: {
        total: this.clients.size,
        authenticated: Array.from(this.clients).filter(client => client.isAuthenticated).length,
        unauthenticated: Array.from(this.clients).filter(client => !client.isAuthenticated).length
      },
      messages: {
        sent: await this.getMetricValue('messages.sent', 0),
        received: await this.getMetricValue('messages.received', 0),
        errors: await this.getMetricValue('messages.errors', 0),
        compressed: await this.getMetricValue('messages.compressed', 0)
      },
      performance: {
        avgMessageSize: await this.getMetricValue('messages.size', 0),
        avgProcessingTime: await this.getMetricValue('messages.processing_time', 0)
      }
    };

    return metrics;
  }

  private async getMetricValue(metric: string, defaultValue: number): Promise<number> {
    const date = new Date().toISOString().split('T')[0];
    const key = `metrics:${metric}:${date}`;
    const value = await this.redisService.get(key);
    return value ? parseFloat(value) : defaultValue;
  }

  public async close(): Promise<void> {
    await metricsService.close();
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
    }

    this.clients.forEach(client => {
      client.terminate();
    });
    this.wss.close();
  }
}

export default WebSocketServer; 