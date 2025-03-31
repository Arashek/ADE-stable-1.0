import { Project, ProjectSettings, ProjectStatistics, ProjectActivity, ProjectSearch } from '../interfaces/project';
import { APIError } from '../types/error';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export class ProjectService {
    private static instance: ProjectService;
    private token: string;

    private constructor() {
        this.token = localStorage.getItem('auth_token') || '';
    }

    public static getInstance(): ProjectService {
        if (!ProjectService.instance) {
            ProjectService.instance = new ProjectService();
        }
        return ProjectService.instance;
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

    // Project CRUD Operations
    public async createProject(project: Partial<Project>): Promise<Project> {
        const response = await this.fetchWithAuth('/api/projects', {
            method: 'POST',
            body: JSON.stringify(project),
        });
        return response.json();
    }

    public async getProject(id: string): Promise<Project> {
        const response = await this.fetchWithAuth(`/api/projects/${id}`);
        return response.json();
    }

    public async updateProject(id: string, updates: Partial<Project>): Promise<Project> {
        const response = await this.fetchWithAuth(`/api/projects/${id}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
        return response.json();
    }

    public async deleteProject(id: string): Promise<void> {
        await this.fetchWithAuth(`/api/projects/${id}`, {
            method: 'DELETE',
        });
    }

    // Project Settings
    public async getProjectSettings(id: string): Promise<ProjectSettings> {
        const response = await this.fetchWithAuth(`/api/projects/${id}/settings`);
        return response.json();
    }

    public async updateProjectSettings(id: string, settings: Partial<ProjectSettings>): Promise<ProjectSettings> {
        const response = await this.fetchWithAuth(`/api/projects/${id}/settings`, {
            method: 'PATCH',
            body: JSON.stringify(settings),
        });
        return response.json();
    }

    // Project Statistics
    public async getProjectStatistics(id: string): Promise<ProjectStatistics> {
        const response = await this.fetchWithAuth(`/api/projects/${id}/statistics`);
        return response.json();
    }

    // Project Activity
    public async getProjectActivity(id: string, options: {
        limit?: number;
        offset?: number;
        type?: string[];
        startDate?: string;
        endDate?: string;
    } = {}): Promise<ProjectActivity[]> {
        const queryParams = new URLSearchParams();
        if (options.limit) queryParams.append('limit', options.limit.toString());
        if (options.offset) queryParams.append('offset', options.offset.toString());
        if (options.type) queryParams.append('type', options.type.join(','));
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);

        const response = await this.fetchWithAuth(`/api/projects/${id}/activity?${queryParams}`);
        return response.json();
    }

    // Project Search
    public async searchProjects(query: string, filters: ProjectSearch['filters']): Promise<ProjectSearch> {
        const response = await this.fetchWithAuth('/api/projects/search', {
            method: 'POST',
            body: JSON.stringify({ query, filters }),
        });
        return response.json();
    }

    // Project Collaboration
    public async addCollaborator(projectId: string, userId: string, role: string): Promise<void> {
        await this.fetchWithAuth(`/api/projects/${projectId}/collaborators`, {
            method: 'POST',
            body: JSON.stringify({ userId, role }),
        });
    }

    public async removeCollaborator(projectId: string, userId: string): Promise<void> {
        await this.fetchWithAuth(`/api/projects/${projectId}/collaborators/${userId}`, {
            method: 'DELETE',
        });
    }

    public async updateCollaboratorRole(projectId: string, userId: string, role: string): Promise<void> {
        await this.fetchWithAuth(`/api/projects/${projectId}/collaborators/${userId}`, {
            method: 'PATCH',
            body: JSON.stringify({ role }),
        });
    }

    // Project Branches
    public async createBranch(projectId: string, name: string, sourceBranch: string): Promise<void> {
        await this.fetchWithAuth(`/api/projects/${projectId}/branches`, {
            method: 'POST',
            body: JSON.stringify({ name, sourceBranch }),
        });
    }

    public async deleteBranch(projectId: string, branchName: string): Promise<void> {
        await this.fetchWithAuth(`/api/projects/${projectId}/branches/${branchName}`, {
            method: 'DELETE',
        });
    }

    // Project Tags
    public async createTag(projectId: string, name: string, commit: string, description?: string): Promise<void> {
        await this.fetchWithAuth(`/api/projects/${projectId}/tags`, {
            method: 'POST',
            body: JSON.stringify({ name, commit, description }),
        });
    }

    public async deleteTag(projectId: string, tagName: string): Promise<void> {
        await this.fetchWithAuth(`/api/projects/${projectId}/tags/${tagName}`, {
            method: 'DELETE',
        });
    }

    // Project CI/CD
    public async triggerPipeline(projectId: string, branch: string): Promise<void> {
        await this.fetchWithAuth(`/api/projects/${projectId}/pipeline`, {
            method: 'POST',
            body: JSON.stringify({ branch }),
        });
    }

    public async getPipelineStatus(projectId: string, pipelineId: string): Promise<any> {
        const response = await this.fetchWithAuth(`/api/projects/${projectId}/pipeline/${pipelineId}`);
        return response.json();
    }
} 