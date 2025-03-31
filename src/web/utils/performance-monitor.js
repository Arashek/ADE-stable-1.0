import useFeatureFlags from './feature-flags';

// Performance metrics store
const metrics = {
  timings: {},
  memory: {},
  interactions: {},
  errors: [],
  network: {
    requests: [],
    resources: [],
    connections: []
  }
};

// Web Worker for heavy computations
const worker = new Worker(new URL('./performance-worker.js', import.meta.url));

// Performance monitoring class
class PerformanceMonitor {
  constructor() {
    this.featureFlags = useFeatureFlags();
    this.setupPerformanceObserver();
    this.setupErrorTracking();
    this.setupMemoryTracking();
    this.setupNetworkTracking();
  }

  // Setup Performance Observer for long tasks
  setupPerformanceObserver() {
    if ('PerformanceObserver' in window) {
      const observer = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.duration > 50) { // Log tasks longer than 50ms
            this.trackTiming('longTask', entry.duration, {
              name: entry.name,
              startTime: entry.startTime
            });
          }
        }
      });

      observer.observe({ entryTypes: ['longtask'] });
    }
  }

  // Setup error tracking
  setupErrorTracking() {
    window.addEventListener('error', (event) => {
      this.trackError({
        message: event.message,
        stack: event.stack,
        filename: event.filename,
        lineNumber: event.lineno,
        columnNumber: event.colno,
        timestamp: new Date().toISOString()
      });
    });

    window.addEventListener('unhandledrejection', (event) => {
      this.trackError({
        message: event.reason?.message || 'Unhandled Promise Rejection',
        stack: event.reason?.stack,
        timestamp: new Date().toISOString()
      });
    });
  }

  // Setup memory tracking
  setupMemoryTracking() {
    if ('performance' in window && 'memory' in performance) {
      setInterval(() => {
        const memory = performance.memory;
        this.trackMemory({
          usedJSHeapSize: memory.usedJSHeapSize,
          totalJSHeapSize: memory.totalJSHeapSize,
          jsHeapSizeLimit: memory.jsHeapSizeLimit,
          timestamp: new Date().toISOString()
        });
      }, 5000); // Check every 5 seconds
    }
  }

  // Setup network tracking
  setupNetworkTracking() {
    if ('PerformanceObserver' in window) {
      // Track resource loading
      const resourceObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          if (entry.initiatorType) {
            this.trackResourceLoading(entry);
          }
        }
      });
      resourceObserver.observe({ entryTypes: ['resource'] });

      // Track navigation timing
      const navigationObserver = new PerformanceObserver((list) => {
        for (const entry of list.getEntries()) {
          this.trackNavigationTiming(entry);
        }
      });
      navigationObserver.observe({ entryTypes: ['navigation'] });

      // Track connection information
      if ('connection' in navigator) {
        this.trackConnectionInfo(navigator.connection);
        navigator.connection.addEventListener('change', () => {
          this.trackConnectionInfo(navigator.connection);
        });
      }
    }
  }

  // Track timing metrics
  trackTiming(name, duration, metadata = {}) {
    if (!metrics.timings[name]) {
      metrics.timings[name] = [];
    }

    metrics.timings[name].push({
      duration,
      timestamp: new Date().toISOString(),
      ...metadata
    });

    // Send to analytics if enabled
    if (this.featureFlags.isFeatureEnabled('performanceTracking')) {
      this.featureFlags.trackPerformanceMetric(name, duration);
    }

    // Alert if performance threshold exceeded
    if (duration > 1000) { // Alert for tasks longer than 1s
      this.trackError({
        message: `Performance warning: ${name} took ${duration}ms`,
        type: 'performance',
        timestamp: new Date().toISOString()
      });
    }
  }

  // Track memory usage
  trackMemory(data) {
    metrics.memory[new Date().toISOString()] = data;

    // Alert if memory usage is high
    if (data.usedJSHeapSize > data.totalJSHeapSize * 0.8) {
      this.trackError({
        message: 'High memory usage detected',
        type: 'memory',
        data,
        timestamp: new Date().toISOString()
      });
    }
  }

  // Track user interactions
  trackInteraction(name, duration, metadata = {}) {
    if (!metrics.interactions[name]) {
      metrics.interactions[name] = [];
    }

    metrics.interactions[name].push({
      duration,
      timestamp: new Date().toISOString(),
      ...metadata
    });
  }

  // Track errors
  trackError(error) {
    metrics.errors.push(error);

    // Send to analytics if enabled
    if (this.featureFlags.isFeatureEnabled('errorTracking')) {
      this.featureFlags.trackError('error', error);
    }

    // Log to console in development
    if (process.env.NODE_ENV === 'development') {
      console.error('Performance Error:', error);
    }
  }

  // Track resource loading
  trackResourceLoading(entry) {
    const resource = {
      name: entry.name,
      type: entry.initiatorType,
      duration: entry.duration,
      size: entry.transferSize,
      startTime: entry.startTime,
      timestamp: new Date().toISOString()
    };

    metrics.network.resources.push(resource);

    // Alert on slow resource loading
    if (entry.duration > 1000) {
      this.trackError({
        message: `Slow resource loading: ${entry.name} took ${entry.duration}ms`,
        type: 'network',
        data: resource,
        timestamp: new Date().toISOString()
      });
    }
  }

  // Track navigation timing
  trackNavigationTiming(entry) {
    const navigation = {
      url: entry.name,
      loadTime: entry.loadEventEnd - entry.navigationStart,
      domContentLoaded: entry.domContentLoadedEventEnd - entry.navigationStart,
      firstPaint: entry.firstPaint,
      firstContentfulPaint: entry.firstContentfulPaint,
      timestamp: new Date().toISOString()
    };

    metrics.network.requests.push(navigation);

    // Alert on slow page loads
    if (navigation.loadTime > 3000) {
      this.trackError({
        message: `Slow page load: ${entry.name} took ${navigation.loadTime}ms`,
        type: 'navigation',
        data: navigation,
        timestamp: new Date().toISOString()
      });
    }
  }

  // Track connection information
  trackConnectionInfo(connection) {
    const info = {
      type: connection.type,
      effectiveType: connection.effectiveType,
      rtt: connection.rtt,
      downlink: connection.downlink,
      saveData: connection.saveData,
      timestamp: new Date().toISOString()
    };

    metrics.network.connections.push(info);

    // Alert on poor connection
    if (connection.effectiveType === '2g' || connection.effectiveType === 'slow-2g') {
      this.trackError({
        message: `Poor network connection detected: ${connection.effectiveType}`,
        type: 'connection',
        data: info,
        timestamp: new Date().toISOString()
      });
    }
  }

  // Get performance report
  getReport() {
    return {
      timings: this.getTimingStats(),
      memory: this.getMemoryStats(),
      interactions: this.getInteractionStats(),
      network: this.getNetworkStats(),
      errors: metrics.errors
    };
  }

  // Get timing statistics
  getTimingStats() {
    const stats = {};
    for (const [name, data] of Object.entries(metrics.timings)) {
      const durations = data.map(d => d.duration);
      stats[name] = {
        count: durations.length,
        average: durations.reduce((a, b) => a + b, 0) / durations.length,
        max: Math.max(...durations),
        min: Math.min(...durations),
        p95: this.calculatePercentile(durations, 95),
        p99: this.calculatePercentile(durations, 99)
      };
    }
    return stats;
  }

  // Get memory statistics
  getMemoryStats() {
    const data = Object.values(metrics.memory);
    if (data.length === 0) return null;

    const usedHeap = data.map(d => d.usedJSHeapSize);
    const totalHeap = data.map(d => d.totalJSHeapSize);

    return {
      averageUsed: usedHeap.reduce((a, b) => a + b, 0) / usedHeap.length,
      averageTotal: totalHeap.reduce((a, b) => a + b, 0) / totalHeap.length,
      maxUsed: Math.max(...usedHeap),
      maxTotal: Math.max(...totalHeap)
    };
  }

  // Get interaction statistics
  getInteractionStats() {
    const stats = {};
    for (const [name, data] of Object.entries(metrics.interactions)) {
      const durations = data.map(d => d.duration);
      stats[name] = {
        count: durations.length,
        average: durations.reduce((a, b) => a + b, 0) / durations.length,
        max: Math.max(...durations),
        min: Math.min(...durations)
      };
    }
    return stats;
  }

  // Get network statistics
  getNetworkStats() {
    const stats = {
      resources: this.getResourceStats(),
      navigation: this.getNavigationStats(),
      connection: this.getConnectionStats()
    };

    return stats;
  }

  // Get resource loading statistics
  getResourceStats() {
    const resources = metrics.network.resources;
    if (resources.length === 0) return null;

    const byType = {};
    resources.forEach(resource => {
      if (!byType[resource.type]) {
        byType[resource.type] = [];
      }
      byType[resource.type].push(resource);
    });

    const stats = {};
    for (const [type, items] of Object.entries(byType)) {
      const durations = items.map(r => r.duration);
      const sizes = items.map(r => r.size);
      
      stats[type] = {
        count: items.length,
        averageDuration: durations.reduce((a, b) => a + b, 0) / durations.length,
        averageSize: sizes.reduce((a, b) => a + b, 0) / sizes.length,
        totalSize: sizes.reduce((a, b) => a + b, 0),
        maxDuration: Math.max(...durations),
        minDuration: Math.min(...durations)
      };
    }

    return stats;
  }

  // Get navigation timing statistics
  getNavigationStats() {
    const navigations = metrics.network.requests;
    if (navigations.length === 0) return null;

    const loadTimes = navigations.map(n => n.loadTime);
    const domContentLoadedTimes = navigations.map(n => n.domContentLoaded);
    const firstPaints = navigations.map(n => n.firstPaint).filter(Boolean);
    const firstContentfulPaints = navigations.map(n => n.firstContentfulPaint).filter(Boolean);

    return {
      count: navigations.length,
      averageLoadTime: loadTimes.reduce((a, b) => a + b, 0) / loadTimes.length,
      averageDomContentLoaded: domContentLoadedTimes.reduce((a, b) => a + b, 0) / domContentLoadedTimes.length,
      averageFirstPaint: firstPaints.length > 0 ? firstPaints.reduce((a, b) => a + b, 0) / firstPaints.length : null,
      averageFirstContentfulPaint: firstContentfulPaints.length > 0 ? firstContentfulPaints.reduce((a, b) => a + b, 0) / firstContentfulPaints.length : null,
      maxLoadTime: Math.max(...loadTimes),
      minLoadTime: Math.min(...loadTimes)
    };
  }

  // Get connection statistics
  getConnectionStats() {
    const connections = metrics.network.connections;
    if (connections.length === 0) return null;

    const types = {};
    const effectiveTypes = {};
    const rtts = connections.map(c => c.rtt);
    const downlinks = connections.map(c => c.downlink);

    connections.forEach(connection => {
      types[connection.type] = (types[connection.type] || 0) + 1;
      effectiveTypes[connection.effectiveType] = (effectiveTypes[connection.effectiveType] || 0) + 1;
    });

    return {
      count: connections.length,
      types,
      effectiveTypes,
      averageRtt: rtts.reduce((a, b) => a + b, 0) / rtts.length,
      averageDownlink: downlinks.reduce((a, b) => a + b, 0) / downlinks.length,
      maxRtt: Math.max(...rtts),
      minRtt: Math.min(...rtts),
      maxDownlink: Math.max(...downlinks),
      minDownlink: Math.min(...downlinks)
    };
  }

  // Calculate percentile
  calculatePercentile(values, percentile) {
    const sorted = [...values].sort((a, b) => a - b);
    const index = Math.ceil((percentile / 100) * sorted.length) - 1;
    return sorted[index];
  }

  // Export performance data
  exportData() {
    const data = this.getReport();
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `performance-report-${new Date().toISOString()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }
}

// Create singleton instance
const performanceMonitor = new PerformanceMonitor();

export default performanceMonitor; 