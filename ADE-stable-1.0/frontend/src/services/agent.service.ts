import { APIError } from '../types/error';
import {
  GenerationType,
  ReviewType,
  TestType,
  DocumentationType,
  CodeGenerationRequest,
  CodeGenerationResponse,
  CodeReviewRequest,
  CodeReviewResponse,
  TestGenerationRequest,
  TestGenerationResponse,
  DocumentationRequest,
  DocumentationResponse,
  AgentCapabilities,
} from '../types/agent.types';
import { MonitoringService } from './monitoring.service';

export interface GenerationContext {
  project_id: string;
  language: string;
  framework?: string;
  requirements: string[];
  constraints?: string[];
  style_guide?: Record<string, any>;
  existing_code?: string;
  metadata?: Record<string, any>;
}

export interface GeneratedCode {
  id: string;
  type: GenerationType;
  content: string;
  language: string;
  file_path: string;
  dependencies?: string[];
  tests?: string[];
  documentation?: string;
  generated_at: string;
  metadata?: Record<string, any>;
}

export interface ReviewComment {
  id: string;
  line_number: number;
  type: string;
  message: string;
  suggestion?: string;
  severity: string;
  category: string;
  metadata?: Record<string, any>;
}

export interface CodeReview {
  id: string;
  project_id: string;
  file_path: string;
  review_types: ReviewType[];
  comments: ReviewComment[];
  summary: string;
  recommendations: string[];
  generated_at: string;
  metadata?: Record<string, any>;
}

export interface TestRequest {
  project_id: string;
  file_path: string;
  test_types: TestType[];
  coverage_target?: number;
  framework?: string;
  metadata?: Record<string, any>;
}

export interface TestCase {
  id: string;
  name: string;
  description: string;
  type: TestType;
  setup?: string;
  teardown?: string;
  test_code: string;
  expected_result: string;
  metadata?: Record<string, any>;
}

export interface TestSuite {
  id: string;
  project_id: string;
  file_path: string;
  test_types: TestType[];
  test_cases: TestCase[];
  coverage?: number;
  generated_at: string;
  metadata?: Record<string, any>;
}

export interface Documentation {
  id: string;
  project_id: string;
  doc_types: DocumentationType[];
  content: string;
  format: string;
  examples?: string[];
  generated_at: string;
  metadata?: Record<string, any>;
}

interface AgentContext {
  taskDescription?: string;
  progressStatus?: string;
  blockers?: string[];
  previousSolutions?: any[];
}

interface AgentSolution {
  agent: string;
  response: string;
  model: string;
  metrics: {
    latency: number;
    tokens: number;
  };
}

interface WorkflowGuidance {
  initiative_guidance: string;
  progress_assessment: string;
}

interface AgentResponse {
  workflow_guidance: WorkflowGuidance;
  agent_solutions: AgentSolution[];
  coordinator_result: string;
}

interface AgentConfig {
  name: string;
  role: string;
  model: string;
}

interface AgentList {
  solver_agents: AgentConfig[];
  workflow_agents: AgentConfig[];
  coordinator: AgentConfig;
}

class AgentServiceImpl {
  private readonly API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
  private readonly monitoring: MonitoringService;

  constructor(monitoring: MonitoringService) {
    this.monitoring = monitoring;
  }

  async processWithAgents(
    prompt: string,
    context: AgentContext = {}
  ): Promise<AgentResponse> {
    const startTime = performance.now();

    try {
      const response = await fetch(`${this.API_BASE_URL}/api/agents/process`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          context: {
            task_description: context.taskDescription || '',
            progress_status: context.progressStatus || 'Not started',
            blockers: context.blockers || [],
            previous_solutions: context.previousSolutions || [],
          },
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const latency = performance.now() - startTime;

      // Track performance metrics
      this.monitoring.trackPerformance({
        name: 'agent_processing',
        value: latency,
        tags: {
          num_agents: data.agent_solutions.length.toString(),
          prompt_length: prompt.length.toString(),
        }
      });

      return data;
    } catch (error) {
      // Track error
      this.monitoring.trackError({
        message: (error as Error).message,
        stack: (error as Error).stack,
        severity: 'error',
        tags: {
          context: 'agent_processing'
        }
      });
      throw error;
    }
  }

  async listAgents(): Promise<AgentList> {
    try {
      const response = await fetch(`${this.API_BASE_URL}/api/agents/agents`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      this.monitoring.trackError({
        message: (error as Error).message,
        stack: (error as Error).stack,
        severity: 'error',
        tags: {
          context: 'list_agents'
        }
      });
      throw error;
    }
  }

  async trackAgentMetrics(metrics: {
    agent: string;
    latency: number;
    tokens: number;
  }): Promise<void> {
    this.monitoring.trackPerformance({
      name: 'agent_metrics',
      value: metrics.latency,
      tags: {
        agent: metrics.agent,
        tokens: metrics.tokens.toString(),
      }
    });
  }
}

export const agentService = new AgentServiceImpl(MonitoringService.getInstance());

export class AgentService {
  private baseUrl: string;
  private token: string;

  constructor() {
    this.baseUrl = process.env.REACT_APP_API_URL || 'http://localhost:8000';
    this.token = localStorage.getItem('token') || '';
  }

  private async fetchWithAuth<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${this.token}`,
        ...options.headers,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'An error occurred');
    }

    return response.json();
  }

  async getCapabilities(): Promise<AgentCapabilities> {
    return this.fetchWithAuth<AgentCapabilities>('/api/agent/capabilities');
  }

  async generateCode(request: CodeGenerationRequest): Promise<CodeGenerationResponse> {
    return this.fetchWithAuth<CodeGenerationResponse>('/api/agent/generate', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getGenerationHistory(projectId: string): Promise<CodeGenerationResponse[]> {
    return this.fetchWithAuth<CodeGenerationResponse[]>(
      `/api/agent/generate/history/${projectId}`
    );
  }

  async reviewCode(request: CodeReviewRequest): Promise<CodeReviewResponse> {
    return this.fetchWithAuth<CodeReviewResponse>('/api/agent/review', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getReviews(projectId: string): Promise<CodeReviewResponse[]> {
    return this.fetchWithAuth<CodeReviewResponse[]>(
      `/api/agent/review/history/${projectId}`
    );
  }

  async generateTests(request: TestGenerationRequest): Promise<TestGenerationResponse> {
    return this.fetchWithAuth<TestGenerationResponse>('/api/agent/tests', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getTestSuites(projectId: string): Promise<TestGenerationResponse[]> {
    return this.fetchWithAuth<TestGenerationResponse[]>(
      `/api/agent/tests/history/${projectId}`
    );
  }

  async generateDocumentation(
    request: DocumentationRequest
  ): Promise<DocumentationResponse> {
    return this.fetchWithAuth<DocumentationResponse>('/api/agent/docs', {
      method: 'POST',
      body: JSON.stringify(request),
    });
  }

  async getDocumentation(projectId: string): Promise<DocumentationResponse[]> {
    return this.fetchWithAuth<DocumentationResponse[]>(
      `/api/agent/docs/history/${projectId}`
    );
  }

  async downloadGeneratedCode(id: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/agent/generate/${id}/download`, {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to download generated code');
    }

    return response.blob();
  }

  async downloadTestSuite(id: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/agent/tests/${id}/download`, {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to download test suite');
    }

    return response.blob();
  }

  async downloadDocumentation(id: string): Promise<Blob> {
    const response = await fetch(`${this.baseUrl}/api/agent/docs/${id}/download`, {
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message || 'Failed to download documentation');
    }

    return response.blob();
  }

  async cancelOperation(id: string): Promise<void> {
    await this.fetchWithAuth(`/api/agent/operations/${id}/cancel`, {
      method: 'POST',
    });
  }

  async getOperationStatus(id: string): Promise<{
    status: 'pending' | 'processing' | 'completed' | 'failed' | 'cancelled';
    progress?: number;
    error?: string;
  }> {
    return this.fetchWithAuth(`/api/agent/operations/${id}/status`);
  }
} 