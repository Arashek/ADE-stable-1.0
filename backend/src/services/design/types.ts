import { ProjectContext } from '../../types/ProjectContext';

export interface DesignRequest {
    id: string;
    requirements: string[];
    projectContext: ProjectContext;
    constraints?: {
        responsive?: boolean;
        accessibility?: string[];
        theme?: string;
        platform?: string[];
    };
    style?: {
        colorScheme?: string;
        typography?: string;
        spacing?: string;
        layout?: string;
    };
    dimensions?: {
        width: number;
        height: number;
    };
    assetRequirements?: string[];
    assetFormat?: 'svg' | 'png' | 'jpg';
}

export interface DesignResponse {
    id: string;
    mockup: string; // Base64 encoded image
    styles: string; // CSS/SCSS code
    components: UIComponent[];
    designSystem: DesignSystem;
    timestamp: string;
}

export interface UIComponent {
    id: string;
    name: string;
    type: string;
    props: Record<string, any>;
    children?: UIComponent[];
    styles: string;
    context?: {
        parent?: string;
        siblings?: string[];
        depth: number;
    };
}

export interface DesignSystem {
    colors: {
        primary: string;
        secondary: string;
        accent: string;
        background: string;
        text: string;
        [key: string]: string;
    };
    typography: {
        fontFamily: string;
        headings: Record<string, any>;
        body: Record<string, any>;
    };
    spacing: {
        unit: number;
        scale: number[];
    };
    breakpoints: {
        [key: string]: number;
    };
}

export interface DesignFeedback {
    analysis: {
        usability: {
            score: number;
            issues: string[];
            recommendations: string[];
        };
        accessibility: {
            score: number;
            issues: string[];
            recommendations: string[];
        };
        consistency: {
            score: number;
            issues: string[];
            recommendations: string[];
        };
        performance: {
            score: number;
            issues: string[];
            recommendations: string[];
        };
    };
    suggestions: string;
    timestamp: string;
} 