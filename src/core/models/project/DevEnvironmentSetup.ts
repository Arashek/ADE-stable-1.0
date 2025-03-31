import { Logger } from '../logging/Logger';
import { ProjectConfig } from './ProjectAnalyzer';
import * as fs from 'fs';
import * as path from 'path';

export interface DevTool {
  name: string;
  version: string;
  type: 'ide' | 'extension' | 'plugin' | 'build' | 'test' | 'tool';
  installCommand: string;
  config?: Record<string, any>;
}

export interface DevEnvironmentConfig {
  tools: DevTool[];
  environmentVariables: Record<string, string>;
  buildTools: {
    name: string;
    version: string;
    config: Record<string, any>;
  }[];
  testTools: {
    name: string;
    version: string;
    config: Record<string, any>;
  }[];
}

export class DevEnvironmentSetup {
  private logger: Logger;
  private projectRoot: string;

  constructor(projectRoot: string) {
    this.logger = new Logger('DevEnvironmentSetup');
    this.projectRoot = projectRoot;
  }

  async generateConfig(projectConfig: ProjectConfig): Promise<DevEnvironmentConfig> {
    try {
      const tools = this.getDevelopmentTools(projectConfig);
      const environmentVariables = this.getEnvironmentVariables(projectConfig);
      const buildTools = this.getBuildTools(projectConfig);
      const testTools = this.getTestTools(projectConfig);

      return {
        tools,
        environmentVariables,
        buildTools,
        testTools
      };
    } catch (error) {
      this.logger.error('Failed to generate dev environment config', error);
      throw error;
    }
  }

  private getDevelopmentTools(projectConfig: ProjectConfig): DevTool[] {
    const tools: DevTool[] = [];
    const { language, framework } = projectConfig;

    // Common development tools
    tools.push(
      {
        name: 'git',
        version: 'latest',
        type: 'tool',
        installCommand: 'apt-get install -y git'
      },
      {
        name: 'curl',
        version: 'latest',
        type: 'tool',
        installCommand: 'apt-get install -y curl'
      }
    );

    // Language-specific tools
    switch (language) {
      case 'javascript':
        tools.push(
          {
            name: 'node',
            version: '18.x',
            type: 'tool',
            installCommand: 'curl -fsSL https://deb.nodesource.com/setup_18.x | bash - && apt-get install -y nodejs'
          },
          {
            name: 'npm',
            version: 'latest',
            type: 'tool',
            installCommand: 'npm install -g npm@latest'
          }
        );
        break;
      case 'python':
        tools.push(
          {
            name: 'python',
            version: '3.11',
            type: 'tool',
            installCommand: 'apt-get install -y python3.11 python3.11-venv'
          },
          {
            name: 'pip',
            version: 'latest',
            type: 'tool',
            installCommand: 'python3 -m pip install --upgrade pip'
          }
        );
        break;
      case 'java':
        tools.push(
          {
            name: 'jdk',
            version: '17',
            type: 'tool',
            installCommand: 'apt-get install -y openjdk-17-jdk'
          }
        );
        break;
    }

    // Framework-specific tools
    if (framework) {
      switch (framework) {
        case 'react':
          tools.push({
            name: 'create-react-app',
            version: 'latest',
            type: 'tool',
            installCommand: 'npm install -g create-react-app'
          });
          break;
        case 'next':
          tools.push({
            name: 'next',
            version: 'latest',
            type: 'tool',
            installCommand: 'npm install -g next'
          });
          break;
        case 'django':
          tools.push({
            name: 'django-admin',
            version: 'latest',
            type: 'tool',
            installCommand: 'pip install django'
          });
          break;
      }
    }

    return tools;
  }

  private getEnvironmentVariables(projectConfig: ProjectConfig): Record<string, string> {
    const env: Record<string, string> = {
      ...projectConfig.environment,
      NODE_ENV: 'development',
      PYTHONUNBUFFERED: '1',
      JAVA_HOME: '/usr/lib/jvm/java-17-openjdk-amd64'
    };

    // Add language-specific environment variables
    switch (projectConfig.language) {
      case 'javascript':
        env.PATH = '/usr/local/bin:${PATH}';
        break;
      case 'python':
        env.PYTHONPATH = '/app:${PYTHONPATH}';
        break;
      case 'java':
        env.JAVA_OPTS = '-Xmx4g -Xms2g';
        break;
    }

    return env;
  }

  private getBuildTools(projectConfig: ProjectConfig): { name: string; version: string; config: Record<string, any> }[] {
    const tools = [];
    const { language, buildTool } = projectConfig;

    switch (language) {
      case 'javascript':
        if (buildTool === 'webpack') {
          tools.push({
            name: 'webpack',
            version: '5.x',
            config: {
              mode: 'development',
              devtool: 'source-map',
              output: {
                path: '/app/dist',
                filename: '[name].bundle.js'
              }
            }
          });
        } else if (buildTool === 'vite') {
          tools.push({
            name: 'vite',
            version: 'latest',
            config: {
              server: {
                host: '0.0.0.0',
                port: 3000
              }
            }
          });
        }
        break;
      case 'java':
        if (buildTool === 'maven') {
          tools.push({
            name: 'maven',
            version: '3.8.x',
            config: {
              settings: {
                localRepository: '/root/.m2/repository'
              }
            }
          });
        }
        break;
      case 'python':
        tools.push({
          name: 'setuptools',
          version: 'latest',
          config: {
            installDir: '/app/venv/lib/python3.11/site-packages'
          }
        });
        break;
    }

    return tools;
  }

  private getTestTools(projectConfig: ProjectConfig): { name: string; version: string; config: Record<string, any> }[] {
    const tools = [];
    const { language, framework } = projectConfig;

    switch (language) {
      case 'javascript':
        tools.push({
          name: 'jest',
          version: 'latest',
          config: {
            testEnvironment: 'node',
            coverageDirectory: '/app/coverage'
          }
        });
        break;
      case 'python':
        tools.push({
          name: 'pytest',
          version: 'latest',
          config: {
            testpaths: ['tests'],
            python_files: 'test_*.py'
          }
        });
        break;
      case 'java':
        if (framework === 'spring') {
          tools.push({
            name: 'junit',
            version: '5.x',
            config: {
              testClasses: 'src/test/java',
              resources: 'src/test/resources'
            }
          });
        }
        break;
    }

    return tools;
  }

  async installDevTools(config: DevEnvironmentConfig): Promise<void> {
    try {
      // Install system tools
      for (const tool of config.tools) {
        if (tool.type === 'tool') {
          this.logger.info(`Installing ${tool.name}...`);
          // Execute install command
          // Note: In a real implementation, this would use a proper command execution system
          console.log(`Executing: ${tool.installCommand}`);
        }
      }

      // Configure environment variables
      const envContent = Object.entries(config.environmentVariables)
        .map(([key, value]) => `${key}=${value}`)
        .join('\n');
      await fs.promises.writeFile(path.join(this.projectRoot, '.env'), envContent);

      // Configure build tools
      for (const tool of config.buildTools) {
        const configPath = path.join(this.projectRoot, `${tool.name}.config.json`);
        await fs.promises.writeFile(configPath, JSON.stringify(tool.config, null, 2));
      }

      // Configure test tools
      for (const tool of config.testTools) {
        const configPath = path.join(this.projectRoot, `${tool.name}.config.json`);
        await fs.promises.writeFile(configPath, JSON.stringify(tool.config, null, 2));
      }

      this.logger.info('Development environment setup completed successfully');
    } catch (error) {
      this.logger.error('Failed to install development tools', error);
      throw error;
    }
  }
} 