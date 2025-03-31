import { Observable, Subject } from 'rxjs';

export interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
  category: 'editor' | 'refactoring' | 'debugging' | 'security' | 'general';
}

export interface PerformanceReport {
  metrics: PerformanceMetric[];
  summary: {
    average: number;
    min: number;
    max: number;
    p95: number;
    p99: number;
  };
}

export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: PerformanceMetric[] = [];
  private metricsSubject = new Subject<PerformanceMetric>();
  private readonly MAX_METRICS = 1000;

  private constructor() {
    // Set up automatic cleanup of old metrics
    setInterval(() => this.cleanupOldMetrics(), 3600000); // Cleanup every hour
  }

  public static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  public recordMetric(metric: Omit<PerformanceMetric, 'timestamp'>): void {
    const fullMetric: PerformanceMetric = {
      ...metric,
      timestamp: Date.now()
    };

    this.metrics.push(fullMetric);
    this.metricsSubject.next(fullMetric);

    // Keep only the most recent metrics
    if (this.metrics.length > this.MAX_METRICS) {
      this.metrics = this.metrics.slice(-this.MAX_METRICS);
    }
  }

  public getMetrics(): PerformanceMetric[] {
    return [...this.metrics];
  }

  public getMetricsByCategory(category: PerformanceMetric['category']): PerformanceMetric[] {
    return this.metrics.filter(m => m.category === category);
  }

  public getMetricsObservable(): Observable<PerformanceMetric> {
    return this.metricsSubject.asObservable();
  }

  public generateReport(category?: PerformanceMetric['category']): PerformanceReport {
    const relevantMetrics = category
      ? this.metrics.filter(m => m.category === category)
      : this.metrics;

    const values = relevantMetrics.map(m => m.value);
    const sortedValues = [...values].sort((a, b) => a - b);

    return {
      metrics: relevantMetrics,
      summary: {
        average: values.reduce((a, b) => a + b, 0) / values.length,
        min: Math.min(...values),
        max: Math.max(...values),
        p95: this.calculatePercentile(sortedValues, 95),
        p99: this.calculatePercentile(sortedValues, 99)
      }
    };
  }

  private calculatePercentile(sortedValues: number[], percentile: number): number {
    const index = Math.ceil((percentile / 100) * sortedValues.length) - 1;
    return sortedValues[index];
  }

  private cleanupOldMetrics(): void {
    const oneHourAgo = Date.now() - 3600000;
    this.metrics = this.metrics.filter(m => m.timestamp > oneHourAgo);
  }

  // Convenience methods for common metrics
  public recordEditorOperation(name: string, duration: number): void {
    this.recordMetric({
      name,
      value: duration,
      category: 'editor'
    });
  }

  public recordRefactoringOperation(name: string, duration: number): void {
    this.recordMetric({
      name,
      value: duration,
      category: 'refactoring'
    });
  }

  public recordDebuggingOperation(name: string, duration: number): void {
    this.recordMetric({
      name,
      value: duration,
      category: 'debugging'
    });
  }

  public recordSecurityOperation(name: string, duration: number): void {
    this.recordMetric({
      name,
      value: duration,
      category: 'security'
    });
  }
} 