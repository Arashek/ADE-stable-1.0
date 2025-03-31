import { APIError } from '../types/error';
import { performanceMonitor } from './performance';
import { cacheService } from './cache.service';

interface AnalyticsEvent {
    id: string;
    type: string;
    timestamp: string;
    userId: string;
    projectId?: string;
    teamId?: string;
    properties: Record<string, any>;
}

interface AnalyticsMetric {
    name: string;
    value: number;
    unit?: string;
    timestamp: string;
    tags?: Record<string, string>;
}

interface AnalyticsReport {
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

interface AnalyticsDashboard {
    id: string;
    name: string;
    description: string;
    layout: Array<{
        id: string;
        type: 'chart' | 'metric' | 'table';
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

interface AnalyticsExport {
    id: string;
    type: 'csv' | 'json' | 'excel';
    status: 'pending' | 'processing' | 'completed' | 'failed';
    filters: Record<string, any>;
    metrics: string[];
    startDate: string;
    endDate: string;
    createdAt: string;
    completedAt?: string;
    url?: string;
    error?: string;
}

interface TimeSeriesData {
    timestamp: number;
    value: number;
}

interface AnalyticsConfig {
    batchSize?: number;
    flushInterval?: number;
    samplingRate?: number;
}

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export class AnalyticsService {
    private static instance: AnalyticsService;
    private token: string;
    private events: AnalyticsEvent[] = [];
    private metrics: AnalyticsMetric[] = [];
    private readonly config: Required<AnalyticsConfig>;
    private flushTimeout: NodeJS.Timeout | null = null;
    private sessionId: string;

    private constructor() {
        this.token = localStorage.getItem('auth_token') || '';
        this.config = {
            batchSize: 50,
            flushInterval: 30000,
            samplingRate: 1.0,
        };
        this.sessionId = this.generateSessionId();
        this.startAutoFlush();
    }

    public static getInstance(): AnalyticsService {
        if (!AnalyticsService.instance) {
            AnalyticsService.instance = new AnalyticsService();
        }
        return AnalyticsService.instance;
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

    // Event Tracking
    public async trackEvent(event: Omit<AnalyticsEvent, 'id' | 'timestamp'>): Promise<AnalyticsEvent> {
        const response = await this.fetchWithAuth('/api/analytics/events', {
            method: 'POST',
            body: JSON.stringify(event),
        });
        return response.json();
    }

    public async getEvents(options: {
        type?: string;
        userId?: string;
        projectId?: string;
        teamId?: string;
        startDate?: string;
        endDate?: string;
        limit?: number;
        offset?: number;
    } = {}): Promise<AnalyticsEvent[]> {
        const queryParams = new URLSearchParams();
        if (options.type) queryParams.append('type', options.type);
        if (options.userId) queryParams.append('userId', options.userId);
        if (options.projectId) queryParams.append('projectId', options.projectId);
        if (options.teamId) queryParams.append('teamId', options.teamId);
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);
        if (options.limit) queryParams.append('limit', options.limit.toString());
        if (options.offset) queryParams.append('offset', options.offset.toString());

        const response = await this.fetchWithAuth(`/api/analytics/events?${queryParams}`);
        return response.json();
    }

    // Metrics
    public async recordMetric(metric: Omit<AnalyticsMetric, 'timestamp'>): Promise<AnalyticsMetric> {
        const response = await this.fetchWithAuth('/api/analytics/metrics', {
            method: 'POST',
            body: JSON.stringify(metric),
        });
        return response.json();
    }

    public async getMetrics(options: {
        name?: string;
        startDate?: string;
        endDate?: string;
        tags?: Record<string, string>;
    } = {}): Promise<AnalyticsMetric[]> {
        const queryParams = new URLSearchParams();
        if (options.name) queryParams.append('name', options.name);
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);
        if (options.tags) queryParams.append('tags', JSON.stringify(options.tags));

        const response = await this.fetchWithAuth(`/api/analytics/metrics?${queryParams}`);
        return response.json();
    }

    // Reports
    public async createReport(report: Omit<AnalyticsReport, 'id' | 'lastGenerated'>): Promise<AnalyticsReport> {
        const response = await this.fetchWithAuth('/api/analytics/reports', {
            method: 'POST',
            body: JSON.stringify(report),
        });
        return response.json();
    }

    public async getReports(): Promise<AnalyticsReport[]> {
        const response = await this.fetchWithAuth('/api/analytics/reports');
        return response.json();
    }

    public async updateReport(reportId: string, updates: Partial<AnalyticsReport>): Promise<AnalyticsReport> {
        const response = await this.fetchWithAuth(`/api/analytics/reports/${reportId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
        return response.json();
    }

    public async deleteReport(reportId: string): Promise<void> {
        await this.fetchWithAuth(`/api/analytics/reports/${reportId}`, {
            method: 'DELETE',
        });
    }

    public async generateReport(reportId: string): Promise<void> {
        await this.fetchWithAuth(`/api/analytics/reports/${reportId}/generate`, {
            method: 'POST',
        });
    }

    // Dashboards
    public async createDashboard(dashboard: Omit<AnalyticsDashboard, 'id' | 'createdAt' | 'updatedAt'>): Promise<AnalyticsDashboard> {
        const response = await this.fetchWithAuth('/api/analytics/dashboards', {
            method: 'POST',
            body: JSON.stringify(dashboard),
        });
        return response.json();
    }

    public async getDashboards(): Promise<AnalyticsDashboard[]> {
        const response = await this.fetchWithAuth('/api/analytics/dashboards');
        return response.json();
    }

    public async updateDashboard(dashboardId: string, updates: Partial<AnalyticsDashboard>): Promise<AnalyticsDashboard> {
        const response = await this.fetchWithAuth(`/api/analytics/dashboards/${dashboardId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
        return response.json();
    }

    public async deleteDashboard(dashboardId: string): Promise<void> {
        await this.fetchWithAuth(`/api/analytics/dashboards/${dashboardId}`, {
            method: 'DELETE',
        });
    }

    // Exports
    public async createExport(options: {
        type: 'csv' | 'json' | 'excel';
        metrics: string[];
        filters: Record<string, any>;
        startDate: string;
        endDate: string;
    }): Promise<AnalyticsExport> {
        const response = await this.fetchWithAuth('/api/analytics/exports', {
            method: 'POST',
            body: JSON.stringify(options),
        });
        return response.json();
    }

    public async getExports(): Promise<AnalyticsExport[]> {
        const response = await this.fetchWithAuth('/api/analytics/exports');
        return response.json();
    }

    public async getExportStatus(exportId: string): Promise<AnalyticsExport> {
        const response = await this.fetchWithAuth(`/api/analytics/exports/${exportId}`);
        return response.json();
    }

    // Analytics Queries
    public async queryAnalytics(query: {
        metrics: string[];
        dimensions?: string[];
        filters?: Record<string, any>;
        startDate: string;
        endDate: string;
        groupBy?: string[];
        orderBy?: Array<{
            metric: string;
            direction: 'asc' | 'desc';
        }>;
        limit?: number;
    }): Promise<{
        data: Array<Record<string, any>>;
        metadata: {
            totalRows: number;
            queryTime: number;
            cacheHit: boolean;
        };
    }> {
        const response = await this.fetchWithAuth('/api/analytics/query', {
            method: 'POST',
            body: JSON.stringify(query),
        });
        return response.json();
    }

    // Analytics Insights
    public async getInsights(options: {
        projectId?: string;
        teamId?: string;
        startDate?: string;
        endDate?: string;
        types?: string[];
    } = {}): Promise<Array<{
        id: string;
        type: string;
        title: string;
        description: string;
        severity: 'high' | 'medium' | 'low';
        metrics: string[];
        recommendations: string[];
        timestamp: string;
    }>> {
        const queryParams = new URLSearchParams();
        if (options.projectId) queryParams.append('projectId', options.projectId);
        if (options.teamId) queryParams.append('teamId', options.teamId);
        if (options.startDate) queryParams.append('startDate', options.startDate);
        if (options.endDate) queryParams.append('endDate', options.endDate);
        if (options.types) queryParams.append('types', options.types.join(','));

        const response = await this.fetchWithAuth(`/api/analytics/insights?${queryParams}`);
        return response.json();
    }

    // Analytics Alerts
    public async createAlert(options: {
        name: string;
        description: string;
        metric: string;
        condition: {
            operator: 'gt' | 'lt' | 'eq' | 'gte' | 'lte';
            value: number;
        };
        frequency: string;
        recipients: string[];
        enabled: boolean;
    }): Promise<{
        id: string;
        name: string;
        description: string;
        metric: string;
        condition: {
            operator: 'gt' | 'lt' | 'eq' | 'gte' | 'lte';
            value: number;
        };
        frequency: string;
        recipients: string[];
        enabled: boolean;
        createdAt: string;
        lastTriggered?: string;
    }> {
        const response = await this.fetchWithAuth('/api/analytics/alerts', {
            method: 'POST',
            body: JSON.stringify(options),
        });
        return response.json();
    }

    public async getAlerts(): Promise<Array<{
        id: string;
        name: string;
        description: string;
        metric: string;
        condition: {
            operator: string;
            value: number;
        };
        frequency: string;
        recipients: string[];
        enabled: boolean;
        createdAt: string;
        lastTriggered?: string;
    }>> {
        const response = await this.fetchWithAuth('/api/analytics/alerts');
        return response.json();
    }

    public async updateAlert(alertId: string, updates: Partial<{
        name: string;
        description: string;
        metric: string;
        condition: {
            operator: string;
            value: number;
        };
        frequency: string;
        recipients: string[];
        enabled: boolean;
    }>): Promise<void> {
        await this.fetchWithAuth(`/api/analytics/alerts/${alertId}`, {
            method: 'PATCH',
            body: JSON.stringify(updates),
        });
    }

    public async deleteAlert(alertId: string): Promise<void> {
        await this.fetchWithAuth(`/api/analytics/alerts/${alertId}`, {
            method: 'DELETE',
        });
    }

    /**
     * Track an analytics event
     */
    trackEvent(type: string, data: Record<string, any> = {}): void {
        if (Math.random() > this.config.samplingRate) return;

        const startTime = performance.now();
        try {
            const event: AnalyticsEvent = {
                type,
                timestamp: Date.now().toString(),
                data,
                userId: '',
                sessionId: this.sessionId,
            };

            this.events.push(event);
            performanceMonitor.recordMetric('analytics-event-tracked', performance.now() - startTime);

            if (this.events.length >= this.config.batchSize) {
                this.flush();
            }
        } catch (error) {
            performanceMonitor.recordMetric('analytics-error', 1);
            console.error('Error tracking event:', error);
        }
    }

    /**
     * Record a metric value
     */
    recordMetric(name: string, value: number, tags: Record<string, string> = {}): void {
        const startTime = performance.now();
        try {
            const metric: AnalyticsMetric = {
                name,
                value,
                timestamp: Date.now().toString(),
                tags,
            };

            this.metrics.push(metric);
            performanceMonitor.recordMetric('analytics-metric-recorded', performance.now() - startTime);
        } catch (error) {
            performanceMonitor.recordMetric('analytics-error', 1);
            console.error('Error recording metric:', error);
        }
    }

    /**
     * Get time series data for a metric
     */
    getTimeSeriesData(metricName: string, timeWindow: number): TimeSeriesData[] {
        const startTime = performance.now();
        try {
            const cacheKey = `timeseries-${metricName}-${timeWindow}`;
            const cached = cacheService.get<TimeSeriesData[]>(cacheKey);
            if (cached) return cached;

            const now = Date.now();
            const cutoff = now - timeWindow;

            const data = this.metrics
                .filter(m => m.name === metricName && m.timestamp >= cutoff)
                .map(m => ({
                    timestamp: m.timestamp,
                    value: m.value,
                }))
                .sort((a, b) => a.timestamp - b.timestamp);

            cacheService.set(cacheKey, data, 60000); // Cache for 1 minute
            performanceMonitor.recordMetric('analytics-timeseries-generated', performance.now() - startTime);
            return data;
        } catch (error) {
            performanceMonitor.recordMetric('analytics-error', 1);
            console.error('Error generating time series:', error);
            return [];
        }
    }

    /**
     * Get aggregated metric value
     */
    getAggregatedMetric(metricName: string, aggregation: 'sum' | 'avg' | 'max' | 'min', timeWindow: number): number {
        const startTime = performance.now();
        try {
            const cacheKey = `aggregated-${metricName}-${aggregation}-${timeWindow}`;
            const cached = cacheService.get<number>(cacheKey);
            if (cached !== null) return cached;

            const now = Date.now();
            const cutoff = now - timeWindow;
            const values = this.metrics
                .filter(m => m.name === metricName && m.timestamp >= cutoff)
                .map(m => m.value);

            let result = 0;
            switch (aggregation) {
                case 'sum':
                    result = values.reduce((a, b) => a + b, 0);
                    break;
                case 'avg':
                    result = values.length ? values.reduce((a, b) => a + b, 0) / values.length : 0;
                    break;
                case 'max':
                    result = values.length ? Math.max(...values) : 0;
                    break;
                case 'min':
                    result = values.length ? Math.min(...values) : 0;
                    break;
            }

            cacheService.set(cacheKey, result, 60000); // Cache for 1 minute
            performanceMonitor.recordMetric('analytics-aggregation-calculated', performance.now() - startTime);
            return result;
        } catch (error) {
            performanceMonitor.recordMetric('analytics-error', 1);
            console.error('Error calculating aggregation:', error);
            return 0;
        }
    }

    /**
     * Flush events to backend
     */
    private async flush(): Promise<void> {
        if (!this.events.length && !this.metrics.length) return;

        const startTime = performance.now();
        try {
            const eventsToSend = [...this.events];
            const metricsToSend = [...this.metrics];
            this.events = [];
            this.metrics = [];

            // Send to backend
            await fetch('/api/analytics/events', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ events: eventsToSend, metrics: metricsToSend }),
            });

            performanceMonitor.recordMetric('analytics-flush', performance.now() - startTime);
        } catch (error) {
            performanceMonitor.recordMetric('analytics-flush-error', 1);
            console.error('Error flushing analytics:', error);
            // Restore events and metrics on error
            this.events.push(...this.events);
            this.metrics.push(...this.metrics);
        }
    }

    /**
     * Start auto-flush interval
     */
    private startAutoFlush(): void {
        this.flushTimeout = setInterval(() => {
            this.flush();
        }, this.config.flushInterval);
    }

    /**
     * Generate a unique session ID
     */
    private generateSessionId(): string {
        return Math.random().toString(36).substring(2) + Date.now().toString(36);
    }

    /**
     * Clean up resources
     */
    destroy(): void {
        if (this.flushTimeout) {
            clearInterval(this.flushTimeout);
        }
        this.flush();
    }
}

// Create a singleton instance
export const analyticsService = new AnalyticsService(); 