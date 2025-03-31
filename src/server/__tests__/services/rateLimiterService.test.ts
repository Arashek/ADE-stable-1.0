import { Redis } from 'ioredis';
import { rateLimiterService } from '../../services/rateLimiterService';
import { metricsService } from '../../services/metricsService';

jest.mock('ioredis');
jest.mock('../../services/metricsService');

describe('RateLimiterService', () => {
  let mockRedis: jest.Mocked<Redis>;

  beforeEach(() => {
    jest.clearAllMocks();
    mockRedis = new Redis() as jest.Mocked<Redis>;
    (Redis as jest.Mock).mockImplementation(() => mockRedis);
  });

  afterEach(async () => {
    await rateLimiterService.close();
  });

  describe('isRateLimited', () => {
    it('should allow requests within limit', async () => {
      mockRedis.get.mockResolvedValue('3'); // 3 points remaining
      mockRedis.decrby.mockResolvedValue(2);

      const isLimited = await rateLimiterService.isRateLimited('user123', 'message');

      expect(isLimited).toBe(false);
      expect(mockRedis.decrby).toHaveBeenCalledWith(
        'ratelimit:message:user123',
        1
      );
    });

    it('should block requests when limit exceeded', async () => {
      mockRedis.get.mockResolvedValue('0'); // No points remaining

      const isLimited = await rateLimiterService.isRateLimited('user123', 'message');

      expect(isLimited).toBe(true);
      expect(metricsService.incrementCounter).toHaveBeenCalledWith('rateLimit.blocked');
    });

    it('should initialize new rate limit', async () => {
      mockRedis.get.mockResolvedValue(null);
      mockRedis.setex.mockResolvedValue('OK');

      const isLimited = await rateLimiterService.isRateLimited('user123', 'message');

      expect(isLimited).toBe(false);
      expect(mockRedis.setex).toHaveBeenCalledWith(
        'ratelimit:message:user123',
        60, // duration
        99  // points - 1
      );
    });

    it('should issue warning when approaching limit', async () => {
      mockRedis.get.mockResolvedValue('15'); // 15% of 100 points
      mockRedis.decrby.mockResolvedValue(14);

      await rateLimiterService.isRateLimited('user123', 'message');

      expect(metricsService.incrementCounter).toHaveBeenCalledWith('rateLimit.warnings');
    });

    it('should throw error for unknown action', async () => {
      await expect(
        rateLimiterService.isRateLimited('user123', 'unknown')
      ).rejects.toThrow('Unknown rate limit action: unknown');
    });
  });

  describe('getRemainingPoints', () => {
    it('should return remaining points and reset time', async () => {
      mockRedis.get.mockResolvedValue('42');
      mockRedis.ttl.mockResolvedValue(30);

      const info = await rateLimiterService.getRemainingPoints('user123', 'message');

      expect(info.remaining).toBe(42);
      expect(info.resetTime).toBeGreaterThan(Date.now());
      expect(info.resetTime).toBeLessThanOrEqual(Date.now() + 30000);
    });

    it('should return max points for new rate limit', async () => {
      mockRedis.get.mockResolvedValue(null);
      mockRedis.ttl.mockResolvedValue(-2);

      const info = await rateLimiterService.getRemainingPoints('user123', 'message');

      expect(info.remaining).toBe(100); // Default points for message action
      expect(info.resetTime).toBeGreaterThan(Date.now());
    });
  });

  describe('getRateLimitMetrics', () => {
    it('should return comprehensive metrics', async () => {
      const mockDate = new Date().toISOString().split('T')[0];
      
      mockRedis.get
        .mockResolvedValueOnce('5')   // blocked count
        .mockResolvedValueOnce('10'); // warnings count

      mockRedis.keys.mockResolvedValue(['ratelimit:message:user1', 'ratelimit:message:user2']);
      mockRedis.get
        .mockResolvedValueOnce('80')  // remaining points for user1
        .mockResolvedValueOnce('90'); // remaining points for user2

      const metrics = await rateLimiterService.getRateLimitMetrics();

      expect(metrics).toEqual({
        blocked: 5,
        warnings: 10,
        actions: {
          message: {
            activeUsers: 2,
            totalUsage: 30, // (100 - 80) + (100 - 90)
            avgUsage: 15,   // 30 / 2
            limit: 100,
            duration: 60
          }
        }
      });
    });

    it('should handle no active rate limits', async () => {
      mockRedis.get.mockResolvedValue(null);
      mockRedis.keys.mockResolvedValue([]);

      const metrics = await rateLimiterService.getRateLimitMetrics();

      expect(metrics).toEqual({
        blocked: 0,
        warnings: 0,
        actions: {
          connection: {
            activeUsers: 0,
            totalUsage: 0,
            avgUsage: 0,
            limit: 5,
            duration: 60
          },
          message: {
            activeUsers: 0,
            totalUsage: 0,
            avgUsage: 0,
            limit: 100,
            duration: 60
          },
          broadcast: {
            activeUsers: 0,
            totalUsage: 0,
            avgUsage: 0,
            limit: 10,
            duration: 60
          }
        }
      });
    });
  });
}); 