export interface ModuleDependency {
  path: string;
  name: string;
  type: 'component' | 'service' | 'util' | 'model' | 'test';
  complexity: number;
  dependencies: string[];
}

export interface DependencyAnalysis {
  modules: ModuleDependency[];
  timestamp: number;
}

export class DependencyService {
  private static instance: DependencyService;
  private lastAnalysis: DependencyAnalysis | null = null;
  private analyzePromise: Promise<DependencyAnalysis> | null = null;

  private constructor() {}

  public static getInstance(): DependencyService {
    if (!DependencyService.instance) {
      DependencyService.instance = new DependencyService();
    }
    return DependencyService.instance;
  }

  public async analyzeDependencies(): Promise<DependencyAnalysis> {
    // If there's an ongoing analysis, return its promise
    if (this.analyzePromise) {
      return this.analyzePromise;
    }

    // If we have a recent analysis (less than 5 minutes old), return it
    if (this.lastAnalysis && Date.now() - this.lastAnalysis.timestamp < 5 * 60 * 1000) {
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

  private async performAnalysis(): Promise<DependencyAnalysis> {
    try {
      const response = await fetch('/api/analyze/dependencies', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        throw new Error('Failed to analyze dependencies');
      }

      const data = await response.json();
      return {
        modules: data.modules,
        timestamp: Date.now(),
      };
    } catch (error) {
      console.error('Error analyzing dependencies:', error);
      throw error;
    }
  }

  public clearCache(): void {
    this.lastAnalysis = null;
  }
} 