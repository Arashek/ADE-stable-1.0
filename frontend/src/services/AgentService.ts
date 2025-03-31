import { Observable, Subject } from 'rxjs';
import { MonitoringService } from './monitoring.service';
import { WebSocketService } from './websocket.service';
import { PerformanceMetric } from '../types/metrics';
import { Agent, AgentTask, AgentResponse } from '../types/agent';

export class AgentService {
    private static instance: AgentService;
    private readonly API_BASE = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
    private readonly wsService: WebSocketService;
    private readonly monitoring: MonitoringService;
    private agentSubject = new Subject<Agent[]>();
    private taskSubject = new Subject<AgentTask>();

    private constructor() {
        this.wsService = WebSocketService.getInstance();
        this.monitoring = MonitoringService.getInstance();
        this.setupWebSocketListeners();
    }

    static getInstance(): AgentService {
        if (!AgentService.instance) {
            AgentService.instance = new AgentService();
        }
        return AgentService.instance;
    }

    private setupWebSocketListeners(): void {
        this.wsService.subscribe('agent_update', (data: any) => {
            this.agentSubject.next(data.agents);
        });

        this.wsService.subscribe('task_update', (data: any) => {
            this.taskSubject.next(data.task);
        });
    }

    async getAgents(): Promise<Agent[]> {
        try {
            const response = await fetch(`${this.API_BASE}/api/agents`);
            const data = await response.json();
            return data.agents;
        } catch (error) {
            this.monitoring.recordError('get_agents_failed', error);
            throw error;
        }
    }

    async executeTask(task: AgentTask): Promise<AgentResponse> {
        const startTime = performance.now();

        try {
            const response = await fetch(`${this.API_BASE}/api/agents/execute`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(task),
            });

            const data = await response.json();

            // Record metrics
            const duration = performance.now() - startTime;
            this.monitoring.recordMetric({
                category: 'agent_task',
                name: task.type,
                value: duration,
                tags: { agent_id: task.agent_id }
            });

            return data;
        } catch (error) {
            this.monitoring.recordError('execute_task_failed', error);
            throw error;
        }
    }

    async evaluateSolution(solution: any): Promise<AgentResponse> {
        try {
            const response = await fetch(`${this.API_BASE}/api/agents/evaluate`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ solution }),
            });

            return await response.json();
        } catch (error) {
            this.monitoring.recordError('evaluate_solution_failed', error);
            throw error;
        }
    }

    async getAgentMetrics(agentId: string): Promise<PerformanceMetric[]> {
        try {
            const response = await fetch(
                `${this.API_BASE}/api/agents/${agentId}/metrics`
            );
            return await response.json();
        } catch (error) {
            this.monitoring.recordError('get_metrics_failed', error);
            throw error;
        }
    }

    watchAgents(): Observable<Agent[]> {
        return this.agentSubject.asObservable();
    }

    watchTasks(): Observable<AgentTask> {
        return this.taskSubject.asObservable();
    }

    async updateAgentConfig(
        agentId: string,
        config: Partial<Agent>
    ): Promise<Agent> {
        try {
            const response = await fetch(
                `${this.API_BASE}/api/agents/${agentId}/config`,
                {
                    method: 'PATCH',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(config),
                }
            );

            return await response.json();
        } catch (error) {
            this.monitoring.recordError('update_config_failed', error);
            throw error;
        }
    }
}
