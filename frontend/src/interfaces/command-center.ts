import { SystemMetrics, ProcessMetrics, Alert } from './monitoring';
import { ExecutionResult, ExecutionMetrics } from './execution';
import { SecurityEvent, SecurityMetrics } from './security';
import { AIAgentResponse, AIAgentMetrics } from './ai';

export interface CommandCenterLayout {
    sidebar: {
        width: number;
        collapsed: boolean;
        sections: SidebarSection[];
    };
    mainContent: {
        layout: 'grid' | 'list';
        columns: number;
        widgets: Widget[];
    };
    header: {
        height: number;
        components: HeaderComponent[];
    };
}

export interface SidebarSection {
    id: string;
    title: string;
    icon: string;
    items: SidebarItem[];
    collapsed?: boolean;
}

export interface SidebarItem {
    id: string;
    title: string;
    icon: string;
    path: string;
    badge?: {
        count: number;
        color: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
    };
}

export interface Widget {
    id: string;
    type: WidgetType;
    title: string;
    position: {
        x: number;
        y: number;
        width: number;
        height: number;
    };
    data: any;
    refreshInterval?: number;
    actions?: WidgetAction[];
}

export type WidgetType = 
    | 'terminal'
    | 'metrics'
    | 'alerts'
    | 'execution-history'
    | 'security-events'
    | 'ai-suggestions'
    | 'resource-usage'
    | 'process-list'
    | 'network-monitor'
    | 'system-status';

export interface WidgetAction {
    id: string;
    label: string;
    icon: string;
    action: () => void;
}

export interface HeaderComponent {
    id: string;
    type: 'search' | 'notifications' | 'user-menu' | 'system-status';
    position: 'left' | 'center' | 'right';
    data?: any;
}

export interface CommandCenterState {
    layout: CommandCenterLayout;
    metrics: {
        system: SystemMetrics;
        process: ProcessMetrics[];
        execution: ExecutionMetrics;
        security: SecurityMetrics;
        ai: AIAgentMetrics;
    };
    alerts: Alert[];
    securityEvents: SecurityEvent[];
    executionHistory: ExecutionResult[];
    aiSuggestions: AIAgentResponse[];
    activeTerminals: TerminalSession[];
}

export interface TerminalSession {
    id: string;
    title: string;
    type: 'local' | 'remote' | 'ai';
    status: 'active' | 'inactive' | 'error';
    lastActivity: string;
    metrics?: ProcessMetrics;
}

export interface CommandCenterConfig {
    theme: {
        mode: 'light' | 'dark';
        primaryColor: string;
        secondaryColor: string;
    };
    layout: {
        defaultLayout: CommandCenterLayout;
        savedLayouts: CommandCenterLayout[];
    };
    notifications: {
        enabled: boolean;
        sound: boolean;
        desktop: boolean;
    };
    refreshRates: {
        metrics: number;
        alerts: number;
        security: number;
        ai: number;
    };
} 