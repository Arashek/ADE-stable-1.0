import { APIError } from '../types/error';

interface CodeAnalysisResult {
    complexity: number;
    maintainability: number;
    testCoverage: number;
    issues: CodeIssue[];
    metrics: CodeMetrics;
    dependencies: DependencyGraph;
}

interface CodeIssue {
    id: string;
    type: 'error' | 'warning' | 'info';
    message: string;
    file: string;
    line: number;
    column: number;
    severity: 'high' | 'medium' | 'low';
    category: string;
    fix?: string;
}

interface CodeMetrics {
    linesOfCode: number;
    commentLines: number;
    blankLines: number;
    complexity: number;
    maintainability: number;
    testCoverage: number;
    dependencies: number;
    circularDependencies: number;
}

interface DependencyGraph {
    nodes: DependencyNode[];
    edges: DependencyEdge[];
}

interface DependencyNode {
    id: string;
    name: string;
    type: 'file' | 'module' | 'package';
    metrics: Partial<CodeMetrics>;
}

interface DependencyEdge {
    source: string;
    target: string;
    type: 'import' | 'require' | 'extends' | 'implements';
    weight: number;
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export class CodeAnalysisService {
    private static instance: CodeAnalysisService;
    private token: string;

    private constructor() {
        this.token = localStorage.getItem('auth_token') || '';
    }

    public static getInstance(): CodeAnalysisService {
        if (!CodeAnalysisService.instance) {
            CodeAnalysisService.instance = new CodeAnalysisService();
        }
        return CodeAnalysisService.instance;
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

    // Code Analysis
    public async analyzeCode(projectId: string, options: {
        files?: string[];
        includeDependencies?: boolean;
        includeMetrics?: boolean;
    } = {}): Promise<CodeAnalysisResult> {
        const response = await this.fetchWithAuth(`/api/code-analysis/${projectId}`, {
            method: 'POST',
            body: JSON.stringify(options),
        });
        return response.json();
    }

    public async getAnalysisHistory(projectId: string, options: {
        limit?: number;
        offset?: number;
        startDate?: string;
        endDate?: string;
    } = {}): Promise<CodeAnalysisResult[]> {
        const queryParams = new URLSearchParams();
        if (options.limit) queryParams.append('limit', options.limit.toString());
        if (options.offset) queryParams.append('offset', options.offset.toString());
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);

        const response = await this.fetchWithAuth(`/api/code-analysis/${projectId}/history?${queryParams}`);
        return response.json();
    }

    // Code Issues
    public async getIssues(projectId: string, options: {
        type?: string[];
        severity?: string[];
        category?: string[];
        file?: string;
    } = {}): Promise<CodeIssue[]> {
        const queryParams = new URLSearchParams();
        if (options.type) queryParams.append('type', options.type.join(','));
        if (options.severity) queryParams.append('severity', options.severity.join(','));
        if (options.category) queryParams.append('category', options.category.join(','));
        if (options.file) queryParams.append('file', options.file);

        const response = await this.fetchWithAuth(`/api/code-analysis/${projectId}/issues?${queryParams}`);
        return response.json();
    }

    public async fixIssue(projectId: string, issueId: string): Promise<void> {
        await this.fetchWithAuth(`/api/code-analysis/${projectId}/issues/${issueId}/fix`, {
            method: 'POST',
        });
    }

    // Code Metrics
    public async getMetrics(projectId: string, options: {
        includeDependencies?: boolean;
        includeTestCoverage?: boolean;
    } = {}): Promise<CodeMetrics> {
        const queryParams = new URLSearchParams();
        if (options.includeDependencies) queryParams.append('includeDependencies', 'true');
        if (options.includeTestCoverage) queryParams.append('includeTestCoverage', 'true');

        const response = await this.fetchWithAuth(`/api/code-analysis/${projectId}/metrics?${queryParams}`);
        return response.json();
    }

    // Dependency Analysis
    public async getDependencyGraph(projectId: string): Promise<DependencyGraph> {
        const response = await this.fetchWithAuth(`/api/code-analysis/${projectId}/dependencies`);
        return response.json();
    }

    public async findCircularDependencies(projectId: string): Promise<DependencyEdge[]> {
        const response = await this.fetchWithAuth(`/api/code-analysis/${projectId}/dependencies/circular`);
        return response.json();
    }

    // Code Quality
    public async getQualityScore(projectId: string): Promise<number> {
        const response = await this.fetchWithAuth(`/api/code-analysis/${projectId}/quality-score`);
        return response.json();
    }

    public async getQualityTrend(projectId: string, options: {
        days?: number;
        interval?: 'day' | 'week' | 'month';
    } = {}): Promise<Array<{ date: string; score: number }>> {
        const queryParams = new URLSearchParams();
        if (options.days) queryParams.append('days', options.days.toString());
        if (options.interval) queryParams.append('interval', options.interval);

        const response = await this.fetchWithAuth(`/api/code-analysis/${projectId}/quality-trend?${queryParams}`);
        return response.json();
    }

    // Code Review
    public async generateReview(projectId: string, options: {
        files?: string[];
        focus?: string[];
        includeSuggestions?: boolean;
    } = {}): Promise<{
        summary: string;
        issues: CodeIssue[];
        suggestions: string[];
        metrics: CodeMetrics;
    }> {
        const response = await this.fetchWithAuth(`/api/code-analysis/${projectId}/review`, {
            method: 'POST',
            body: JSON.stringify(options),
        });
        return response.json();
    }

    // Code Optimization
    public async suggestOptimizations(projectId: string, options: {
        type?: 'performance' | 'memory' | 'security' | 'all';
        files?: string[];
    } = {}): Promise<Array<{
        file: string;
        line: number;
        suggestion: string;
        impact: 'high' | 'medium' | 'low';
        category: string;
    }>> {
        const response = await this.fetchWithAuth(`/api/code-analysis/${projectId}/optimizations`, {
            method: 'POST',
            body: JSON.stringify(options),
        });
        return response.json();
    }

    // Code Security
    public async scanSecurityIssues(projectId: string): Promise<Array<{
        vulnerability: string;
        severity: 'critical' | 'high' | 'medium' | 'low';
        file: string;
        line: number;
        description: string;
        fix?: string;
    }>> {
        const response = await this.fetchWithAuth(`/api/code-analysis/${projectId}/security`);
        return response.json();
    }

    // Code Documentation
    public async generateDocumentation(projectId: string, options: {
        format?: 'markdown' | 'html' | 'pdf';
        includeDiagrams?: boolean;
        includeExamples?: boolean;
    } = {}): Promise<{
        content: string;
        format: string;
        diagrams?: string[];
        examples?: string[];
    }> {
        const response = await this.fetchWithAuth(`/api/code-analysis/${projectId}/documentation`, {
            method: 'POST',
            body: JSON.stringify(options),
        });
        return response.json();
    }
} 