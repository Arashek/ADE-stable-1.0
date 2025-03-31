import WebSocket from 'ws';
import http from 'http';
import WebSocketServer from '../../../server/websocket/websocketServer';
import { metricsService } from '../../../server/services/metricsService';
import { redisService } from '../../../server/services/redisService';

jest.mock('../../../server/services/metricsService');
jest.mock('../../../server/services/redisService');

describe('WebSocketServer', () => {
  let wss: WebSocketServer;
  let server: http.Server;
  const jwtSecret = 'test-secret';

  beforeEach(() => {
    server = new http.Server();
    wss = new WebSocketServer(server, jwtSecret);
  });

  afterEach(async () => {
    await wss.close();
    server.close();
  });

  describe('handleConnection', () => {
    it('should increment connection metrics on new connection', async () => {
      const mockSocket = new WebSocket(null) as any;
      mockSocket.on = jest.fn();
      
      await wss['handleConnection'](mockSocket, {} as http.IncomingMessage);

      expect(metricsService.incrementCounter).toHaveBeenCalledWith('connections.total');
      expect(metricsService.updateGauge).toHaveBeenCalledWith('connections.active', expect.any(Number));
    });

    it('should setup message handler', async () => {
      const mockSocket = new WebSocket(null) as any;
      const onSpy = jest.fn();
      mockSocket.on = onSpy;
      
      await wss['handleConnection'](mockSocket, {} as http.IncomingMessage);

      expect(onSpy).toHaveBeenCalledWith('message', expect.any(Function));
    });
  });

  describe('handleMessage', () => {
    it('should handle authentication message', async () => {
      const mockClient = {
        isAuthenticated: false,
        send: jest.fn(),
      } as any;

      const message = {
        type: 'auth',
        token: 'valid-token'
      };

      await wss['handleMessage'](mockClient, JSON.stringify(message));

      expect(metricsService.incrementCounter).toHaveBeenCalledWith('messages.received');
      expect(metricsService.recordTiming).toHaveBeenCalledWith('messages.size', expect.any(Number));
    });

    it('should reject unauthenticated messages', async () => {
      const mockClient = {
        isAuthenticated: false,
        send: jest.fn(),
      } as any;

      const message = {
        type: 'activity',
        action: 'create',
        data: {}
      };

      await wss['handleMessage'](mockClient, JSON.stringify(message));

      expect(mockClient.send).toHaveBeenCalledWith(
        expect.stringContaining('Not authenticated')
      );
    });

    it('should handle entity messages from authenticated clients', async () => {
      const mockClient = {
        isAuthenticated: true,
        userId: 'test-user',
        send: jest.fn(),
      } as any;

      const message = {
        type: 'activity',
        action: 'create',
        data: { id: 1 }
      };

      await wss['handleMessage'](mockClient, JSON.stringify(message));

      expect(metricsService.incrementCounter).toHaveBeenCalledWith('messages.sent');
    });
  });

  describe('broadcast', () => {
    it('should send message to all authenticated clients', async () => {
      const mockClient1 = {
        isAuthenticated: true,
        readyState: WebSocket.OPEN,
        send: jest.fn(),
      } as any;

      const mockClient2 = {
        isAuthenticated: true,
        readyState: WebSocket.OPEN,
        send: jest.fn(),
      } as any;

      wss['clients'].add(mockClient1);
      wss['clients'].add(mockClient2);

      const message = {
        type: 'notification',
        data: { text: 'test' }
      };

      await wss.broadcast(message);

      expect(mockClient1.send).toHaveBeenCalledWith(JSON.stringify(message));
      expect(mockClient2.send).toHaveBeenCalledWith(JSON.stringify(message));
    });

    it('should queue messages for offline clients', async () => {
      const mockClient = {
        isAuthenticated: true,
        readyState: WebSocket.CLOSED,
        userId: 'offline-user',
      } as any;

      wss['clients'].add(mockClient);

      const message = {
        type: 'notification',
        data: { text: 'test' }
      };

      await wss.broadcast(message);

      expect(redisService.queueMessage).toHaveBeenCalledWith(
        'offline-user',
        message
      );
    });
  });

  describe('getServerMetrics', () => {
    it('should return current server metrics', async () => {
      const mockClient1 = { isAuthenticated: true } as any;
      const mockClient2 = { isAuthenticated: false } as any;
      wss['clients'].add(mockClient1);
      wss['clients'].add(mockClient2);

      const metrics = await wss.getServerMetrics();

      expect(metrics).toEqual({
        connections: {
          total: 2,
          authenticated: 1,
          unauthenticated: 1
        },
        messages: expect.any(Object),
        performance: expect.any(Object)
      });
    });
  });
}); 