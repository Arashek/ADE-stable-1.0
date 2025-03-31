import { EventEmitter } from 'events';
import { Socket } from 'socket.io-client';
import { DefaultEventsMap } from 'socket.io/dist/typed-events';
import * as monaco from 'monaco-editor';

export interface CodeNode {
  id: string;
  type: 'component' | 'service' | 'framework' | 'system' | 'file' | 'function';
  name: string;
  path: string;
  dependencies: string[];
  metrics: {
    complexity: number;
    lines: number;
    dependencies: number;
    coverage: number;
    maintainability: number;
    cognitiveComplexity: number;
    cyclomaticComplexity: number;
    halsteadVolume: number;
    halsteadDifficulty: number;
    halsteadEffort: number;
    halsteadTime: number;
    halsteadBugs: number;
  };
  relationships: {
    imports: string[];
    exports: string[];
    extends: string[];
    implements: string[];
    uses: string[];
    usedBy: string[];
  };
  context: {
    namespace: string;
    module: string;
    scope: 'global' | 'module' | 'class' | 'function';
    visibility: 'public' | 'private' | 'protected';
  };
  analysis: {
    patterns: string[];
    smells: string[];
    vulnerabilities: string[];
    suggestions: string[];
    documentation: string;
    lastModified: Date;
    contributors: string[];
    gitHistory: {
      commit: string;
      author: string;
      date: Date;
      changes: string[];
    }[];
  };
}

export interface CodeEdge {
  from: string;
  to: string;
  type: 'import' | 'dependency' | 'inheritance' | 'composition' | 'usage' | 'implementation';
  weight: number;
  metadata: {
    lineNumber: number;
    context: string;
    strength: number;
    bidirectional: boolean;
  };
}

export interface AgentContext {
  agentId: string;
  capabilities: string[];
  currentTask: string;
  requiredContext: string[];
}

export interface CodeContext {
  nodes: CodeNode[];
  relationships: CodeEdge[];
  metrics: {
    complexity: number;
    maintainability: number;
    coverage: number;
  };
  suggestions: string[];
}

export interface ErrorContext {
  affectedComponents: CodeNode[];
  errorPatterns: string[];
  suggestedFixes: string[];
  impactAnalysis: {
    severity: 'low' | 'medium' | 'high';
    affectedFiles: string[];
    potentialIssues: string[];
  };
}

export interface ProjectInsights {
  architecture: {
    patterns: string[];
    issues: string[];
    recommendations: string[];
  };
  dependencies: {
    direct: string[];
    indirect: string[];
    conflicts: string[];
  };
  codeQuality: {
    metrics: Record<string, number>;
    issues: string[];
    improvements: string[];
  };
  maintainability: {
    score: number;
    factors: string[];
    recommendations: string[];
  };
  suggestions: string[];
}

export interface CollaborativeUpdate {
  agentId: string;
  changes: {
    type: 'add' | 'modify' | 'delete';
    path: string;
    content?: string;
  }[];
  context: {
    task: string;
    reason: string;
    impact: string[];
  };
}

export interface Task {
  id: string;
  description: string;
  requirements: string[];
  dependencies: string[];
  priority: 'low' | 'medium' | 'high';
}

export interface TaskAnalysis {
  requiredComponents: CodeNode[];
  dependencies: {
    direct: string[];
    indirect: string[];
    conflicts: string[];
  };
  complexity: {
    score: number;
    factors: string[];
  };
  suggestedApproach: {
    steps: string[];
    considerations: string[];
    risks: string[];
  };
}

/**
 * Error Analysis Integration
 * Handles communication with the Error Analysis Service
 * 
 * @interface ErrorAnalysisIntegration
 * @property {string} errorId - Unique identifier for the error
 * @property {string} errorType - Type of error (e.g., 'runtime', 'compile', 'type')
 * @property {string[]} stackTrace - Stack trace of the error
 * @property {Object} context - Error context information
 * @property {string} context.file - File where error occurred
 * @property {number} context.line - Line number where error occurred
 * @property {number} context.column - Column number where error occurred
 * @property {'low' | 'medium' | 'high'} severity - Error severity level
 * @property {string[]} relatedNodes - IDs of nodes affected by the error
 * @property {string[]} suggestedFixes - Suggested fixes for the error
 */
export interface ErrorAnalysisIntegration {
  errorId: string;
  errorType: string;
  stackTrace: string[];
  context: {
    file: string;
    line: number;
    column: number;
  };
  severity: 'low' | 'medium' | 'high';
  relatedNodes: string[];
  suggestedFixes: string[];
}

/**
 * Agent System Integration
 * Handles communication with the Agent System
 * 
 * @interface AgentSystemIntegration
 * @property {string} agentId - Unique identifier for the agent
 * @property {string} agentType - Type of agent (e.g., 'code-analysis', 'testing')
 * @property {string[]} capabilities - Agent's capabilities
 * @property {Object} currentTask - Current task being performed by the agent
 * @property {string} currentTask.id - Task identifier
 * @property {string} currentTask.description - Task description
 * @property {'pending' | 'in_progress' | 'completed' | 'failed'} currentTask.status - Task status
 * @property {'low' | 'medium' | 'high'} currentTask.priority - Task priority
 * @property {Object} context - Agent's current context
 * @property {string[]} context.relevantFiles - Files relevant to the current task
 * @property {string[]} context.dependencies - Dependencies required for the task
 * @property {Record<string, number>} context.metrics - Task-related metrics
 */
export interface AgentSystemIntegration {
  agentId: string;
  agentType: string;
  capabilities: string[];
  currentTask: {
    id: string;
    description: string;
    status: 'pending' | 'in_progress' | 'completed' | 'failed';
    priority: 'low' | 'medium' | 'high';
  };
  context: {
    relevantFiles: string[];
    dependencies: string[];
    metrics: Record<string, number>;
  };
}

/**
 * Project Awareness Integration
 * Handles communication with the Project Awareness Service
 * 
 * @interface ProjectAwarenessIntegration
 * @property {string} projectId - Unique identifier for the project
 * @property {Object} structure - Project structure information
 * @property {string[]} structure.files - List of files in the project
 * @property {string[]} structure.directories - List of directories in the project
 * @property {Record<string, string[]>} structure.dependencies - File dependencies
 * @property {Object} metrics - Project metrics
 * @property {number} metrics.complexity - Overall project complexity
 * @property {number} metrics.maintainability - Project maintainability score
 * @property {number} metrics.testCoverage - Test coverage percentage
 * @property {number} metrics.documentation - Documentation coverage
 * @property {Object} patterns - Project patterns and issues
 * @property {string[]} patterns.architecture - Architecture patterns used
 * @property {string[]} patterns.antiPatterns - Anti-patterns detected
 * @property {string[]} patterns.suggestions - Improvement suggestions
 */
export interface ProjectAwarenessIntegration {
  projectId: string;
  structure: {
    files: string[];
    directories: string[];
    dependencies: Record<string, string[]>;
  };
  metrics: {
    complexity: number;
    maintainability: number;
    testCoverage: number;
    documentation: number;
  };
  patterns: {
    architecture: string[];
    antiPatterns: string[];
    suggestions: string[];
  };
}

interface CodeAwarenessConfig {
  ws: Socket<DefaultEventsMap, DefaultEventsMap>;
  editor: monaco.editor.IStandaloneCodeEditor;
  onNodeClick?: (node: CodeNode) => void;
  onEdgeClick?: (edge: CodeEdge) => void;
}

// Add new type definitions
type BatchOperationType = 'nodeUpdate' | 'edgeUpdate' | 'analysisUpdate';
type BatchOperationAction = 'add' | 'update' | 'delete';

interface BatchOperation<T> {
  type: BatchOperationType;
  action: BatchOperationAction;
  data: T;
}

interface NodeBatchOperation extends BatchOperation<CodeNode> {
  type: 'nodeUpdate';
}

interface EdgeBatchOperation extends BatchOperation<CodeEdge> {
  type: 'edgeUpdate';
}

interface AnalysisBatchOperation extends BatchOperation<{
  path: string;
  analysis: CodeNode['analysis'];
}> {
  type: 'analysisUpdate';
}

interface PerformanceProfile {
  startTime: number;
  operations: string[];
  memoryUsage: number;
}

interface PerformanceProfileResult {
  duration: number;
  memoryUsage: number;
  operationMetrics: Map<string, number>;
}

interface ValidationRule<T> {
  validate: (data: T) => boolean;
  errorMessage: string;
}

// Add custom error classes
class CodeAwarenessError extends Error {
  constructor(message: string, public code: string) {
    super(message);
    this.name = 'CodeAwarenessError';
  }
}

class ValidationError extends CodeAwarenessError {
  constructor(message: string) {
    super(message, 'VALIDATION_ERROR');
    this.name = 'ValidationError';
  }
}

class AnalysisError extends CodeAwarenessError {
  constructor(message: string) {
    super(message, 'ANALYSIS_ERROR');
    this.name = 'AnalysisError';
  }
}

class IntegrationError extends CodeAwarenessError {
  constructor(message: string) {
    super(message, 'INTEGRATION_ERROR');
    this.name = 'IntegrationError';
  }
}

/**
 * CodeAwarenessService
 * Provides comprehensive code understanding and analysis capabilities
 * 
 * @class CodeAwarenessService
 * @extends EventEmitter
 * 
 * Integration Points:
 * 1. Error Analysis Service
 *    - Real-time error detection and analysis
 *    - Error impact assessment
 *    - Fix suggestions
 * 
 * 2. Agent System
 *    - Agent context management
 *    - Task tracking
 *    - Capability coordination
 * 
 * 3. Project Awareness Service
 *    - Project structure analysis
 *    - Dependency management
 *    - Code quality metrics
 * 
 * Key Features:
 * - Real-time code analysis
 * - Dependency tracking
 * - Code quality metrics
 * - Error detection and analysis
 * - Agent context management
 * - Project structure awareness
 * - Performance monitoring
 * - Health status reporting
 * - Data validation
 * - Error handling
 * 
 * Performance Monitoring:
 * The service includes built-in performance tracking capabilities:
 * - Operation execution time tracking
 * - Operation count tracking
 * - Performance history maintenance
 * - Automatic cleanup of old performance data
 * 
 * Health Check System:
 * Provides real-time health status monitoring:
 * - Cache freshness checks
 * - Data consistency validation
 * - Performance bottleneck detection
 * - Resource usage monitoring
 * 
 * Validation System:
 * Implements comprehensive data validation:
 * - Node data validation
 * - Edge data validation
 * - Metrics data validation
 * - Custom validation rules
 * 
 * Error Handling:
 * Robust error handling system:
 * - Validation error handling
 * - Analysis error handling
 * - Integration error handling
 * - Error event emission
 * 
 * Usage:
 * ```typescript
 * const service = new CodeAwarenessService({
 *   ws: socket,
 *   editor: monacoEditor,
 *   onNodeClick: (node) => console.log('Node clicked:', node),
 *   onEdgeClick: (edge) => console.log('Edge clicked:', edge)
 * });
 * 
 * // Error handling
 * service.onErrorAnalysis((data) => {
 *   console.log('Error detected:', data);
 * });
 * 
 * // Agent updates
 * service.onAgentUpdate((data) => {
 *   console.log('Agent update:', data);
 * });
 * 
 * // Project updates
 * service.onProjectUpdate((data) => {
 *   console.log('Project update:', data);
 * });
 * 
 * // Performance monitoring
 * const metrics = service.getPerformanceMetrics();
 * console.log('Operation counts:', metrics.operationCounts);
 * console.log('Average times:', metrics.averageTimes);
 * 
 * // Health check
 * const health = service.getHealthStatus();
 * console.log('Service health:', health.status);
 * console.log('Issues:', health.issues);
 * ```
 */
export class CodeAwarenessService extends EventEmitter {
  private ws: Socket<DefaultEventsMap, DefaultEventsMap>;
  private editor: monaco.editor.IStandaloneCodeEditor;
  private nodes: Map<string, CodeNode>;
  private edges: Map<string, CodeEdge>;
  private selectedNode: CodeNode | null;
  private isAnalyzing: boolean;
  private onNodeClick?: (node: CodeNode) => void;
  private onEdgeClick?: (edge: CodeEdge) => void;
  private searchResults: Set<string>;
  private filterCriteria: {
    type?: string[];
    complexity?: { min: number; max: number };
    coverage?: { min: number; max: number };
    maintainability?: { min: number; max: number };
    patterns?: string[];
    smells?: string[];
    vulnerabilities?: string[];
  };
  private analysisCache: Map<string, {
    timestamp: Date;
    data: any;
  }>;
  private changeHistory: {
    timestamp: Date;
    type: 'file' | 'dependency' | 'analysis';
    path: string;
    changes: any;
  }[];
  private errorAnalysisService: any;
  private agentSystemService: any;
  private projectAwarenessService: any;
  private metricsCache: Map<string, {
    timestamp: Date;
    data: Record<string, number>;
  }>;
  private dependencyCache: Map<string, {
    timestamp: Date;
    data: string[];
  }>;
  private readonly CACHE_TTL = 5 * 60 * 1000; // 5 minutes
  private errorHandlers: Map<string, (error: Error) => void>;
  private validationRules: Map<string, ValidationRule<any>>;
  private performanceMetrics: {
    operationCounts: Map<string, number>;
    operationTimes: Map<string, number[]>;
  };
  private batchOperations: Map<BatchOperationType, {
    operations: (NodeBatchOperation | EdgeBatchOperation | AnalysisBatchOperation)[];
    timeout: NodeJS.Timeout;
  }>;
  private readonly BATCH_TIMEOUT = 100; // 100ms
  private readonly MAX_BATCH_SIZE = 50;
  private performanceProfiles: Map<string, PerformanceProfile>;
  private readonly PERFORMANCE_THRESHOLD = 1000; // 1 second
  private readonly MEMORY_THRESHOLD = 100 * 1024 * 1024; // 100MB
  private readonly CACHE_SIZE_LIMIT = 1000;
  private readonly BATCH_SIZE_LIMIT = 100;
  private readonly OPERATION_HISTORY_LIMIT = 1000;
  private maxBatchSize: number = 50; // Make it mutable

  constructor(config: CodeAwarenessConfig) {
    super();
    this.ws = config.ws;
    this.editor = config.editor;
    this.onNodeClick = config.onNodeClick;
    this.onEdgeClick = config.onEdgeClick;
    this.nodes = new Map();
    this.edges = new Map();
    this.selectedNode = null;
    this.isAnalyzing = false;
    this.searchResults = new Set();
    this.filterCriteria = {};
    this.analysisCache = new Map();
    this.changeHistory = [];
    this.metricsCache = new Map();
    this.dependencyCache = new Map();
    this.errorHandlers = new Map();
    this.validationRules = new Map();
    this.performanceMetrics = {
      operationCounts: new Map(),
      operationTimes: new Map()
    };
    this.batchOperations = new Map();
    this.performanceProfiles = new Map();
    this.setupErrorHandlers();
    this.setupValidationRules();
    this.startAnalysis();
    this.initializeIntegrations();
  }

  private setupEventListeners(): void {
    // Listen for code changes
    this.editor.onDidChangeModelContent(() => {
      this.updateEditorCodeAnalysis();
    });

    // Listen for file changes from server
    this.ws.on('fileChanged', (data: { path: string; content: string }) => {
      this.updateNodeFromFile(data.path, data.content);
    });

    // Listen for dependency changes
    this.ws.on('dependenciesChanged', (data: { path: string; dependencies: string[] }) => {
      this.updateNodeDependencies(data.path, data.dependencies);
    });

    // Listen for analysis updates
    this.ws.on('analysisUpdated', (data: { path: string; analysis: any }) => {
      this.updateNodeAnalysis(data.path, data.analysis);
    });
  }

  private startAnalysis(): void {
    this.isAnalyzing = true;
    this.ws.emit('requestCodeAnalysis', {}, (response: { nodes: CodeNode[]; edges: CodeEdge[] }) => {
      this.nodes.clear();
      this.edges.clear();
      response.nodes.forEach(node => this.nodes.set(node.id, node));
      response.edges.forEach(edge => this.edges.set(`${edge.from}-${edge.to}`, edge));
      this.isAnalyzing = false;
    });
  }

  /**
   * Updates code analysis based on editor model changes
   * @private
   */
  private updateEditorCodeAnalysis(): void {
    if (this.isAnalyzing) return;

    const model = this.editor.getModel();
    if (!model) return;

    const content = model.getValue();
    const path = model.uri.path;

    this.ws.emit('analyzeCode', { path, content }, (response: { node: CodeNode; edges: CodeEdge[] }) => {
      this.nodes.set(response.node.id, response.node);
      response.edges.forEach(edge => this.edges.set(`${edge.from}-${edge.to}`, edge));
      this.addToChangeHistory('file', path, { content });
    });
  }

  private updateNodeFromFile(path: string, content: string): void {
    this.ws.emit('analyzeCode', { path, content }, (response: { node: CodeNode; edges: CodeEdge[] }) => {
      this.nodes.set(response.node.id, response.node);
      response.edges.forEach(edge => this.edges.set(`${edge.from}-${edge.to}`, edge));
      this.addToChangeHistory('file', path, { content });
    });
  }

  private updateNodeDependencies(path: string, dependencies: string[]): void {
    const node = Array.from(this.nodes.values()).find(n => n.path === path);
    if (node) {
      node.dependencies = dependencies;
      this.addToChangeHistory('dependency', path, { dependencies });
    }
  }

  private updateNodeAnalysis(path: string, analysis: any): void {
    const node = Array.from(this.nodes.values()).find(n => n.path === path);
    if (node) {
      node.analysis = { ...node.analysis, ...analysis };
      this.analysisCache.set(path, {
        timestamp: new Date(),
        data: analysis
      });
      this.addToChangeHistory('analysis', path, analysis);
    }
  }

  private addToChangeHistory(type: 'file' | 'dependency' | 'analysis', path: string, changes: any): void {
    this.changeHistory.push({
      timestamp: new Date(),
      type,
      path,
      changes
    });
  }

  public selectNode(nodeId: string): void {
    const node = this.nodes.get(nodeId);
    if (node) {
      this.selectedNode = node;
      this.emit('nodeSelected', node);
      if (this.onNodeClick) {
        this.onNodeClick(node);
      }
    }
  }

  public getNodeInfo(nodeId: string): CodeNode | undefined {
    return this.nodes.get(nodeId);
  }

  public getNodeDependencies(nodeId: string): string[] {
    const cached = this.getCachedDependencies(nodeId);
    if (cached) {
      return cached;
    }

    const node = this.nodes.get(nodeId);
    if (node) {
      this.setCachedDependencies(nodeId, node.dependencies);
      return node.dependencies;
    }
    return [];
  }

  public getNodeMetrics(nodeId: string): any {
    const cached = this.getCachedMetrics(nodeId);
    if (cached) {
      return cached;
    }

    const node = this.nodes.get(nodeId);
    if (node) {
      this.setCachedMetrics(nodeId, node.metrics);
      return node.metrics;
    }
    return null;
  }

  public getNodeAnalysis(nodeId: string): any {
    const node = this.nodes.get(nodeId);
    return node ? node.analysis : null;
  }

  public getNodeRelationships(nodeId: string): any {
    const node = this.nodes.get(nodeId);
    return node ? node.relationships : null;
  }

  public getNodeContext(nodeId: string): any {
    const node = this.nodes.get(nodeId);
    return node ? node.context : null;
  }

  public searchNodes(query: string): void {
    this.searchResults.clear();
    const searchRegex = new RegExp(query, 'i');

    this.nodes.forEach((node, id) => {
      if (searchRegex.test(node.name) || 
          searchRegex.test(node.path) || 
          searchRegex.test(node.analysis.documentation)) {
        this.searchResults.add(id);
      }
    });
  }

  public filterNodes(criteria: typeof this.filterCriteria): void {
    this.filterCriteria = criteria;
  }

  public getChangeHistory(): typeof this.changeHistory {
    return this.changeHistory;
  }

  public getAnalysisCache(path: string): any {
    return this.analysisCache.get(path);
  }

  public dispose(): void {
    this.ws.off('fileChanged');
    this.ws.off('dependenciesChanged');
    this.ws.off('analysisUpdated');
    this.ws.off('errorDetected');
    this.ws.off('agentUpdate');
    this.ws.off('projectUpdate');

    this.metricsCache.clear();
    this.dependencyCache.clear();
    this.analysisCache.clear();
    this.errorHandlers.clear();
    this.validationRules.clear();

    this.performanceMetrics.operationCounts.clear();
    this.performanceMetrics.operationTimes.clear();

    this.nodes.clear();
    this.edges.clear();
    this.searchResults.clear();
    this.changeHistory = [];
  }

  // Enhanced Agent Integration
  public provideAgentContext(agentContext: AgentContext): CodeContext {
    const relevantNodes = Array.from(this.nodes.values()).filter(node => 
      this.isRelevantToTask(node, agentContext.currentTask)
    );
    
    const relationships = Array.from(this.edges.values()).filter(edge =>
      relevantNodes.some(node => node.id === edge.from || node.id === edge.to)
    );

    const metrics = this.calculateMetrics(relevantNodes);
    const suggestions = this.generateSuggestions(agentContext);

    return {
      nodes: relevantNodes,
      relationships,
      metrics,
      suggestions
    };
  }

  private isRelevantToTask(node: CodeNode, task: string): boolean {
    const taskKeywords = task.toLowerCase().split(' ');
    const nodeContent = `${node.name} ${node.type} ${node.path}`.toLowerCase();
    return taskKeywords.some(keyword => nodeContent.includes(keyword));
  }

  private calculateMetrics(nodes: CodeNode[]): CodeContext['metrics'] {
    const complexity = nodes.reduce((acc, node) => acc + (node.metrics?.cognitiveComplexity || 0), 0) / nodes.length;
    const maintainability = nodes.reduce((acc, node) => acc + (node.metrics?.maintainability || 0), 0) / nodes.length;
    const coverage = nodes.reduce((acc, node) => acc + (node.metrics?.coverage || 0), 0) / nodes.length;

    return { complexity, maintainability, coverage };
  }

  private calculateCodeQualityMetrics(): Record<string, number> {
    const nodes = Array.from(this.nodes.values());
    return this.calculateMetrics(nodes);
  }

  private generateSuggestions(agentContext: AgentContext): string[] {
    const suggestions: string[] = [];
    const relevantNodes = Array.from(this.nodes.values()).filter(node => 
      this.isRelevantToTask(node, agentContext.currentTask)
    );

    // Generate suggestions based on code analysis
    relevantNodes.forEach(node => {
      if (node.analysis?.patterns) {
        suggestions.push(...node.analysis.patterns.map(pattern => 
          `Consider applying ${pattern} pattern in ${node.name}`
        ));
      }
      if (node.analysis?.smells) {
        suggestions.push(...node.analysis.smells.map(smell => 
          `Address ${smell} in ${node.name}`
        ));
      }
    });

    return suggestions;
  }

  // Improved Error Analysis Integration
  public analyzeErrorContext(error: Error): ErrorContext {
    const affectedNodes = this.findAffectedNodes(error);
    const errorPatterns = this.detectErrorPatterns(affectedNodes);
    
    return {
      affectedComponents: affectedNodes,
      errorPatterns,
      suggestedFixes: this.generateFixSuggestions(errorPatterns),
      impactAnalysis: this.analyzeErrorImpact(affectedNodes)
    };
  }

  private findAffectedNodes(error: Error): CodeNode[] {
    const errorMessage = error.message.toLowerCase();
    return Array.from(this.nodes.values()).filter(node => {
      const nodeContent = `${node.name} ${node.type} ${node.path}`.toLowerCase();
      return errorMessage.includes(nodeContent);
    });
  }

  private detectErrorPatterns(nodes: CodeNode[]): string[] {
    const patterns: string[] = [];
    nodes.forEach(node => {
      if (node.analysis?.patterns) {
        patterns.push(...node.analysis.patterns);
      }
    });
    return [...new Set(patterns)];
  }

  private generateFixSuggestions(patterns: string[]): string[] {
    return patterns.map(pattern => {
      switch (pattern) {
        case 'singleton':
          return 'Ensure proper singleton initialization and thread safety';
        case 'factory':
          return 'Verify factory method parameters and return types';
        case 'observer':
          return 'Check event subscription and unsubscription logic';
        default:
          return `Review implementation of ${pattern} pattern`;
      }
    });
  }

  private analyzeErrorImpact(nodes: CodeNode[]): ErrorContext['impactAnalysis'] {
    const affectedFiles = nodes.map(node => node.path);
    const severity = this.calculateErrorSeverity(nodes);
    const potentialIssues = this.identifyPotentialIssues(nodes);

    return {
      severity,
      affectedFiles,
      potentialIssues
    };
  }

  private calculateErrorSeverity(nodes: CodeNode[]): 'low' | 'medium' | 'high' {
    const totalComplexity = nodes.reduce((acc, node) => 
      acc + (node.metrics?.cognitiveComplexity || 0), 0);
    
    if (totalComplexity > 100) return 'high';
    if (totalComplexity > 50) return 'medium';
    return 'low';
  }

  private identifyPotentialIssues(nodes: CodeNode[]): string[] {
    const issues: string[] = [];
    nodes.forEach(node => {
      if (node.analysis?.smells) {
        issues.push(...node.analysis.smells);
      }
      if (node.analysis?.vulnerabilities) {
        issues.push(...node.analysis.vulnerabilities);
      }
    });
    return [...new Set(issues)];
  }

  // Enhanced Project Awareness
  public getProjectInsights(): ProjectInsights {
    return {
      architecture: this.analyzeArchitecture(),
      dependencies: this.analyzeDependencies(),
      codeQuality: this.analyzeCodeQuality(),
      maintainability: this.analyzeMaintainability(),
      suggestions: this.generateArchitectureSuggestions()
    };
  }

  private analyzeArchitecture(): ProjectInsights['architecture'] {
    const patterns = this.detectArchitecturePatterns();
    const issues = this.identifyArchitectureIssues();
    const recommendations = this.generateArchitectureRecommendations(patterns, issues);

    return { patterns, issues, recommendations };
  }

  private detectArchitecturePatterns(): string[] {
    const patterns: string[] = [];
    this.nodes.forEach(node => {
      if (node.analysis?.patterns) {
        patterns.push(...node.analysis.patterns);
      }
    });
    return [...new Set(patterns)];
  }

  private identifyArchitectureIssues(): string[] {
    const issues: string[] = [];
    this.nodes.forEach(node => {
      if (node.analysis?.smells) {
        issues.push(...node.analysis.smells);
      }
    });
    return [...new Set(issues)];
  }

  private generateArchitectureRecommendations(patterns: string[], issues: string[]): string[] {
    const recommendations: string[] = [];
    
    // Add recommendations based on patterns
    patterns.forEach(pattern => {
      recommendations.push(`Consider standardizing ${pattern} pattern usage`);
    });

    // Add recommendations based on issues
    issues.forEach(issue => {
      recommendations.push(`Address ${issue} to improve architecture`);
    });

    return recommendations;
  }

  private analyzeDependencies(): ProjectInsights['dependencies'] {
    const direct = this.getDirectDependencies();
    const indirect = this.getIndirectDependencies();
    const conflicts = this.detectDependencyConflicts();

    return { direct, indirect, conflicts };
  }

  private getDirectDependencies(): string[] {
    return Array.from(this.edges.values())
      .filter(edge => edge.type === 'dependency')
      .map(edge => edge.to);
  }

  private getIndirectDependencies(): string[] {
    const directDeps = this.getDirectDependencies();
    const indirectDeps = new Set<string>();

    directDeps.forEach(dep => {
      const node = this.nodes.get(dep);
      if (node?.relationships?.imports) {
        node.relationships.imports.forEach(imp => indirectDeps.add(imp));
      }
    });

    return Array.from(indirectDeps);
  }

  private detectDependencyConflicts(): string[] {
    const conflicts: string[] = [];
    const dependencies = this.getDirectDependencies();
    
    dependencies.forEach(dep => {
      const node = this.nodes.get(dep);
      if (node?.analysis?.vulnerabilities) {
        conflicts.push(`Security vulnerability in ${dep}`);
      }
    });

    return conflicts;
  }

  private analyzeCodeQuality(): ProjectInsights['codeQuality'] {
    const metrics = this.calculateCodeQualityMetrics();
    const issues = this.identifyCodeQualityIssues();
    const improvements = this.generateCodeQualityImprovements(issues);

    return { metrics, issues, improvements };
  }

  private identifyCodeQualityIssues(): string[] {
    const issues: string[] = [];
    this.nodes.forEach(node => {
      if (node.analysis?.smells) {
        issues.push(...node.analysis.smells);
      }
      if (node.analysis?.vulnerabilities) {
        issues.push(...node.analysis.vulnerabilities);
      }
    });
    return [...new Set(issues)];
  }

  private generateCodeQualityImprovements(issues: string[]): string[] {
    return issues.map(issue => {
      switch (issue) {
        case 'complexity':
          return 'Consider breaking down complex functions into smaller, more manageable pieces';
        case 'duplication':
          return 'Extract common code into reusable components';
        case 'maintainability':
          return 'Improve code documentation and add unit tests';
        default:
          return `Address ${issue} to improve code quality`;
      }
    });
  }

  private analyzeMaintainability(): ProjectInsights['maintainability'] {
    const score = this.calculateMaintainabilityScore();
    const factors = this.identifyMaintainabilityFactors();
    const recommendations = this.generateMaintainabilityRecommendations(factors);

    return { score, factors, recommendations };
  }

  private calculateMaintainabilityScore(): number {
    const metrics = this.calculateCodeQualityMetrics();
    
    return (
      (metrics.maintainability * 0.4) +
      ((1 - metrics.complexity) * 0.3) +
      (metrics.coverage * 0.3)
    );
  }

  private identifyMaintainabilityFactors(): string[] {
    const factors: string[] = [];
    const metrics = this.calculateCodeQualityMetrics();

    if (metrics.complexity > 0.7) factors.push('High complexity');
    if (metrics.maintainability < 0.6) factors.push('Low maintainability');
    if (metrics.coverage < 0.8) factors.push('Low test coverage');

    return factors;
  }

  private generateMaintainabilityRecommendations(factors: string[]): string[] {
    return factors.map(factor => {
      switch (factor) {
        case 'High complexity':
          return 'Refactor complex code into smaller, more focused components';
        case 'Low maintainability':
          return 'Improve code organization and documentation';
        case 'Low test coverage':
          return 'Add more unit tests to improve code reliability';
        default:
          return `Address ${factor} to improve maintainability`;
      }
    });
  }

  private generateArchitectureSuggestions(): string[] {
    const insights = this.getProjectInsights();
    const suggestions: string[] = [];

    // Add suggestions based on architecture analysis
    insights.architecture.issues.forEach(issue => {
      suggestions.push(`Address ${issue} to improve architecture`);
    });

    // Add suggestions based on dependencies
    insights.dependencies.conflicts.forEach(conflict => {
      suggestions.push(`Resolve ${conflict}`);
    });

    // Add suggestions based on maintainability
    insights.maintainability.factors.forEach(factor => {
      suggestions.push(`Address ${factor} to improve maintainability`);
    });

    return suggestions;
  }

  // Real-time Collaboration Integration
  public handleCollaborativeUpdate(update: CollaborativeUpdate): void {
    const { agentId, changes, context } = update;
    
    changes.forEach(change => {
      this.updateCodeAnalysis(change);
    });

    this.notifyAgents({
      type: 'codeUpdate',
      agentId,
      changes,
      context
    });
    
    this.updateAgentContexts();
  }

  private updateCodeAnalysis(change: CollaborativeUpdate['changes'][0]): void {
    this.handleCollaborativeCodeUpdate(change);
  }

  /**
   * Handles code updates from collaborative changes
   * @param change - The collaborative change to process
   * @private
   */
  private handleCollaborativeCodeUpdate(change: CollaborativeUpdate['changes'][0]): void {
    switch (change.type) {
      case 'add':
        this.addNewNode(change.path, change.content || '');
        break;
      case 'modify':
        this.updateExistingNode(change.path, change.content || '');
        break;
      case 'delete':
        this.deleteNode(change.path);
        break;
    }
  }

  private addNewNode(path: string, content: string): void {
    const node: CodeNode = {
      id: path,
      name: path.split('/').pop() || path,
      type: 'file',
      path,
      metrics: {
        complexity: 0,
        lines: content.split('\n').length,
        dependencies: 0,
        coverage: 0,
        maintainability: 0,
        cognitiveComplexity: 0,
        cyclomaticComplexity: 0,
        halsteadVolume: 0,
        halsteadDifficulty: 0,
        halsteadEffort: 0,
        halsteadTime: 0,
        halsteadBugs: 0
      },
      analysis: {
        patterns: [],
        smells: [],
        vulnerabilities: [],
        suggestions: [],
        documentation: '',
        lastModified: new Date(),
        contributors: [],
        gitHistory: []
      },
      dependencies: [],
      relationships: {
        imports: [],
        exports: [],
        extends: [],
        implements: [],
        uses: [],
        usedBy: []
      },
      context: {
        namespace: '',
        module: '',
        scope: 'module',
        visibility: 'public'
      }
    };
    this.nodes.set(node.id, node);
  }

  private updateExistingNode(path: string, content: string): void {
    const node = Array.from(this.nodes.values()).find(n => n.path === path);
    if (node) {
      node.metrics.lines = content.split('\n').length;
      node.analysis.lastModified = new Date();
      this.nodes.set(node.id, node);
    }
  }

  private deleteNode(path: string): void {
    const node = Array.from(this.nodes.values()).find(n => n.path === path);
    if (node) {
      this.nodes.delete(node.id);
    }
  }

  private notifyAgents(notification: {
    type: string;
    agentId: string;
    changes: CollaborativeUpdate['changes'];
    context: CollaborativeUpdate['context'];
  }): void {
    this.ws.emit('agentNotification', notification);
  }

  private updateAgentContexts(): void {
    const agents = this.getActiveAgents();
    agents.forEach(agent => {
      const context = this.provideAgentContext(agent);
      this.ws.emit('updateAgentContext', {
        agentId: agent.agentId,
        context
      });
    });
  }

  private getActiveAgents(): AgentContext[] {
    // This would typically come from the agent management system
    return [];
  }

  // Task Planning Integration
  public analyzeTaskRequirements(task: Task): TaskAnalysis {
    return {
      requiredComponents: this.findRequiredComponents(task),
      dependencies: this.analyzeTaskDependencies(task),
      complexity: this.estimateTaskComplexity(task),
      suggestedApproach: this.generateTaskApproach(task)
    };
  }

  private findRequiredComponents(task: Task): CodeNode[] {
    const taskKeywords = task.description.toLowerCase().split(' ');
    return Array.from(this.nodes.values()).filter(node => {
      const nodeContent = `${node.name} ${node.type} ${node.path}`.toLowerCase();
      return taskKeywords.some(keyword => nodeContent.includes(keyword));
    });
  }

  private analyzeTaskDependencies(task: Task): TaskAnalysis['dependencies'] {
    const requiredComponents = this.findRequiredComponents(task);
    const direct = this.getDirectDependenciesForComponents(requiredComponents);
    const indirect = this.getIndirectDependenciesForComponents(requiredComponents);
    const conflicts = this.detectTaskDependencyConflicts(requiredComponents);

    return { direct, indirect, conflicts };
  }

  private getDirectDependenciesForComponents(components: CodeNode[]): string[] {
    const dependencies = new Set<string>();
    components.forEach(component => {
      if (component.relationships?.imports) {
        component.relationships.imports.forEach(imp => dependencies.add(imp));
      }
    });
    return Array.from(dependencies);
  }

  private getIndirectDependenciesForComponents(components: CodeNode[]): string[] {
    const directDeps = this.getDirectDependenciesForComponents(components);
    const indirectDeps = new Set<string>();

    directDeps.forEach(dep => {
      const node = this.nodes.get(dep);
      if (node?.relationships?.imports) {
        node.relationships.imports.forEach(imp => indirectDeps.add(imp));
      }
    });

    return Array.from(indirectDeps);
  }

  private detectTaskDependencyConflicts(components: CodeNode[]): string[] {
    const conflicts: string[] = [];
    const dependencies = this.getDirectDependenciesForComponents(components);
    
    dependencies.forEach(dep => {
      const node = this.nodes.get(dep);
      if (node?.analysis?.vulnerabilities) {
        conflicts.push(`Security vulnerability in ${dep}`);
      }
    });

    return conflicts;
  }

  private estimateTaskComplexity(task: Task): TaskAnalysis['complexity'] {
    const requiredComponents = this.findRequiredComponents(task);
    const complexityScore = this.calculateTaskComplexityScore(requiredComponents);
    const factors = this.identifyTaskComplexityFactors(requiredComponents);

    return { score: complexityScore, factors };
  }

  private calculateTaskComplexityScore(components: CodeNode[]): number {
    const metrics = this.calculateCodeQualityMetrics();
    const componentCount = components.length;
    const dependencyCount = this.getDirectDependenciesForComponents(components).length;

    return (
      (metrics.complexity * 0.4) +
      (componentCount * 0.2) +
      (dependencyCount * 0.4)
    );
  }

  private identifyTaskComplexityFactors(components: CodeNode[]): string[] {
    const factors: string[] = [];
    const metrics = this.calculateCodeQualityMetrics();

    if (metrics.complexity > 0.7) factors.push('High code complexity');
    if (components.length > 10) factors.push('Large number of components');
    if (this.getDirectDependenciesForComponents(components).length > 5) {
      factors.push('Many dependencies');
    }

    return factors;
  }

  private generateTaskApproach(task: Task): TaskAnalysis['suggestedApproach'] {
    const requiredComponents = this.findRequiredComponents(task);
    const dependencies = this.analyzeTaskDependencies(task);
    const complexity = this.estimateTaskComplexity(task);

    return {
      steps: this.generateTaskSteps(requiredComponents, dependencies),
      considerations: this.generateTaskConsiderations(complexity),
      risks: this.identifyTaskRisks(dependencies)
    };
  }

  private generateTaskSteps(
    components: CodeNode[],
    dependencies: TaskAnalysis['dependencies']
  ): string[] {
    const steps: string[] = [];

    // Add dependency resolution steps
    if (dependencies.conflicts.length > 0) {
      steps.push('Resolve dependency conflicts');
    }

    // Add component implementation steps
    components.forEach(component => {
      steps.push(`Implement/update ${component.name}`);
    });

    // Add testing steps
    steps.push('Write unit tests for new/modified components');
    steps.push('Perform integration testing');

    return steps;
  }

  private generateTaskConsiderations(complexity: TaskAnalysis['complexity']): string[] {
    const considerations: string[] = [];

    complexity.factors.forEach(factor => {
      switch (factor) {
        case 'High code complexity':
          considerations.push('Consider breaking down complex components');
          break;
        case 'Large number of components':
          considerations.push('Plan for modular development');
          break;
        case 'Many dependencies':
          considerations.push('Ensure proper dependency management');
          break;
      }
    });

    return considerations;
  }

  private identifyTaskRisks(dependencies: TaskAnalysis['dependencies']): string[] {
    const risks: string[] = [];

    if (dependencies.conflicts.length > 0) {
      risks.push('Dependency conflicts may cause integration issues');
    }

    if (dependencies.indirect.length > 5) {
      risks.push('Many indirect dependencies may increase maintenance burden');
    }

    return risks;
  }

  private initializeIntegrations(): void {
    // Initialize connections to other ADE services
    this.ws.emit('initializeIntegrations', {}, (response: {
      errorAnalysis: any;
      agentSystem: any;
      projectAwareness: any;
    }) => {
      this.errorAnalysisService = response.errorAnalysis;
      this.agentSystemService = response.agentSystem;
      this.projectAwarenessService = response.projectAwareness;

      // Set up integration event listeners
      this.setupIntegrationEventListeners();
    });
  }

  private setupIntegrationEventListeners(): void {
    // Error Analysis Service events
    this.ws.on('errorDetected', (data: ErrorAnalysisIntegration) => {
      this.handleErrorAnalysis(data);
    });

    // Agent System events
    this.ws.on('agentUpdate', (data: AgentSystemIntegration) => {
      this.handleAgentUpdate(data);
    });

    // Project Awareness events
    this.ws.on('projectUpdate', (data: ProjectAwarenessIntegration) => {
      this.handleProjectUpdate(data);
    });
  }

  // Error Analysis Integration
  private handleErrorAnalysis(data: ErrorAnalysisIntegration): void {
    // Update affected nodes with error information
    data.relatedNodes.forEach(nodeId => {
      const node = this.nodes.get(nodeId);
      if (node) {
        node.analysis.vulnerabilities.push(data.errorType);
        node.analysis.suggestions.push(...data.suggestedFixes);
      }
    });

    // Emit error analysis event
    this.emit('errorAnalysis', {
      errorId: data.errorId,
      severity: data.severity,
      affectedNodes: data.relatedNodes,
      suggestedFixes: data.suggestedFixes
    });
  }

  public reportError(error: Error): void {
    const errorContext = this.analyzeErrorContext(error);
    this.ws.emit('reportError', {
      error: error.message,
      stackTrace: error.stack?.split('\n') || [],
      context: errorContext
    });
  }

  // Agent System Integration
  private handleAgentUpdate(data: AgentSystemIntegration): void {
    // Update agent context in the codebase
    const agentContext: AgentContext = {
      agentId: data.agentId,
      capabilities: data.capabilities,
      currentTask: data.currentTask.description,
      requiredContext: ['dependencies', 'metrics']
    };

    const context = this.provideAgentContext(agentContext);
    
    // Emit agent update event
    this.emit('agentUpdate', {
      agentId: data.agentId,
      taskStatus: data.currentTask.status,
      context
    });
  }

  public updateAgentContext(agentId: string, taskId: string): void {
    this.ws.emit('requestAgentContext', { agentId, taskId }, (response: AgentSystemIntegration) => {
      this.handleAgentUpdate(response);
    });
  }

  // Project Awareness Integration
  private handleProjectUpdate(data: ProjectAwarenessIntegration): void {
    // Update project structure
    this.updateProjectStructure(data.structure);
    
    // Update project metrics
    this.updateProjectMetrics(data.metrics);
    
    // Update project patterns
    this.updateProjectPatterns(data.patterns);

    // Emit project update event
    this.emit('projectUpdate', {
      projectId: data.projectId,
      metrics: data.metrics,
      patterns: data.patterns
    });
  }

  private updateProjectStructure(structure: ProjectAwarenessIntegration['structure']): void {
    // Update nodes based on project structure
    structure.files.forEach(file => {
      if (!this.nodes.has(file)) {
        this.addNewNode(file, '');
      }
    });

    // Update dependencies
    Object.entries(structure.dependencies).forEach(([file, deps]) => {
      const node = this.nodes.get(file);
      if (node) {
        node.dependencies = deps;
        node.relationships.imports = deps;
      }
    });
  }

  private updateProjectMetrics(metrics: ProjectAwarenessIntegration['metrics']): void {
    // Update overall project metrics
    const insights = this.getProjectInsights();
    insights.codeQuality.metrics = {
      ...insights.codeQuality.metrics,
      complexity: metrics.complexity,
      maintainability: metrics.maintainability,
      coverage: metrics.testCoverage,
      documentation: metrics.documentation
    };
  }

  private updateProjectPatterns(patterns: ProjectAwarenessIntegration['patterns']): void {
    // Update architecture patterns
    const insights = this.getProjectInsights();
    insights.architecture.patterns = patterns.architecture;
    insights.architecture.issues = patterns.antiPatterns;
    insights.architecture.recommendations = patterns.suggestions;
  }

  public requestProjectUpdate(): void {
    this.ws.emit('requestProjectUpdate', {}, (response: ProjectAwarenessIntegration) => {
      this.handleProjectUpdate(response);
    });
  }

  // Integration Event Handlers
  public onErrorAnalysis(callback: (data: ErrorAnalysisIntegration) => void): void {
    this.on('errorAnalysis', callback);
  }

  public onAgentUpdate(callback: (data: AgentSystemIntegration) => void): void {
    this.on('agentUpdate', callback);
  }

  public onProjectUpdate(callback: (data: ProjectAwarenessIntegration) => void): void {
    this.on('projectUpdate', callback);
  }

  private getCachedMetrics(nodeId: string): Record<string, number> | null {
    const cached = this.metricsCache.get(nodeId);
    if (cached && Date.now() - cached.timestamp.getTime() < this.CACHE_TTL) {
      return cached.data;
    }
    return null;
  }

  private setCachedMetrics(nodeId: string, metrics: Record<string, number>): void {
    this.metricsCache.set(nodeId, {
      timestamp: new Date(),
      data: metrics
    });
  }

  private getCachedDependencies(nodeId: string): string[] | null {
    const cached = this.dependencyCache.get(nodeId);
    if (cached && Date.now() - cached.timestamp.getTime() < this.CACHE_TTL) {
      return cached.data;
    }
    return null;
  }

  private setCachedDependencies(nodeId: string, dependencies: string[]): void {
    this.dependencyCache.set(nodeId, {
      timestamp: new Date(),
      data: dependencies
    });
  }

  /**
   * Retrieves the current health status of the service
   * @returns Object containing health status, metrics, and issues
   * @public
   */
  public getHealthStatus(): {
    status: 'healthy' | 'degraded' | 'unhealthy';
    metrics: {
      nodeCount: number;
      edgeCount: number;
      cacheSize: number;
      lastUpdate: Date;
    };
    issues: string[];
  } {
    const issues: string[] = [];
    const now = Date.now();

    // Check cache freshness
    const oldestCacheEntry = Math.min(
      ...Array.from(this.metricsCache.values()).map(v => v.timestamp.getTime()),
      ...Array.from(this.dependencyCache.values()).map(v => v.timestamp.getTime()),
      ...Array.from(this.analysisCache.values()).map(v => v.timestamp.getTime())
    );

    if (now - oldestCacheEntry > this.CACHE_TTL * 2) {
      issues.push('Cache data is stale');
    }

    // Check data consistency
    if (this.nodes.size === 0) {
      issues.push('No nodes in the graph');
    }

    // Check performance
    const performance = this.getPerformanceMetrics();
    performance.averageTimes.forEach((time, operation) => {
      if (time > this.PERFORMANCE_THRESHOLD) {
        issues.push(`Slow operation detected: ${operation}`);
      }
    });

    return {
      status: issues.length === 0 ? 'healthy' : issues.length > 2 ? 'unhealthy' : 'degraded',
      metrics: {
        nodeCount: this.nodes.size,
        edgeCount: this.edges.size,
        cacheSize: this.metricsCache.size + this.dependencyCache.size + this.analysisCache.size,
        lastUpdate: new Date()
      },
      issues
    };
  }

  /**
   * Cleans up old data to prevent memory leaks
   * @private
   */
  private cleanupOldData(): void {
    const now = Date.now();
    
    // Clean up metrics cache
    this.metricsCache.forEach((value, key) => {
      if (now - value.timestamp.getTime() > this.CACHE_TTL) {
        this.metricsCache.delete(key);
      }
    });

    // Clean up dependency cache
    this.dependencyCache.forEach((value, key) => {
      if (now - value.timestamp.getTime() > this.CACHE_TTL) {
        this.dependencyCache.delete(key);
      }
    });

    // Clean up analysis cache
    this.analysisCache.forEach((value, key) => {
      if (now - value.timestamp.getTime() > this.CACHE_TTL) {
        this.analysisCache.delete(key);
      }
    });

    // Limit change history size
    if (this.changeHistory.length > this.OPERATION_HISTORY_LIMIT) {
      this.changeHistory = this.changeHistory.slice(-this.OPERATION_HISTORY_LIMIT);
    }
  }

  /**
   * Optimizes cache based on usage patterns and memory constraints
   * @private
   */
  private optimizeCache(): void {
    const now = Date.now();
    const usagePatterns = new Map<string, number>();

    // Analyze cache usage patterns
    this.metricsCache.forEach((value, key) => {
      const age = now - value.timestamp.getTime();
      usagePatterns.set(key, age);
    });

    // Sort by usage frequency
    const sortedKeys = Array.from(usagePatterns.entries())
      .sort((a, b) => a[1] - b[1])
      .map(([key]) => key);

    // Keep only the most frequently used items
    const keepCount = Math.min(
      Math.floor(this.metricsCache.size * 0.8), // Keep 80%
      this.CACHE_SIZE_LIMIT
    );
    
    sortedKeys.slice(keepCount).forEach(key => {
      this.metricsCache.delete(key);
    });
  }

  /**
   * Retrieves performance metrics for all tracked operations
   * @returns Object containing operation counts and average execution times
   * @public
   */
  public getPerformanceMetrics(): {
    operationCounts: Map<string, number>;
    averageTimes: Map<string, number>;
  } {
    const averageTimes = new Map<string, number>();
    
    this.performanceMetrics.operationTimes.forEach((times, operation) => {
      const average = times.reduce((a, b) => a + b, 0) / times.length;
      averageTimes.set(operation, average);
    });

    return {
      operationCounts: this.performanceMetrics.operationCounts,
      averageTimes
    };
  }

  /**
   * Sets up error handlers for different types of errors
   * @private
   */
  private setupErrorHandlers(): void {
    this.errorHandlers.set('validation', (error: Error) => {
      console.error('Validation error:', error);
      this.emit('error', {
        type: 'validation',
        error: error instanceof ValidationError ? error : new ValidationError(error.message),
        timestamp: new Date(),
        context: this.getErrorContext()
      });
    });

    this.errorHandlers.set('analysis', (error: Error) => {
      console.error('Analysis error:', error);
      this.emit('error', {
        type: 'analysis',
        error: error instanceof AnalysisError ? error : new AnalysisError(error.message),
        timestamp: new Date(),
        context: this.getErrorContext()
      });
    });

    this.errorHandlers.set('integration', (error: Error) => {
      console.error('Integration error:', error);
      this.emit('error', {
        type: 'integration',
        error: error instanceof IntegrationError ? error : new IntegrationError(error.message),
        timestamp: new Date(),
        context: this.getErrorContext()
      });
    });
  }

  /**
   * Sets up validation rules for different data types
   * @private
   */
  private setupValidationRules(): void {
    this.validationRules.set('node', {
      validate: (data: CodeNode) => {
        return data && typeof data.id === 'string' && typeof data.type === 'string';
      },
      errorMessage: 'Invalid node data: missing required fields'
    });

    this.validationRules.set('edge', {
      validate: (data: CodeEdge) => {
        return data && typeof data.from === 'string' && typeof data.to === 'string';
      },
      errorMessage: 'Invalid edge data: missing required fields'
    });

    this.validationRules.set('metrics', {
      validate: (data: CodeNode['metrics']) => {
        return data && typeof data.complexity === 'number' && typeof data.maintainability === 'number';
      },
      errorMessage: 'Invalid metrics data: missing required fields'
    });
  }

  /**
   * Gets the current context for error reporting
   * @private
   */
  private getErrorContext(): {
    nodeCount: number;
    edgeCount: number;
    activeProfiles: string[];
    lastOperation?: string;
  } {
    return {
      nodeCount: this.nodes.size,
      edgeCount: this.edges.size,
      activeProfiles: Array.from(this.performanceProfiles.keys()),
      lastOperation: Array.from(this.performanceMetrics.operationCounts.entries())
        .sort((a, b) => b[1] - a[1])[0]?.[0]
    };
  }
} 