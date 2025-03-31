import { APIError } from '../types/error';

interface Commit {
    id: string;
    message: string;
    author: {
        name: string;
        email: string;
        date: string;
    };
    files: Array<{
        path: string;
        status: 'added' | 'modified' | 'deleted' | 'renamed';
        changes: number;
    }>;
    branch: string;
    tags: string[];
}

interface Branch {
    name: string;
    commit: string;
    isRemote: boolean;
    isTracking: boolean;
    ahead: number;
    behind: number;
    lastCommit: Commit;
}

interface Remote {
    name: string;
    url: string;
    type: 'fetch' | 'push' | 'both';
}

interface FileStatus {
    path: string;
    status: 'untracked' | 'modified' | 'deleted' | 'renamed' | 'conflicted' | 'staged';
    changes: number;
    stagedChanges: number;
    unstagedChanges: number;
}

interface MergeResult {
    success: boolean;
    conflicts?: Array<{
        file: string;
        status: 'both_modified' | 'both_added' | 'deleted_by_them' | 'deleted_by_us';
        resolution?: string;
    }>;
    message?: string;
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export class VersionControlService {
    private static instance: VersionControlService;
    private token: string;

    private constructor() {
        this.token = localStorage.getItem('auth_token') || '';
    }

    public static getInstance(): VersionControlService {
        if (!VersionControlService.instance) {
            VersionControlService.instance = new VersionControlService();
        }
        return VersionControlService.instance;
    }

    public setToken(token: string): void {
        this.token = token;
        localStorage.setItem('auth_token', token);
    }

    private async fetchWithAuth(endpoint: string, options: RequestInit = {}): Promise<Response> {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${this.token}`,
                ...options.headers,
            },
        });

        if (!response.ok) {
            const error: APIError = await response.json();
            throw new Error(error.message || 'API request failed');
        }

        return response;
    }

    // Repository Operations
    public async initializeRepository(projectId: string): Promise<void> {
        await this.fetchWithAuth(`/api/version-control/${projectId}/init`, {
            method: 'POST',
        });
    }

    public async cloneRepository(projectId: string, url: string, options: {
        branch?: string;
        depth?: number;
    } = {}): Promise<void> {
        await this.fetchWithAuth(`/api/version-control/${projectId}/clone`, {
            method: 'POST',
            body: JSON.stringify({ url, ...options }),
        });
    }

    // Branch Operations
    public async getBranches(projectId: string): Promise<Branch[]> {
        const response = await this.fetchWithAuth(`/api/version-control/${projectId}/branches`);
        return response.json();
    }

    public async createBranch(projectId: string, name: string, options: {
        from?: string;
        checkout?: boolean;
    } = {}): Promise<Branch> {
        const response = await this.fetchWithAuth(`/api/version-control/${projectId}/branches`, {
            method: 'POST',
            body: JSON.stringify({ name, ...options }),
        });
        return response.json();
    }

    public async deleteBranch(projectId: string, name: string, options: {
        force?: boolean;
        remote?: boolean;
    } = {}): Promise<void> {
        await this.fetchWithAuth(`/api/version-control/${projectId}/branches/${name}`, {
            method: 'DELETE',
            body: JSON.stringify(options),
        });
    }

    public async checkoutBranch(projectId: string, name: string): Promise<void> {
        await this.fetchWithAuth(`/api/version-control/${projectId}/checkout/${name}`, {
            method: 'POST',
        });
    }

    // Commit Operations
    public async getCommits(projectId: string, options: {
        branch?: string;
        limit?: number;
        offset?: number;
        since?: string;
        until?: string;
    } = {}): Promise<Commit[]> {
        const queryParams = new URLSearchParams();
        if (options.branch) queryParams.append('branch', options.branch);
        if (options.limit) queryParams.append('limit', options.limit.toString());
        if (options.offset) queryParams.append('offset', options.offset.toString());
        if (options.since) queryParams.append('since', options.since);
        if (options.until) queryParams.append('until', options.until);

        const response = await this.fetchWithAuth(`/api/version-control/${projectId}/commits?${queryParams}`);
        return response.json();
    }

    public async createCommit(projectId: string, message: string, options: {
        files?: string[];
        amend?: boolean;
    } = {}): Promise<Commit> {
        const response = await this.fetchWithAuth(`/api/version-control/${projectId}/commits`, {
            method: 'POST',
            body: JSON.stringify({ message, ...options }),
        });
        return response.json();
    }

    // File Operations
    public async getFileStatus(projectId: string): Promise<FileStatus[]> {
        const response = await this.fetchWithAuth(`/api/version-control/${projectId}/status`);
        return response.json();
    }

    public async stageFiles(projectId: string, files: string[]): Promise<void> {
        await this.fetchWithAuth(`/api/version-control/${projectId}/stage`, {
            method: 'POST',
            body: JSON.stringify({ files }),
        });
    }

    public async unstageFiles(projectId: string, files: string[]): Promise<void> {
        await this.fetchWithAuth(`/api/version-control/${projectId}/unstage`, {
            method: 'POST',
            body: JSON.stringify({ files }),
        });
    }

    // Remote Operations
    public async getRemotes(projectId: string): Promise<Remote[]> {
        const response = await this.fetchWithAuth(`/api/version-control/${projectId}/remotes`);
        return response.json();
    }

    public async addRemote(projectId: string, name: string, url: string): Promise<Remote> {
        const response = await this.fetchWithAuth(`/api/version-control/${projectId}/remotes`, {
            method: 'POST',
            body: JSON.stringify({ name, url }),
        });
        return response.json();
    }

    public async removeRemote(projectId: string, name: string): Promise<void> {
        await this.fetchWithAuth(`/api/version-control/${projectId}/remotes/${name}`, {
            method: 'DELETE',
        });
    }

    // Push and Pull Operations
    public async push(projectId: string, options: {
        remote?: string;
        branch?: string;
        force?: boolean;
    } = {}): Promise<void> {
        await this.fetchWithAuth(`/api/version-control/${projectId}/push`, {
            method: 'POST',
            body: JSON.stringify(options),
        });
    }

    public async pull(projectId: string, options: {
        remote?: string;
        branch?: string;
        rebase?: boolean;
    } = {}): Promise<void> {
        await this.fetchWithAuth(`/api/version-control/${projectId}/pull`, {
            method: 'POST',
            body: JSON.stringify(options),
        });
    }

    // Merge Operations
    public async merge(projectId: string, source: string, options: {
        strategy?: 'recursive' | 'resolve' | 'octopus' | 'ours' | 'subtree';
        abortOnConflict?: boolean;
    } = {}): Promise<MergeResult> {
        const response = await this.fetchWithAuth(`/api/version-control/${projectId}/merge`, {
            method: 'POST',
            body: JSON.stringify({ source, ...options }),
        });
        return response.json();
    }

    public async abortMerge(projectId: string): Promise<void> {
        await this.fetchWithAuth(`/api/version-control/${projectId}/merge/abort`, {
            method: 'POST',
        });
    }

    // Tag Operations
    public async createTag(projectId: string, name: string, options: {
        message?: string;
        commit?: string;
        annotated?: boolean;
    } = {}): Promise<void> {
        await this.fetchWithAuth(`/api/version-control/${projectId}/tags`, {
            method: 'POST',
            body: JSON.stringify({ name, ...options }),
        });
    }

    public async deleteTag(projectId: string, name: string): Promise<void> {
        await this.fetchWithAuth(`/api/version-control/${projectId}/tags/${name}`, {
            method: 'DELETE',
        });
    }

    // History and Diff
    public async getFileHistory(projectId: string, file: string, options: {
        limit?: number;
        offset?: number;
    } = {}): Promise<Commit[]> {
        const queryParams = new URLSearchParams();
        if (options.limit) queryParams.append('limit', options.limit.toString());
        if (options.offset) queryParams.append('offset', options.offset.toString());

        const response = await this.fetchWithAuth(`/api/version-control/${projectId}/history/${file}?${queryParams}`);
        return response.json();
    }

    public async getDiff(projectId: string, options: {
        file?: string;
        commit1?: string;
        commit2?: string;
        staged?: boolean;
        unstaged?: boolean;
    } = {}): Promise<string> {
        const queryParams = new URLSearchParams();
        if (options.file) queryParams.append('file', options.file);
        if (options.commit1) queryParams.append('commit1', options.commit1);
        if (options.commit2) queryParams.append('commit2', options.commit2);
        if (options.staged) queryParams.append('staged', 'true');
        if (options.unstaged) queryParams.append('unstaged', 'true');

        const response = await this.fetchWithAuth(`/api/version-control/${projectId}/diff?${queryParams}`);
        return response.text();
    }
} 