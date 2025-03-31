import performanceMonitor from '../performance-monitor';

// Mock the feature flags
jest.mock('../feature-flags', () => ({
  __esModule: true,
  default: () => ({
    isFeatureEnabled: jest.fn().mockReturnValue(true),
    trackPerformanceMetric: jest.fn(),
    trackError: jest.fn()
  })
}));

// Mock PerformanceObserver
const mockPerformanceObserver = jest.fn().mockImplementation((callback) => ({
  observe: jest.fn(),
  disconnect: jest.fn()
}));
global.PerformanceObserver = mockPerformanceObserver;

// Mock navigator.connection
const mockConnection = {
  type: 'wifi',
  effectiveType: '4g',
  rtt: 50,
  downlink: 10,
  saveData: false,
  addEventListener: jest.fn(),
  removeEventListener: jest.fn()
};
Object.defineProperty(navigator, 'connection', {
  value: mockConnection,
  writable: true
});

describe('PerformanceMonitor', () => {
  beforeEach(() => {
    // Clear all metrics before each test
    performanceMonitor.metrics = {
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
  });

  describe('trackTiming', () => {
    it('should track timing metrics correctly', () => {
      performanceMonitor.trackTiming('testOperation', 100);
      performanceMonitor.trackTiming('testOperation', 200);

      const stats = performanceMonitor.getTimingStats();
      expect(stats.testOperation).toBeDefined();
      expect(stats.testOperation.count).toBe(2);
      expect(stats.testOperation.average).toBe(150);
      expect(stats.testOperation.max).toBe(200);
      expect(stats.testOperation.min).toBe(100);
    });

    it('should track timing metadata', () => {
      performanceMonitor.trackTiming('testOperation', 100, { source: 'test' });

      const stats = performanceMonitor.getTimingStats();
      expect(stats.testOperation.metadata).toBeDefined();
      expect(stats.testOperation.metadata[0].source).toBe('test');
    });

    it('should alert on high latency', () => {
      performanceMonitor.trackTiming('testOperation', 1500);

      const stats = performanceMonitor.getTimingStats();
      expect(stats.testOperation.alerts).toBeDefined();
      expect(stats.testOperation.alerts[0].type).toBe('highLatency');
    });
  });

  describe('trackMemory', () => {
    it('should track memory usage correctly', () => {
      performanceMonitor.trackMemory({
        usedJSHeapSize: 50 * 1024 * 1024,
        totalJSHeapSize: 100 * 1024 * 1024,
        jsHeapSizeLimit: 200 * 1024 * 1024
      });

      const stats = performanceMonitor.getMemoryStats();
      expect(stats.averageUsed).toBe(50 * 1024 * 1024);
      expect(stats.averageTotal).toBe(100 * 1024 * 1024);
      expect(stats.maxUsed).toBe(50 * 1024 * 1024);
      expect(stats.maxTotal).toBe(100 * 1024 * 1024);
    });

    it('should alert on high memory usage', () => {
      performanceMonitor.trackMemory({
        usedJSHeapSize: 90 * 1024 * 1024,
        totalJSHeapSize: 100 * 1024 * 1024,
        jsHeapSizeLimit: 200 * 1024 * 1024
      });

      const stats = performanceMonitor.getMemoryStats();
      expect(stats.alerts).toBeDefined();
      expect(stats.alerts[0].type).toBe('highMemoryUsage');
    });
  });

  describe('trackInteraction', () => {
    it('should track user interactions correctly', () => {
      performanceMonitor.trackInteraction('buttonClick', 50);
      performanceMonitor.trackInteraction('buttonClick', 100);

      const stats = performanceMonitor.getInteractionStats();
      expect(stats.buttonClick).toBeDefined();
      expect(stats.buttonClick.count).toBe(2);
      expect(stats.buttonClick.average).toBe(75);
      expect(stats.buttonClick.max).toBe(100);
      expect(stats.buttonClick.min).toBe(50);
    });

    it('should track interaction metadata', () => {
      performanceMonitor.trackInteraction('buttonClick', 50, { buttonId: 'test' });

      const stats = performanceMonitor.getInteractionStats();
      expect(stats.buttonClick.metadata).toBeDefined();
      expect(stats.buttonClick.metadata[0].buttonId).toBe('test');
    });
  });

  describe('trackError', () => {
    it('should track errors correctly', () => {
      const error = {
        message: 'Test error',
        stack: 'Test stack',
        timestamp: new Date().toISOString()
      };

      performanceMonitor.trackError(error);

      const report = performanceMonitor.getReport();
      expect(report.errors).toContainEqual(error);
    });

    it('should send errors to analytics when enabled', () => {
      const error = {
        message: 'Test error',
        type: 'test'
      };

      performanceMonitor.trackError(error);

      // Verify that trackError was called with the error
      expect(performanceMonitor.featureFlags.trackError).toHaveBeenCalledWith('error', error);
    });
  });

  describe('getReport', () => {
    it('should generate a complete report', () => {
      // Add some test data
      performanceMonitor.trackTiming('testOperation', 100);
      performanceMonitor.trackMemory({
        usedJSHeapSize: 50 * 1024 * 1024,
        totalJSHeapSize: 100 * 1024 * 1024,
        jsHeapSizeLimit: 200 * 1024 * 1024
      });
      performanceMonitor.trackInteraction('buttonClick', 50);
      performanceMonitor.trackError({ message: 'Test error' });

      const report = performanceMonitor.getReport();
      expect(report.timings).toBeDefined();
      expect(report.memory).toBeDefined();
      expect(report.interactions).toBeDefined();
      expect(report.errors).toBeDefined();
    });
  });

  describe('exportData', () => {
    it('should create a downloadable JSON file', () => {
      // Mock the Blob and URL.createObjectURL
      global.Blob = jest.fn();
      global.URL.createObjectURL = jest.fn().mockReturnValue('test-url');
      global.URL.revokeObjectURL = jest.fn();

      // Mock document.createElement
      const mockAnchor = {
        href: '',
        download: '',
        click: jest.fn()
      };
      document.createElement = jest.fn().mockReturnValue(mockAnchor);

      performanceMonitor.exportData();

      expect(global.Blob).toHaveBeenCalled();
      expect(global.URL.createObjectURL).toHaveBeenCalled();
      expect(mockAnchor.click).toHaveBeenCalled();
      expect(global.URL.revokeObjectURL).toHaveBeenCalledWith('test-url');
    });
  });

  describe('Network Performance Monitoring', () => {
    describe('Resource Loading', () => {
      it('should track resource loading metrics', () => {
        const mockEntry = {
          name: 'test.js',
          initiatorType: 'script',
          duration: 100,
          transferSize: 1024,
          startTime: 0
        };

        performanceMonitor.trackResourceLoading(mockEntry);

        const stats = performanceMonitor.getResourceStats();
        expect(stats.script).toBeDefined();
        expect(stats.script.count).toBe(1);
        expect(stats.script.averageDuration).toBe(100);
        expect(stats.script.totalSize).toBe(1024);
      });

      it('should alert on slow resource loading', () => {
        const mockEntry = {
          name: 'large.js',
          initiatorType: 'script',
          duration: 1500,
          transferSize: 2048,
          startTime: 0
        };

        performanceMonitor.trackResourceLoading(mockEntry);

        expect(performanceMonitor.featureFlags.trackError).toHaveBeenCalledWith('error', expect.objectContaining({
          message: expect.stringContaining('Slow resource loading'),
          type: 'network'
        }));
      });
    });

    describe('Navigation Timing', () => {
      it('should track navigation timing metrics', () => {
        const mockEntry = {
          name: 'https://example.com',
          navigationStart: 0,
          loadEventEnd: 2000,
          domContentLoadedEventEnd: 1500,
          firstPaint: 1000,
          firstContentfulPaint: 1200
        };

        performanceMonitor.trackNavigationTiming(mockEntry);

        const stats = performanceMonitor.getNavigationStats();
        expect(stats.count).toBe(1);
        expect(stats.averageLoadTime).toBe(2000);
        expect(stats.averageDomContentLoaded).toBe(1500);
        expect(stats.averageFirstPaint).toBe(1000);
        expect(stats.averageFirstContentfulPaint).toBe(1200);
      });

      it('should alert on slow page loads', () => {
        const mockEntry = {
          name: 'https://example.com',
          navigationStart: 0,
          loadEventEnd: 4000,
          domContentLoadedEventEnd: 3500,
          firstPaint: 3000,
          firstContentfulPaint: 3200
        };

        performanceMonitor.trackNavigationTiming(mockEntry);

        expect(performanceMonitor.featureFlags.trackError).toHaveBeenCalledWith('error', expect.objectContaining({
          message: expect.stringContaining('Slow page load'),
          type: 'navigation'
        }));
      });
    });

    describe('Connection Information', () => {
      it('should track connection information', () => {
        performanceMonitor.trackConnectionInfo(mockConnection);

        const stats = performanceMonitor.getConnectionStats();
        expect(stats.count).toBe(1);
        expect(stats.types.wifi).toBe(1);
        expect(stats.effectiveTypes['4g']).toBe(1);
        expect(stats.averageRtt).toBe(50);
        expect(stats.averageDownlink).toBe(10);
      });

      it('should alert on poor connection', () => {
        const poorConnection = {
          ...mockConnection,
          effectiveType: '2g'
        };

        performanceMonitor.trackConnectionInfo(poorConnection);

        expect(performanceMonitor.featureFlags.trackError).toHaveBeenCalledWith('error', expect.objectContaining({
          message: expect.stringContaining('Poor network connection'),
          type: 'connection'
        }));
      });

      it('should handle connection changes', () => {
        const changeCallback = mockConnection.addEventListener.mock.calls[0][1];
        const newConnection = {
          ...mockConnection,
          effectiveType: '3g'
        };

        changeCallback();
        performanceMonitor.trackConnectionInfo(newConnection);

        const stats = performanceMonitor.getConnectionStats();
        expect(stats.count).toBe(2);
        expect(stats.effectiveTypes['3g']).toBe(1);
      });
    });

    describe('Network Statistics', () => {
      it('should generate complete network statistics', () => {
        // Add test data
        performanceMonitor.trackResourceLoading({
          name: 'test.js',
          initiatorType: 'script',
          duration: 100,
          transferSize: 1024,
          startTime: 0
        });

        performanceMonitor.trackNavigationTiming({
          name: 'https://example.com',
          navigationStart: 0,
          loadEventEnd: 2000,
          domContentLoadedEventEnd: 1500,
          firstPaint: 1000,
          firstContentfulPaint: 1200
        });

        performanceMonitor.trackConnectionInfo(mockConnection);

        const stats = performanceMonitor.getNetworkStats();
        expect(stats.resources).toBeDefined();
        expect(stats.navigation).toBeDefined();
        expect(stats.connection).toBeDefined();
      });
    });
  });
}); 