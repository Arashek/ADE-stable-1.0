import { Logger } from '../logging/Logger';
import { ProjectConfig, ProjectAnalyzer } from './ProjectAnalyzer';
import * as fs from 'fs';
import * as path from 'path';

export interface ContainerResources {
  cpu: number;
  memory: string;
  storage: string;
  gpu?: {
    count: number;
    type: string;
  };
}

export interface ContainerConfig {
  baseImage: string;
  ports: number[];
  environment: Record<string, string>;
  volumes: string[];
  resources: ContainerResources;
  commands: {
    build: string[];
    start: string[];
    test: string[];
    dev: string[];
  };
  developmentTools: string[];
}

export class ContainerConfigurator {
  private logger: Logger;
  private projectRoot: string;
  private analyzer: ProjectAnalyzer;

  constructor(projectRoot: string) {
    this.logger = new Logger('ContainerConfigurator');
    this.projectRoot = projectRoot;
    this.analyzer = new ProjectAnalyzer(projectRoot);
  }

  async generateConfig(): Promise<ContainerConfig> {
    try {
      const projectConfig = await this.analyzer.analyze();
      const resources = this.calculateResources(projectConfig);
      const developmentTools = this.detectDevelopmentTools(projectConfig);

      return {
        baseImage: this.selectBaseImage(projectConfig),
        ports: projectConfig.ports,
        environment: projectConfig.environment,
        volumes: this.generateVolumes(projectConfig),
        resources,
        commands: this.generateCommands(projectConfig),
        developmentTools
      };
    } catch (error) {
      this.logger.error('Failed to generate container config', error);
      throw error;
    }
  }

  private selectBaseImage(projectConfig: ProjectConfig): string {
    const { language, framework } = projectConfig;

    // Define base images for different languages and frameworks
    const baseImages: Record<string, Record<string, string>> = {
      javascript: {
        default: 'node:18-alpine',
        react: 'node:18-alpine',
        next: 'node:18-alpine',
        express: 'node:18-alpine',
        nestjs: 'node:18-alpine'
      },
      python: {
        default: 'python:3.11-slim',
        django: 'python:3.11-slim',
        flask: 'python:3.11-slim',
        fastapi: 'python:3.11-slim'
      },
      java: {
        default: 'openjdk:17-slim',
        spring: 'openjdk:17-slim',
        quarkus: 'registry.access.redhat.com/ubi8/openjdk-17:latest'
      },
      rust: {
        default: 'rust:1.70-slim',
        actix: 'rust:1.70-slim',
        rocket: 'rust:1.70-slim'
      },
      go: {
        default: 'golang:1.21-alpine',
        gin: 'golang:1.21-alpine',
        echo: 'golang:1.21-alpine'
      },
      ruby: {
        default: 'ruby:3.2-slim',
        rails: 'ruby:3.2-slim',
        sinatra: 'ruby:3.2-slim'
      },
      php: {
        default: 'php:8.2-apache',
        laravel: 'php:8.2-apache',
        symfony: 'php:8.2-apache'
      }
    };

    return baseImages[language]?.[framework || 'default'] || baseImages[language]?.default || 'ubuntu:latest';
  }

  private calculateResources(projectConfig: ProjectConfig): ContainerResources {
    const { language, framework, dependencies } = projectConfig;
    
    // Base resource requirements
    let resources: ContainerResources = {
      cpu: 1,
      memory: '2Gi',
      storage: '10Gi'
    };

    // Adjust resources based on language and framework
    switch (language) {
      case 'java':
        resources.memory = '4Gi';
        break;
      case 'python':
        if (framework === 'django') {
          resources.memory = '3Gi';
        }
        break;
      case 'javascript':
        if (framework === 'next') {
          resources.memory = '3Gi';
        }
        break;
    }

    // Check for GPU requirements
    const hasGpuDependencies = dependencies.some(dep => 
      dep.name.includes('tensorflow') || 
      dep.name.includes('pytorch') || 
      dep.name.includes('cuda')
    );

    if (hasGpuDependencies) {
      resources.gpu = {
        count: 1,
        type: 'nvidia'
      };
    }

    return resources;
  }

  private generateVolumes(projectConfig: ProjectConfig): string[] {
    const volumes: string[] = [
      `${this.projectRoot}:/app`,
      'node_modules:/app/node_modules' // For JavaScript projects
    ];

    // Add language-specific volumes
    switch (projectConfig.language) {
      case 'python':
        volumes.push('venv:/app/venv');
        break;
      case 'java':
        volumes.push('maven:/root/.m2');
        break;
      case 'go':
        volumes.push('go-modules:/go/pkg/mod');
        break;
      case 'ruby':
        volumes.push('bundle:/usr/local/bundle');
        break;
    }

    return volumes;
  }

  private generateCommands(projectConfig: ProjectConfig): {
    build: string[];
    start: string[];
    test: string[];
    dev: string[];
  } {
    const { language, framework, buildTool } = projectConfig;

    const commands = {
      build: [] as string[],
      start: [] as string[],
      test: [] as string[],
      dev: [] as string[]
    };

    switch (language) {
      case 'javascript':
        commands.build = ['npm install'];
        commands.start = ['npm start'];
        commands.test = ['npm test'];
        commands.dev = ['npm run dev'];
        break;
      case 'python':
        commands.build = ['pip install -r requirements.txt'];
        commands.start = ['python app.py'];
        commands.test = ['pytest'];
        commands.dev = ['python -m flask run --host=0.0.0.0'];
        break;
      case 'java':
        if (buildTool === 'maven') {
          commands.build = ['mvn clean install'];
          commands.start = ['mvn spring-boot:run'];
          commands.test = ['mvn test'];
          commands.dev = ['mvn spring-boot:run'];
        } else if (buildTool === 'gradle') {
          commands.build = ['gradle build'];
          commands.start = ['gradle bootRun'];
          commands.test = ['gradle test'];
          commands.dev = ['gradle bootRun'];
        }
        break;
      case 'rust':
        commands.build = ['cargo build'];
        commands.start = ['cargo run'];
        commands.test = ['cargo test'];
        commands.dev = ['cargo watch -x run'];
        break;
      case 'go':
        commands.build = ['go build'];
        commands.start = ['./main'];
        commands.test = ['go test ./...'];
        commands.dev = ['go run main.go'];
        break;
      case 'ruby':
        commands.build = ['bundle install'];
        commands.start = ['bundle exec rails server'];
        commands.test = ['bundle exec rspec'];
        commands.dev = ['bundle exec rails server'];
        break;
      case 'php':
        commands.build = ['composer install'];
        commands.start = ['php-fpm'];
        commands.test = ['phpunit'];
        commands.dev = ['php artisan serve'];
        break;
    }

    return commands;
  }

  private detectDevelopmentTools(projectConfig: ProjectConfig): string[] {
    const tools: string[] = [];
    const { language, framework, buildTool } = projectConfig;

    // Common development tools
    tools.push('git', 'curl', 'wget');

    // Language-specific tools
    switch (language) {
      case 'javascript':
        tools.push('npm', 'yarn');
        if (framework === 'react') tools.push('vite');
        break;
      case 'python':
        tools.push('pip', 'pytest', 'black', 'flake8');
        break;
      case 'java':
        tools.push('maven', 'gradle', 'jdk');
        break;
      case 'rust':
        tools.push('cargo', 'rustc', 'rustfmt');
        break;
      case 'go':
        tools.push('go', 'gofmt');
        break;
      case 'ruby':
        tools.push('ruby', 'gem', 'bundler');
        break;
      case 'php':
        tools.push('composer', 'phpunit');
        break;
    }

    // Framework-specific tools
    if (framework) {
      switch (framework) {
        case 'react':
          tools.push('create-react-app');
          break;
        case 'next':
          tools.push('next');
          break;
        case 'django':
          tools.push('django-admin');
          break;
        case 'flask':
          tools.push('flask');
          break;
        case 'spring':
          tools.push('spring-boot-cli');
          break;
        case 'rails':
          tools.push('rails');
          break;
        case 'laravel':
          tools.push('artisan');
          break;
      }
    }

    return tools;
  }
} 