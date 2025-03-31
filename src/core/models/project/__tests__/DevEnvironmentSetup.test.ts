import { DevEnvironmentSetup, DevEnvironmentConfig } from '../DevEnvironmentSetup';
import * as fs from 'fs';
import * as path from 'path';

jest.mock('fs');
jest.mock('path');

describe('DevEnvironmentSetup', () => {
  let setup: DevEnvironmentSetup;
  const mockProjectRoot = '/mock/project/root';

  beforeEach(() => {
    setup = new DevEnvironmentSetup(mockProjectRoot);
    jest.clearAllMocks();
  });

  describe('generateConfig', () => {
    it('should generate config for a JavaScript project', async () => {
      const mockProjectConfig = {
        language: 'javascript',
        framework: 'next',
        buildTool: 'vite',
        dependencies: [],
        devDependencies: [],
        scripts: {},
        ports: [],
        environment: {}
      };

      const result = await setup.generateConfig(mockProjectConfig);

      expect(result.tools).toContainEqual(
        expect.objectContaining({
          name: 'node',
          version: '18.x',
          type: 'tool'
        })
      );
      expect(result.tools).toContainEqual(
        expect.objectContaining({
          name: 'next',
          version: 'latest',
          type: 'tool'
        })
      );
      expect(result.environmentVariables).toHaveProperty('NODE_ENV', 'development');
      expect(result.buildTools).toContainEqual(
        expect.objectContaining({
          name: 'vite',
          version: 'latest'
        })
      );
      expect(result.testTools).toContainEqual(
        expect.objectContaining({
          name: 'jest',
          version: 'latest'
        })
      );
    });

    it('should generate config for a Python project', async () => {
      const mockProjectConfig = {
        language: 'python',
        framework: 'django',
        buildTool: 'setuptools',
        dependencies: [],
        devDependencies: [],
        scripts: {},
        ports: [],
        environment: {}
      };

      const result = await setup.generateConfig(mockProjectConfig);

      expect(result.tools).toContainEqual(
        expect.objectContaining({
          name: 'python',
          version: '3.11',
          type: 'tool'
        })
      );
      expect(result.tools).toContainEqual(
        expect.objectContaining({
          name: 'django-admin',
          version: 'latest',
          type: 'tool'
        })
      );
      expect(result.environmentVariables).toHaveProperty('PYTHONUNBUFFERED', '1');
      expect(result.buildTools).toContainEqual(
        expect.objectContaining({
          name: 'setuptools',
          version: 'latest'
        })
      );
      expect(result.testTools).toContainEqual(
        expect.objectContaining({
          name: 'pytest',
          version: 'latest'
        })
      );
    });

    it('should generate config for a Java project', async () => {
      const mockProjectConfig = {
        language: 'java',
        framework: 'spring',
        buildTool: 'maven',
        dependencies: [],
        devDependencies: [],
        scripts: {},
        ports: [],
        environment: {}
      };

      const result = await setup.generateConfig(mockProjectConfig);

      expect(result.tools).toContainEqual(
        expect.objectContaining({
          name: 'jdk',
          version: '17',
          type: 'tool'
        })
      );
      expect(result.environmentVariables).toHaveProperty('JAVA_HOME');
      expect(result.buildTools).toContainEqual(
        expect.objectContaining({
          name: 'maven',
          version: '3.8.x'
        })
      );
      expect(result.testTools).toContainEqual(
        expect.objectContaining({
          name: 'junit',
          version: '5.x'
        })
      );
    });
  });

  describe('installDevTools', () => {
    it('should install development tools and create config files', async () => {
      const mockConfig: DevEnvironmentConfig = {
        tools: [
          {
            name: 'git',
            version: 'latest',
            type: 'tool' as const,
            installCommand: 'apt-get install -y git'
          }
        ],
        environmentVariables: {
          TEST_VAR: 'test_value'
        },
        buildTools: [
          {
            name: 'webpack',
            version: '5.x',
            config: { mode: 'development' }
          }
        ],
        testTools: [
          {
            name: 'jest',
            version: 'latest',
            config: { testEnvironment: 'node' }
          }
        ]
      };

      await setup.installDevTools(mockConfig);

      expect(fs.promises.writeFile).toHaveBeenCalledWith(
        expect.stringContaining('.env'),
        expect.stringContaining('TEST_VAR=test_value')
      );
      expect(fs.promises.writeFile).toHaveBeenCalledWith(
        expect.stringContaining('webpack.config.json'),
        expect.stringContaining('"mode": "development"')
      );
      expect(fs.promises.writeFile).toHaveBeenCalledWith(
        expect.stringContaining('jest.config.json'),
        expect.stringContaining('"testEnvironment": "node"')
      );
    });

    it('should handle errors during installation', async () => {
      const mockConfig = {
        tools: [],
        environmentVariables: {},
        buildTools: [],
        testTools: []
      };

      (fs.promises.writeFile as jest.Mock).mockRejectedValue(new Error('Write failed'));

      await expect(setup.installDevTools(mockConfig)).rejects.toThrow('Write failed');
    });
  });
}); 