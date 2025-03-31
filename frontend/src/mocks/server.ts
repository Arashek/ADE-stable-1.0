import { setupServer } from 'msw/node';
import { rest } from 'msw';

// Mock API endpoints
const handlers = [
  // Authentication endpoints
  rest.post('/api/auth/login', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        token: 'mock-token',
        user: {
          id: '1',
          name: 'Test User',
          email: 'test@example.com',
        },
      })
    );
  }),

  rest.post('/api/auth/logout', (req, res, ctx) => {
    return res(ctx.status(200));
  }),

  // User endpoints
  rest.get('/api/user/profile', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: '1',
        name: 'Test User',
        email: 'test@example.com',
        preferences: {
          theme: 'light',
          language: 'en',
        },
      })
    );
  }),

  // Project endpoints
  rest.get('/api/projects', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: '1',
          name: 'Test Project',
          description: 'A test project',
          createdAt: '2024-01-01T00:00:00Z',
          updatedAt: '2024-01-01T00:00:00Z',
        },
      ])
    );
  }),

  rest.post('/api/projects', (req, res, ctx) => {
    return res(
      ctx.status(201),
      ctx.json({
        id: '2',
        name: 'New Project',
        description: 'A new project',
        createdAt: '2024-01-02T00:00:00Z',
        updatedAt: '2024-01-02T00:00:00Z',
      })
    );
  }),

  // Model endpoints
  rest.get('/api/models', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([
        {
          id: '1',
          name: 'Test Model',
          type: 'classification',
          status: 'active',
          metrics: {
            accuracy: 0.95,
            precision: 0.94,
            recall: 0.93,
          },
        },
      ])
    );
  }),

  // Training endpoints
  rest.post('/api/training/start', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: '1',
        status: 'started',
        progress: 0,
      })
    );
  }),

  rest.get('/api/training/:id', (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json({
        id: req.params.id,
        status: 'in_progress',
        progress: 50,
        metrics: {
          loss: 0.5,
          accuracy: 0.85,
        },
      })
    );
  }),

  // Error handling
  rest.get('/api/error', (req, res, ctx) => {
    return res(
      ctx.status(500),
      ctx.json({
        error: 'Internal Server Error',
        message: 'Something went wrong',
      })
    );
  }),

  // WebSocket endpoint
  rest.get('/ws', (req, res, ctx) => {
    return res(
      ctx.status(101),
      ctx.json({
        status: 'connected',
      })
    );
  }),
];

export const server = setupServer(...handlers); 