import { performanceMonitor } from './performance';
import { createSecureFetch } from './security';

interface ApiError extends Error {
  statusCode?: number;
  details?: any;
}

interface ApiResponse<T> {
  data: T;
  metadata?: {
    timestamp: string;
    requestId: string;
  };
}

interface ApiConfig {
  baseUrl: string;
  apiKey: string;
  apiSecret: string;
  timeout?: number;
}

export class ApiService {
  private readonly secureFetch: ReturnType<typeof createSecureFetch>;
  private readonly baseUrl: string;
  private readonly timeout: number;

  constructor(config: ApiConfig) {
    this.baseUrl = config.baseUrl;
    this.timeout = config.timeout || 30000;
    this.secureFetch = createSecureFetch(config.apiKey, config.apiSecret);
  }

  private async handleRequest<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const startTime = performance.now();
    const url = `${this.baseUrl}${endpoint}`;

    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), this.timeout);

      const response = await this.secureFetch(url, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      const duration = performance.now() - startTime;
      performanceMonitor.recordMetric(`api-${endpoint}`, duration);

      if (!response.ok) {
        const error: ApiError = new Error('API request failed');
        error.statusCode = response.status;
        try {
          error.details = await response.json();
        } catch {
          error.details = await response.text();
        }
        performanceMonitor.recordMetric(`api-error-${response.status}`, 1);
        throw error;
      }

      const data = await response.json();
      return data as ApiResponse<T>;
    } catch (error) {
      if (error.name === 'AbortError') {
        performanceMonitor.recordMetric('api-timeout', 1);
        throw new Error(`Request timeout after ${this.timeout}ms`);
      }
      throw error;
    }
  }

  // Project endpoints
  async getProject(id: string) {
    return this.handleRequest(`/api/projects/${id}`);
  }

  async createProject(data: any) {
    return this.handleRequest('/api/projects', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  // Code generation endpoints
  async generateCode(data: any) {
    return this.handleRequest('/api/code/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getGenerationHistory(projectId: string) {
    return this.handleRequest(`/api/code/history/${projectId}`);
  }

  // Code review endpoints
  async reviewCode(data: any) {
    return this.handleRequest('/api/code/review', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getReviews(projectId: string) {
    return this.handleRequest(`/api/code/reviews/${projectId}`);
  }

  // Test generation endpoints
  async generateTests(data: any) {
    return this.handleRequest('/api/tests/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getTestSuites(projectId: string) {
    return this.handleRequest(`/api/tests/${projectId}`);
  }

  // Documentation endpoints
  async generateDocumentation(data: any) {
    return this.handleRequest('/api/docs/generate', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async getDocumentation(projectId: string) {
    return this.handleRequest(`/api/docs/${projectId}`);
  }

  // Collaboration endpoints
  async getCollaborators(projectId: string) {
    return this.handleRequest(`/api/projects/${projectId}/collaborators`);
  }

  async addCollaborator(projectId: string, userId: string, role: string) {
    return this.handleRequest(`/api/projects/${projectId}/collaborators`, {
      method: 'POST',
      body: JSON.stringify({ userId, role }),
    });
  }

  // Real-time endpoints
  async subscribeToChanges(projectId: string) {
    return this.handleRequest(`/api/projects/${projectId}/subscribe`, {
      method: 'POST',
    });
  }

  async unsubscribeFromChanges(projectId: string) {
    return this.handleRequest(`/api/projects/${projectId}/unsubscribe`, {
      method: 'POST',
    });
  }

  // Cache management
  async invalidateCache(key: string) {
    return this.handleRequest('/api/cache/invalidate', {
      method: 'POST',
      body: JSON.stringify({ key }),
    });
  }
} 