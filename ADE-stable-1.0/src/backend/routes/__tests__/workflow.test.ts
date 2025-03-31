import request from 'supertest';
import express from 'express';
import workflowRouter from '../workflow';
import { Container } from '../../../core/models/project/Container';
import { DevelopmentWorkflowManager } from '../../../core/models/project/DevelopmentWorkflowManager';
import { Logger } from '../../../core/logging/Logger';
import { WorkflowStatus, WorkflowResult, WorkflowStage } from '../../../core/models/project/DevelopmentWorkflowManager';

jest.mock('../../../core/models/project/Container');
jest.mock('../../../core/models/project/DevelopmentWorkflowManager');
jest.mock('../../../core/logging/Logger');

describe('Workflow Routes', () => {
  let app: express.Application;
  let mockContainer: jest.Mocked<Container>;
  let mockWorkflowManager: jest.Mocked<DevelopmentWorkflowManager>;
  let mockLogger: jest.Mocked<Logger>;

  beforeEach(() => {
    app = express();
    app.use(express.json());
    app.use('/api/workflow', workflowRouter);

    mockContainer = new Container('test-id', 'test-container') as jest.Mocked<Container>;
    mockWorkflowManager = new DevelopmentWorkflowManager(
      mockContainer,
      {} as any,
      new Logger()
    ) as jest.Mocked<DevelopmentWorkflowManager>;
    mockLogger = new Logger() as jest.Mocked<Logger>;

    (Container.getById as jest.Mock).mockResolvedValue(mockContainer);
  });

  describe('GET /:containerId/config', () => {
    it('should return workflow configuration', async () => {
      const response = await request(app)
        .get('/api/workflow/test-id/config')
        .set('Authorization', 'Bearer test-token');

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('versionControl');
      expect(response.body).toHaveProperty('ci');
      expect(response.body).toHaveProperty('cd');
      expect(response.body).toHaveProperty('testing');
    });

    it('should return 404 when container not found', async () => {
      (Container.getById as jest.Mock).mockResolvedValue(null);

      const response = await request(app)
        .get('/api/workflow/nonexistent/config')
        .set('Authorization', 'Bearer test-token');

      expect(response.status).toBe(404);
      expect(response.body).toHaveProperty('error', 'Container not found');
    });

    it('should return 401 when no token provided', async () => {
      const response = await request(app)
        .get('/api/workflow/test-id/config');

      expect(response.status).toBe(401);
      expect(response.body).toHaveProperty('error', 'Authentication token required');
    });
  });

  describe('PUT /:containerId/config', () => {
    it('should update workflow configuration', async () => {
      const config = {
        versionControl: {
          type: 'git',
          repository: 'https://github.com/test/repo',
          branch: 'main',
          enabled: true
        },
        ci: {
          enabled: true,
          stages: ['build', 'test'],
          testCommand: 'npm test',
          buildCommand: 'npm run build'
        },
        cd: {
          enabled: true,
          deploymentTargets: ['staging'],
          deploymentStrategy: 'rolling'
        },
        testing: {
          environment: 'development',
          coverageThreshold: 80,
          testSuites: ['unit'],
          testCommand: 'npm test'
        }
      };

      const response = await request(app)
        .put('/api/workflow/test-id/config')
        .set('Authorization', 'Bearer test-token')
        .send(config);

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('message', 'Configuration updated successfully');
    });
  });

  describe('GET /:containerId/status', () => {
    it('should return workflow status', async () => {
      const mockStatus: WorkflowStatus = {
        status: 'idle',
        progress: 0,
        lastUpdated: new Date()
      };

      mockWorkflowManager.getStatus.mockReturnValue(mockStatus);

      const response = await request(app)
        .get('/api/workflow/test-id/status')
        .set('Authorization', 'Bearer test-token');

      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockStatus);
    });
  });

  describe('GET /:containerId/result', () => {
    it('should return workflow result', async () => {
      const mockStage: WorkflowStage = {
        name: 'Build',
        status: 'success',
        duration: 1000,
        output: 'Build completed successfully'
      };

      const mockResult: WorkflowResult = {
        success: true,
        stages: [mockStage],
        summary: {
          passedTests: 10,
          totalTests: 10,
          coverage: 85
        }
      };

      mockWorkflowManager.getResult.mockReturnValue(mockResult);

      const response = await request(app)
        .get('/api/workflow/test-id/result')
        .set('Authorization', 'Bearer test-token');

      expect(response.status).toBe(200);
      expect(response.body).toEqual(mockResult);
    });
  });

  describe('POST /:containerId/start', () => {
    it('should start the workflow', async () => {
      mockWorkflowManager.startWorkflow.mockResolvedValue(undefined);

      const response = await request(app)
        .post('/api/workflow/test-id/start')
        .set('Authorization', 'Bearer test-token');

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('message', 'Workflow started successfully');
    });

    it('should handle workflow start errors', async () => {
      mockWorkflowManager.startWorkflow.mockRejectedValue(new Error('Start failed'));

      const response = await request(app)
        .post('/api/workflow/test-id/start')
        .set('Authorization', 'Bearer test-token');

      expect(response.status).toBe(500);
      expect(response.body).toHaveProperty('error', 'Failed to start workflow');
    });
  });

  describe('POST /:containerId/stop', () => {
    it('should stop the workflow', async () => {
      mockWorkflowManager.stopWorkflow.mockResolvedValue(undefined);

      const response = await request(app)
        .post('/api/workflow/test-id/stop')
        .set('Authorization', 'Bearer test-token');

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('message', 'Workflow stopped successfully');
    });

    it('should handle workflow stop errors', async () => {
      mockWorkflowManager.stopWorkflow.mockRejectedValue(new Error('Stop failed'));

      const response = await request(app)
        .post('/api/workflow/test-id/stop')
        .set('Authorization', 'Bearer test-token');

      expect(response.status).toBe(500);
      expect(response.body).toHaveProperty('error', 'Failed to stop workflow');
    });
  });
}); 