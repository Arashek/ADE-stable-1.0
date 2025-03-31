export enum ProjectType {
  WEB = 'web',
  MOBILE = 'mobile',
  DESKTOP = 'desktop',
  MICROSERVICE = 'microservice',
  DATABASE = 'database',
  MACHINE_LEARNING = 'machine_learning',
  EMBEDDED = 'embedded',
  CLOUD = 'cloud'
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

export interface ContainerConfig {
  name: string;
  image: string;
  projectType: ProjectType;
  resources: ResourceAllocation;
  environment: EnvironmentVariable[];
  ports: PortMapping[];
  volumes: VolumeMount[];
  networks: NetworkConfig[];
  healthCheck?: HealthCheckConfig;
  command?: string[];
  workingDir?: string;
  user?: string;
}

export interface ContainerTemplate {
  id: string;
  name: string;
  projectType: ProjectType;
  baseImage: string;
  defaultResources: ResourceAllocation;
  defaultEnvironment: EnvironmentVariable[];
  defaultPorts: PortMapping[];
  defaultVolumes: VolumeMount[];
  defaultNetworks: NetworkConfig[];
  defaultHealthCheck?: HealthCheckConfig;
  defaultCommand?: string[];
  defaultWorkingDir?: string;
  defaultUser?: string;
  description: string;
  tags: string[];
}

export interface ResourceAllocation {
  cpu: {
    limit: number;
    reservation: number;
  };
  memory: {
    limit: string;
    reservation: string;
  };
  disk: {
    limit: string;
    reservation: string;
  };
}

export interface EnvironmentVariable {
  name: string;
  value: string;
  isSecret?: boolean;
}

export interface PortMapping {
  hostPort: number;
  containerPort: number;
  protocol: 'tcp' | 'udp';
}

export interface VolumeMount {
  source: string;
  target: string;
  type: 'bind' | 'volume' | 'tmpfs';
  options?: Record<string, string>;
}

export interface NetworkConfig {
  name: string;
  driver: string;
  options?: Record<string, string>;
}

export interface HealthCheckConfig {
  test: string[];
  interval: string;
  timeout: string;
  retries: number;
  startPeriod: string;
}

export interface ProjectConfig {
  id: string;
  name: string;
  type: ProjectType;
  description: string;
  requirements: ProjectRequirements;
  resources: ResourceAllocation;
  environment: EnvironmentVariable[];
  ports: PortMapping[];
  volumes: VolumeMount[];
  networks: NetworkConfig[];
}

export interface ProjectRequirements {
  language: string;
  framework?: string;
  dependencies: string[];
  buildTools: string[];
  testingFrameworks: string[];
  developmentTools: string[];
  minimumResources: ResourceAllocation;
} 