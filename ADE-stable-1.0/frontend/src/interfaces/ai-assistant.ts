import { AIAgentConfig, AIAgentContext, AIAgentResponse } from './ai';
import { FileNode } from './ide';

export interface AIAssistantState {
    isActive: boolean;
    isProcessing: boolean;
    context: AIAssistantContext;
    history: AIAssistantHistory[];
    suggestions: AIAssistantSuggestion[];
    settings: AIAssistantSettings;
}

export interface AIAssistantContext {
    currentFile: FileNode | null;
    selection: {
        start: number;
        end: number;
        text: string;
    };
    cursor: {
        line: number;
        column: number;
    };
    projectContext: {
        files: FileNode[];
        dependencies: Record<string, string>;
        config: Record<string, any>;
    };
    systemContext: {
        os: string;
        runtime: string;
        environment: Record<string, string>;
    };
}

export interface AIAssistantHistory {
    id: string;
    timestamp: string;
    type: 'user' | 'assistant' | 'system';
    content: string;
    metadata?: {
        command?: string;
        file?: string;
        line?: number;
        suggestions?: string[];
        projectId?: string;
        user?: string;
        cached?: boolean;
        thinkingProcess?: {
            analysis: {
                problem: string;
                context: string;
                constraints: string[];
                assumptions: string[];
                risks: string[];
            };
            reasoning: {
                approach: string;
                steps: string[];
                alternatives: {
                    option: string;
                    pros: string[];
                    cons: string[];
                    feasibility: number;
                }[];
                decision: {
                    chosen: string;
                    rationale: string;
                    confidence: number;
                };
            };
            implementation: {
                strategy: string;
                steps: string[];
                dependencies: string[];
                timeline: string;
                resources: string[];
            };
            validation: {
                criteria: string[];
                tests: string[];
                successMetrics: string[];
                fallbackPlan: string;
            };
        };
    };
}

export interface SafetyCheck {
    type: string;
    message: string;
    status: 'safe' | 'warning' | 'unsafe';
    file?: string;
    line?: number;
    column?: number;
    solutions?: Solution[];
}

export interface SolutionMetrics {
    effectiveness: number;
    impact: number;
    complexity: number;
    maintainability: number;
}

export interface Solution {
    code: string;
    description: string;
    metrics: SolutionMetrics;
    metadata?: Record<string, any>;
}

export interface AIAssistantSuggestion {
    id: string;
    type: 'code' | 'command' | 'explanation' | 'fix' | 'refactor';
    content: string;
    confidence: number;
    context: {
        file?: string;
        line?: number;
        column?: number;
    };
    actions: AIAssistantAction[];
    metadata?: Record<string, any>;
    solutions?: Solution[];
}

export interface AIAssistantAction {
    id: string;
    type: 'apply' | 'explain' | 'modify' | 'reject';
    label: string;
    description: string;
    execute: () => Promise<void>;
}

export interface AIAssistantSettings {
    model: AIAgentConfig;
    features: {
        codeCompletion: boolean;
        commandSuggestions: boolean;
        errorExplanations: boolean;
        refactoring: boolean;
        documentation: boolean;
    };
    preferences: {
        language: string;
        style: 'concise' | 'detailed';
        suggestions: 'inline' | 'panel';
        autoComplete: boolean;
        autoExplain: boolean;
    };
    shortcuts: Record<string, string>;
}

export interface AIAssistantCommand {
    id: string;
    name: string;
    description: string;
    category: 'code' | 'git' | 'terminal' | 'project' | 'system';
    parameters: AIAssistantParameter[];
    execute: (params: Record<string, any>) => Promise<void>;
}

export interface AIAssistantParameter {
    name: string;
    type: 'string' | 'number' | 'boolean' | 'file' | 'directory' | 'command';
    description: string;
    required: boolean;
    default?: any;
    validation?: (value: any) => boolean;
}

export interface AIAssistantFeedback {
    id: string;
    suggestionId: string;
    rating: 'helpful' | 'not_helpful';
    comment?: string;
    timestamp: string;
    user: string;
}

export interface AIAssistantAnalytics {
    totalInteractions: number;
    successfulSuggestions: number;
    rejectedSuggestions: number;
    averageConfidence: number;
    popularCommands: Array<{ name: string; count: number }>;
    userFeedback: {
        helpful: number;
        notHelpful: number;
    };
    performance: {
        averageResponseTime: number;
        errorRate: number;
        suggestionAccuracy: number;
    };
    userEngagement: {
        activeHours: Array<{ hour: number; count: number }>;
        averageSessionLength: number;
        mostUsedFeatures: Array<{ feature: string; count: number }>;
    };
    codeMetrics: {
        languageStats: Array<{ language: string; count: number }>;
        complexityDistribution: Array<{ level: string; count: number }>;
        refactoringFrequency: number;
        bugFixRate: number;
    };
    learningMetrics: {
        skillLevels: Array<{ level: string; count: number }>;
        knowledgeGaps: Array<{ area: string; count: number }>;
        improvementAreas: Array<{ area: string; count: number }>;
        topicProgression: Array<{ topic: string; count: number }>;
    };
    visualization: {
        timeSeries: {
            interactions: Array<{ timestamp: string; count: number }>;
            suggestions: Array<{ timestamp: string; count: number }>;
            errors: Array<{ timestamp: string; count: number }>;
        };
        heatmaps: {
            activity: Array<{ day: number; hour: number; count: number }>;
            errors: Array<{ day: number; hour: number; count: number }>;
            suggestions: Array<{ day: number; hour: number; count: number }>;
        };
        distributions: {
            responseTime: Array<{ range: string; count: number }>;
            confidence: Array<{ range: string; count: number }>;
            complexity: Array<{ range: string; count: number }>;
        };
        correlations: {
            features: Array<{ feature1: string; feature2: string; correlation: number }>;
            metrics: Array<{ metric1: string; metric2: string; correlation: number }>;
        };
        trends: {
            daily: Array<{ date: string; metrics: Record<string, number> }>;
            weekly: Array<{ week: string; metrics: Record<string, number> }>;
            monthly: Array<{ month: string; metrics: Record<string, number> }>;
        };
        comparisons: {
            beforeAfter: Array<{ metric: string; before: number; after: number; change: number }>;
            benchmarks: Array<{ metric: string; current: number; target: number; industry: number }>;
        };
        predictions: {
            shortTerm: Array<{ metric: string; current: number; predicted: number; confidence: number }>;
            longTerm: Array<{ metric: string; current: number; predicted: number; confidence: number }>;
        };
        insights: {
            anomalies: Array<{ metric: string; value: number; expected: number; deviation: number }>;
            patterns: Array<{ pattern: string; confidence: number; examples: string[] }>;
            recommendations: Array<{ area: string; suggestion: string; impact: number }>;
        };
    };
}

export interface ChainOfThought {
    analysis: {
        problem: string;
        context: string;
        constraints: string[];
        assumptions: string[];
        risks: string[];
        keywords: string[];
        sentiment: 'positive' | 'negative' | 'neutral';
        complexity: {
            score: number;
            factors: Array<{ factor: string; weight: number }>;
        };
        dependencies: {
            internal: Array<{ component: string; type: string }>;
            external: Array<{ component: string; type: string }>;
        };
        impact: {
            scope: 'local' | 'module' | 'system' | 'global';
            severity: 'low' | 'medium' | 'high';
            affected: string[];
        };
    } | null;
    reasoning: {
        approach: string;
        steps: string[];
        alternatives: Array<{
            option: string;
            pros: string[];
            cons: string[];
            feasibility: number;
            confidence: number;
            complexity: number;
            risks: string[];
            dependencies: string[];
            timeline: string;
            resources: string[];
        }>;
        decision: {
            chosen: string;
            rationale: string;
            confidence: number;
            alternatives: number;
            tradeoffs: Array<{ aspect: string; impact: number }>;
            justification: {
                technical: string[];
                business: string[];
                operational: string[];
            };
        };
        metrics: {
            confidence: number;
            complexity: number;
            risk: number;
            efficiency: number;
            maintainability: number;
        };
    } | null;
    implementation: {
        strategy: string;
        steps: string[];
        dependencies: string[];
        timeline: string;
        resources: string[];
        complexity: 'low' | 'medium' | 'high';
        phases: Array<{
            name: string;
            steps: string[];
            dependencies: string[];
            timeline: string;
            resources: string[];
            risks: string[];
            validation: string[];
        }>;
        optimization: {
            performance: Array<{ aspect: string; improvement: number }>;
            resource: Array<{ resource: string; efficiency: number }>;
            cost: Array<{ factor: string; reduction: number }>;
        };
        monitoring: {
            metrics: Array<{ metric: string; threshold: number }>;
            alerts: Array<{ condition: string; severity: string }>;
            logging: Array<{ event: string; level: string }>;
        };
    } | null;
    validation: {
        criteria: string[];
        tests: string[];
        successMetrics: string[];
        fallbackPlan: string;
        coverage: number;
        scenarios: Array<{
            name: string;
            steps: string[];
            expected: string;
            actual: string;
            status: 'pass' | 'fail' | 'pending';
        }>;
        performance: {
            metrics: Array<{ metric: string; target: number; actual: number }>;
            benchmarks: Array<{ benchmark: string; score: number }>;
            bottlenecks: Array<{ component: string; impact: number }>;
        };
        security: {
            vulnerabilities: Array<{ type: string; severity: string; mitigation: string }>;
            compliance: Array<{ standard: string; status: string; gaps: string[] }>;
            threats: Array<{ threat: string; risk: string; controls: string[] }>;
        };
        reliability: {
            metrics: Array<{ metric: string; target: number; actual: number }>;
            failures: Array<{ type: string; frequency: number; impact: string }>;
            recovery: Array<{ scenario: string; time: number; success: boolean }>;
        };
    } | null;
    confidence: number;
    complexity: 'low' | 'medium' | 'high';
    metrics: {
        overall: {
            confidence: number;
            complexity: number;
            risk: number;
            efficiency: number;
            maintainability: number;
        };
        progress: {
            completed: number;
            inProgress: number;
            pending: number;
            blocked: number;
        };
        quality: {
            codeQuality: number;
            testCoverage: number;
            documentation: number;
            maintainability: number;
        };
        performance: {
            responseTime: number;
            resourceUsage: number;
            scalability: number;
            reliability: number;
        };
    };
    timeline: {
        start: string;
        end: string;
        milestones: Array<{
            name: string;
            date: string;
            status: 'completed' | 'in-progress' | 'pending';
            dependencies: string[];
        }>;
    };
    resources: {
        required: Array<{
            type: string;
            name: string;
            quantity: number;
            availability: string;
        }>;
        allocation: Array<{
            resource: string;
            start: string;
            end: string;
            usage: number;
        }>;
        constraints: Array<{
            resource: string;
            limit: number;
            current: number;
        }>;
    };
}

export interface ProjectMetadata {
    lastUpdated: string;
    totalInteractions: number;
    uniqueUsers: number;
    commandStats: Map<string, number>;
    fileStats: Map<string, number>;
    topicStats: Map<string, number>;
    entityStats: Map<string, number>;
    performanceMetrics: {
        averageResponseTime: number;
        responseTimeDistribution: Map<number, number>;
        errorRate: number;
        errorTypes: Map<string, number>;
        suggestionAccuracy: number;
        suggestionTypes: Map<string, number>;
    };
    userEngagement: {
        activeHours: Map<number, number>;
        sessionLengths: number[];
        interactionFrequency: Map<string, number>;
        featureUsage: Map<string, number>;
    };
    codeMetrics: {
        languageStats: Map<string, number>;
        complexityMetrics: Map<string, number>;
        refactoringStats: Map<string, number>;
        bugFixStats: Map<string, number>;
    };
    learningMetrics: {
        topicProgression: Map<string, number>;
        skillLevels: Map<string, number>;
        knowledgeGaps: Map<string, number>;
        improvementAreas: Map<string, number>;
    };
    analytics: {
        successfulSolutions: number;
        solutionMetrics: SolutionMetrics[];
    };
}

export interface AIAssistantContextMenu {
    items: AIAssistantContextMenuItem[];
    position: {
        x: number;
        y: number;
    };
}

export interface AIAssistantContextMenuItem {
    id: string;
    label: string;
    icon?: string;
    action: () => void;
    shortcut?: string;
    disabled?: boolean;
    children?: AIAssistantContextMenuItem[];
} 