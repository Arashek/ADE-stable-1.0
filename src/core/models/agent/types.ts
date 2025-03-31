export interface UserInput {
  description: string;
  requirements: string[];
  constraints?: string[];
  preferences?: UserPreferences;
}

export interface UserPreferences {
  technologyStack?: string[];
  securityLevel?: 'high' | 'medium' | 'low';
  performanceRequirements?: PerformanceRequirements;
  budget?: BudgetConstraints;
}

export interface PerformanceRequirements {
  responseTime?: string;
  throughput?: string;
  scalability?: string;
  availability?: string;
}

export interface BudgetConstraints {
  development?: number;
  infrastructure?: number;
  maintenance?: number;
}

export interface ProjectSpecification {
  requirements: ProjectRequirements;
  architecture: ArchitectureSpec;
  security: SecuritySpec;
  performance: PerformanceSpec;
  development: DevelopmentSpec;
}

export interface ProjectRequirements {
  functional: FunctionalRequirement[];
  nonFunctional: NonFunctionalRequirement[];
  constraints: Constraint[];
  dependencies: Dependency[];
}

export interface FunctionalRequirement {
  id: string;
  description: string;
  priority: 'high' | 'medium' | 'low';
  category: string;
}

export interface NonFunctionalRequirement {
  id: string;
  type: string;
  description: string;
  metrics: string[];
}

export interface ArchitectureSpec {
  components: Component[];
  interactions: Interaction[];
  patterns: Pattern[];
  technologies: Technology[];
}

export interface SecuritySpec {
  threats: Threat[];
  mitigations: Mitigation[];
  compliance: Compliance[];
  bestPractices: BestPractice[];
}

export interface PerformanceSpec {
  metrics: Metric[];
  bottlenecks: Bottleneck[];
  optimizations: Optimization[];
  scaling: ScalingConfig[];
}

export interface DevelopmentSpec {
  environment: EnvironmentConfig;
  tools: Tool[];
  workflows: Workflow[];
  testing: TestingConfig;
}

export interface LLMSpecification {
  type: string;
  specification: Partial<ProjectSpecification>;
  confidence: number;
}

export interface SpecificationAnalysis {
  requirements: RequirementsAnalysis;
  architecture: ArchitectureAnalysis;
  security: SecurityAnalysis;
  performance: PerformanceAnalysis;
  conflicts: Conflict[];
}

export interface RequirementsAnalysis {
  coreRequirements: FunctionalRequirement[];
  optionalRequirements: FunctionalRequirement[];
  dependencies: Dependency[];
  constraints: Constraint[];
}

export interface ArchitectureAnalysis {
  components: Component[];
  interactions: Interaction[];
  patterns: Pattern[];
  technologies: Technology[];
}

export interface SecurityAnalysis {
  threats: Threat[];
  mitigations: Mitigation[];
  compliance: Compliance[];
  bestPractices: BestPractice[];
}

export interface PerformanceAnalysis {
  metrics: Metric[];
  bottlenecks: Bottleneck[];
  optimizations: Optimization[];
  scaling: ScalingConfig[];
}

export interface Conflict {
  type: string;
  description: string;
  resolution: string;
  severity: 'high' | 'medium' | 'low';
}

export interface Component {
  name: string;
  type: string;
  responsibilities: string[];
  dependencies: string[];
}

export interface Interaction {
  source: string;
  target: string;
  type: string;
  protocol: string;
}

export interface Pattern {
  name: string;
  type: string;
  description: string;
  implementation: string;
}

export interface Technology {
  name: string;
  version: string;
  purpose: string;
  alternatives: string[];
}

export interface Threat {
  id: string;
  description: string;
  impact: string;
  likelihood: 'high' | 'medium' | 'low';
}

export interface Mitigation {
  threatId: string;
  description: string;
  implementation: string;
  effectiveness: number;
}

export interface Compliance {
  standard: string;
  requirements: string[];
  implementation: string;
}

export interface BestPractice {
  category: string;
  description: string;
  implementation: string;
}

export interface Metric {
  name: string;
  type: string;
  target: string;
  measurement: string;
}

export interface Bottleneck {
  component: string;
  description: string;
  impact: string;
  solution: string;
}

export interface Optimization {
  area: string;
  description: string;
  implementation: string;
  impact: string;
}

export interface ScalingConfig {
  type: 'horizontal' | 'vertical';
  trigger: string;
  action: string;
  limits: {
    min: number;
    max: number;
  };
}

export interface EnvironmentConfig {
  type: string;
  dependencies: string[];
  configuration: Record<string, any>;
}

export interface Tool {
  name: string;
  version: string;
  purpose: string;
  configuration: Record<string, any>;
}

export interface Workflow {
  name: string;
  steps: string[];
  triggers: string[];
  conditions: string[];
}

export interface TestingConfig {
  types: string[];
  frameworks: string[];
  coverage: number;
  automation: boolean;
}

export interface Constraint {
  id: string;
  type: string;
  description: string;
  impact: string;
  priority: 'high' | 'medium' | 'low';
}

export interface Dependency {
  id: string;
  name: string;
  version: string;
  type: 'internal' | 'external';
  description: string;
  criticality: 'high' | 'medium' | 'low';
}

// Backup Types
export interface BackupSpec {
  schedule: Schedule;
  retention: Retention;
  locations: Location[];
  recovery: RecoveryOption[];
  monitoring: Monitoring;
}

export interface Schedule {
  frequency: 'hourly' | 'daily' | 'weekly' | 'monthly';
  time: string;
}

export interface Retention {
  period: number;
  keepLatest: boolean;
}

export interface Location {
  type: string;
  provider: string;
  region: string;
  encryption: boolean;
}

export interface RecoveryOption {
  type: string;
  description: string;
  timeEstimate: string;
  priority: 'high' | 'medium' | 'low';
}

export interface Monitoring {
  enabled: boolean;
  alertThreshold: 'critical' | 'warning' | 'info';
}

// Extended User Preferences Types
export interface ExtendedUserPreferences extends UserPreferences {
  ideTheme: 'light' | 'dark' | 'system';
  autoSave: boolean;
  fontSize: number;
  indentation: 'spaces' | 'tabs';
  indentationSize: number;
  formatOnSave: boolean;
  gitAutoCommit: boolean;
  commitMessageTemplate: string;
  gitPushOnCommit: boolean;
  notifications: NotificationPreferences;
  keyboardShortcuts: KeyboardShortcut[];
  languages: string[];
  defaultLanguage: string;
}

export interface NotificationPreferences {
  enabled: boolean;
  level: 'all' | 'important' | 'none';
}

export interface KeyboardShortcut {
  action: string;
  key: string;
  description: string;
} 