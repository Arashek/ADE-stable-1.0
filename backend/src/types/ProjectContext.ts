export interface ProjectContext {
    name: string;
    description: string;
    type: 'web' | 'mobile' | 'desktop';
    framework: string;
    dependencies: {
        [key: string]: string;
    };
    designTokens?: {
        colors?: Record<string, string>;
        typography?: Record<string, any>;
        spacing?: Record<string, any>;
    };
    existingComponents?: string[];
    targetAudience?: string[];
    browserSupport?: string[];
    accessibility?: {
        level: 'A' | 'AA' | 'AAA';
        requirements: string[];
    };
    performance?: {
        targets: {
            firstContentfulPaint?: number;
            timeToInteractive?: number;
            speedIndex?: number;
        };
    };
    repository?: {
        url: string;
        branch: string;
    };
} 