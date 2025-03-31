import { ExecutionResult } from './execution';

export interface SystemMetrics {
    cpu: number;
    memory: number;
    disk: number;
    network: number;
}

export interface ProcessMetrics {
    cpu: number;
    memory: number;
    threads: number;
    handles: number;
}

export interface AIAgentConfig {
    model: string;
    temperature: number;
    maxTokens: number;
    apiKey: string;
}

export interface AIAgentContext {
    systemMetrics: SystemMetrics;
    processMetrics: ProcessMetrics;
    executionHistory: ExecutionResult[];
    availableCommands: string[];
    environmentVariables: Record<string, string>;
}

export interface AIAgentResponse {
    command?: string;
    explanation: string;
    expectedOutcome: string;
    safetyChecks: SafetyCheck[];
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
    environmentVariables?: Record<string, string>;
}

export interface SafetyCheck {
    type: 'command' | 'resource' | 'permission' | 'environment';
    status: 'safe' | 'warning' | 'dangerous';
    message: string;
    details?: any;
}

export interface AIExecutionRequest {
    prompt: string;
    context: AIAgentContext;
    config: AIAgentConfig;
    projectHistory?: AIAssistantHistory[];
}

export interface AIExecutionResponse {
    response: AIAgentResponse;
    executionResult?: ExecutionResult;
    error?: string;
}

export interface AIAgentMetrics {
    responseTime: number;
    tokenUsage: {
        prompt: number;
        completion: number;
    };
    safetyChecks: SafetyCheck[];
    resourceUsage: {
        cpu: number;
        memory: number;
        network: number;
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