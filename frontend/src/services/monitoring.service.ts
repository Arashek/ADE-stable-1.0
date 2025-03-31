import { APIError } from '../types/error';
import { WebSocketService } from './websocket.service';

interface MonitoringMetric {
    id: string;
    name: string;
    value: number;
    unit: string;
    timestamp: string;
    tags: Record<string, string>;
    source: string;
}

interface MonitoringAlert {
    id: string;
    name: string;
    description: string;
    metric: string;
    condition: {
        operator: 'gt' | 'lt' | 'eq' | 'gte' | 'lte';
        value: number;
        duration: string;
    };
    severity: 'critical' | 'high' | 'medium' | 'low';
    status: 'active' | 'resolved' | 'acknowledged';
    recipients: string[];
    createdAt: string;
    lastTriggered?: string;
    lastResolved?: string;
}

interface MonitoringLog {
    id: string;
    level: 'debug' | 'info' | 'warn' | 'error' | 'fatal';
    message: string;
    timestamp: string;
    source: string;
    context: Record<string, any>;
    traceId?: string;
    userId?: string;
}

interface MonitoringDashboard {
    id: string;
    name: string;
    description: string;
    layout: Array<{
        id: string;
        type: 'chart' | 'metric' | 'table' | 'log';
        title: string;
        position: {
            x: number;
            y: number;
            width: number;
            height: number;
        };
        config: Record<string, any>;
    }>;
    filters: Record<string, any>;
    createdAt: string;
    updatedAt: string;
}

interface MonitoringReport {
    id: string;
    name: string;
    description: string;
    type: 'daily' | 'weekly' | 'monthly' | 'custom';
    metrics: string[];
    filters: Record<string, any>;
    schedule?: {
        frequency: string;
        timezone: string;
    };
    recipients: string[];
    lastGenerated?: string;
}

export interface PerformanceMetric {
    name: string;
    value: number;
    timestamp: number;
    tags?: Record<string, string>;
}

export interface ErrorEvent {
    message: string;
    stack?: string;
    timestamp: number;
    severity: 'error' | 'warning' | 'info';
    tags?: Record<string, string>;
}

export interface UserEvent {
    type: string;
    timestamp: number;
    userId: string;
    data: Record<string, any>;
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export class MonitoringService {
    private static instance: MonitoringService;
    private token: string;
    private wsService: WebSocketService;
    private performanceMetrics: PerformanceMetric[] = [];
    private errorEvents: ErrorEvent[] = [];
    private userEvents: UserEvent[] = [];
    private readonly maxMetrics = 1000;
    private readonly maxErrors = 100;
    private readonly maxUserEvents = 1000;

    private constructor() {
        this.token = localStorage.getItem('auth_token') || '';
        this.wsService = WebSocketService.getInstance();
        this.setupWebSocketListeners();
    }

    public static getInstance(): MonitoringService {
        if (!MonitoringService.instance) {
            MonitoringService.instance = new MonitoringService();
        }
        return MonitoringService.instance;
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

    // Metrics
    public async recordMetric(metric: Omit<MonitoringMetric, 'id' | 'timestamp'>): Promise<MonitoringMetric> {
        const response = await this.fetchWithAuth('/api/monitoring/metrics', {
            method: 'POST',
            body: JSON.stringify(metric),
        });
        return response.json();
    }

    public async getMetrics(options: {
        name?: string;
        source?: string;
        startDate?: string;
        endDate?: string;
        tags?: Record<string, string>;
        limit?: number;
        offset?: number;
    } = {}): Promise<MonitoringMetric[]> {
        const queryParams = new URLSearchParams();
        if (options.name) queryParams.append('name', options.name);
        if (options.source) queryParams.append('source', options.source);
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);
        if (options.tags) queryParams.append('tags', JSON.stringify(options.tags));
        if (options.limit) queryParams.append('limit', options.limit.toString());
        if (options.offset) queryParams.append('offset', options.offset.toString());

        const response = await this.fetchWithAuth(`/api/monitoring/metrics?${queryParams}`);
        return response.json();
    }

    // Alerts
    public async createAlert(alert: Omit<MonitoringAlert, 'id' | 'createdAt' | 'lastTriggered' | 'lastResolved'>): Promise<MonitoringAlert> {
        const response = await this.fetchWithAuth('/api/monitoring/alerts', {
            method: 'POST',
            body: JSON.stringify(alert),
        });
        return response.json();
    }

    public async getAlerts(options: {
        status?: 'active' | 'resolved' | 'acknowledged';
        severity?: 'critical' | 'high' | 'medium' | 'low';
        metric?: string;
        startDate?: string;
        endDate?: string;
    } = {}): Promise<MonitoringAlert[]> {
        const queryParams = new URLSearchParams();
        if (options.status) queryParams.append('status', options.status);
        if (options.severity) queryParams.append('severity', options.severity);
        if (options.metric) queryParams.append('metric', options.metric);
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);

        const response = await this.fetchWithAuth(`/api/monitoring/alerts?${queryParams}`);
        return response.json();
    }

    public async updateAlert(alertId: string, updates: Partial<MonitoringAlert>): Promise<MonitoringAlert> {
        const response = await this.fetchWithAuth(`/api/monitoring/alerts/${alertId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
        return response.json();
    }

    public async deleteAlert(alertId: string): Promise<void> {
        await this.fetchWithAuth(`/api/monitoring/alerts/${alertId}`, {
            method: 'DELETE',
        });
    }

    // Logs
    public async getLogs(options: {
        level?: 'debug' | 'info' | 'warn' | 'error' | 'fatal';
        source?: string;
        startDate?: string;
        endDate?: string;
        userId?: string;
        traceId?: string;
        limit?: number;
        offset?: number;
    } = {}): Promise<MonitoringLog[]> {
        const queryParams = new URLSearchParams();
        if (options.level) queryParams.append('level', options.level);
        if (options.source) queryParams.append('source', options.source);
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);
        if (options.userId) queryParams.append('userId', options.userId);
        if (options.traceId) queryParams.append('traceId', options.traceId);
        if (options.limit) queryParams.append('limit', options.limit.toString());
        if (options.offset) queryParams.append('offset', options.offset.toString());

        const response = await this.fetchWithAuth(`/api/monitoring/logs?${queryParams}`);
        return response.json();
    }

    public async searchLogs(query: string, options: {
        level?: 'debug' | 'info' | 'warn' | 'error' | 'fatal';
        source?: string;
        startDate?: string;
        endDate?: string;
        limit?: number;
        offset?: number;
    } = {}): Promise<MonitoringLog[]> {
        const queryParams = new URLSearchParams();
        queryParams.append('q', query);
        if (options.level) queryParams.append('level', options.level);
        if (options.source) queryParams.append('source', options.source);
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);
        if (options.limit) queryParams.append('limit', options.limit.toString());
        if (options.offset) queryParams.append('offset', options.offset.toString());

        const response = await this.fetchWithAuth(`/api/monitoring/logs/search?${queryParams}`);
        return response.json();
    }

    // Dashboards
    public async createDashboard(dashboard: Omit<MonitoringDashboard, 'id' | 'createdAt' | 'updatedAt'>): Promise<MonitoringDashboard> {
        const response = await this.fetchWithAuth('/api/monitoring/dashboards', {
            method: 'POST',
            body: JSON.stringify(dashboard),
        });
        return response.json();
    }

    public async getDashboards(): Promise<MonitoringDashboard[]> {
        const response = await this.fetchWithAuth('/api/monitoring/dashboards');
        return response.json();
    }

    public async updateDashboard(dashboardId: string, updates: Partial<MonitoringDashboard>): Promise<MonitoringDashboard> {
        const response = await this.fetchWithAuth(`/api/monitoring/dashboards/${dashboardId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
        return response.json();
    }

    public async deleteDashboard(dashboardId: string): Promise<void> {
        await this.fetchWithAuth(`/api/monitoring/dashboards/${dashboardId}`, {
            method: 'DELETE',
        });
    }

    // Reports
    public async createReport(report: Omit<MonitoringReport, 'id' | 'lastGenerated'>): Promise<MonitoringReport> {
        const response = await this.fetchWithAuth('/api/monitoring/reports', {
            method: 'POST',
            body: JSON.stringify(report),
        });
        return response.json();
    }

    public async getReports(): Promise<MonitoringReport[]> {
        const response = await this.fetchWithAuth('/api/monitoring/reports');
        return response.json();
    }

    public async updateReport(reportId: string, updates: Partial<MonitoringReport>): Promise<MonitoringReport> {
        const response = await this.fetchWithAuth(`/api/monitoring/reports/${reportId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
        return response.json();
    }

    public async deleteReport(reportId: string): Promise<void> {
        await this.fetchWithAuth(`/api/monitoring/reports/${reportId}`, {
            method: 'DELETE',
        });
    }

    public async generateReport(reportId: string): Promise<void> {
        await this.fetchWithAuth(`/api/monitoring/reports/${reportId}/generate`, {
            method: 'POST',
        });
    }

    // Health Checks
    public async getHealthStatus(): Promise<{
        status: 'healthy' | 'degraded' | 'unhealthy';
        components: Array<{
            name: string;
            status: 'healthy' | 'degraded' | 'unhealthy';
            message?: string;
            lastChecked: string;
        }>;
        uptime: number;
        responseTime: number;
    }> {
        const response = await this.fetchWithAuth('/api/monitoring/health');
        return response.json();
    }

    // Performance Metrics
    public async getPerformanceMetrics(options: {
        startDate?: string;
        endDate?: string;
        metrics?: string[];
    } = {}): Promise<{
        responseTime: Array<{
            timestamp: string;
            value: number;
        }>;
        throughput: Array<{
            timestamp: string;
            value: number;
        }>;
        errorRate: Array<{
            timestamp: string;
            value: number;
        }>;
        resourceUsage: {
            cpu: Array<{
                timestamp: string;
                value: number;
            }>;
            memory: Array<{
                timestamp: string;
                value: number;
            }>;
            disk: Array<{
                timestamp: string;
                value: number;
            }>;
        };
    }> {
        const queryParams = new URLSearchParams();
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);
        if (options.metrics) queryParams.append('metrics', options.metrics.join(','));

        const response = await this.fetchWithAuth(`/api/monitoring/performance?${queryParams}`);
        return response.json();
    }

    // Incident Management
    public async createIncident(options: {
        title: string;
        description: string;
        severity: 'critical' | 'high' | 'medium' | 'low';
        status: 'open' | 'investigating' | 'resolved' | 'closed';
        affectedServices: string[];
        assignees: string[];
    }): Promise<{
        id: string;
        title: string;
        description: string;
        severity: 'critical' | 'high' | 'medium' | 'low';
        status: 'open' | 'investigating' | 'resolved' | 'closed';
        affectedServices: string[];
        assignees: string[];
        createdAt: string;
        updatedAt: string;
        resolvedAt?: string;
        closedAt?: string;
    }> {
        const response = await this.fetchWithAuth('/api/monitoring/incidents', {
            method: 'POST',
            body: JSON.stringify(options),
        });
        return response.json();
    }

    public async getIncidents(options: {
        status?: 'open' | 'investigating' | 'resolved' | 'closed';
        severity?: 'critical' | 'high' | 'medium' | 'low';
        startDate?: string;
        endDate?: string;
    } = {}): Promise<Array<{
        id: string;
        title: string;
        description: string;
        severity: 'critical' | 'high' | 'medium' | 'low';
        status: 'open' | 'investigating' | 'resolved' | 'closed';
        affectedServices: string[];
        assignees: string[];
        createdAt: string;
        updatedAt: string;
        resolvedAt?: string;
        closedAt?: string;
    }>> {
        const queryParams = new URLSearchParams();
        if (options.status) queryParams.append('status', options.status);
        if (options.severity) queryParams.append('severity', options.severity);
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);

        const response = await this.fetchWithAuth(`/api/monitoring/incidents?${queryParams}`);
        return response.json();
    }

    public async updateIncident(incidentId: string, updates: Partial<{
        title: string;
        description: string;
        severity: 'critical' | 'high' | 'medium' | 'low';
        status: 'open' | 'investigating' | 'resolved' | 'closed';
        affectedServices: string[];
        assignees: string[];
    }>): Promise<void> {
        await this.fetchWithAuth(`/api/monitoring/incidents/${incidentId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
    }

    public async addIncidentComment(incidentId: string, comment: {
        content: string;
        userId: string;
    }): Promise<void> {
        await this.fetchWithAuth(`/api/monitoring/incidents/${incidentId}/comments`, {
            method: 'POST',
            body: JSON.stringify(comment),
        });
    }

    private setupWebSocketListeners() {
        this.wsService.subscribe('performance_metric', (metric: PerformanceMetric) => {
            this.addPerformanceMetric(metric);
        });

        this.wsService.subscribe('error_event', (error: ErrorEvent) => {
            this.addErrorEvent(error);
        });

        this.wsService.subscribe('user_event', (event: UserEvent) => {
            this.addUserEvent(event);
        });
    }

    // Performance Monitoring
    public trackPerformance(metric: Omit<PerformanceMetric, 'timestamp'>) {
        const fullMetric: PerformanceMetric = {
            ...metric,
            timestamp: Date.now(),
        };
        this.addPerformanceMetric(fullMetric);
        this.wsService.send({
            type: 'performance_metric',
            payload: fullMetric,
        });
    }

    private addPerformanceMetric(metric: PerformanceMetric) {
        this.performanceMetrics.push(metric);
        if (this.performanceMetrics.length > this.maxMetrics) {
            this.performanceMetrics.shift();
        }
    }

    // Error Tracking
    public trackError(error: Omit<ErrorEvent, 'timestamp'>) {
        const fullError: ErrorEvent = {
            ...error,
            timestamp: Date.now(),
        };
        this.addErrorEvent(fullError);
        this.wsService.send({
            type: 'error_event',
            payload: fullError,
        });
    }

    private addErrorEvent(error: ErrorEvent) {
        this.errorEvents.push(error);
        if (this.errorEvents.length > this.maxErrors) {
            this.errorEvents.shift();
        }
    }

    // User Analytics
    public trackUserEvent(event: Omit<UserEvent, 'timestamp'>) {
        const fullEvent: UserEvent = {
            ...event,
            timestamp: Date.now(),
        };
        this.addUserEvent(fullEvent);
        this.wsService.send({
            type: 'user_event',
            payload: fullEvent,
        });
    }

    private addUserEvent(event: UserEvent) {
        this.userEvents.push(event);
        if (this.userEvents.length > this.maxUserEvents) {
            this.userEvents.shift();
        }
    }

    // Performance Monitoring Methods
    public startPerformanceMonitoring() {
        // Monitor Core Web Vitals
        if ('PerformanceObserver' in window) {
            const observer = new PerformanceObserver((list) => {
                for (const entry of list.getEntries()) {
                    this.trackPerformance({
                        name: entry.name,
                        value: entry.startTime,
                        tags: {
                            type: entry.entryType,
                            duration: entry.duration.toString(),
                        },
                    });
                }
            });

            observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input', 'layout-shift'] });
        }

        // Monitor Resource Loading
        window.addEventListener('load', () => {
            const resources = performance.getEntriesByType('resource');
            resources.forEach((resource) => {
                this.trackPerformance({
                    name: 'resource_load',
                    value: resource.duration,
                    tags: {
                        name: resource.name,
                        type: resource.initiatorType,
                    },
                });
            });
        });
    }

    // Error Tracking Methods
    public setupErrorTracking() {
        window.addEventListener('error', (event) => {
            this.trackError({
                message: event.message,
                stack: event.error?.stack,
                severity: 'error',
                tags: {
                    filename: event.filename,
                    lineno: event.lineno.toString(),
                    colno: event.colno.toString(),
                },
            });
        });

        window.addEventListener('unhandledrejection', (event) => {
            this.trackError({
                message: event.reason?.message || 'Unhandled Promise Rejection',
                stack: event.reason?.stack,
                severity: 'error',
                tags: {
                    type: 'promise_rejection',
                },
            });
        });
    }

    // Analytics Methods
    public trackPageView(page: string) {
        this.trackUserEvent({
            type: 'page_view',
            userId: this.getUserId(),
            data: {
                page,
                referrer: document.referrer,
                userAgent: navigator.userAgent,
            },
        });
    }

    public trackUserAction(action: string, data: Record<string, any> = {}) {
        this.trackUserEvent({
            type: 'user_action',
            userId: this.getUserId(),
            data: {
                action,
                ...data,
            },
        });
    }

    private getUserId(): string {
        // Implement user ID retrieval logic
        return 'anonymous';
    }

    // Data Retrieval Methods
    public getPerformanceMetrics(): PerformanceMetric[] {
        return [...this.performanceMetrics];
    }

    public getErrorEvents(): ErrorEvent[] {
        return [...this.errorEvents];
    }

    public getUserEvents(): UserEvent[] {
        return [...this.userEvents];
    }

    // Cleanup
    public cleanup() {
        this.wsService.disconnect();
    }
}

export const monitoringService = MonitoringService.getInstance(); 