import { z } from 'zod';

// Common validation schemas
export const emailSchema = z.string().email('Invalid email address');
export const passwordSchema = z
  .string()
  .min(8, 'Password must be at least 8 characters')
  .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
  .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
  .regex(/[0-9]/, 'Password must contain at least one number')
  .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character');

export const usernameSchema = z
  .string()
  .min(3, 'Username must be at least 3 characters')
  .max(30, 'Username must be less than 30 characters')
  .regex(/^[a-zA-Z0-9_-]+$/, 'Username can only contain letters, numbers, underscores, and hyphens');

// Command validation schemas
export const commandSchema = z.object({
  type: z.enum(['code', 'ai', 'tools']),
  content: z.string().min(1, 'Command cannot be empty'),
  parameters: z.record(z.any()).optional(),
});

// Code generation validation schemas
export const codeGenerationSchema = z.object({
  language: z.string(),
  framework: z.string().optional(),
  options: z.object({
    includeTests: z.boolean().optional(),
    includeDocs: z.boolean().optional(),
    format: z.enum(['pretty', 'minified']).optional(),
  }).optional(),
});

// Chat message validation schemas
export const chatMessageSchema = z.object({
  content: z.string().min(1, 'Message cannot be empty'),
  type: z.enum(['user', 'system', 'assistant']),
  metadata: z.object({
    timestamp: z.string(),
    userId: z.string().optional(),
    agent: z.enum(['code', 'ai', 'tools']).optional(),
  }).optional(),
});

// Validation helper functions
export const validateInput = <T>(schema: z.ZodSchema<T>, data: unknown): { success: boolean; data?: T; error?: string } => {
  try {
    const validatedData = schema.safeParse(data);
    if (!validatedData.success) {
      return { success: false, error: validatedData.error.issues[0].message };
    }
    return { success: true, data: validatedData.data };
  } catch (error) {
    return { success: false, error: 'Validation failed' };
  }
};

export const sanitizeInput = (input: string): string => {
  // Remove potentially dangerous HTML/script tags
  return input.replace(/<[^>]*>/g, '');
};

// Rate limiting helper
export class RateLimiter {
  private requests: Map<string, number[]> = new Map();
  private readonly windowMs: number;
  private readonly maxRequests: number;

  constructor(windowMs: number = 60000, maxRequests: number = 100) {
    this.windowMs = windowMs;
    this.maxRequests = maxRequests;
  }

  isAllowed(key: string): boolean {
    const now = Date.now();
    const timestamps = this.requests.get(key) || [];
    
    // Remove old timestamps
    const recentTimestamps = timestamps.filter(
      timestamp => now - timestamp < this.windowMs
    );
    
    if (recentTimestamps.length >= this.maxRequests) {
      return false;
    }
    
    recentTimestamps.push(now);
    this.requests.set(key, recentTimestamps);
    return true;
  }

  clear(key: string): void {
    this.requests.delete(key);
  }
}

// Create a singleton instance
export const rateLimiter = new RateLimiter();