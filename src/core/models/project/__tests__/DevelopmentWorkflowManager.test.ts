import { DevelopmentWorkflowManager, WorkflowConfig } from '../DevelopmentWorkflowManager';
import { Container } from '../Container';
import { Logger } from '../../../logging/Logger';

jest.mock('../Container');
jest.mock('../../../logging/Logger');

describe('DevelopmentWorkflowManager', () => {
  let workflowManager: DevelopmentWorkflowManager;
  let mockContainer: jest.Mocked<Container>;
  let mockLogger: jest.Mocked<Logger>;

  beforeEach(() => {
    mockContainer = new Container('test-id', 'test-container') as jest.Mocked<Container>;
    mockLogger = new Logger() as jest.Mocked<Logger>;
    workflowManager = new DevelopmentWorkflowManager(mockContainer, {}, mockLogger);
  });

  describe('getConfiguration', () => {
    it('should return default configuration', () => {
      const config = workflowManager.getConfiguration();
      expect(config).toEqual({
        versionControl: {
          type: 'git',
          repository: '',
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
      });
    });
  });

  describe('updateConfiguration', () => {
    it('should update configuration with new values', async () => {
      const newConfig: Partial<WorkflowConfig> = {
        versionControl: {
          type: 'git',
          repository: 'https://github.com/test/repo',
          branch: 'develop',
          enabled: true
        },
        ci: {
          enabled: true,
          stages: ['build', 'test', 'lint'],
          testCommand: 'jest',
          buildCommand: 'tsc'
        }
      };

      await workflowManager.updateConfiguration(newConfig);
      const config = workflowManager.getConfiguration();

      expect(config.versionControl.repository).toBe('https://github.com/test/repo');
      expect(config.versionControl.branch).toBe('develop');
      expect(config.ci.stages).toContain('lint');
      expect(config.ci.testCommand).toBe('jest');
      expect(config.ci.buildCommand).toBe('tsc');
    });
  });

  describe('getStatus', () => {
    it('should return initial status', () => {
      const status = workflowManager.getStatus();
      expect(status).toEqual({
        status: 'idle',
        progress: 0,
        lastUpdated: expect.any(Date)
      });
    });
  });

  describe('getResult', () => {
    it('should return null initially', () => {
      const result = workflowManager.getResult();
      expect(result).toBeNull();
    });
  });

  describe('startWorkflow', () => {
    it('should start workflow and execute stages', async () => {
      mockContainer.executeCommand.mockResolvedValue('Command output');

      await workflowManager.startWorkflow();

      expect(mockContainer.executeCommand).toHaveBeenCalledWith('npm run build');
      expect(mockContainer.executeCommand).toHaveBeenCalledWith('npm test');
      expect(workflowManager.getStatus().status).toBe('completed');
      expect(workflowManager.getResult()).toBeTruthy();
    });

    it('should handle stage failures', async () => {
      mockContainer.executeCommand
        .mockResolvedValueOnce('Build output')
        .mockRejectedValueOnce(new Error('Test failed'));

      await expect(workflowManager.startWorkflow()).rejects.toThrow('Test failed');
      expect(workflowManager.getStatus().status).toBe('failed');
    });

    it('should not start if already running', async () => {
      mockContainer.executeCommand.mockResolvedValue('Command output');

      // Start workflow
      await workflowManager.startWorkflow();

      // Try to start again
      await expect(workflowManager.startWorkflow()).rejects.toThrow('Workflow is already running');
    });
  });

  describe('stopWorkflow', () => {
    it('should stop running workflow', async () => {
      mockContainer.executeCommand.mockResolvedValue('Command output');

      // Start workflow
      await workflowManager.startWorkflow();

      // Stop workflow
      await workflowManager.stopWorkflow();

      expect(workflowManager.getStatus().status).toBe('idle');
      expect(workflowManager.getStatus().progress).toBe(0);
    });

    it('should not stop if not running', async () => {
      await expect(workflowManager.stopWorkflow()).rejects.toThrow('Workflow is not running');
    });
  });
}); 