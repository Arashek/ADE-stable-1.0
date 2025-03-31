import { Logger } from '../logging/Logger';
import * as fs from 'fs';
import * as path from 'path';
import { execSync } from 'child_process';

export interface ProjectDependency {
  name: string;
  version: string;
  type: 'dependencies' | 'devDependencies' | 'peerDependencies';
}

export interface ProjectConfig {
  language: string;
  framework?: string;
  buildTool?: string;
  dependencies: ProjectDependency[];
  devDependencies: ProjectDependency[];
  scripts: Record<string, string>;
  ports: number[];
  environment: Record<string, string>;
}

export class ProjectAnalyzer {
  private logger: Logger;
  private projectRoot: string;

  constructor(projectRoot: string) {
    this.logger = new Logger('ProjectAnalyzer');
    this.projectRoot = projectRoot;
  }

  async analyze(): Promise<ProjectConfig> {
    try {
      const packageJson = await this.readPackageJson();
      const language = await this.detectLanguage();
      const framework = await this.detectFramework(language);
      const buildTool = await this.detectBuildTool(language);
      const ports = await this.detectPorts();
      const environment = await this.detectEnvironment();

      return {
        language,
        framework,
        buildTool,
        dependencies: this.parseDependencies(packageJson.dependencies || {}),
        devDependencies: this.parseDependencies(packageJson.devDependencies || {}),
        scripts: packageJson.scripts || {},
        ports,
        environment
      };
    } catch (error) {
      this.logger.error('Failed to analyze project', error);
      throw error;
    }
  }

  private async readPackageJson(): Promise<any> {
    const packageJsonPath = path.join(this.projectRoot, 'package.json');
    if (fs.existsSync(packageJsonPath)) {
      const content = await fs.promises.readFile(packageJsonPath, 'utf-8');
      return JSON.parse(content);
    }
    throw new Error('package.json not found');
  }

  private async detectLanguage(): Promise<string> {
    // Check for language-specific files
    const files = await fs.promises.readdir(this.projectRoot);
    
    if (files.includes('package.json')) {
      return 'javascript';
    } else if (files.includes('requirements.txt')) {
      return 'python';
    } else if (files.includes('pom.xml')) {
      return 'java';
    } else if (files.includes('Cargo.toml')) {
      return 'rust';
    } else if (files.includes('go.mod')) {
      return 'go';
    } else if (files.includes('Gemfile')) {
      return 'ruby';
    } else if (files.includes('composer.json')) {
      return 'php';
    }

    throw new Error('Could not detect project language');
  }

  private async detectFramework(language: string): Promise<string | undefined> {
    const packageJson = await this.readPackageJson();
    
    switch (language) {
      case 'javascript':
        if (packageJson.dependencies?.react) return 'react';
        if (packageJson.dependencies?.next) return 'next';
        if (packageJson.dependencies?.express) return 'express';
        if (packageJson.dependencies?.nestjs) return 'nestjs';
        break;
      case 'python':
        if (packageJson.dependencies?.django) return 'django';
        if (packageJson.dependencies?.flask) return 'flask';
        if (packageJson.dependencies?.fastapi) return 'fastapi';
        break;
      case 'java':
        if (packageJson.dependencies?.spring) return 'spring';
        if (packageJson.dependencies?.quarkus) return 'quarkus';
        break;
      case 'rust':
        if (packageJson.dependencies?.actix) return 'actix';
        if (packageJson.dependencies?.rocket) return 'rocket';
        break;
      case 'go':
        if (packageJson.dependencies?.gin) return 'gin';
        if (packageJson.dependencies?.echo) return 'echo';
        break;
      case 'ruby':
        if (packageJson.dependencies?.rails) return 'rails';
        if (packageJson.dependencies?.sinatra) return 'sinatra';
        break;
      case 'php':
        if (packageJson.dependencies?.laravel) return 'laravel';
        if (packageJson.dependencies?.symfony) return 'symfony';
        break;
    }

    return undefined;
  }

  private async detectBuildTool(language: string): Promise<string | undefined> {
    const files = await fs.promises.readdir(this.projectRoot);
    
    switch (language) {
      case 'javascript':
        if (files.includes('webpack.config.js')) return 'webpack';
        if (files.includes('vite.config.js')) return 'vite';
        if (files.includes('rollup.config.js')) return 'rollup';
        break;
      case 'java':
        if (files.includes('pom.xml')) return 'maven';
        if (files.includes('build.gradle')) return 'gradle';
        break;
      case 'python':
        if (files.includes('setup.py')) return 'setuptools';
        if (files.includes('pyproject.toml')) return 'poetry';
        break;
      case 'rust':
        if (files.includes('Cargo.toml')) return 'cargo';
        break;
      case 'go':
        return 'go';
      case 'ruby':
        if (files.includes('Gemfile')) return 'bundler';
        break;
      case 'php':
        if (files.includes('composer.json')) return 'composer';
        break;
    }

    return undefined;
  }

  private async detectPorts(): Promise<number[]> {
    const ports: number[] = [];
    
    // Check for common port configurations in various files
    const files = await fs.promises.readdir(this.projectRoot);
    
    for (const file of files) {
      if (file.endsWith('.js') || file.endsWith('.ts') || file.endsWith('.py')) {
        const content = await fs.promises.readFile(path.join(this.projectRoot, file), 'utf-8');
        const portMatches = content.match(/port\s*[:=]\s*(\d+)/gi);
        if (portMatches) {
          portMatches.forEach(match => {
            const port = parseInt(match.match(/\d+/)?.[0] || '0');
            if (port > 0 && port < 65536 && !ports.includes(port)) {
              ports.push(port);
            }
          });
        }
      }
    }

    // Add default ports based on framework
    const framework = await this.detectFramework(await this.detectLanguage());
    if (framework) {
      const defaultPorts: Record<string, number> = {
        react: 3000,
        next: 3000,
        express: 3000,
        nestjs: 3000,
        django: 8000,
        flask: 5000,
        fastapi: 8000,
        spring: 8080,
        quarkus: 8080,
        actix: 8080,
        rocket: 8000,
        gin: 8080,
        echo: 8080,
        rails: 3000,
        sinatra: 4567,
        laravel: 8000,
        symfony: 8000
      };

      const defaultPort = defaultPorts[framework];
      if (defaultPort && !ports.includes(defaultPort)) {
        ports.push(defaultPort);
      }
    }

    return ports;
  }

  private async detectEnvironment(): Promise<Record<string, string>> {
    const env: Record<string, string> = {};
    
    // Check for .env files
    const files = await fs.promises.readdir(this.projectRoot);
    const envFiles = files.filter(file => file.startsWith('.env'));
    
    for (const file of envFiles) {
      const content = await fs.promises.readFile(path.join(this.projectRoot, file), 'utf-8');
      content.split('\n').forEach(line => {
        const [key, value] = line.split('=').map(s => s.trim());
        if (key && value) {
          env[key] = value;
        }
      });
    }

    return env;
  }

  private parseDependencies(deps: Record<string, string>): ProjectDependency[] {
    return Object.entries(deps).map(([name, version]) => ({
      name,
      version,
      type: 'dependencies'
    }));
  }
} 