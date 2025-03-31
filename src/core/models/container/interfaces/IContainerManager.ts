import { ContainerConfig, ContainerTemplate, ProjectType, ResourceAllocation } from '../types';

export interface IContainerManager {
  // Container lifecycle management
  createContainer(config: ContainerConfig): Promise<string>;
  startContainer(containerId: string): Promise<void>;
  stopContainer(containerId: string): Promise<void>;
  deleteContainer(containerId: string): Promise<void>;
  pauseContainer(containerId: string): Promise<void>;
  resumeContainer(containerId: string): Promise<void>;
  
  // Container status and information
  getContainerStatus(containerId: string): Promise<ContainerStatus>;
  getContainerLogs(containerId: string): Promise<string>;
  getContainerResources(containerId: string): Promise<ResourceUsage>;
  
  // Template management
  getContainerTemplate(projectType: ProjectType): Promise<ContainerTemplate>;
  listAvailableTemplates(): Promise<ContainerTemplate[]>;
  
  // Resource management
  allocateResources(containerId: string, allocation: ResourceAllocation): Promise<void>;
  updateResourceAllocation(containerId: string, allocation: ResourceAllocation): Promise<void>;
  
  // Project initialization
  initializeProjectContainer(projectConfig: ProjectConfig): Promise<string>;
  
  // Container operations
  executeCommand(containerId: string, command: string): Promise<CommandResult>;
  copyFileToContainer(containerId: string, sourcePath: string, targetPath: string): Promise<void>;
  copyFileFromContainer(containerId: string, sourcePath: string, targetPath: string): Promise<void>;
}

export interface ContainerStatus {
  id: string;
  name: string;
  state: ContainerState;
  health: ContainerHealth;
  uptime: number;
  lastUpdated: Date;
}

export interface ResourceUsage {
  cpu: {
    usage: number;
    limit: number;
    percentage: number;
  };
  memory: {
    usage: number;
    limit: number;
    percentage: number;
  };
  disk: {
    usage: number;
    limit: number;
    percentage: number;
  };
  network: {
    bytesReceived: number;
    bytesSent: number;
  };
}

export interface CommandResult {
  exitCode: number;
  stdout: string;
  stderr: string;
}

export enum ContainerState {
  CREATED = 'created',
  RUNNING = 'running',
  PAUSED = 'paused',
  STOPPED = 'stopped',
  DELETED = 'deleted'
}

export enum ContainerHealth {
  HEALTHY = 'healthy',
  UNHEALTHY = 'unhealthy',
  STARTING = 'starting',
  UNKNOWN = 'unknown'
} 