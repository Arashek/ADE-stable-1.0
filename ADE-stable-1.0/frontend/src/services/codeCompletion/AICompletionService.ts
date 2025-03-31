import { APIService } from '../api';
import { debounce } from 'lodash';

export interface CompletionContext {
  filePath: string;
  fileContent: string;
  cursorPosition: {
    line: number;
    column: number;
  };
  language: string;
  precedingCode: string;
  followingCode: string;
}

export interface CompletionSuggestion {
  id: string;
  text: string;
  displayText: string;
  type: 'function' | 'variable' | 'class' | 'keyword' | 'snippet' | 'import';
  documentation?: string;
  insertText: string;
  range: {
    startLine: number;
    startColumn: number;
    endLine: number;
    endColumn: number;
  };
  confidence: number;
  source: 'openai' | 'anthropic' | 'local' | 'codebase';
}

export interface CompletionResponse {
  suggestions: CompletionSuggestion[];
  metadata: {
    model: string;
    latency: number;
    tokenCount: number;
  };
}

export class AICompletionService {
  private static instance: AICompletionService;
  private api: APIService;
  private cache: Map<string, CompletionResponse>;
  private contextWindow: string[] = [];
  private maxContextLength = 1000;

  private constructor() {
    this.api = APIService.getInstance();
    this.cache = new Map();
  }

  static getInstance(): AICompletionService {
    if (!AICompletionService.instance) {
      AICompletionService.instance = new AICompletionService();
    }
    return AICompletionService.instance;
  }

  // Update context with new code
  private updateContext(code: string) {
    this.contextWindow.push(code);
    while (
      this.contextWindow.join('').length > this.maxContextLength &&
      this.contextWindow.length > 1
    ) {
      this.contextWindow.shift();
    }
  }

  // Generate cache key for completion request
  private generateCacheKey(context: CompletionContext): string {
    return `${context.filePath}:${context.cursorPosition.line}:${
      context.cursorPosition.column
    }:${context.precedingCode.slice(-100)}`;
  }

  // Debounced completion request
  private requestCompletion = debounce(
    async (
      context: CompletionContext,
      callback: (response: CompletionResponse) => void
    ) => {
      try {
        const cacheKey = this.generateCacheKey(context);
        const cached = this.cache.get(cacheKey);
        if (cached) {
          callback(cached);
          return;
        }

        const response = await this.api.request<CompletionResponse>({
          method: 'POST',
          url: '/api/completion/suggest',
          data: {
            ...context,
            context: this.contextWindow.join('\n'),
          },
        });

        this.cache.set(cacheKey, response);
        this.updateContext(context.precedingCode);
        callback(response);
      } catch (error) {
        console.error('Code completion request failed:', error);
        callback({
          suggestions: [],
          metadata: {
            model: 'error',
            latency: 0,
            tokenCount: 0,
          },
        });
      }
    },
    100
  );

  // Get completion suggestions
  async getCompletions(
    context: CompletionContext,
    callback: (response: CompletionResponse) => void
  ): Promise<void> {
    this.requestCompletion(context, callback);
  }

  // Clear completion cache
  clearCache(filePath?: string) {
    if (filePath) {
      for (const [key] of this.cache) {
        if (key.startsWith(filePath)) {
          this.cache.delete(key);
        }
      }
    } else {
      this.cache.clear();
    }
  }

  // Clear context window
  clearContext() {
    this.contextWindow = [];
  }

  // Get completion statistics
  getStats() {
    return {
      cacheSize: this.cache.size,
      contextLength: this.contextWindow.join('').length,
      contextChunks: this.contextWindow.length,
    };
  }
} 