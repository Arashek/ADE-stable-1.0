import { Request, Response, NextFunction } from 'express';
import { container } from 'tsyringe';
import { Logger } from '../services/logger/Logger';
import { Redis } from 'ioredis';

const logger = container.resolve(Logger);
const redis = new Redis(process.env.REDIS_URL || 'redis://localhost:6379');

interface RateLimitInfo {
  requests: number;
  resetTime: number;
}

export function rateLimiter(maxRequests: number, windowSeconds: number) {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      const key = getRateLimitKey(req);
      const currentTime = Math.floor(Date.now() / 1000);
      const windowStart = currentTime - windowSeconds;

      // Get current rate limit info
      const rateLimitInfo = await getRateLimitInfo(key);

      if (!rateLimitInfo) {
        // First request, initialize rate limit info
        await setRateLimitInfo(key, {
          requests: 1,
          resetTime: currentTime + windowSeconds
        });
        setRateLimitHeaders(res, maxRequests, maxRequests - 1, windowSeconds);
        next();
        return;
      }

      if (currentTime >= rateLimitInfo.resetTime) {
        // Window expired, reset rate limit info
        await setRateLimitInfo(key, {
          requests: 1,
          resetTime: currentTime + windowSeconds
        });
        setRateLimitHeaders(res, maxRequests, maxRequests - 1, windowSeconds);
        next();
        return;
      }

      if (rateLimitInfo.requests >= maxRequests) {
        // Rate limit exceeded
        const retryAfter = rateLimitInfo.resetTime - currentTime;
        setRateLimitHeaders(res, maxRequests, 0, retryAfter);
        res.status(429).json({
          error: 'Too many requests',
          retryAfter: retryAfter
        });
        return;
      }

      // Increment request count
      rateLimitInfo.requests += 1;
      await setRateLimitInfo(key, rateLimitInfo);

      setRateLimitHeaders(
        res,
        maxRequests,
        maxRequests - rateLimitInfo.requests,
        rateLimitInfo.resetTime - currentTime
      );
      next();
    } catch (error) {
      logger.error('Rate limiter error:', error);
      // Allow request to proceed on rate limiter error
      next();
    }
  };
}

function getRateLimitKey(req: Request): string {
  // Use IP address as default key
  let key = req.ip;

  // If authenticated, use user ID
  if ((req as any).user?.id) {
    key = (req as any).user.id;
  }

  // If API key present, use that
  const apiKey = req.headers['x-api-key'];
  if (apiKey) {
    key = apiKey as string;
  }

  return `ratelimit:${key}`;
}

async function getRateLimitInfo(key: string): Promise<RateLimitInfo | null> {
  try {
    const data = await redis.get(key);
    return data ? JSON.parse(data) : null;
  } catch (error) {
    logger.error('Redis get error:', error);
    return null;
  }
}

async function setRateLimitInfo(key: string, info: RateLimitInfo): Promise<void> {
  try {
    // Set expiration to reset time plus 1 minute for safety
    const ttl = (info.resetTime - Math.floor(Date.now() / 1000)) + 60;
    await redis.set(key, JSON.stringify(info), 'EX', ttl);
  } catch (error) {
    logger.error('Redis set error:', error);
  }
}

function setRateLimitHeaders(
  res: Response,
  limit: number,
  remaining: number,
  reset: number
): void {
  res.setHeader('X-RateLimit-Limit', limit);
  res.setHeader('X-RateLimit-Remaining', Math.max(0, remaining));
  res.setHeader('X-RateLimit-Reset', reset);
  
  if (remaining <= 0) {
    res.setHeader('Retry-After', reset);
  }
} 