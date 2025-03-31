import { APIService } from '../api';
import { WebSocketService } from '../websocket';
import { debounce } from 'lodash';

export interface CodeQualityMetrics {
  complexity: number;
  maintainability: number;
  testability: number;
  security: number;
  performance: number;
}

export interface CodeIssue {
  id: string;
  type: 'error' | 'warning' | 'info' | 'suggestion';
  message: string;
  line: number;
  column: number;
  severity: 1 | 2 | 3 | 4; // 1 = lowest, 4 = highest
  rule: string;
  fix?: {
    description: string;
    code: string;
  };
}

export interface FileAnalysis {
  metrics: CodeQualityMetrics;
  issues: CodeIssue[];
  suggestions: string[];
  aiInsights: string[];
}

export class CodeQualityService {
  private static instance: CodeQualityService;
  private api: APIService;
  private ws: WebSocketService;
  private analysisCache: Map<string, FileAnalysis>;
  private subscribers: Map<string, Set<(analysis: FileAnalysis) => void>>;

  private constructor() {
    this.api = APIService.getInstance();
    this.ws = WebSocketService.getInstance();
    this.analysisCache = new Map();
    this.subscribers = new Map();
    this.setupWebSocket();
  }

  static getInstance(): CodeQualityService {
    if (!CodeQualityService.instance) {
      CodeQualityService.instance = new CodeQualityService();
    }
    return CodeQualityService.instance;
  }

  private setupWebSocket() {
    this.ws.connect('code-analysis', {
      onMessage: (data) => {
        if (data.type === 'analysis-update') {
          this.updateAnalysis(data.filePath, data.analysis);
        }
      },
      onError: (error) => {
        console.error('Code analysis WebSocket error:', error);
      }
    });
  }

  private updateAnalysis(filePath: string, analysis: FileAnalysis) {
    this.analysisCache.set(filePath, analysis);
    const subscribers = this.subscribers.get(filePath);
    if (subscribers) {
      subscribers.forEach(callback => callback(analysis));
    }
  }

  // Debounced analysis request to prevent overwhelming the server
  private requestAnalysis = debounce(async (filePath: string, content: string) => {
    try {
      const analysis = await this.api.request<FileAnalysis>({
        method: 'POST',
        url: '/api/code-analysis/analyze',
        data: {
          filePath,
          content,
          options: {
            metrics: true,
            suggestions: true,
            aiInsights: true
          }
        }
      });
      this.updateAnalysis(filePath, analysis);
    } catch (error) {
      console.error('Code analysis request failed:', error);
    }
  }, 500);

  // Subscribe to analysis updates for a file
  subscribeToAnalysis(
    filePath: string,
    callback: (analysis: FileAnalysis) => void
  ): () => void {
    if (!this.subscribers.has(filePath)) {
      this.subscribers.set(filePath, new Set());
    }
    this.subscribers.get(filePath)!.add(callback);

    // Return unsubscribe function
    return () => {
      const subscribers = this.subscribers.get(filePath);
      if (subscribers) {
        subscribers.delete(callback);
        if (subscribers.size === 0) {
          this.subscribers.delete(filePath);
        }
      }
    };
  }

  // Request analysis for a file
  analyzeCode(filePath: string, content: string) {
    this.requestAnalysis(filePath, content);
  }

  // Get cached analysis for a file
  getCachedAnalysis(filePath: string): FileAnalysis | undefined {
    return this.analysisCache.get(filePath);
  }

  // Clear analysis cache for a file
  clearCache(filePath?: string) {
    if (filePath) {
      this.analysisCache.delete(filePath);
    } else {
      this.analysisCache.clear();
    }
  }
} 