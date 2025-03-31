import Redis from 'ioredis';
import { config } from '../config';

class RedisService {
  private client: Redis;
  private readonly messageQueuePrefix = 'ws:queue:';
  private readonly messageExpiry = 24 * 60 * 60; // 24 hours in seconds

  constructor() {
    this.client = new Redis(config.redis.url);
    this.client.on('error', (error) => {
      console.error('Redis error:', error);
    });
  }

  private getQueueKey(userId: string): string {
    return `${this.messageQueuePrefix}${userId}`;
  }

  public async queueMessage(userId: string, message: any): Promise<void> {
    const queueKey = this.getQueueKey(userId);
    try {
      await this.client.rpush(queueKey, JSON.stringify(message));
      await this.client.expire(queueKey, this.messageExpiry);
    } catch (error) {
      console.error('Failed to queue message:', error);
      throw error;
    }
  }

  public async getQueuedMessages(userId: string): Promise<any[]> {
    const queueKey = this.getQueueKey(userId);
    try {
      const messages = await this.client.lrange(queueKey, 0, -1);
      await this.client.del(queueKey);
      return messages.map(msg => JSON.parse(msg));
    } catch (error) {
      console.error('Failed to get queued messages:', error);
      return [];
    }
  }

  public async close(): Promise<void> {
    await this.client.quit();
  }
}

export const redisService = new RedisService(); 