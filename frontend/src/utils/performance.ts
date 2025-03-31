interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
  tags?: Record<string, string>;
}

interface PerformanceEvent {
  name: string;
  duration: number;
  timestamp: number;
  metadata?: Record<string, any>;
}

// Extended Performance interface for memory API
interface ExtendedPerformance extends Performance {
  memory?: {
    usedJSHeapSize: number;
    totalJSHeapSize: number;
    jsHeapSizeLimit: number;
  };
}

// Extended PerformanceNavigationTiming interface
interface ExtendedPerformanceNavigationTiming extends PerformanceEntry {
  loadEventEnd: number;
  navigationStart: number;
  domContentLoadedEventEnd: number;
}

// Extended PerformanceResourceTiming interface
interface ExtendedPerformanceResourceTiming extends PerformanceEntry {
  initiatorType: string;
}

export class PerformanceMonitor {
  private static instance: PerformanceMonitor;
  private metrics: PerformanceMetric[] = [];
  private events: PerformanceEvent[] = [];
  private readonly MAX_METRICS = 1000;
  private readonly MAX_EVENTS = 1000;

  private constructor() {
    // Start periodic metric collection
    setInterval(() => this.collectSystemMetrics(), 60000);
  }

  static getInstance(): PerformanceMonitor {
    if (!PerformanceMonitor.instance) {
      PerformanceMonitor.instance = new PerformanceMonitor();
    }
    return PerformanceMonitor.instance;
  }

  // Track custom metrics
  trackMetric(name: string, value: number, tags?: Record<string, string>): void {
    const metric: PerformanceMetric = {
      name,
      value,
      timestamp: Date.now(),
      tags,
    };

    this.metrics.push(metric);
    if (this.metrics.length > this.MAX_METRICS) {
      this.metrics.shift();
    }

    // Send to analytics service in production
    if (process.env.NODE_ENV === 'production') {
      this.sendToAnalytics(metric);
    }
  }

  // Track performance events
  trackEvent(name: string, duration: number, metadata?: Record<string, any>): void {
    const event: PerformanceEvent = {
      name,
      duration,
      timestamp: Date.now(),
      metadata,
    };

    this.events.push(event);
    if (this.events.length > this.MAX_EVENTS) {
      this.events.shift();
    }

    // Send to analytics service in production
    if (process.env.NODE_ENV === 'production') {
      this.sendToAnalytics(event);
    }
  }

  // Performance measurement function wrapper
  static measure<T extends (...args: any[]) => any>(fn: T): T {
    const monitor = PerformanceMonitor.getInstance();
    return ((...args: Parameters<T>): ReturnType<T> => {
      const start = performance.now();
      const result = fn(...args);
      const duration = performance.now() - start;

      monitor.trackEvent(fn.name, duration, {
        args: args.map(arg => typeof arg === 'object' ? JSON.stringify(arg) : arg),
      });

      return result;
    }) as T;
  }

  // Collect system metrics
  private collectSystemMetrics(): void {
    // Memory usage
    const perf = performance as ExtendedPerformance;
    if (perf.memory) {
      this.trackMetric('memory.used', perf.memory.usedJSHeapSize);
      this.trackMetric('memory.total', perf.memory.totalJSHeapSize);
      this.trackMetric('memory.limit', perf.memory.jsHeapSizeLimit);
    }

    // Navigation timing
    const navigation = performance.getEntriesByType('navigation')[0] as ExtendedPerformanceNavigationTiming;
    if (navigation) {
      this.trackMetric('navigation.loadTime', navigation.loadEventEnd - navigation.navigationStart);
      this.trackMetric('navigation.domContentLoaded', navigation.domContentLoadedEventEnd - navigation.navigationStart);
    }

    // Resource timing
    const resources = performance.getEntriesByType('resource') as ExtendedPerformanceResourceTiming[];
    resources.forEach(resource => {
      this.trackMetric(`resource.${resource.name}`, resource.duration, {
        type: resource.initiatorType,
      });
    });
  }

  // Send metrics to analytics service
  private async sendToAnalytics(data: PerformanceMetric | PerformanceEvent): Promise<void> {
    try {
      await fetch('/api/analytics', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
    } catch (error) {
      console.error('Failed to send analytics data:', error);
    }
  }

  // Get performance report
  getReport(): {
    metrics: PerformanceMetric[];
    events: PerformanceEvent[];
    summary: {
      averageEventDuration: number;
      totalEvents: number;
      totalMetrics: number;
    };
  } {
    const totalDuration = this.events.reduce((sum, event) => sum + event.duration, 0);
    const averageDuration = this.events.length > 0 ? totalDuration / this.events.length : 0;

    return {
      metrics: [...this.metrics],
      events: [...this.events],
      summary: {
        averageEventDuration: averageDuration,
        totalEvents: this.events.length,
        totalMetrics: this.metrics.length,
      },
    };
  }

  // Clear all data
  clear(): void {
    this.metrics = [];
    this.events = [];
  }
}

// Create a singleton instance
export const performanceMonitor = PerformanceMonitor.getInstance();

// Example usage:
/*
class ApiService {
  @PerformanceMonitor.measure
  async fetchUser(id: string) {
    const response = await fetch(`/api/users/${id}`);
    return response.json();
  }
}

// Track custom metrics
performanceMonitor.trackMetric('user.actions', 1, { action: 'click' });

// Track custom events
performanceMonitor.trackEvent('page.load', 1200, { page: 'dashboard' });
*/ 