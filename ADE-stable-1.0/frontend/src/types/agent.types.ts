export enum GenerationType {
  COMPONENT = 'component',
  FUNCTION = 'function',
  CLASS = 'class',
  API = 'api',
  DATABASE = 'database',
  CONFIG = 'config',
}

export enum ReviewType {
  SECURITY = 'security',
  PERFORMANCE = 'performance',
  CODE_QUALITY = 'code_quality',
  BEST_PRACTICES = 'best_practices',
  ARCHITECTURE = 'architecture',
  TESTING = 'testing',
}

export enum TestType {
  UNIT = 'unit',
  INTEGRATION = 'integration',
  E2E = 'e2e',
  PERFORMANCE = 'performance',
  SECURITY = 'security',
}

export enum DocumentationType {
  API = 'api',
  CODE = 'code',
  ARCHITECTURE = 'architecture',
  DEPLOYMENT = 'deployment',
  USER_GUIDE = 'user_guide',
}

export interface CodeGenerationRequest {
  project_id: string;
  language: string;
  framework?: string;
  requirements: string[];
  constraints?: string[];
  metadata?: {
    generate_tests?: boolean;
    generate_docs?: boolean;
  };
}

export interface CodeGenerationResponse {
  id: string;
  project_id: string;
  language: string;
  framework?: string;
  generated_code: string;
  tests?: string;
  documentation?: string;
  metadata: {
    generate_tests: boolean;
    generate_docs: boolean;
    timestamp: string;
  };
}

export interface CodeReviewRequest {
  project_id: string;
  file_path: string;
  review_types: ReviewType[];
  focus_areas?: string[];
}

export interface CodeReviewResponse {
  id: string;
  project_id: string;
  file_path: string;
  review_types: ReviewType[];
  comments: {
    line_number: number;
    type: 'error' | 'warning' | 'info';
    message: string;
    suggestion?: string;
  }[];
  summary: string;
  timestamp: string;
}

export interface TestGenerationRequest {
  project_id: string;
  file_path: string;
  test_types: TestType[];
  framework: string;
  coverage_target: number;
}

export interface TestGenerationResponse {
  id: string;
  project_id: string;
  file_path: string;
  test_types: TestType[];
  framework: string;
  test_suite: string;
  coverage_report: {
    total_lines: number;
    covered_lines: number;
    coverage_percentage: number;
  };
  timestamp: string;
}

export interface DocumentationRequest {
  project_id: string;
  doc_types: DocumentationType[];
  format: string;
  style: string;
  include_examples: boolean;
}

export interface DocumentationResponse {
  id: string;
  project_id: string;
  doc_types: DocumentationType[];
  format: string;
  style: string;
  content: string;
  examples?: string[];
  timestamp: string;
}

export interface AgentCapabilities {
  code_generation: {
    supported_languages: string[];
    supported_frameworks: string[];
    max_requirements: number;
    max_constraints: number;
  };
  code_review: {
    types: ReviewType[];
    max_focus_areas: number;
    supported_languages: string[];
  };
  testing: {
    types: TestType[];
    supported_frameworks: string[];
    max_coverage_target: number;
  };
  documentation: {
    types: DocumentationType[];
    formats: string[];
    max_examples: number;
  };
} 