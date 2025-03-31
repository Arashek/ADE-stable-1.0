export interface ExecutionRequest {
    command: string;
    environmentVariables?: Record<string, string>;
    timeout?: number;
    maxOutputSize?: number;
    workingDirectory?: string;
}

export interface ExecutionResult {
    success: boolean;
    output: string;
    error?: string;
    exitCode: number;
    executionTime: number;
    resourceUsage: ResourceUsage;
    timestamp: string;
    commandHash: string;
}

export interface ResourceUsage {
    cpu: {
        percent: number;
        cores: number;
    };
    memory: {
        used: number;
        total: number;
        percent: number;
    };
    disk: {
        read: number;
        written: number;
        iops: number;
    };
    network: {
        bytesSent: number;
        bytesReceived: number;
        packetsSent: number;
        packetsReceived: number;
    };
}

export interface ExecutionConfig {
    maxConcurrentExecutions: number;
    defaultTimeout: number;
    maxOutputSize: number;
    allowedCommands: string[];
    blockedCommands: string[];
    resourceLimits: {
        cpu: number;
        memory: number;
        disk: number;
        network: number;
    };
}

export interface ExecutionMetrics {
    totalExecutions: number;
    successfulExecutions: number;
    failedExecutions: number;
    averageExecutionTime: number;
    resourceUsageHistory: ResourceUsage[];
    errorRates: {
        timeout: number;
        resourceLimit: number;
        permission: number;
        other: number;
    };
}

export interface ExecutionValidation {
    isValid: boolean;
    errors: string[];
    warnings: string[];
    safetyScore: number;
    resourceImpact: {
        cpu: number;
        memory: number;
        disk: number;
        network: number;
    };
} 