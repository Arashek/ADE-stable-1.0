export interface ModelMetrics {
  responseTime: number;
  successRate: number;
  errorRate: number;
  tokenUsage: number;
  costPerRequest: number;
  historicalData: Array<{
    timestamp: string;
    responseTime: number;
    successRate: number;
    errorRate: number;
    tokenUsage: number;
    costPerRequest: number;
  }>;
}

export interface AgentMetrics {
  taskCompletionRate: number;
  errorRecoveryRate: number;
  coordinationEfficiency: number;
  resourceUsage: number;
  historicalData: Array<{
    timestamp: string;
    taskCompletionRate: number;
    errorRecoveryRate: number;
    coordinationEfficiency: number;
    resourceUsage: number;
  }>;
}

export interface SystemMetrics {
  apiLatency: number;
  queueLength: number;
  resourceUtilization: number;
  costTracking: number;
  historicalData: Array<{
    timestamp: string;
    apiLatency: number;
    queueLength: number;
    resourceUtilization: number;
    costTracking: number;
  }>;
}

export interface QualityMetrics {
  codeQualityScore: number;
  testCoverage: number;
  documentationCompleteness: number;
  errorPreventionRate: number;
  historicalData: Array<{
    timestamp: string;
    codeQualityScore: number;
    testCoverage: number;
    documentationCompleteness: number;
    errorPreventionRate: number;
  }>;
}

export interface PerformanceMetrics {
  model: ModelMetrics;
  agent: AgentMetrics;
  system: SystemMetrics;
  quality: QualityMetrics;
}

export interface HistoricalData {
  model: ModelMetrics['historicalData'];
  agent: AgentMetrics['historicalData'];
  system: SystemMetrics['historicalData'];
  quality: QualityMetrics['historicalData'];
} 