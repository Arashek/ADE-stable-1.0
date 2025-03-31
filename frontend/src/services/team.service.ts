import { APIError } from '../types/error';

interface TeamMember {
    id: string;
    userId: string;
    teamId: string;
    role: 'owner' | 'admin' | 'member' | 'viewer';
    joinedAt: string;
    lastActive: string;
    permissions: string[];
    status: 'active' | 'inactive' | 'pending';
}

interface Team {
    id: string;
    name: string;
    description: string;
    createdAt: string;
    updatedAt: string;
    ownerId: string;
    members: TeamMember[];
    settings: TeamSettings;
    projects: string[];
}

interface TeamSettings {
    defaultRole: string;
    allowMemberInvites: boolean;
    requireApproval: boolean;
    projectVisibility: 'public' | 'private' | 'team';
    notificationPreferences: {
        email: boolean;
        inApp: boolean;
        slack?: boolean;
    };
}

interface Invitation {
    id: string;
    teamId: string;
    email: string;
    role: string;
    status: 'pending' | 'accepted' | 'rejected' | 'expired';
    invitedBy: string;
    invitedAt: string;
    expiresAt: string;
}

interface Activity {
    id: string;
    teamId: string;
    userId: string;
    type: 'project_created' | 'member_joined' | 'member_left' | 'role_changed' | 'settings_updated';
    details: Record<string, any>;
    timestamp: string;
}

interface TeamStats {
    totalMembers: number;
    activeMembers: number;
    totalProjects: number;
    recentActivity: Activity[];
    memberGrowth: Array<{
        date: string;
        count: number;
    }>;
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export class TeamService {
    private static instance: TeamService;
    private token: string;

    private constructor() {
        this.token = localStorage.getItem('auth_token') || '';
    }

    public static getInstance(): TeamService {
        if (!TeamService.instance) {
            TeamService.instance = new TeamService();
        }
        return TeamService.instance;
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

    // Team Operations
    public async createTeam(name: string, description: string): Promise<Team> {
        const response = await this.fetchWithAuth('/api/teams', {
            method: 'POST',
            body: JSON.stringify({ name, description }),
        });
        return response.json();
    }

    public async getTeam(teamId: string): Promise<Team> {
        const response = await this.fetchWithAuth(`/api/teams/${teamId}`);
        return response.json();
    }

    public async updateTeam(teamId: string, updates: Partial<Team>): Promise<Team> {
        const response = await this.fetchWithAuth(`/api/teams/${teamId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
        return response.json();
    }

    public async deleteTeam(teamId: string): Promise<void> {
        await this.fetchWithAuth(`/api/teams/${teamId}`, {
            method: 'DELETE',
        });
    }

    // Member Operations
    public async getTeamMembers(teamId: string): Promise<TeamMember[]> {
        const response = await this.fetchWithAuth(`/api/teams/${teamId}/members`);
        return response.json();
    }

    public async addTeamMember(teamId: string, userId: string, role: string): Promise<TeamMember> {
        const response = await this.fetchWithAuth(`/api/teams/${teamId}/members`, {
            method: 'POST',
            body: JSON.stringify({ userId, role }),
        });
        return response.json();
    }

    public async updateMemberRole(teamId: string, userId: string, role: string): Promise<TeamMember> {
        const response = await this.fetchWithAuth(`/api/teams/${teamId}/members/${userId}`, {
            method: 'PATCH',
            body: JSON.stringify({ role }),
        });
        return response.json();
    }

    public async removeTeamMember(teamId: string, userId: string): Promise<void> {
        await this.fetchWithAuth(`/api/teams/${teamId}/members/${userId}`, {
            method: 'DELETE',
        });
    }

    // Invitation Operations
    public async sendInvitation(teamId: string, email: string, role: string): Promise<Invitation> {
        const response = await this.fetchWithAuth(`/api/teams/${teamId}/invitations`, {
            method: 'POST',
            body: JSON.stringify({ email, role }),
        });
        return response.json();
    }

    public async getInvitations(teamId: string): Promise<Invitation[]> {
        const response = await this.fetchWithAuth(`/api/teams/${teamId}/invitations`);
        return response.json();
    }

    public async cancelInvitation(teamId: string, invitationId: string): Promise<void> {
        await this.fetchWithAuth(`/api/teams/${teamId}/invitations/${invitationId}`, {
            method: 'DELETE',
        });
    }

    // Settings Operations
    public async getTeamSettings(teamId: string): Promise<TeamSettings> {
        const response = await this.fetchWithAuth(`/api/teams/${teamId}/settings`);
        return response.json();
    }

    public async updateTeamSettings(teamId: string, settings: Partial<TeamSettings>): Promise<TeamSettings> {
        const response = await this.fetchWithAuth(`/api/teams/${teamId}/settings`, {
            method: 'PATCH',
            body: JSON.stringify(settings),
        });
        return response.json();
    }

    // Activity and Stats
    public async getTeamActivity(teamId: string, options: {
        limit?: number;
        offset?: number;
        types?: string[];
    } = {}): Promise<Activity[]> {
        const queryParams = new URLSearchParams();
        if (options.limit) queryParams.append('limit', options.limit.toString());
        if (options.offset) queryParams.append('offset', options.offset.toString());
        if (options.types) queryParams.append('types', options.types.join(','));

        const response = await this.fetchWithAuth(`/api/teams/${teamId}/activity?${queryParams}`);
        return response.json();
    }

    public async getTeamStats(teamId: string): Promise<TeamStats> {
        const response = await this.fetchWithAuth(`/api/teams/${teamId}/stats`);
        return response.json();
    }

    // Project Operations
    public async addProjectToTeam(teamId: string, projectId: string): Promise<void> {
        await this.fetchWithAuth(`/api/teams/${teamId}/projects`, {
            method: 'POST',
            body: JSON.stringify({ projectId }),
        });
    }

    public async removeProjectFromTeam(teamId: string, projectId: string): Promise<void> {
        await this.fetchWithAuth(`/api/teams/${teamId}/projects/${projectId}`, {
            method: 'DELETE',
        });
    }

    // Member Preferences
    public async updateMemberPreferences(teamId: string, userId: string, preferences: {
        notifications?: {
            email?: boolean;
            inApp?: boolean;
            slack?: boolean;
        };
        theme?: string;
        language?: string;
    }): Promise<void> {
        await this.fetchWithAuth(`/api/teams/${teamId}/members/${userId}/preferences`, {
            method: 'PATCH',
            body: JSON.stringify(preferences),
        });
    }

    // Team Search
    public async searchTeams(query: string, options: {
        limit?: number;
        offset?: number;
    } = {}): Promise<Team[]> {
        const queryParams = new URLSearchParams();
        queryParams.append('q', query);
        if (options.limit) queryParams.append('limit', options.limit.toString());
        if (options.offset) queryParams.append('offset', options.offset.toString());

        const response = await this.fetchWithAuth(`/api/teams/search?${queryParams}`);
        return response.json();
    }

    // Team Analytics
    public async getTeamAnalytics(teamId: string, options: {
        startDate?: string;
        endDate?: string;
        metrics?: string[];
    } = {}): Promise<{
        memberActivity: Array<{
            userId: string;
            activityCount: number;
            lastActive: string;
        }>;
        projectStats: Array<{
            projectId: string;
            commits: number;
            issues: number;
            pullRequests: number;
        }>;
        collaborationMetrics: {
            averageResponseTime: number;
            codeReviewTime: number;
            mergeFrequency: number;
        };
    }> {
        const queryParams = new URLSearchParams();
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);
        if (options.metrics) queryParams.append('metrics', options.metrics.join(','));

        const response = await this.fetchWithAuth(`/api/teams/${teamId}/analytics?${queryParams}`);
        return response.json();
    }
} 