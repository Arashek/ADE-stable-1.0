import Redis from 'ioredis';
import { MetricsService } from '../../services/metricsService';
import { format } from 'date-fns';

jest.mock('ioredis');

describe('MetricsService', () => {
  let redis: Redis;
  let metricsService: MetricsService;
  const currentDate = format(new Date(), 'yyyy-MM-dd');

  beforeEach(() => {
    // Create a new Redis instance
    redis = new Redis();

    // Create a new instance of MetricsService with the mock Redis client
    metricsService = new MetricsService(redis);
  });

  afterEach(async () => {
    await metricsService.close();
  });

  describe('incrementCounter', () => {
    it('should increment a counter and set expiry', async () => {
      const spy1 = jest.spyOn(redis, 'incrby').mockResolvedValue(1);
      const spy2 = jest.spyOn(redis, 'expire').mockResolvedValue(1);

      await metricsService.incrementCounter('test.counter');

      expect(spy1).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.counter:'),
        1
      );
      expect(spy2).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.counter:'),
        86400
      );
    });

    it('should handle Redis errors gracefully', async () => {
      jest.spyOn(redis, 'incrby').mockRejectedValue(new Error('Redis connection error'));
      
      await expect(metricsService.incrementCounter('test.counter'))
        .rejects.toThrow('Redis connection error');
    });

    it('should handle large increment values', async () => {
      jest.spyOn(redis, 'incrby').mockResolvedValue(Number.MAX_SAFE_INTEGER);
      jest.spyOn(redis, 'expire').mockResolvedValue(1);

      await metricsService.incrementCounter('test.counter', 1000000);

      expect(redis.incrby).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.counter:'),
        1000000
      );
    });
  });

  describe('updateGauge', () => {
    it('should set gauge value and expiry', async () => {
      const spy1 = jest.spyOn(redis, 'set').mockResolvedValue('OK');
      const spy2 = jest.spyOn(redis, 'expire').mockResolvedValue(1);

      await metricsService.updateGauge('test.gauge', 42);

      expect(spy1).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.gauge:'),
        42
      );
      expect(spy2).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.gauge:'),
        86400
      );
    });

    it('should handle negative values', async () => {
      jest.spyOn(redis, 'set').mockResolvedValue('OK');
      jest.spyOn(redis, 'expire').mockResolvedValue(1);

      await metricsService.updateGauge('test.gauge', -42);

      expect(redis.set).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.gauge:'),
        -42
      );
    });

    it('should handle floating point values', async () => {
      jest.spyOn(redis, 'set').mockResolvedValue('OK');
      jest.spyOn(redis, 'expire').mockResolvedValue(1);

      await metricsService.updateGauge('test.gauge', 3.14159);

      expect(redis.set).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.gauge:'),
        3.14159
      );
    });
  });

  describe('recordTiming', () => {
    it('should record timing value and maintain list size', async () => {
      const spy1 = jest.spyOn(redis, 'lpush').mockResolvedValue(1);
      const spy2 = jest.spyOn(redis, 'ltrim').mockResolvedValue('OK');
      const spy3 = jest.spyOn(redis, 'expire').mockResolvedValue(1);

      await metricsService.recordTiming('test.timing', 100);

      expect(spy1).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.timing:'),
        '100'
      );
      expect(spy2).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.timing:'),
        0,
        999
      );
      expect(spy3).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.timing:'),
        86400
      );
    });

    it('should handle microsecond timings', async () => {
      jest.spyOn(redis, 'lpush').mockResolvedValue(1);
      jest.spyOn(redis, 'ltrim').mockResolvedValue('OK');
      jest.spyOn(redis, 'expire').mockResolvedValue(1);

      await metricsService.recordTiming('test.timing', 0.000042);

      expect(redis.lpush).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.timing:'),
        '0.000042'
      );
    });

    it('should maintain list size when exceeding limit', async () => {
      jest.spyOn(redis, 'lpush').mockResolvedValue(1001);
      jest.spyOn(redis, 'ltrim').mockResolvedValue('OK');
      jest.spyOn(redis, 'expire').mockResolvedValue(1);

      await metricsService.recordTiming('test.timing', 100);

      expect(redis.ltrim).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.timing:'),
        0,
        999
      );
    });
  });

  describe('getMetrics', () => {
    it('should retrieve all metrics', async () => {
      const mockKeys = [
        `metrics:connections.total:${currentDate}`,
        `metrics:connections.active:${currentDate}`,
        `metrics:connections.peak:${currentDate}`
      ];

      jest.spyOn(redis, 'keys').mockResolvedValue(mockKeys);
      const getSpy = jest.spyOn(redis, 'get');
      getSpy
        .mockResolvedValueOnce('100')
        .mockResolvedValueOnce('500')
        .mockResolvedValueOnce('42.5');

      const metrics = await metricsService.getMetrics();

      expect(metrics.connections.total).toBe(100);
      expect(metrics.connections.active).toBe(500);
      expect(metrics.connections.peak).toBe(42.5);
    });

    it('should handle missing metrics', async () => {
      jest.spyOn(redis, 'keys').mockResolvedValue([]);
      jest.spyOn(redis, 'get').mockResolvedValue(null);

      const metrics = await metricsService.getMetrics();

      expect(metrics).toEqual({
        connections: {
          total: 0,
          active: 0,
          peak: 0
        }
      });
    });

    it('should handle malformed metric values', async () => {
      const mockKeys = [
        `metrics:connections.total:${currentDate}`,
        `metrics:connections.active:${currentDate}`
      ];

      jest.spyOn(redis, 'keys').mockResolvedValue(mockKeys);
      const getSpy = jest.spyOn(redis, 'get');
      getSpy
        .mockResolvedValueOnce('not-a-number')
        .mockResolvedValueOnce('500');

      const metrics = await metricsService.getMetrics();

      expect(metrics.connections.total).toBe(0); // Should default to 0 for invalid number
      expect(metrics.connections.active).toBe(500);
    });

    it('should handle nested metric paths', async () => {
      const mockKeys = [
        `metrics:deep.nested.path.value:${currentDate}`
      ];

      jest.spyOn(redis, 'keys').mockResolvedValue(mockKeys);
      jest.spyOn(redis, 'get').mockResolvedValueOnce('42');

      const metrics = await metricsService.getMetrics();

      expect(metrics.deep?.nested?.path?.value).toBe(42);
    });
  });

  describe('getHistogram', () => {
    it('should retrieve histogram values', async () => {
      const mockValues = ['10', '20', '30', '40', '50'];
      const spy = jest.spyOn(redis, 'lrange').mockResolvedValue(mockValues);

      const histogram = await metricsService.getHistogram('test.histogram');

      expect(histogram).toEqual([10, 20, 30, 40, 50]);
      expect(spy).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.histogram:'),
        0,
        -1
      );
    });

    it('should handle empty histogram', async () => {
      jest.spyOn(redis, 'lrange').mockResolvedValue([]);

      const histogram = await metricsService.getHistogram('test.histogram');

      expect(histogram).toEqual([]);
    });

    it('should handle invalid histogram values', async () => {
      jest.spyOn(redis, 'lrange').mockResolvedValue(['10', 'invalid', '30', 'NaN', '50']);

      const histogram = await metricsService.getHistogram('test.histogram');

      expect(histogram).toEqual([10, 0, 30, 0, 50]); // Invalid values should be converted to 0
    });
  });

  describe('error handling', () => {
    it('should handle Redis connection loss', async () => {
      // Verify that error handler is registered
      expect(redis.on).toHaveBeenCalledWith('error', expect.any(Function));

      // Get the error handler function
      const calls = (redis.on as jest.Mock).mock.calls;
      const errorCall = calls.find(call => call[0] === 'error');
      const errorHandler = errorCall?.[1] as ((error: Error) => void) | undefined;

      // Ensure error handler was found
      expect(errorHandler).toBeDefined();

      // Simulate Redis error
      const error = new Error('Connection lost');
      errorHandler?.(error);

      // Verify that subsequent operations throw errors
      await expect(metricsService.getMetrics()).rejects.toThrow('Redis connection error');
    });

    it('should handle Redis timeout', async () => {
      const timeoutError = new Error('Redis operation timed out');
      (redis.get as jest.Mock).mockRejectedValueOnce(timeoutError);

      await expect(metricsService.getMetrics()).rejects.toThrow('Redis operation failed');
    });
  });
}); 