import { performanceMonitor } from './performance';

interface CacheConfig {
  maxAge?: number;
  maxSize?: number;
}

interface CacheEntry<T> {
  value: T;
  timestamp: number;
  expiresAt: number;
}

export class CacheService {
  private cache: Map<string, CacheEntry<any>>;
  private maxAge: number;
  private maxSize: number;

  constructor(config: CacheConfig = {}) {
    this.cache = new Map();
    this.maxAge = config.maxAge || 5 * 60 * 1000; // 5 minutes default
    this.maxSize = config.maxSize || 100; // 100 items default
  }

  /**
   * Set a value in the cache
   */
  set<T>(key: string, value: T, maxAge?: number): void {
    const startTime = performance.now();

    try {
      // Clean up expired entries before setting new one
      this.cleanup();

      // If cache is full, remove oldest entry
      if (this.cache.size >= this.maxSize) {
        const oldestKey = this.findOldestEntry();
        if (oldestKey) {
          this.cache.delete(oldestKey);
          performanceMonitor.recordMetric('cache-eviction', 1);
        }
      }

      const timestamp = Date.now();
      const entry: CacheEntry<T> = {
        value,
        timestamp,
        expiresAt: timestamp + (maxAge || this.maxAge)
      };

      this.cache.set(key, entry);
      performanceMonitor.recordMetric('cache-set', performance.now() - startTime);
    } catch (error) {
      performanceMonitor.recordMetric('cache-error', 1);
      throw error;
    }
  }

  /**
   * Get a value from the cache
   */
  get<T>(key: string): T | null {
    const startTime = performance.now();

    try {
      const entry = this.cache.get(key);

      if (!entry) {
        performanceMonitor.recordMetric('cache-miss', 1);
        return null;
      }

      if (Date.now() > entry.expiresAt) {
        this.cache.delete(key);
        performanceMonitor.recordMetric('cache-expired', 1);
        return null;
      }

      performanceMonitor.recordMetric('cache-hit', 1);
      performanceMonitor.recordMetric('cache-get', performance.now() - startTime);
      return entry.value as T;
    } catch (error) {
      performanceMonitor.recordMetric('cache-error', 1);
      throw error;
    }
  }

  /**
   * Delete a value from the cache
   */
  delete(key: string): boolean {
    const startTime = performance.now();

    try {
      const result = this.cache.delete(key);
      performanceMonitor.recordMetric('cache-delete', performance.now() - startTime);
      return result;
    } catch (error) {
      performanceMonitor.recordMetric('cache-error', 1);
      throw error;
    }
  }

  /**
   * Clear all values from the cache
   */
  clear(): void {
    const startTime = performance.now();

    try {
      this.cache.clear();
      performanceMonitor.recordMetric('cache-clear', performance.now() - startTime);
    } catch (error) {
      performanceMonitor.recordMetric('cache-error', 1);
      throw error;
    }
  }

  /**
   * Get the number of entries in the cache
   */
  size(): number {
    return this.cache.size;
  }

  /**
   * Clean up expired entries
   */
  private cleanup(): void {
    const startTime = performance.now();
    let removedCount = 0;

    try {
      const now = Date.now();
      for (const [key, entry] of this.cache.entries()) {
        if (now > entry.expiresAt) {
          this.cache.delete(key);
          removedCount++;
        }
      }

      if (removedCount > 0) {
        performanceMonitor.recordMetric('cache-cleanup-removed', removedCount);
      }
      performanceMonitor.recordMetric('cache-cleanup', performance.now() - startTime);
    } catch (error) {
      performanceMonitor.recordMetric('cache-error', 1);
      throw error;
    }
  }

  /**
   * Find the oldest entry in the cache
   */
  private findOldestEntry(): string | null {
    let oldestKey: string | null = null;
    let oldestTimestamp = Infinity;

    for (const [key, entry] of this.cache.entries()) {
      if (entry.timestamp < oldestTimestamp) {
        oldestTimestamp = entry.timestamp;
        oldestKey = key;
      }
    }

    return oldestKey;
  }
}

// Create a singleton instance
export const cacheService = new CacheService(); 