import { metricsService } from '../../../server/services/metricsService';
import { rateLimiterService } from '../../../server/services/rateLimiterService';

describe('Metrics Performance Tests', () => {
  const NUM_ITERATIONS = 10000;
  const CONCURRENT_OPERATIONS = 100;

  beforeEach(() => {
    jest.clearAllMocks();
  });

  afterAll(async () => {
    await metricsService.close();
    await rateLimiterService.close();
  });

  describe('Metrics Collection Performance', () => {
    it('should handle rapid counter increments', async () => {
      const startTime = Date.now();

      // Perform concurrent counter increments
      await Promise.all(
        Array(CONCURRENT_OPERATIONS).fill(null).map(() =>
          Promise.all(
            Array(NUM_ITERATIONS / CONCURRENT_OPERATIONS).fill(null).map(() =>
              metricsService.incrementCounter('perf.test.counter')
            )
          )
        )
      );

      const duration = Date.now() - startTime;
      const opsPerSecond = (NUM_ITERATIONS / duration) * 1000;

      console.log(`Counter increments: ${opsPerSecond.toFixed(2)} ops/sec`);
      expect(opsPerSecond).toBeGreaterThan(5000); // At least 5000 ops/sec
    });

    it('should handle concurrent gauge updates', async () => {
      const startTime = Date.now();

      await Promise.all(
        Array(CONCURRENT_OPERATIONS).fill(null).map((_, i) =>
          Promise.all(
            Array(NUM_ITERATIONS / CONCURRENT_OPERATIONS).fill(null).map(() =>
              metricsService.updateGauge('perf.test.gauge', Math.random() * 100)
            )
          )
        )
      );

      const duration = Date.now() - startTime;
      const opsPerSecond = (NUM_ITERATIONS / duration) * 1000;

      console.log(`Gauge updates: ${opsPerSecond.toFixed(2)} ops/sec`);
      expect(opsPerSecond).toBeGreaterThan(5000); // At least 5000 ops/sec
    });

    it('should handle concurrent timing records', async () => {
      const startTime = Date.now();

      await Promise.all(
        Array(CONCURRENT_OPERATIONS).fill(null).map(() =>
          Promise.all(
            Array(NUM_ITERATIONS / CONCURRENT_OPERATIONS).fill(null).map(() =>
              metricsService.recordTiming('perf.test.timing', Math.random() * 100)
            )
          )
        )
      );

      const duration = Date.now() - startTime;
      const opsPerSecond = (NUM_ITERATIONS / duration) * 1000;

      console.log(`Timing records: ${opsPerSecond.toFixed(2)} ops/sec`);
      expect(opsPerSecond).toBeGreaterThan(2000); // At least 2000 ops/sec
    });
  });

  describe('Metrics Retrieval Performance', () => {
    beforeEach(async () => {
      // Setup test data
      await Promise.all(
        Array(1000).fill(null).map((_, i) =>
          Promise.all([
            metricsService.incrementCounter('perf.test.counter'),
            metricsService.updateGauge('perf.test.gauge', i),
            metricsService.recordTiming('perf.test.timing', i)
          ])
        )
      );
    });

    it('should efficiently retrieve metrics', async () => {
      const startTime = Date.now();

      await Promise.all(
        Array(100).fill(null).map(() =>
          metricsService.getMetrics()
        )
      );

      const duration = Date.now() - startTime;
      const avgDuration = duration / 100;

      console.log(`Average metrics retrieval time: ${avgDuration.toFixed(2)}ms`);
      expect(avgDuration).toBeLessThan(50); // Less than 50ms per retrieval
    });

    it('should efficiently retrieve histograms', async () => {
      const startTime = Date.now();

      await Promise.all(
        Array(100).fill(null).map(() =>
          metricsService.getHistogram('perf.test.timing')
        )
      );

      const duration = Date.now() - startTime;
      const avgDuration = duration / 100;

      console.log(`Average histogram retrieval time: ${avgDuration.toFixed(2)}ms`);
      expect(avgDuration).toBeLessThan(20); // Less than 20ms per retrieval
    });
  });

  describe('Rate Limiter Performance', () => {
    const NUM_USERS = 1000;
    const REQUESTS_PER_USER = 100;

    it('should handle concurrent rate limit checks', async () => {
      const startTime = Date.now();

      await Promise.all(
        Array(NUM_USERS).fill(null).map((_, userId) =>
          Promise.all(
            Array(REQUESTS_PER_USER).fill(null).map(() =>
              rateLimiterService.isRateLimited(`user${userId}`, 'message')
            )
          )
        )
      );

      const duration = Date.now() - startTime;
      const opsPerSecond = ((NUM_USERS * REQUESTS_PER_USER) / duration) * 1000;

      console.log(`Rate limit checks: ${opsPerSecond.toFixed(2)} ops/sec`);
      expect(opsPerSecond).toBeGreaterThan(10000); // At least 10000 ops/sec
    });

    it('should efficiently retrieve rate limit metrics', async () => {
      // Setup test data
      await Promise.all(
        Array(100).fill(null).map((_, i) =>
          rateLimiterService.isRateLimited(`user${i}`, 'message')
        )
      );

      const startTime = Date.now();

      await Promise.all(
        Array(100).fill(null).map(() =>
          rateLimiterService.getRateLimitMetrics()
        )
      );

      const duration = Date.now() - startTime;
      const avgDuration = duration / 100;

      console.log(`Average rate limit metrics retrieval time: ${avgDuration.toFixed(2)}ms`);
      expect(avgDuration).toBeLessThan(50); // Less than 50ms per retrieval
    });
  });

  describe('Memory Usage', () => {
    it('should maintain stable memory usage under load', async () => {
      const initialMemory = process.memoryUsage().heapUsed;

      // Perform intensive operations
      await Promise.all([
        // Metrics operations
        ...Array(1000).fill(null).map(() => metricsService.incrementCounter('memory.test.counter')),
        ...Array(1000).fill(null).map(() => metricsService.updateGauge('memory.test.gauge', 42)),
        ...Array(1000).fill(null).map(() => metricsService.recordTiming('memory.test.timing', 100)),
        
        // Rate limit operations
        ...Array(1000).fill(null).map((_, i) => 
          rateLimiterService.isRateLimited(`user${i}`, 'message')
        )
      ]);

      // Force garbage collection if available
      if (global.gc) {
        global.gc();
      }

      const finalMemory = process.memoryUsage().heapUsed;
      const memoryIncrease = (finalMemory - initialMemory) / 1024 / 1024; // MB

      console.log(`Memory increase: ${memoryIncrease.toFixed(2)}MB`);
      expect(memoryIncrease).toBeLessThan(50); // Less than 50MB increase
    });
  });
}); 