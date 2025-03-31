interface CacheItem<T> {
  value: T;
  timestamp: number;
  ttl: number;
}

export class Cache {
  private static instance: Cache;
  private cache: Map<string, CacheItem<any>> = new Map();
  private readonly defaultTTL: number = 5 * 60 * 1000; // 5 minutes

  private constructor() {
    // Start cleanup interval
    setInterval(() => this.cleanup(), 60000); // Cleanup every minute
  }

  static getInstance(): Cache {
    if (!Cache.instance) {
      Cache.instance = new Cache();
    }
    return Cache.instance;
  }

  set<T>(key: string, value: T, ttl: number = this.defaultTTL): void {
    this.cache.set(key, {
      value,
      timestamp: Date.now(),
      ttl,
    });
  }

  get<T>(key: string): T | null {
    const item = this.cache.get(key);
    if (!item) return null;

    if (this.isExpired(item)) {
      this.cache.delete(key);
      return null;
    }

    return item.value as T;
  }

  delete(key: string): void {
    this.cache.delete(key);
  }

  clear(): void {
    this.cache.clear();
  }

  private isExpired(item: CacheItem<any>): boolean {
    return Date.now() - item.timestamp > item.ttl;
  }

  private cleanup(): void {
    for (const [key, item] of this.cache.entries()) {
      if (this.isExpired(item)) {
        this.cache.delete(key);
      }
    }
  }

  // Cache decorator for methods
  static cache(ttl: number = 5 * 60 * 1000) {
    return function (
      target: any,
      propertyKey: string,
      descriptor: PropertyDescriptor
    ) {
      const originalMethod = descriptor.value;
      const cache = Cache.getInstance();

      descriptor.value = function (...args: any[]) {
        const cacheKey = `${propertyKey}:${JSON.stringify(args)}`;
        const cachedValue = cache.get(cacheKey);

        if (cachedValue !== null) {
          return cachedValue;
        }

        const result = originalMethod.apply(this, args);
        cache.set(cacheKey, result, ttl);
        return result;
      };

      return descriptor;
    };
  }
}

// Create a singleton instance
export const cache = Cache.getInstance();

// Example usage:
/*
class ApiService {
  @Cache.cache(60000) // Cache for 1 minute
  async fetchUser(id: string) {
    const response = await fetch(`/api/users/${id}`);
    return response.json();
  }
}
*/ 