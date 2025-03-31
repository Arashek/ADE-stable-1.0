export interface ArchitectureSuggestion {
  id: string;
  title: string;
  description: string;
  type: 'performance' | 'security' | 'scalability' | 'maintainability';
  impact: 'high' | 'medium' | 'low';
  details: string;
  recommendations: string[];
  confidence: number;
}

export interface ArchitectureAnalysis {
  suggestions: ArchitectureSuggestion[];
  timestamp: number;
}

export class ArchitectureService {
  private static instance: ArchitectureService;
  private lastAnalysis: ArchitectureAnalysis | null = null;
  private analyzePromise: Promise<ArchitectureAnalysis> | null = null;

  private constructor() {}

  public static getInstance(): ArchitectureService {
    if (!ArchitectureService.instance) {
      ArchitectureService.instance = new ArchitectureService();
    }
    return ArchitectureService.instance;
  }

  public async analyzeCurrent(): Promise<ArchitectureAnalysis> {
    // If there's an ongoing analysis, return its promise
    if (this.analyzePromise) {
      return this.analyzePromise;
    }

    // If we have a recent analysis (less than 30 minutes old), return it
    if (this.lastAnalysis && Date.now() - this.lastAnalysis.timestamp < 30 * 60 * 1000) {
      return this.lastAnalysis;
    }

    // Start a new analysis
    this.analyzePromise = this.performAnalysis();

    try {
      const result = await this.analyzePromise;
      this.lastAnalysis = result;
      return result;
    } finally {
      this.analyzePromise = null;
    }
  }

  private async performAnalysis(): Promise<ArchitectureAnalysis> {
    try {
      const response = await fetch('/api/analyze/architecture', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to analyze architecture');
      }

      const data = await response.json();
      return {
        suggestions: data.suggestions.map((suggestion: any) => ({
          ...suggestion,
          confidence: suggestion.confidence || 0.7,
        })),
        timestamp: Date.now(),
      };
    } catch (error) {
      console.error('Error analyzing architecture:', error);
      throw error;
    }
  }

  public clearCache(): void {
    this.lastAnalysis = null;
  }
} 