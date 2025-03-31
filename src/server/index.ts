import express from 'express';
import http from 'http';
import cors from 'cors';
import { config } from './config';
import WebSocketServer from './websocket/websocketServer';
import { redisService } from './services/redisService';
import metricsRoutes from './routes/metricsRoutes';

const app = express();
const server = http.createServer(app);

// Initialize WebSocket server
const wss = new WebSocketServer(server, config.jwtSecret);

// Middleware
app.use(cors({
  origin: config.corsOrigins,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'PATCH'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true
}));
app.use(express.json({ limit: '1mb' }));

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({ status: 'ok' });
});

// Example of broadcasting updates when entities change
app.post('/api/activities', async (req, res) => {
  try {
    // ... handle activity creation
    const newActivity = req.body;

    // Broadcast to all connected clients
    await wss.broadcast({
      type: 'activity',
      action: 'create',
      data: newActivity
    });

    res.status(201).json(newActivity);
  } catch (error) {
    console.error('Failed to create activity:', error);
    res.status(500).json({ error: 'Failed to create activity' });
  }
});

// Example of sending updates to specific users
app.post('/api/tasks/:userId', async (req, res) => {
  try {
    const { userId } = req.params;
    const newTask = req.body;

    // ... handle task creation

    // Send to specific user
    await wss.sendToUser(userId, {
      type: 'task',
      action: 'create',
      data: newTask
    });

    res.status(201).json(newTask);
  } catch (error) {
    console.error('Failed to create task:', error);
    res.status(500).json({ error: 'Failed to create task' });
  }
});

// Listen for WebSocket events
wss.on('project:update', ({ userId, data }) => {
  console.log(`Project update from user ${userId}:`, data);
  // Handle project updates (e.g., update database)
});

// Add metrics routes
app.use('/api', metricsRoutes);

// Graceful shutdown handling
const shutdown = async () => {
  console.log('Shutting down server...');
  
  // Close HTTP server
  server.close(() => {
    console.log('HTTP server closed');
  });

  // Close WebSocket server
  wss.close();
  console.log('WebSocket server closed');

  // Close Redis connection
  await redisService.close();
  console.log('Redis connection closed');

  process.exit(0);
};

// Handle shutdown signals
process.on('SIGTERM', shutdown);
process.on('SIGINT', shutdown);

// Start server
server.listen(config.port, () => {
  console.log(`Server running on port ${config.port}`);
  console.log(`WebSocket server running on ws://localhost:${config.port}${config.wsPath}`);
}); 