import { ContainerConfigurator } from '../ContainerConfigurator';
import { ProjectAnalyzer } from '../ProjectAnalyzer';

jest.mock('../ProjectAnalyzer');

describe('ContainerConfigurator', () => {
  let configurator: ContainerConfigurator;
  const mockProjectRoot = '/mock/project/root';

  beforeEach(() => {
    configurator = new ContainerConfigurator(mockProjectRoot);
    jest.clearAllMocks();
  });

  describe('generateConfig', () => {
    it('should generate config for a Next.js project', async () => {
      const mockProjectConfig = {
        language: 'javascript',
        framework: 'next',
        buildTool: 'next',
        dependencies: [
          { name: 'next', version: '^13.0.0', type: 'dependencies' },
          { name: 'react', version: '^18.2.0', type: 'dependencies' }
        ],
        devDependencies: [],
        scripts: {
          start: 'next start',
          dev: 'next dev',
          test: 'jest'
        },
        ports: [3000],
        environment: {
          NODE_ENV: 'development'
        }
      };

      (ProjectAnalyzer.prototype.analyze as jest.Mock).mockResolvedValue(mockProjectConfig);

      const result = await configurator.generateConfig();

      expect(result.baseImage).toBe('node:18-alpine');
      expect(result.ports).toEqual([3000]);
      expect(result.environment).toEqual(mockProjectConfig.environment);
      expect(result.resources.memory).toBe('3Gi');
      expect(result.developmentTools).toContain('next');
    });

    it('should generate config for a Python Django project', async () => {
      const mockProjectConfig = {
        language: 'python',
        framework: 'django',
        buildTool: 'setuptools',
        dependencies: [
          { name: 'django', version: '^3.2.0', type: 'dependencies' }
        ],
        devDependencies: [],
        scripts: {},
        ports: [8000],
        environment: {}
      };

      (ProjectAnalyzer.prototype.analyze as jest.Mock).mockResolvedValue(mockProjectConfig);

      const result = await configurator.generateConfig();

      expect(result.baseImage).toBe('python:3.11-slim');
      expect(result.ports).toEqual([8000]);
      expect(result.resources.memory).toBe('3Gi');
      expect(result.developmentTools).toContain('django-admin');
    });

    it('should generate config for a Java Spring project', async () => {
      const mockProjectConfig = {
        language: 'java',
        framework: 'spring',
        buildTool: 'maven',
        dependencies: [
          { name: 'spring-boot-starter-web', version: '^2.7.0', type: 'dependencies' }
        ],
        devDependencies: [],
        scripts: {},
        ports: [8080],
        environment: {}
      };

      (ProjectAnalyzer.prototype.analyze as jest.Mock).mockResolvedValue(mockProjectConfig);

      const result = await configurator.generateConfig();

      expect(result.baseImage).toBe('openjdk:17-slim');
      expect(result.ports).toEqual([8080]);
      expect(result.resources.memory).toBe('4Gi');
      expect(result.developmentTools).toContain('maven');
    });

    it('should add GPU resources for ML projects', async () => {
      const mockProjectConfig = {
        language: 'python',
        framework: undefined,
        buildTool: 'setuptools',
        dependencies: [
          { name: 'tensorflow', version: '^2.12.0', type: 'dependencies' }
        ],
        devDependencies: [],
        scripts: {},
        ports: [],
        environment: {}
      };

      (ProjectAnalyzer.prototype.analyze as jest.Mock).mockResolvedValue(mockProjectConfig);

      const result = await configurator.generateConfig();

      expect(result.resources.gpu).toEqual({
        count: 1,
        type: 'nvidia'
      });
    });

    it('should generate appropriate volumes for different languages', async () => {
      const mockProjectConfig = {
        language: 'python',
        framework: undefined,
        buildTool: 'setuptools',
        dependencies: [],
        devDependencies: [],
        scripts: {},
        ports: [],
        environment: {}
      };

      (ProjectAnalyzer.prototype.analyze as jest.Mock).mockResolvedValue(mockProjectConfig);

      const result = await configurator.generateConfig();

      expect(result.volumes).toContain('venv:/app/venv');
    });

    it('should generate appropriate commands for different languages', async () => {
      const mockProjectConfig = {
        language: 'python',
        framework: 'flask',
        buildTool: 'setuptools',
        dependencies: [],
        devDependencies: [],
        scripts: {},
        ports: [],
        environment: {}
      };

      (ProjectAnalyzer.prototype.analyze as jest.Mock).mockResolvedValue(mockProjectConfig);

      const result = await configurator.generateConfig();

      expect(result.commands.build).toContain('pip install -r requirements.txt');
      expect(result.commands.dev).toContain('python -m flask run --host=0.0.0.0');
    });
  });
}); 