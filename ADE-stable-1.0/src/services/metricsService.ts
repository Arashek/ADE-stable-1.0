import Redis from 'ioredis';
import { format } from 'date-fns';

interface MetricsData {
  connections: {
    total: number;
    active: number;
    peak: number;
  };
  messages: {
    sent: number;
    received: number;
    errors: number;
    compressed: number;
  };
  performance: {
    avgProcessingTime: number;
    p95ProcessingTime: number;
    p99ProcessingTime: number;
  };
  rateLimit: {
    blocked: number;
    remaining: number;
  };
  [key: string]: any;
}

export class MetricsService {
  private redis: Redis;
  private readonly METRICS_PREFIX = 'metrics:';
  private readonly HISTOGRAM_MAX_SIZE = 1000;
  private readonly METRICS_TTL = 24 * 60 * 60; // 24 hours

  constructor(redisClient?: Redis) {
    if (redisClient) {
      this.redis = redisClient;
    } else {
      this.redis = new Redis({
        host: process.env.REDIS_HOST || 'localhost',
        port: parseInt(process.env.REDIS_PORT || '6379'),
        password: process.env.REDIS_PASSWORD,
        retryStrategy: (times) => Math.min(times * 50, 2000)
      });

      this.redis.on('error', (error: Error) => {
        console.error('Redis connection error:', error);
      });
    }
  }

  private getMetricKey(name: string): string {
    const date = format(new Date(), 'yyyy-MM-dd');
    return `${this.METRICS_PREFIX}${name}:${date}`;
  }

  async incrementCounter(name: string, value = 1): Promise<void> {
    const key = this.getMetricKey(name);
    await this.redis.incrby(key, value);
    await this.redis.expire(key, this.METRICS_TTL);
  }

  async updateGauge(name: string, value: number): Promise<void> {
    const key = this.getMetricKey(name);
    await this.redis.set(key, value);
    await this.redis.expire(key, this.METRICS_TTL);
  }

  async recordTiming(name: string, value: number): Promise<void> {
    const key = this.getMetricKey(name);
    await this.redis.lpush(key, value.toString());
    await this.redis.ltrim(key, 0, this.HISTOGRAM_MAX_SIZE - 1);
    await this.redis.expire(key, this.METRICS_TTL);
  }

  async getMetrics(): Promise<MetricsData> {
    const date = format(new Date(), 'yyyy-MM-dd');
    const keys = await this.redis.keys(`${this.METRICS_PREFIX}*:${date}`);
    const metrics: MetricsData = {
      connections: {
        total: 0,
        active: 0,
        peak: 0
      },
      messages: {
        sent: 0,
        received: 0,
        errors: 0,
        compressed: 0
      },
      performance: {
        avgProcessingTime: 0,
        p95ProcessingTime: 0,
        p99ProcessingTime: 0
      },
      rateLimit: {
        blocked: 0,
        remaining: 0
      }
    };

    for (const key of keys) {
      const value = await this.redis.get(key);
      if (value === null) continue;

      const metricPath = key
        .replace(`${this.METRICS_PREFIX}`, '')
        .replace(`:${date}`, '')
        .split('.');

      let current: any = metrics;
      for (let i = 0; i < metricPath.length - 1; i++) {
        const segment = metricPath[i];
        if (!current[segment]) {
          current[segment] = {};
        }
        current = current[segment];
      }

      const lastSegment = metricPath[metricPath.length - 1];
      const numValue = parseFloat(value);
      current[lastSegment] = isNaN(numValue) ? 0 : numValue;
    }

    return metrics;
  }

  async getHistogram(name: string): Promise<number[]> {
    const key = this.getMetricKey(name);
    const values = await this.redis.lrange(key, 0, -1);
    return values.map(v => {
      const num = parseFloat(v);
      return isNaN(num) ? 0 : num;
    });
  }

  async close(): Promise<void> {
    await this.redis.quit();
  }
}

export const metricsService = new MetricsService(); 