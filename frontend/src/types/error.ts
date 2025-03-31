export interface APIError {
    message: string;
    code: string;
    details?: Record<string, any>;
    status?: number;
}

export interface ValidationError extends APIError {
    field: string;
    value: any;
    constraint: string;
}

export interface AuthenticationError extends APIError {
    token?: string;
    expiresAt?: string;
}

export interface AuthorizationError extends APIError {
    requiredPermissions: string[];
    currentPermissions: string[];
}

export interface NetworkError extends APIError {
    status: number;
    url: string;
    method: string;
}

export interface RateLimitError extends APIError {
    limit: number;
    remaining: number;
    reset: string;
} 