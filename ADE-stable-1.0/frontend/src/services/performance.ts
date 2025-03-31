interface PerformanceMetric {
  name: string;
  value: number;
  timestamp: number;
}

interface PerformanceEntry {
  entryType: string;
  name: string;
  startTime: number;
  duration: number;
  [key: string]: any;
}

class PerformanceMonitor {
  private metrics: PerformanceMetric[] = [];
  private observers: Set<(metrics: PerformanceMetric[]) => void> = new Set();

  constructor() {
    this.setupObservers();
  }

  private setupObservers() {
    // Observe page load metrics
    if ('PerformanceObserver' in window) {
      // Paint timing
      const paintObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          this.recordMetric(entry.name, entry.startTime);
        });
      });
      paintObserver.observe({ entryTypes: ['paint'] });

      // Long tasks
      const longTaskObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry) => {
          this.recordMetric('long-task', entry.duration);
        });
      });
      longTaskObserver.observe({ entryTypes: ['longtask'] });

      // Resource timing
      const resourceObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry: PerformanceEntry) => {
          if (entry.entryType === 'resource') {
            this.recordMetric(`resource-${entry.name}`, entry.duration);
          }
        });
      });
      resourceObserver.observe({ entryTypes: ['resource'] });

      // Navigation timing
      const navigationObserver = new PerformanceObserver((list) => {
        list.getEntries().forEach((entry: PerformanceEntry) => {
          if (entry.entryType === 'navigation') {
            this.recordNavigationMetrics(entry);
          }
        });
      });
      navigationObserver.observe({ entryTypes: ['navigation'] });
    }

    // Record memory usage if available
    if ('memory' in performance) {
      setInterval(() => {
        const memory = (performance as any).memory;
        if (memory) {
          this.recordMetric('heap-used', memory.usedJSHeapSize);
          this.recordMetric('heap-total', memory.totalJSHeapSize);
        }
      }, 5000);
    }
  }

  private recordNavigationMetrics(entry: PerformanceEntry) {
    const metrics = {
      'dns-time': entry.domainLookupEnd - entry.domainLookupStart,
      'connection-time': entry.connectEnd - entry.connectStart,
      'ttfb': entry.responseStart - entry.requestStart,
      'dom-load': entry.domContentLoadedEventEnd - entry.domContentLoadedEventStart,
      'page-load': entry.loadEventEnd - entry.loadEventStart
    };

    Object.entries(metrics).forEach(([name, value]) => {
      this.recordMetric(name, value);
    });
  }

  public recordMetric(name: string, value: number) {
    const metric: PerformanceMetric = {
      name,
      value,
      timestamp: Date.now()
    };

    this.metrics.push(metric);
    this.notifyObservers();
  }

  public getMetrics(): PerformanceMetric[] {
    return [...this.metrics];
  }

  public clearMetrics() {
    this.metrics = [];
    this.notifyObservers();
  }

  public subscribe(callback: (metrics: PerformanceMetric[]) => void) {
    this.observers.add(callback);
    return () => {
      this.observers.delete(callback);
    };
  }

  private notifyObservers() {
    this.observers.forEach(callback => {
      callback(this.getMetrics());
    });
  }

  public getAverageMetric(name: string, timeWindow: number = 60000): number {
    const now = Date.now();
    const relevantMetrics = this.metrics.filter(
      metric => metric.name === name && (now - metric.timestamp) <= timeWindow
    );

    if (relevantMetrics.length === 0) return 0;

    const sum = relevantMetrics.reduce((acc, metric) => acc + metric.value, 0);
    return sum / relevantMetrics.length;
  }

  public getMetricsByType(type: string): PerformanceMetric[] {
    return this.metrics.filter(metric => metric.name.startsWith(type));
  }
}

export const performanceMonitor = new PerformanceMonitor(); 