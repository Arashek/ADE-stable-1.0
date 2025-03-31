export interface CodeSnippet {
  content: string;
  language: string;
  file: string;
}

export interface AnalysisSuggestion {
  type: 'improvement' | 'warning' | 'error';
  message: string;
  line: number;
  confidence: number;
}

export interface CodeMetrics {
  complexity: number;
  maintainability: number;
  testability: number;
}

export interface AnalysisResult {
  suggestions: AnalysisSuggestion[];
  metrics: CodeMetrics;
}

export class AICodeAnalysisService {
  private static instance: AICodeAnalysisService;
  private cache: Map<string, Promise<AnalysisResult>> = new Map();

  private constructor() {}

  public static getInstance(): AICodeAnalysisService {
    if (!AICodeAnalysisService.instance) {
      AICodeAnalysisService.instance = new AICodeAnalysisService();
    }
    return AICodeAnalysisService.instance;
  }

  public async analyzeCode(snippet: CodeSnippet): Promise<AnalysisResult> {
    const cacheKey = this.generateCacheKey(snippet);
    
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }

    const analysisPromise = this.performAnalysis(snippet);
    this.cache.set(cacheKey, analysisPromise);
    
    return analysisPromise;
  }

  private async performAnalysis(snippet: CodeSnippet): Promise<AnalysisResult> {
    try {
      const response = await fetch('/api/ai/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(snippet),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze code');
      }

      const result = await response.json();
      return {
        suggestions: result.suggestions || [],
        metrics: {
          complexity: result.metrics?.complexity || 0,
          maintainability: result.metrics?.maintainability || 0,
          testability: result.metrics?.testability || 0,
        },
      };
    } catch (error) {
      this.cache.clear(); // Clear cache on error
      throw error;
    }
  }

  public generateCacheKey(snippet: CodeSnippet): string {
    return `${snippet.file}:${snippet.language}:${snippet.content}`;
  }

  public clearCache(): void {
    this.cache.clear();
  }
} 