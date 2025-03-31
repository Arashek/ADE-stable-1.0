export interface CodeMetrics {
  complexity: number;
  maintainability: number;
  testCoverage: number;
  performance: {
    timeComplexity: string;
    spaceComplexity: string;
  };
  dependencies: number;
  linesOfCode: number;
}

export interface DependencyNode {
  id: string;
  label: string;
  type: 'file' | 'function' | 'class' | 'variable';
  metrics?: Partial<CodeMetrics>;
}

export interface DependencyLink {
  source: string;
  target: string;
  type: 'imports' | 'calls' | 'extends' | 'implements';
  weight: number;
}

export interface DependencyGraph {
  nodes: DependencyNode[];
  links: DependencyLink[];
}

export interface CodeContext {
  repository: string;
  branch: string;
  path: string;
  language: string;
  framework?: string;
}

export interface AISuggestion {
  id: string;
  type: 'improvement' | 'warning' | 'error' | 'optimization';
  title: string;
  description: string;
  code?: string;
  impact: 'high' | 'medium' | 'low';
  category: 'performance' | 'security' | 'maintainability' | 'functionality';
  location?: {
    startLine: number;
    endLine: number;
    startColumn: number;
    endColumn: number;
  };
}

export interface User {
  id: string;
  name: string;
  avatar: string;
  status: 'online' | 'offline' | 'away';
  cursor?: {
    line: number;
    column: number;
    file: string;
  };
}

export interface CodeChange {
  id: string;
  userId: string;
  timestamp: Date;
  type: 'edit' | 'delete' | 'add' | 'rename';
  file: string;
  description: string;
  diff?: string;
  metadata?: Record<string, any>;
} 