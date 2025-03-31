import { Logger } from '../logging/Logger';
import * as fs from 'fs';
import * as path from 'path';
import { exec } from 'child_process';
import { promisify } from 'util';

const execAsync = promisify(exec);

export interface VolumeConfig {
  name: string;
  mountPath: string;
  type: 'bind' | 'volume' | 'tmpfs';
  options?: {
    readonly?: boolean;
    size?: string;
    permissions?: string;
  };
}

export interface WorkspaceConfig {
  root: string;
  directories: {
    source: string;
    build: string;
    test: string;
    cache: string;
    logs: string;
    data: string;
  };
  permissions: {
    owner: string;
    group: string;
    mode: string;
  };
}

export interface SyncConfig {
  watchPaths: string[];
  ignorePatterns: string[];
  syncInterval: number;
  maxFileSize: number;
}

export class FileSystemManager {
  private logger: Logger;
  private projectRoot: string;
  private workspaceConfig: WorkspaceConfig;
  private volumeConfigs: VolumeConfig[];
  private syncConfig: SyncConfig;

  constructor(projectRoot: string) {
    this.logger = new Logger('FileSystemManager');
    this.projectRoot = projectRoot;
    this.workspaceConfig = this.getDefaultWorkspaceConfig();
    this.volumeConfigs = [];
    this.syncConfig = this.getDefaultSyncConfig();
  }

  private getDefaultWorkspaceConfig(): WorkspaceConfig {
    return {
      root: this.projectRoot,
      directories: {
        source: 'src',
        build: 'dist',
        test: 'tests',
        cache: '.cache',
        logs: 'logs',
        data: 'data'
      },
      permissions: {
        owner: 'node',
        group: 'node',
        mode: '755'
      }
    };
  }

  private getDefaultSyncConfig(): SyncConfig {
    return {
      watchPaths: ['src', 'tests', 'config'],
      ignorePatterns: [
        'node_modules',
        'dist',
        '.git',
        '*.log',
        '*.tmp'
      ],
      syncInterval: 1000,
      maxFileSize: 100 * 1024 * 1024 // 100MB
    };
  }

  async initialize(): Promise<void> {
    try {
      await this.createWorkspaceDirectories();
      await this.setupPermissions();
      await this.initializeVolumes();
      this.logger.info('File system initialized successfully');
    } catch (error) {
      this.logger.error('Failed to initialize file system', error);
      throw error;
    }
  }

  private async createWorkspaceDirectories(): Promise<void> {
    const { directories } = this.workspaceConfig;
    
    for (const [name, dirPath] of Object.entries(directories)) {
      const fullPath = path.join(this.projectRoot, dirPath);
      try {
        await fs.promises.mkdir(fullPath, { recursive: true });
        this.logger.info(`Created directory: ${dirPath}`);
      } catch (error) {
        this.logger.error(`Failed to create directory: ${dirPath}`, error);
        throw error;
      }
    }
  }

  private async setupPermissions(): Promise<void> {
    const { permissions } = this.workspaceConfig;
    const { owner, group, mode } = permissions;

    try {
      // Set ownership
      await execAsync(`chown -R ${owner}:${group} ${this.projectRoot}`);
      
      // Set directory permissions
      await execAsync(`find ${this.projectRoot} -type d -exec chmod ${mode} {} +`);
      
      // Set file permissions (readable and writable by owner, readable by group)
      await execAsync(`find ${this.projectRoot} -type f -exec chmod 644 {} +`);
      
      // Make scripts executable
      await execAsync(`find ${this.projectRoot} -type f -name "*.sh" -exec chmod +x {} +`);
      
      this.logger.info('Permissions set successfully');
    } catch (error) {
      this.logger.error('Failed to set permissions', error);
      throw error;
    }
  }

  async addVolume(config: VolumeConfig): Promise<void> {
    try {
      // Validate volume configuration
      this.validateVolumeConfig(config);

      // Create volume if it doesn't exist
      if (config.type === 'volume') {
        await this.createDockerVolume(config.name);
      }

      // Add to volume configs
      this.volumeConfigs.push(config);
      this.logger.info(`Added volume: ${config.name}`);
    } catch (error) {
      this.logger.error(`Failed to add volume: ${config.name}`, error);
      throw error;
    }
  }

  private validateVolumeConfig(config: VolumeConfig): void {
    if (!config.name || !config.mountPath) {
      throw new Error('Volume name and mount path are required');
    }

    if (!['bind', 'volume', 'tmpfs'].includes(config.type)) {
      throw new Error('Invalid volume type');
    }

    if (config.type === 'volume' && !config.name.match(/^[a-zA-Z0-9][a-zA-Z0-9_.-]+$/)) {
      throw new Error('Invalid volume name format');
    }
  }

  private async createDockerVolume(name: string): Promise<void> {
    try {
      await execAsync(`docker volume create ${name}`);
      this.logger.info(`Created Docker volume: ${name}`);
    } catch (error) {
      this.logger.error(`Failed to create Docker volume: ${name}`, error);
      throw error;
    }
  }

  async initializeVolumes(): Promise<void> {
    for (const volume of this.volumeConfigs) {
      try {
        const mountPath = path.join(this.projectRoot, volume.mountPath);
        
        // Create mount point if it doesn't exist
        await fs.promises.mkdir(mountPath, { recursive: true });

        // Set volume permissions
        const { owner, group } = this.workspaceConfig.permissions;
        await execAsync(`chown ${owner}:${group} ${mountPath}`);

        this.logger.info(`Initialized volume: ${volume.name}`);
      } catch (error) {
        this.logger.error(`Failed to initialize volume: ${volume.name}`, error);
        throw error;
      }
    }
  }

  async startFileSync(): Promise<void> {
    try {
      // In a real implementation, this would use a file system watcher
      // like chokidar or fs.watch with proper event handling
      this.logger.info('File synchronization started');
      
      // Example of setting up a file watcher
      const watcher = fs.watch(this.projectRoot, { recursive: true }, (eventType, filename) => {
        if (filename) {
          this.handleFileChange(eventType, filename);
        }
      });

      // Store watcher reference for cleanup
      this.fileWatcher = watcher;
    } catch (error) {
      this.logger.error('Failed to start file synchronization', error);
      throw error;
    }
  }

  private async handleFileChange(eventType: string, filename: string): Promise<void> {
    try {
      const filePath = path.join(this.projectRoot, filename);
      
      // Check if file should be ignored
      if (this.shouldIgnoreFile(filename)) {
        return;
      }

      // Check file size
      const stats = await fs.promises.stat(filePath);
      if (stats.size > this.syncConfig.maxFileSize) {
        this.logger.warn(`File too large to sync: ${filename}`);
        return;
      }

      // Handle different event types
      switch (eventType) {
        case 'rename':
          await this.handleFileRenameEvent(filename);
          break;
        case 'change':
          await this.handleFileModificationEvent(filename);
          break;
      }
    } catch (error) {
      this.logger.error(`Failed to handle file change: ${filename}`, error);
    }
  }

  private shouldIgnoreFile(filename: string): boolean {
    return this.syncConfig.ignorePatterns.some(pattern => {
      if (pattern.includes('*')) {
        const regex = new RegExp(pattern.replace('*', '.*'));
        return regex.test(filename);
      }
      return filename === pattern;
    });
  }

  private async handleFileRenameEvent(filename: string): Promise<void> {
    // Implement file rename handling
    this.logger.info(`File renamed: ${filename}`);
  }

  private async handleFileModificationEvent(filename: string): Promise<void> {
    // Implement file change handling
    this.logger.info(`File changed: ${filename}`);
  }

  async stopFileSync(): Promise<void> {
    if (this.fileWatcher) {
      this.fileWatcher.close();
      this.fileWatcher = null;
      this.logger.info('File synchronization stopped');
    }
  }

  async cleanup(): Promise<void> {
    try {
      await this.stopFileSync();
      
      // Clean up volumes if needed
      for (const volume of this.volumeConfigs) {
        if (volume.type === 'volume') {
          await this.removeDockerVolume(volume.name);
        }
      }

      this.logger.info('File system cleanup completed');
    } catch (error) {
      this.logger.error('Failed to cleanup file system', error);
      throw error;
    }
  }

  private async removeDockerVolume(name: string): Promise<void> {
    try {
      await execAsync(`docker volume rm ${name}`);
      this.logger.info(`Removed Docker volume: ${name}`);
    } catch (error) {
      this.logger.error(`Failed to remove Docker volume: ${name}`, error);
      throw error;
    }
  }

  private fileWatcher: fs.FSWatcher | null = null;
} 