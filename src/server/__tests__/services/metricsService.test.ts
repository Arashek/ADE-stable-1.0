import { Redis } from 'ioredis';
import { metricsService } from '../../services/metricsService';

// Mock Redis client
jest.mock('ioredis');

describe('MetricsService', () => {
  let mockRedis: jest.Mocked<Redis>;

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    
    // Setup Redis mock
    mockRedis = new Redis() as jest.Mocked<Redis>;
    (Redis as jest.Mock).mockImplementation(() => mockRedis);
  });

  afterEach(async () => {
    await metricsService.close();
  });

  describe('incrementCounter', () => {
    it('should increment a counter and set expiry', async () => {
      mockRedis.incrby.mockResolvedValue(1);
      mockRedis.expire.mockResolvedValue(1);

      await metricsService.incrementCounter('test.counter');

      expect(mockRedis.incrby).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.counter:'),
        1
      );
      expect(mockRedis.expire).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.counter:'),
        24 * 60 * 60
      );
    });

    it('should handle Redis errors gracefully', async () => {
      mockRedis.incrby.mockRejectedValue(new Error('Redis connection error'));
      
      await expect(metricsService.incrementCounter('test.counter'))
        .rejects.toThrow('Redis connection error');
    });

    it('should handle large increment values', async () => {
      mockRedis.incrby.mockResolvedValue(Number.MAX_SAFE_INTEGER);
      mockRedis.expire.mockResolvedValue(1);

      await metricsService.incrementCounter('test.counter', 1000000);

      expect(mockRedis.incrby).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.counter:'),
        1000000
      );
    });
  });

  describe('updateGauge', () => {
    it('should set gauge value and expiry', async () => {
      mockRedis.set.mockResolvedValue('OK');
      mockRedis.expire.mockResolvedValue(1);

      await metricsService.updateGauge('test.gauge', 42);

      expect(mockRedis.set).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.gauge:'),
        42
      );
      expect(mockRedis.expire).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.gauge:'),
        24 * 60 * 60
      );
    });

    it('should handle negative values', async () => {
      mockRedis.set.mockResolvedValue('OK');
      mockRedis.expire.mockResolvedValue(1);

      await metricsService.updateGauge('test.gauge', -42);

      expect(mockRedis.set).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.gauge:'),
        -42
      );
    });

    it('should handle floating point values', async () => {
      mockRedis.set.mockResolvedValue('OK');
      mockRedis.expire.mockResolvedValue(1);

      await metricsService.updateGauge('test.gauge', 3.14159);

      expect(mockRedis.set).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.gauge:'),
        3.14159
      );
    });
  });

  describe('recordTiming', () => {
    it('should record timing value and maintain list size', async () => {
      mockRedis.lpush.mockResolvedValue(1);
      mockRedis.ltrim.mockResolvedValue('OK');
      mockRedis.expire.mockResolvedValue(1);

      await metricsService.recordTiming('test.timing', 100);

      expect(mockRedis.lpush).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.timing:'),
        '100'
      );
      expect(mockRedis.ltrim).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.timing:'),
        0,
        999
      );
    });

    it('should handle microsecond timings', async () => {
      mockRedis.lpush.mockResolvedValue(1);
      mockRedis.ltrim.mockResolvedValue('OK');
      mockRedis.expire.mockResolvedValue(1);

      await metricsService.recordTiming('test.timing', 0.000042);

      expect(mockRedis.lpush).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.timing:'),
        '0.000042'
      );
    });

    it('should maintain list size when exceeding limit', async () => {
      mockRedis.lpush.mockResolvedValue(1001);
      mockRedis.ltrim.mockResolvedValue('OK');
      mockRedis.expire.mockResolvedValue(1);

      await metricsService.recordTiming('test.timing', 100);

      expect(mockRedis.ltrim).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.timing:'),
        0,
        999
      );
    });
  });

  describe('getMetrics', () => {
    it('should retrieve and format all metrics', async () => {
      const mockDate = '2024-03-20';
      const mockKeys = [
        `metrics:connections.total:${mockDate}`,
        `metrics:messages.sent:${mockDate}`,
        `metrics:performance.avgProcessingTime:${mockDate}`
      ];

      mockRedis.keys.mockResolvedValue(mockKeys);
      mockRedis.get
        .mockResolvedValueOnce('100') // connections.total
        .mockResolvedValueOnce('500') // messages.sent
        .mockResolvedValueOnce('42.5'); // performance.avgProcessingTime

      const metrics = await metricsService.getMetrics();

      expect(metrics).toEqual(expect.objectContaining({
        connections: expect.objectContaining({
          total: 100
        }),
        messages: expect.objectContaining({
          sent: 500
        }),
        performance: expect.objectContaining({
          avgProcessingTime: 42.5
        })
      }));
    });

    it('should handle missing metrics', async () => {
      mockRedis.keys.mockResolvedValue([]);
      mockRedis.get.mockResolvedValue(null);

      const metrics = await metricsService.getMetrics();

      expect(metrics).toEqual(expect.objectContaining({
        connections: expect.objectContaining({
          total: 0,
          active: 0,
          peak: 0
        }),
        messages: expect.objectContaining({
          sent: 0,
          received: 0,
          errors: 0,
          compressed: 0
        })
      }));
    });

    it('should handle malformed metric values', async () => {
      const mockDate = '2024-03-20';
      const mockKeys = [
        `metrics:connections.total:${mockDate}`,
        `metrics:messages.sent:${mockDate}`
      ];

      mockRedis.keys.mockResolvedValue(mockKeys);
      mockRedis.get
        .mockResolvedValueOnce('not-a-number')
        .mockResolvedValueOnce('500');

      const metrics = await metricsService.getMetrics();

      expect(metrics.connections.total).toBe(0); // Should default to 0 for invalid number
      expect(metrics.messages.sent).toBe(500);
    });

    it('should handle deeply nested metric paths', async () => {
      const mockDate = '2024-03-20';
      const mockKeys = [
        `metrics:deep.nested.path.value:${mockDate}`
      ];

      mockRedis.keys.mockResolvedValue(mockKeys);
      mockRedis.get.mockResolvedValueOnce('42');

      const metrics = await metricsService.getMetrics();

      expect(metrics).toEqual(expect.objectContaining({
        deep: expect.objectContaining({
          nested: expect.objectContaining({
            path: expect.objectContaining({
              value: 42
            })
          })
        })
      }));
    });
  });

  describe('getHistogram', () => {
    it('should retrieve histogram values', async () => {
      const mockValues = ['10', '20', '30', '40', '50'];
      mockRedis.lrange.mockResolvedValue(mockValues);

      const histogram = await metricsService.getHistogram('test.histogram');

      expect(histogram).toEqual([10, 20, 30, 40, 50]);
      expect(mockRedis.lrange).toHaveBeenCalledWith(
        expect.stringContaining('metrics:test.histogram:'),
        0,
        -1
      );
    });

    it('should handle empty histogram', async () => {
      mockRedis.lrange.mockResolvedValue([]);

      const histogram = await metricsService.getHistogram('test.histogram');

      expect(histogram).toEqual([]);
    });

    it('should handle invalid histogram values', async () => {
      mockRedis.lrange.mockResolvedValue(['10', 'invalid', '30', 'NaN', '50']);

      const histogram = await metricsService.getHistogram('test.histogram');

      expect(histogram).toEqual([10, 0, 30, 0, 50]); // Invalid values should be converted to 0
    });
  });

  describe('error handling', () => {
    it('should handle Redis connection loss', async () => {
      mockRedis.on.mockImplementation((event, callback) => {
        if (event === 'error') {
          callback(new Error('Connection lost'));
        }
      });

      const redis = new Redis();
      expect(mockRedis.on).toHaveBeenCalledWith('error', expect.any(Function));
    });

    it('should handle Redis timeout', async () => {
      mockRedis.get.mockImplementation(() => new Promise((_, reject) => {
        setTimeout(() => reject(new Error('Redis timeout')), 1000);
      }));

      await expect(metricsService.getMetrics())
        .rejects.toThrow('Redis timeout');
    });
  });
}); 