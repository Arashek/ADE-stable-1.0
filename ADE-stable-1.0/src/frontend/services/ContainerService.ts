import { ContainerConfig, ContainerState, BackupConfig } from '../../core/models/project/ContainerLifecycleManager';
import { ResourceLimits, AutoScalingConfig } from '../../core/models/project/ResourceManager';
import { Logger } from '../../core/logging/Logger';

export interface ContainerInfo {
  id: string;
  name: string;
  status: ContainerState['status'];
  health: ContainerState['health'];
  startedAt: string;
  lastBackup?: string;
  resources: {
    cpu: number;
    memory: string;
    storage: string;
  };
}

export class ContainerService {
  private logger: Logger;
  private baseUrl: string;

  constructor() {
    this.logger = new Logger('ContainerService');
    this.baseUrl = process.env.REACT_APP_API_BASE_URL || 'http://localhost:3000/api';
  }

  async listContainers(): Promise<ContainerInfo[]> {
    try {
      const response = await fetch(`${this.baseUrl}/containers`);
      if (!response.ok) {
        throw new Error('Failed to fetch containers');
      }
      return await response.json();
    } catch (error) {
      this.logger.error('Failed to list containers', error);
      throw error;
    }
  }

  async createContainer(config: ContainerConfig): Promise<ContainerInfo> {
    try {
      const response = await fetch(`${this.baseUrl}/containers`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });
      if (!response.ok) {
        throw new Error('Failed to create container');
      }
      return await response.json();
    } catch (error) {
      this.logger.error('Failed to create container', error);
      throw error;
    }
  }

  async startContainer(id: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${id}/start`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('Failed to start container');
      }
    } catch (error) {
      this.logger.error('Failed to start container', error);
      throw error;
    }
  }

  async stopContainer(id: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${id}/stop`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('Failed to stop container');
      }
    } catch (error) {
      this.logger.error('Failed to stop container', error);
      throw error;
    }
  }

  async pauseContainer(id: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${id}/pause`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('Failed to pause container');
      }
    } catch (error) {
      this.logger.error('Failed to pause container', error);
      throw error;
    }
  }

  async resumeContainer(id: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${id}/resume`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('Failed to resume container');
      }
    } catch (error) {
      this.logger.error('Failed to resume container', error);
      throw error;
    }
  }

  async setResourceLimits(id: string, limits: ResourceLimits): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${id}/resources`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(limits),
      });
      if (!response.ok) {
        throw new Error('Failed to set resource limits');
      }
    } catch (error) {
      this.logger.error('Failed to set resource limits', error);
      throw error;
    }
  }

  async configureAutoScaling(id: string, config: AutoScalingConfig): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${id}/autoscaling`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });
      if (!response.ok) {
        throw new Error('Failed to configure auto-scaling');
      }
    } catch (error) {
      this.logger.error('Failed to configure auto-scaling', error);
      throw error;
    }
  }

  async createBackup(id: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${id}/backup`, {
        method: 'POST',
      });
      if (!response.ok) {
        throw new Error('Failed to create backup');
      }
    } catch (error) {
      this.logger.error('Failed to create backup', error);
      throw error;
    }
  }

  async restoreBackup(id: string, backupPath: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${id}/restore`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ backupPath }),
      });
      if (!response.ok) {
        throw new Error('Failed to restore backup');
      }
    } catch (error) {
      this.logger.error('Failed to restore backup', error);
      throw error;
    }
  }

  async configureBackup(id: string, config: BackupConfig): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${id}/backup/config`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(config),
      });
      if (!response.ok) {
        throw new Error('Failed to configure backup');
      }
    } catch (error) {
      this.logger.error('Failed to configure backup', error);
      throw error;
    }
  }

  async deleteContainer(id: string): Promise<void> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${id}`, {
        method: 'DELETE',
      });
      if (!response.ok) {
        throw new Error('Failed to delete container');
      }
    } catch (error) {
      this.logger.error('Failed to delete container', error);
      throw error;
    }
  }

  async getContainerStatus(containerId: string): Promise<'running' | 'stopped' | 'paused'> {
    try {
      const response = await fetch(`${this.baseUrl}/containers/${containerId}/status`);
      if (!response.ok) {
        throw new Error('Failed to get container status');
      }
      const data = await response.json();
      return data.status;
    } catch (error) {
      console.error('Error getting container status:', error);
      throw error;
    }
  }
} 