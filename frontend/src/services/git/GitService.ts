export interface GitCredentials {
  url: string;
  username?: string;
  password?: string;
}

export interface GitStatus {
  branch: string;
  modified: string[];
  staged: string[];
  untracked: string[];
  ahead: number;
  behind: number;
}

export class GitService {
  private static instance: GitService;
  private isConnected: boolean = false;
  private currentStatus: GitStatus | null = null;

  private constructor() {}

  public static getInstance(): GitService {
    if (!GitService.instance) {
      GitService.instance = new GitService();
    }
    return GitService.instance;
  }

  public async connect(credentials: GitCredentials): Promise<boolean> {
    try {
      const response = await fetch('/api/git/connect', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (!response.ok) {
        throw new Error('Failed to connect to repository');
      }

      this.isConnected = true;
      await this.getStatus();
      return true;
    } catch (error) {
      this.isConnected = false;
      throw error;
    }
  }

  public async getStatus(): Promise<GitStatus> {
    if (!this.isConnected) {
      throw new Error('Not connected to a repository');
    }

    try {
      const response = await fetch('/api/git/status');
      if (!response.ok) {
        throw new Error('Failed to get Git status');
      }

      const status = await response.json() as GitStatus;
      this.currentStatus = status;
      return status;
    } catch (error) {
      throw error;
    }
  }

  public async stage(file: string): Promise<boolean> {
    if (!this.isConnected) {
      throw new Error('Not connected to a repository');
    }

    try {
      const response = await fetch('/api/git/stage', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file }),
      });

      if (!response.ok) {
        throw new Error('Failed to stage file');
      }

      await this.getStatus();
      return true;
    } catch (error) {
      throw error;
    }
  }

  public async unstage(file: string): Promise<boolean> {
    if (!this.isConnected) {
      throw new Error('Not connected to a repository');
    }

    try {
      const response = await fetch('/api/git/unstage', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ file }),
      });

      if (!response.ok) {
        throw new Error('Failed to unstage file');
      }

      await this.getStatus();
      return true;
    } catch (error) {
      throw error;
    }
  }

  public async commit(message: string): Promise<boolean> {
    if (!this.isConnected) {
      throw new Error('Not connected to a repository');
    }

    try {
      const response = await fetch('/api/git/commit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message }),
      });

      if (!response.ok) {
        throw new Error('Failed to commit changes');
      }

      await this.getStatus();
      return true;
    } catch (error) {
      throw error;
    }
  }

  public async pull(): Promise<boolean> {
    if (!this.isConnected) {
      throw new Error('Not connected to a repository');
    }

    try {
      const response = await fetch('/api/git/pull', { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to pull changes');
      }

      await this.getStatus();
      return true;
    } catch (error) {
      throw error;
    }
  }

  public async push(): Promise<boolean> {
    if (!this.isConnected) {
      throw new Error('Not connected to a repository');
    }

    try {
      const response = await fetch('/api/git/push', { method: 'POST' });
      if (!response.ok) {
        throw new Error('Failed to push changes');
      }

      await this.getStatus();
      return true;
    } catch (error) {
      throw error;
    }
  }

  public isRepositoryConnected(): boolean {
    return this.isConnected;
  }

  public getCurrentStatus(): GitStatus | null {
    return this.currentStatus;
  }
} 