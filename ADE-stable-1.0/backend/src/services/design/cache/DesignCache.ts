import { DesignResponse } from '../types';

export class DesignCache {
    private cache: Map<string, {
        response: DesignResponse;
        timestamp: number;
    }>;
    private readonly TTL: number = 1000 * 60 * 60; // 1 hour cache TTL

    constructor() {
        this.cache = new Map();
    }

    public get(id: string): DesignResponse | null {
        const cached = this.cache.get(id);
        if (!cached) {
            return null;
        }

        // Check if cache entry has expired
        if (Date.now() - cached.timestamp > this.TTL) {
            this.cache.delete(id);
            return null;
        }

        return cached.response;
    }

    public set(id: string, response: DesignResponse): void {
        this.cache.set(id, {
            response,
            timestamp: Date.now()
        });
    }

    public delete(id: string): void {
        this.cache.delete(id);
    }

    public clear(): void {
        this.cache.clear();
    }

    public getCacheStats(): {
        size: number;
        oldestEntry: number;
        newestEntry: number;
    } {
        let oldestEntry = Date.now();
        let newestEntry = 0;

        this.cache.forEach(({ timestamp }) => {
            oldestEntry = Math.min(oldestEntry, timestamp);
            newestEntry = Math.max(newestEntry, timestamp);
        });

        return {
            size: this.cache.size,
            oldestEntry,
            newestEntry
        };
    }
} 