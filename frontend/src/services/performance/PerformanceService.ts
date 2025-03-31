export interface SystemMetrics {
  cpu: number;
  memory: number;
  responseTime: number;
  errorRate: number;
  timestamp: number;
}

export class PerformanceService {
  private static instance: PerformanceService;
  private metrics: SystemMetrics | null = null;
  private lastFetch: number = 0;
  private fetchPromise: Promise<SystemMetrics> | null = null;

  private constructor() {}

  public static getInstance(): PerformanceService {
    if (!PerformanceService.instance) {
      PerformanceService.instance = new PerformanceService();
    }
    return PerformanceService.instance;
  }

  public async getCurrentMetrics(): Promise<SystemMetrics> {
    // If there's an ongoing fetch, return its promise
    if (this.fetchPromise) {
      return this.fetchPromise;
    }

    // If we have recent metrics (less than 2 seconds old), return them
    if (this.metrics && Date.now() - this.lastFetch < 2000) {
      return this.metrics;
    }

    // Start a new fetch
    this.fetchPromise = this.fetchMetrics();

    try {
      const metrics = await this.fetchPromise;
      this.metrics = metrics;
      this.lastFetch = Date.now();
      return metrics;
    } finally {
      this.fetchPromise = null;
    }
  }

  private async fetchMetrics(): Promise<SystemMetrics> {
    try {
      const response = await fetch('/api/metrics/current', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to fetch metrics');
      }

      const data = await response.json();
      return {
        cpu: data.cpu,
        memory: data.memory,
        responseTime: data.responseTime,
        errorRate: data.errorRate,
        timestamp: Date.now(),
      };
    } catch (error) {
      console.error('Error fetching metrics:', error);
      throw error;
    }
  }

  public clearCache(): void {
    this.metrics = null;
    this.lastFetch = 0;
  }
} 