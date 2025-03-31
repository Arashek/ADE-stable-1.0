import WebSocket from 'ws';
import http from 'http';
import express from 'express';
import { Redis } from 'ioredis';
import jwt from 'jsonwebtoken';
import { WebSocketServer } from '../../../server/websocket/websocketServer';
import { metricsService } from '../../../server/services/metricsService';
import { rateLimiterService } from '../../../server/services/rateLimiterService';
import { redisService } from '../../../server/services/redisService';
import metricsRoutes from '../../../server/routes/metricsRoutes';

describe('System Integration Tests', () => {
  let app: express.Application;
  let server: http.Server;
  let wss: WebSocketServer;
  let client: WebSocket;
  const TEST_PORT = 8888;
  const JWT_SECRET = 'test-secret';

  beforeAll(async () => {
    // Setup Express app
    app = express();
    app.use(express.json());
    app.use('/api', metricsRoutes);

    // Setup HTTP server
    server = http.createServer(app);
    server.listen(TEST_PORT);

    // Setup WebSocket server
    wss = new WebSocketServer(server, JWT_SECRET);

    // Wait for server to be ready
    await new Promise(resolve => server.once('listening', resolve));
  });

  afterAll(async () => {
    await wss.close();
    await server.close();
    await metricsService.close();
    await rateLimiterService.close();
    await redisService.close();
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('WebSocket Connection Flow', () => {
    it('should handle complete connection and authentication flow', async () => {
      // Create client connection
      client = new WebSocket(`ws://localhost:${TEST_PORT}`);
      
      // Wait for connection
      await new Promise(resolve => client.once('open', resolve));

      // Generate valid JWT
      const token = jwt.sign({ userId: 'test-user' }, JWT_SECRET);

      // Send auth message
      const authMessage = {
        type: 'auth',
        token
      };
      client.send(JSON.stringify(authMessage));

      // Wait for auth response
      const response = await new Promise(resolve => {
        client.once('message', data => {
          resolve(JSON.parse(data.toString()));
        });
      });

      expect(response).toEqual({
        type: 'auth',
        status: 'success'
      });

      // Verify metrics were recorded
      expect(metricsService.incrementCounter).toHaveBeenCalledWith('connections.total');
      expect(metricsService.updateGauge).toHaveBeenCalledWith('connections.active', expect.any(Number));
    });

    it('should handle message rate limiting', async () => {
      const token = jwt.sign({ userId: 'test-user' }, JWT_SECRET);
      client = new WebSocket(`ws://localhost:${TEST_PORT}`);
      
      await new Promise(resolve => client.once('open', resolve));
      client.send(JSON.stringify({ type: 'auth', token }));
      
      // Wait for auth
      await new Promise(resolve => client.once('message', resolve));

      // Send messages rapidly
      const messages = Array(150).fill(null).map((_, i) => ({
        type: 'activity',
        action: 'create',
        data: { id: i }
      }));

      for (const message of messages) {
        client.send(JSON.stringify(message));
      }

      // Wait for rate limit response
      const response = await new Promise(resolve => {
        client.once('message', data => {
          resolve(JSON.parse(data.toString()));
        });
      });

      expect(response).toEqual({
        type: 'error',
        error: 'Rate limit exceeded'
      });

      // Verify rate limit metrics
      expect(metricsService.incrementCounter).toHaveBeenCalledWith('rateLimit.blocked');
    });
  });

  describe('Metrics API Integration', () => {
    it('should return aggregated metrics', async () => {
      const response = await fetch(`http://localhost:${TEST_PORT}/api/metrics`);
      const metrics = await response.json();

      expect(metrics).toEqual(expect.objectContaining({
        connections: expect.any(Object),
        messages: expect.any(Object),
        performance: expect.any(Object),
        rateLimit: expect.any(Object)
      }));
    });

    it('should return histogram data', async () => {
      // Record some timing data
      await metricsService.recordTiming('test.timing', 100);
      await metricsService.recordTiming('test.timing', 200);
      await metricsService.recordTiming('test.timing', 300);

      const response = await fetch(`http://localhost:${TEST_PORT}/api/metrics/histogram/test.timing`);
      const histogram = await response.json();

      expect(histogram).toEqual([300, 200, 100]);
    });
  });

  describe('Message Queueing and Delivery', () => {
    it('should queue messages for offline clients and deliver on reconnection', async () => {
      // Setup: authenticate client and then disconnect
      const token = jwt.sign({ userId: 'test-user' }, JWT_SECRET);
      client = new WebSocket(`ws://localhost:${TEST_PORT}`);
      
      await new Promise(resolve => client.once('open', resolve));
      client.send(JSON.stringify({ type: 'auth', token }));
      await new Promise(resolve => client.once('message', resolve));

      // Queue messages while client is offline
      client.close();
      await new Promise(resolve => client.once('close', resolve));

      const queuedMessages = [
        { type: 'notification', data: { text: 'test1' } },
        { type: 'notification', data: { text: 'test2' } }
      ];

      for (const message of queuedMessages) {
        await redisService.queueMessage('test-user', message);
      }

      // Reconnect client
      client = new WebSocket(`ws://localhost:${TEST_PORT}`);
      await new Promise(resolve => client.once('open', resolve));
      client.send(JSON.stringify({ type: 'auth', token }));

      // Verify queued messages are delivered
      const messages = await Promise.all(
        queuedMessages.map(() => 
          new Promise(resolve => client.once('message', data => resolve(JSON.parse(data.toString()))))
      ));

      expect(messages).toEqual(queuedMessages);
    });
  });

  describe('System Performance', () => {
    it('should handle concurrent connections', async () => {
      const NUM_CLIENTS = 50;
      const clients = await Promise.all(
        Array(NUM_CLIENTS).fill(null).map(async () => {
          const ws = new WebSocket(`ws://localhost:${TEST_PORT}`);
          await new Promise(resolve => ws.once('open', resolve));
          return ws;
        })
      );

      const metrics = await fetch(`http://localhost:${TEST_PORT}/api/metrics`).then(r => r.json());
      expect(metrics.connections.active).toBe(NUM_CLIENTS);

      // Cleanup
      await Promise.all(clients.map(ws => new Promise(resolve => {
        ws.close();
        ws.once('close', resolve);
      })));
    });

    it('should maintain performance under load', async () => {
      const NUM_MESSAGES = 1000;
      const token = jwt.sign({ userId: 'test-user' }, JWT_SECRET);
      client = new WebSocket(`ws://localhost:${TEST_PORT}`);
      
      await new Promise(resolve => client.once('open', resolve));
      client.send(JSON.stringify({ type: 'auth', token }));
      await new Promise(resolve => client.once('message', resolve));

      const startTime = Date.now();
      
      // Send messages in parallel
      await Promise.all(
        Array(NUM_MESSAGES).fill(null).map((_, i) => 
          new Promise<void>(resolve => {
            client.send(JSON.stringify({
              type: 'activity',
              action: 'create',
              data: { id: i }
            }));
            resolve();
          })
        )
      );

      const endTime = Date.now();
      const duration = endTime - startTime;
      const messagesPerSecond = (NUM_MESSAGES / duration) * 1000;

      // Verify performance metrics
      const metrics = await fetch(`http://localhost:${TEST_PORT}/api/metrics`).then(r => r.json());
      expect(messagesPerSecond).toBeGreaterThan(100); // At least 100 msgs/sec
      expect(metrics.performance.avgProcessingTime).toBeLessThan(10); // Less than 10ms per message
    });
  });
}); 