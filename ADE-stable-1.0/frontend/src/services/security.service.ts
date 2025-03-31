import { APIError } from '../types/error';

interface SecurityScan {
    id: string;
    projectId: string;
    type: 'vulnerability' | 'compliance' | 'dependency' | 'code';
    status: 'pending' | 'running' | 'completed' | 'failed';
    startedAt: string;
    completedAt?: string;
    findings: SecurityFinding[];
    summary: {
        total: number;
        critical: number;
        high: number;
        medium: number;
        low: number;
    };
}

interface SecurityFinding {
    id: string;
    scanId: string;
    type: string;
    severity: 'critical' | 'high' | 'medium' | 'low';
    title: string;
    description: string;
    location: {
        file: string;
        line?: number;
        column?: number;
        snippet?: string;
    };
    remediation: string;
    references: string[];
    status: 'open' | 'in_progress' | 'resolved' | 'false_positive';
    createdAt: string;
    updatedAt: string;
    resolvedAt?: string;
    assignedTo?: string;
}

interface SecurityPolicy {
    id: string;
    name: string;
    description: string;
    rules: SecurityRule[];
    scope: {
        projects: string[];
        environments: string[];
    };
    enabled: boolean;
    createdAt: string;
    updatedAt: string;
}

interface SecurityRule {
    id: string;
    name: string;
    description: string;
    type: 'vulnerability' | 'compliance' | 'dependency' | 'code';
    condition: {
        metric: string;
        operator: 'gt' | 'lt' | 'eq' | 'gte' | 'lte';
        value: number;
    };
    action: {
        type: 'alert' | 'block' | 'notify';
        recipients: string[];
    };
    enabled: boolean;
}

interface SecurityAudit {
    id: string;
    type: 'login' | 'resource_access' | 'configuration_change' | 'security_event';
    timestamp: string;
    userId: string;
    action: string;
    resource: string;
    details: Record<string, any>;
    ip: string;
    userAgent: string;
}

interface SecurityConfig {
    id: string;
    projectId: string;
    settings: {
        authentication: {
            mfa: boolean;
            sessionTimeout: number;
            maxLoginAttempts: number;
        };
        authorization: {
            defaultRole: string;
            requireApproval: boolean;
        };
        encryption: {
            algorithm: string;
            keyRotation: number;
        };
        logging: {
            enabled: boolean;
            retention: number;
            level: 'debug' | 'info' | 'warn' | 'error';
        };
    };
    updatedAt: string;
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export class SecurityService {
    private static instance: SecurityService;
    private token: string;

    private constructor() {
        this.token = localStorage.getItem('auth_token') || '';
    }

    public static getInstance(): SecurityService {
        if (!SecurityService.instance) {
            SecurityService.instance = new SecurityService();
        }
        return SecurityService.instance;
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

    // Security Scans
    public async initiateScan(projectId: string, options: {
        type: 'vulnerability' | 'compliance' | 'dependency' | 'code';
        target?: string;
        config?: Record<string, any>;
    }): Promise<SecurityScan> {
        const response = await this.fetchWithAuth(`/api/security/${projectId}/scans`, {
            method: 'POST',
            body: JSON.stringify(options),
        });
        return response.json();
    }

    public async getScans(projectId: string, options: {
        type?: 'vulnerability' | 'compliance' | 'dependency' | 'code';
        status?: 'pending' | 'running' | 'completed' | 'failed';
        startDate?: string;
        endDate?: string;
    } = {}): Promise<SecurityScan[]> {
        const queryParams = new URLSearchParams();
        if (options.type) queryParams.append('type', options.type);
        if (options.status) queryParams.append('status', options.status);
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);

        const response = await this.fetchWithAuth(`/api/security/${projectId}/scans?${queryParams}`);
        return response.json();
    }

    public async getScanDetails(projectId: string, scanId: string): Promise<SecurityScan> {
        const response = await this.fetchWithAuth(`/api/security/${projectId}/scans/${scanId}`);
        return response.json();
    }

    // Security Findings
    public async getFindings(projectId: string, options: {
        scanId?: string;
        severity?: 'critical' | 'high' | 'medium' | 'low';
        status?: 'open' | 'in_progress' | 'resolved' | 'false_positive';
        startDate?: string;
        endDate?: string;
    } = {}): Promise<SecurityFinding[]> {
        const queryParams = new URLSearchParams();
        if (options.scanId) queryParams.append('scanId', options.scanId);
        if (options.severity) queryParams.append('severity', options.severity);
        if (options.status) queryParams.append('status', options.status);
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);

        const response = await this.fetchWithAuth(`/api/security/${projectId}/findings?${queryParams}`);
        return response.json();
    }

    public async updateFinding(projectId: string, findingId: string, updates: Partial<SecurityFinding>): Promise<SecurityFinding> {
        const response = await this.fetchWithAuth(`/api/security/${projectId}/findings/${findingId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
        return response.json();
    }

    // Security Policies
    public async createPolicy(policy: Omit<SecurityPolicy, 'id' | 'createdAt' | 'updatedAt'>): Promise<SecurityPolicy> {
        const response = await this.fetchWithAuth('/api/security/policies', {
            method: 'POST',
            body: JSON.stringify(policy),
        });
        return response.json();
    }

    public async getPolicies(): Promise<SecurityPolicy[]> {
        const response = await this.fetchWithAuth('/api/security/policies');
        return response.json();
    }

    public async updatePolicy(policyId: string, updates: Partial<SecurityPolicy>): Promise<SecurityPolicy> {
        const response = await this.fetchWithAuth(`/api/security/policies/${policyId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
        return response.json();
    }

    public async deletePolicy(policyId: string): Promise<void> {
        await this.fetchWithAuth(`/api/security/policies/${policyId}`, {
            method: 'DELETE',
        });
    }

    // Security Rules
    public async createRule(policyId: string, rule: Omit<SecurityRule, 'id'>): Promise<SecurityRule> {
        const response = await this.fetchWithAuth(`/api/security/policies/${policyId}/rules`, {
            method: 'POST',
            body: JSON.stringify(rule),
        });
        return response.json();
    }

    public async updateRule(policyId: string, ruleId: string, updates: Partial<SecurityRule>): Promise<SecurityRule> {
        const response = await this.fetchWithAuth(`/api/security/policies/${policyId}/rules/${ruleId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
        return response.json();
    }

    public async deleteRule(policyId: string, ruleId: string): Promise<void> {
        await this.fetchWithAuth(`/api/security/policies/${policyId}/rules/${ruleId}`, {
            method: 'DELETE',
        });
    }

    // Security Audits
    public async getAuditLogs(options: {
        type?: 'login' | 'resource_access' | 'configuration_change' | 'security_event';
        userId?: string;
        startDate?: string;
        endDate?: string;
        limit?: number;
        offset?: number;
    } = {}): Promise<SecurityAudit[]> {
        const queryParams = new URLSearchParams();
        if (options.type) queryParams.append('type', options.type);
        if (options.userId) queryParams.append('userId', options.userId);
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);
        if (options.limit) queryParams.append('limit', options.limit.toString());
        if (options.offset) queryParams.append('offset', options.offset.toString());

        const response = await this.fetchWithAuth(`/api/security/audits?${queryParams}`);
        return response.json();
    }

    // Security Configuration
    public async getSecurityConfig(projectId: string): Promise<SecurityConfig> {
        const response = await this.fetchWithAuth(`/api/security/${projectId}/config`);
        return response.json();
    }

    public async updateSecurityConfig(projectId: string, updates: Partial<SecurityConfig['settings']>): Promise<SecurityConfig> {
        const response = await this.fetchWithAuth(`/api/security/${projectId}/config`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
        return response.json();
    }

    // Security Compliance
    public async getComplianceStatus(projectId: string): Promise<{
        status: 'compliant' | 'non_compliant' | 'partial';
        standards: Array<{
            name: string;
            status: 'compliant' | 'non_compliant' | 'partial';
            score: number;
            requirements: Array<{
                id: string;
                name: string;
                status: 'compliant' | 'non_compliant';
                evidence?: string;
            }>;
        }>;
        lastAssessment: string;
    }> {
        const response = await this.fetchWithAuth(`/api/security/${projectId}/compliance`);
        return response.json();
    }

    // Security Reports
    public async generateSecurityReport(projectId: string, options: {
        type: 'vulnerability' | 'compliance' | 'audit';
        startDate: string;
        endDate: string;
        format: 'pdf' | 'csv' | 'json';
    }): Promise<{
        id: string;
        status: 'pending' | 'processing' | 'completed' | 'failed';
        url?: string;
        error?: string;
    }> {
        const response = await this.fetchWithAuth(`/api/security/${projectId}/reports`, {
            method: 'POST',
            body: JSON.stringify(options),
        });
        return response.json();
    }

    public async getReportStatus(projectId: string, reportId: string): Promise<{
        id: string;
        status: 'pending' | 'processing' | 'completed' | 'failed';
        url?: string;
        error?: string;
    }> {
        const response = await this.fetchWithAuth(`/api/security/${projectId}/reports/${reportId}`);
        return response.json();
    }
} 