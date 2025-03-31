export interface ErrorAnalysisResponse {
  error_analysis: string;
  root_cause: string;
  solution_steps: string[];
  confidence_score: number;
  reasoning_chain: string[];
  related_patterns: string[];
  impact_analysis?: {
    system_impact?: {
      components: string[];
      degradation: string;
      data_integrity: string;
    };
    business_impact?: {
      user_experience: string;
      operations: string;
      financial: string;
    };
    recovery?: {
      time: string;
      resources: string[];
      dependencies: string[];
    };
  };
  prevention_strategies?: string[];
  monitoring_suggestions?: string[];
  timestamp: string;
}

export interface PatternMatch {
  pattern_id: string;
  pattern_type: string;
  description: string;
  match_score: number;
  context_similarity: number;
  matched_groups: Record<string, string>;
}

export interface PatternMatchResponse {
  matches: PatternMatch[];
  confidence_scores: number[];
  context_similarity: number[];
}

export interface Solution {
  solution_id: string;
  pattern_type: string;
  description: string;
  steps: string[];
  prerequisites: string[];
  success_criteria: string[];
  created_at: string;
  updated_at: string;
}

export interface SolutionResponse {
  solution: Solution;
  confidence_score: number;
  reasoning_chain: string[];
  risk_assessment: {
    risks: string[];
    mitigation: string[];
    rollback: string;
  };
  monitoring_plan: {
    metrics: string[];
    alerts: string[];
    logging: string[];
  };
  maintenance_requirements: string[];
} 