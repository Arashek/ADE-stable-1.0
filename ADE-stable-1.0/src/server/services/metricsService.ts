import { Redis } from 'ioredis';
import { config } from '../config';

interface Metrics {
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
    avgMessageSize: number;
    avgProcessingTime: number;
  };
  rateLimit: {
    blocked: number;
    warnings: number;
  };
}

class MetricsService {
  private client: Redis;
  private readonly keyPrefix = 'metrics:';
  private readonly metricsExpiry = 24 * 60 * 60; // 24 hours

  constructor() {
    this.client = new Redis(config.redis.url);
    this.client.on('error', (error) => {
      console.error('Metrics Redis error:', error);
    });
  }

  private getKey(metric: string): string {
    const date = new Date().toISOString().split('T')[0];
    return `${this.keyPrefix}${metric}:${date}`;
  }

  public async incrementCounter(metric: string, value = 1): Promise<void> {
    const key = this.getKey(metric);
    await this.client.incrby(key, value);
    await this.client.expire(key, this.metricsExpiry);
  }

  public async updateGauge(metric: string, value: number): Promise<void> {
    const key = this.getKey(metric);
    await this.client.set(key, value);
    await this.client.expire(key, this.metricsExpiry);
  }

  public async recordTiming(metric: string, duration: number): Promise<void> {
    const key = this.getKey(metric);
    await this.client.lpush(key, duration.toString());
    await this.client.ltrim(key, 0, 999); // Keep last 1000 measurements
    await this.client.expire(key, this.metricsExpiry);
  }

  public async getMetrics(): Promise<Metrics> {
    const date = new Date().toISOString().split('T')[0];
    const keys = await this.client.keys(`${this.keyPrefix}*:${date}`);
    const metrics: Partial<Metrics> = {
      connections: {
        total: 0,
        active: 0,
        peak: 0,
      },
      messages: {
        sent: 0,
        received: 0,
        errors: 0,
        compressed: 0,
      },
      performance: {
        avgMessageSize: 0,
        avgProcessingTime: 0,
      },
      rateLimit: {
        blocked: 0,
        warnings: 0,
      },
    };

    for (const key of keys) {
      const value = await this.client.get(key);
      if (!value) continue;

      const metricName = key.split(':')[1];
      this.updateMetricValue(metrics, metricName, parseFloat(value));
    }

    return metrics as Metrics;
  }

  private updateMetricValue(metrics: Partial<Metrics>, metric: string, value: number) {
    const [category, name] = metric.split('.');
    if (category in metrics && name) {
      (metrics[category as keyof Metrics] as any)[name] = value;
    }
  }

  public async getHistogram(metric: string): Promise<number[]> {
    const key = this.getKey(metric);
    const values = await this.client.lrange(key, 0, -1);
    return values.map(v => parseFloat(v));
  }

  public async close(): Promise<void> {
    await this.client.quit();
  }
}

export const metricsService = new MetricsService(); 