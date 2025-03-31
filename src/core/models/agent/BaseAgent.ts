import { Logger } from '../logging/Logger';
import { AgentContext } from './AgentManager';

export interface RetryOptions {
  maxRetries: number;
  delayMs: number;
}

export class BaseAgent {
  protected logger: Logger;
  protected defaultRetryOptions: RetryOptions = {
    maxRetries: 3,
    delayMs: 1000
  };

  constructor(name: string) {
    this.logger = new Logger(name);
  }

  protected async validateContext(context: AgentContext): Promise<void> {
    if (!context.projectId || !context.userId || !context.conversationId) {
      throw new Error('Invalid agent context');
    }
  }

  protected async withRetry<T>(
    operation: () => Promise<T>,
    options: Partial<RetryOptions> = {}
  ): Promise<T> {
    const retryOptions = { ...this.defaultRetryOptions, ...options };
    let lastError: Error | null = null;

    for (let attempt = 1; attempt <= retryOptions.maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error as Error;
        this.logger.warn(`Attempt ${attempt} failed`, error);

        if (attempt < retryOptions.maxRetries) {
          await new Promise(resolve => setTimeout(resolve, retryOptions.delayMs * attempt));
          continue;
        }
      }
    }

    throw lastError || new Error('Operation failed after all retry attempts');
  }

  protected handleApiError(error: any): never {
    if (error.response) {
      // API error with response
      const status = error.response.status;
      const message = error.response.data?.error?.message || error.message;

      switch (status) {
        case 401:
          throw new Error('Authentication failed. Please check your API key.');
        case 403:
          throw new Error('Access denied. Please check your permissions.');
        case 429:
          throw new Error('Rate limit exceeded. Please try again later.');
        case 500:
          throw new Error('Server error. Please try again later.');
        default:
          throw new Error(`API error: ${message}`);
      }
    } else if (error.request) {
      // Network error
      throw new Error('Network error. Please check your connection.');
    } else {
      // Other error
      throw error;
    }
  }
} 