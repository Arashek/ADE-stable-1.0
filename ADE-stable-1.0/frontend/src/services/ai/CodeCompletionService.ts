import { cache } from '../../utils/cache';
import { performanceMonitor } from '../../utils/performance';
import { errorHandler, ErrorSeverity } from '../../utils/errorHandling';

interface CompletionContext {
  code: string;
  cursorPosition: number;
  language: string;
  filePath: string;
  projectContext?: {
    imports: string[];
    dependencies: string[];
    relatedFiles: string[];
  };
}

interface CompletionSuggestion {
  text: string;
  kind: 'function' | 'variable' | 'class' | 'interface' | 'keyword' | 'snippet';
  detail?: string;
  documentation?: string;
  insertText?: string;
  range?: {
    start: number;
    end: number;
  };
  relevance: number;
}

class CodeCompletionService {
  private static instance: CodeCompletionService;
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes
  private readonly MAX_SUGGESTIONS = 10;
  private readonly MIN_RELEVANCE = 0.5;

  private constructor() {}

  static getInstance(): CodeCompletionService {
    if (!CodeCompletionService.instance) {
      CodeCompletionService.instance = new CodeCompletionService();
    }
    return CodeCompletionService.instance;
  }

  @performanceMonitor.measure
  async getCompletions(context: CompletionContext): Promise<CompletionSuggestion[]> {
    try {
      // Check cache first
      const cacheKey = this.generateCacheKey(context);
      const cachedSuggestions = cache.get<CompletionSuggestion[]>(cacheKey);
      if (cachedSuggestions) {
        return cachedSuggestions;
      }

      // Get suggestions from AI service
      const suggestions = await this.fetchSuggestionsFromAI(context);
      
      // Filter and sort suggestions by relevance
      const filteredSuggestions = suggestions
        .filter(s => s.relevance >= this.MIN_RELEVANCE)
        .sort((a, b) => b.relevance - a.relevance)
        .slice(0, this.MAX_SUGGESTIONS);

      // Cache the results
      cache.set(cacheKey, filteredSuggestions, this.CACHE_TTL);

      return filteredSuggestions;
    } catch (error) {
      errorHandler.handleError(error as Error, ErrorSeverity.HIGH, {
        context: 'CodeCompletionService.getCompletions',
        ...context,
      });
      return [];
    }
  }

  private async fetchSuggestionsFromAI(context: CompletionContext): Promise<CompletionSuggestion[]> {
    try {
      const response = await fetch('/api/ai/completions', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(context),
      });

      if (!response.ok) {
        throw new Error(`Failed to fetch completions: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      errorHandler.handleError(error as Error, ErrorSeverity.HIGH, {
        context: 'CodeCompletionService.fetchSuggestionsFromAI',
        ...context,
      });
      return [];
    }
  }

  private generateCacheKey(context: CompletionContext): string {
    return `completion:${context.language}:${context.filePath}:${context.cursorPosition}:${context.code.slice(
      Math.max(0, context.cursorPosition - 100),
      context.cursorPosition
    )}`;
  }

  // Real-time collaboration methods
  async shareCompletionContext(context: CompletionContext): Promise<void> {
    try {
      await fetch('/api/collaboration/share-context', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(context),
      });
    } catch (error) {
      errorHandler.handleError(error as Error, ErrorSeverity.MEDIUM, {
        context: 'CodeCompletionService.shareCompletionContext',
        ...context,
      });
    }
  }

  // Language-specific analysis
  async analyzeCode(code: string, language: string): Promise<{
    complexity: number;
    dependencies: string[];
    potentialIssues: Array<{
      type: string;
      message: string;
      line: number;
      severity: 'low' | 'medium' | 'high';
    }>;
  }> {
    try {
      const response = await fetch('/api/ai/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code, language }),
      });

      if (!response.ok) {
        throw new Error(`Failed to analyze code: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      errorHandler.handleError(error as Error, ErrorSeverity.HIGH, {
        context: 'CodeCompletionService.analyzeCode',
        code,
        language,
      });
      return {
        complexity: 0,
        dependencies: [],
        potentialIssues: [],
      };
    }
  }

  // Visualization support
  async generateCodeVisualization(code: string, language: string): Promise<{
    ast: any;
    dependencies: any;
    flow: any;
  }> {
    try {
      const response = await fetch('/api/ai/visualize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ code, language }),
      });

      if (!response.ok) {
        throw new Error(`Failed to generate visualization: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      errorHandler.handleError(error as Error, ErrorSeverity.MEDIUM, {
        context: 'CodeCompletionService.generateCodeVisualization',
        code,
        language,
      });
      return {
        ast: null,
        dependencies: null,
        flow: null,
      };
    }
  }
}

// Create a singleton instance
export const codeCompletionService = CodeCompletionService.getInstance();

// Example usage:
/*
const context: CompletionContext = {
  code: 'function calculateTotal(items) {\n  return items.reduce((sum, item) => sum + item.price, 0);\n}',
  cursorPosition: 45,
  language: 'typescript',
  filePath: 'src/utils/calculations.ts',
  projectContext: {
    imports: ['import { Item } from "./types";'],
    dependencies: ['lodash'],
    relatedFiles: ['src/types.ts'],
  },
};

const suggestions = await codeCompletionService.getCompletions(context);
*/ 