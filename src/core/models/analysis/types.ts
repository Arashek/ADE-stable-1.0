export interface AnalysisResult {
  timestamp: Date;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  details: any;
}

export interface CodebaseInsights {
  design: DesignInsights | null;
  development: DevelopmentInsights | null;
  testing: TestingInsights | null;
  security: SecurityInsights | null;
  deployment: DeploymentInsights | null;
  suggestions: string[];
}

export interface DesignInsights {
  usesReact: boolean;
  componentStructure: {
    complexity: 'low' | 'medium' | 'high';
  };
  hasAccessibilityIssues: boolean;
}

export interface DevelopmentInsights {
  hasPerformanceBottlenecks: boolean;
  hasAuthIssues: boolean;
  dependencies: {
    outdated: string[];
  };
}

export interface TestingInsights {
  coverage: number;
  gaps: {
    untestedComponents: string[];
  };
}

export interface SecurityInsights {
  vulnerabilities: {
    critical: number;
  };
}

export interface DeploymentInsights {
  infrastructure: string;
  environment: string;
}

export interface Task {
  id: string;
  name: string;
  description: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  priority: 'low' | 'medium' | 'high';
  dependencies: string[];
  estimatedDuration: string;
  actualDuration?: string;
  assignedTo?: string;
  progress: number;
  notes?: string[];
}

export interface ImplementationOption {
  id: string;
  title: string;
  description: string;
  duration: string;
  risk: 'low' | 'medium' | 'high';
  quality: 'low' | 'moderate' | 'high';
  changes: string[];
}

export interface ImplementationPlan {
  option: ImplementationOption;
  phases: any[];
  dependencies: any[];
  timeline: any;
  monitoring: any;
}

export interface ChatResponse {
  type: 'question' | 'clarification' | 'suggestions' | 'options' | 'plan' | 'transition' | 'error';
  content: string;
  suggestions?: string[];
  options?: ImplementationOption[];
  plan?: ImplementationPlan;
  nextPhase: string;
} 