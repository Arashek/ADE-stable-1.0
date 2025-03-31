import { Redis } from 'ioredis';
import { config } from '../config';
import { metricsService } from './metricsService';

interface RateLimitConfig {
  points: number;      // Number of requests allowed
  duration: number;    // Time window in seconds
  blockDuration: number; // How long to block if limit exceeded (seconds)
}

interface RateLimitInfo {
  remaining: number;
  resetTime: number;
}

const defaultLimits: { [key: string]: RateLimitConfig } = {
  connection: {
    points: 5,
    duration: 60,      // 5 connections per minute
    blockDuration: 300 // 5 minutes block
  },
  message: {
    points: 100,
    duration: 60,      // 100 messages per minute
    blockDuration: 300 // 5 minutes block
  },
  broadcast: {
    points: 10,
    duration: 60,      // 10 broadcasts per minute
    blockDuration: 600 // 10 minutes block
  }
};

class RateLimiterService {
  private client: Redis;
  private readonly keyPrefix = 'ratelimit:';
  private readonly configs: Record<string, RateLimitConfig> = {
    connection: { points: 5, duration: 60 }, // 5 connections per minute
    message: { points: 100, duration: 60 }, // 100 messages per minute
    broadcast: { points: 10, duration: 60 }, // 10 broadcasts per minute
  };

  constructor() {
    this.client = new Redis(config.redis.url);
    this.client.on('error', (error) => {
      console.error('Rate Limiter Redis error:', error);
    });
  }

  private getKey(userId: string, action: string): string {
    return `${this.keyPrefix}${action}:${userId}`;
  }

  public async isRateLimited(userId: string, action: string): Promise<boolean> {
    const config = this.configs[action];
    if (!config) {
      throw new Error(`Unknown rate limit action: ${action}`);
    }

    const key = this.getKey(userId, action);
    const points = await this.client.get(key);
    
    if (!points) {
      await this.client.setex(key, config.duration, config.points - 1);
      return false;
    }

    const remaining = parseInt(points, 10);
    if (remaining <= 0) {
      await metricsService.incrementCounter('rateLimit.blocked');
      return true;
    }

    await this.client.decrby(key, 1);
    if (remaining <= config.points * 0.2) { // Warning at 20% remaining
      await metricsService.incrementCounter('rateLimit.warnings');
    }
    return false;
  }

  public async getRemainingPoints(userId: string, action: string): Promise<RateLimitInfo> {
    const config = this.configs[action];
    if (!config) {
      throw new Error(`Unknown rate limit action: ${action}`);
    }

    const key = this.getKey(userId, action);
    const [points, ttl] = await Promise.all([
      this.client.get(key),
      this.client.ttl(key),
    ]);

    const remaining = points ? parseInt(points, 10) : config.points;
    const resetTime = Date.now() + (ttl * 1000);

    return { remaining, resetTime };
  }

  public async getRateLimitMetrics(): Promise<Record<string, any>> {
    const metrics: Record<string, any> = {
      blocked: 0,
      warnings: 0,
      actions: {},
    };

    // Get blocked and warning counts
    const date = new Date().toISOString().split('T')[0];
    const blockedKey = `metrics:rateLimit.blocked:${date}`;
    const warningsKey = `metrics:rateLimit.warnings:${date}`;

    const [blocked, warnings] = await Promise.all([
      this.client.get(blockedKey),
      this.client.get(warningsKey),
    ]);

    metrics.blocked = blocked ? parseInt(blocked, 10) : 0;
    metrics.warnings = warnings ? parseInt(warnings, 10) : 0;

    // Get action-specific metrics
    for (const [action, config] of Object.entries(this.configs)) {
      const keys = await this.client.keys(`${this.keyPrefix}${action}:*`);
      const values = await Promise.all(keys.map(key => this.client.get(key)));
      
      const usageData = values
        .map(v => v ? config.points - parseInt(v, 10) : 0)
        .filter(v => v > 0);

      metrics.actions[action] = {
        activeUsers: keys.length,
        totalUsage: usageData.reduce((sum, v) => sum + v, 0),
        avgUsage: usageData.length ? 
          Math.round(usageData.reduce((sum, v) => sum + v, 0) / usageData.length) : 0,
        limit: config.points,
        duration: config.duration,
      };
    }

    return metrics;
  }

  public async close(): Promise<void> {
    await this.client.quit();
  }
}

export const rateLimiterService = new RateLimiterService(); 