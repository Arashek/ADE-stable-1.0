import { ExecutionRequest, ExecutionResult } from './execution';

export interface SecurityConfig {
    apiKey: string;
    allowedOrigins: string[];
    rateLimit: {
        requests: number;
        window: number;
    };
    commandValidation: {
        enabled: boolean;
        allowedCommands: string[];
        blockedCommands: string[];
        patterns: string[];
    };
    resourceLimits: {
        maxConcurrentExecutions: number;
        maxExecutionTime: number;
        maxOutputSize: number;
        maxMemoryUsage: number;
        maxCpuUsage: number;
    };
    logging: {
        enabled: boolean;
        level: 'debug' | 'info' | 'warning' | 'error';
        retention: number;
    };
}

export interface SecurityContext {
    clientIp: string;
    userAgent: string;
    timestamp: string;
    sessionId: string;
    requestId: string;
}

export interface SecurityValidation {
    isValid: boolean;
    errors: string[];
    warnings: string[];
    riskLevel: 'low' | 'medium' | 'high';
    checks: SecurityCheck[];
}

export interface SecurityCheck {
    type: 'authentication' | 'authorization' | 'rateLimit' | 'command' | 'resource';
    status: 'passed' | 'failed' | 'warning';
    message: string;
    details?: any;
}

export interface SecurityEvent {
    id: string;
    type: 'request' | 'execution' | 'error' | 'violation';
    severity: 'info' | 'warning' | 'error' | 'critical';
    timestamp: string;
    context: SecurityContext;
    details: {
        request?: ExecutionRequest;
        result?: ExecutionResult;
        validation?: SecurityValidation;
        error?: string;
    };
}

export interface SecurityMetrics {
    totalRequests: number;
    blockedRequests: number;
    rateLimitViolations: number;
    commandViolations: number;
    resourceViolations: number;
    averageResponseTime: number;
    events: SecurityEvent[];
    riskTrends: {
        timestamp: string;
        riskLevel: 'low' | 'medium' | 'high';
    }[];
}

export interface SecurityPolicy {
    name: string;
    description: string;
    rules: SecurityRule[];
    priority: number;
    enabled: boolean;
}

export interface SecurityRule {
    id: string;
    type: 'allow' | 'deny' | 'warn';
    condition: string;
    action: string;
    priority: number;
    metadata?: Record<string, any>;
} 