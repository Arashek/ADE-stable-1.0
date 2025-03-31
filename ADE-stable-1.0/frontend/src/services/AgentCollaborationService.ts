import { Socket } from '../types/socket';
import { v4 as uuidv4 } from 'uuid';

export interface Agent {
  id: string;
  type: AgentType;
  name: string;
  status: 'active' | 'idle' | 'busy';
  currentTask?: string;
  capabilities: string[];
  lastUpdate: Date;
}

export type AgentType = 
  | 'project-manager'
  | 'code-implementer'
  | 'designer'
  | 'architect'
  | 'reviewer'
  | 'tester'
  | 'documentation'
  | 'integration';

export interface AgentTask {
  id: string;
  type: string;
  description: string;
  assignedTo: string[];
  status: 'pending' | 'in-progress' | 'completed' | 'blocked';
  dependencies: string[];
  priority: 'low' | 'medium' | 'high';
  createdAt: Date;
  updatedAt: Date;
}

export interface CodebaseMap {
  components: Map<string, ComponentInfo>;
  relationships: Map<string, RelationshipInfo>;
  dependencies: Map<string, DependencyInfo>;
  lastUpdate: Date;
}

interface ComponentInfo {
  id: string;
  type: string;
  name: string;
  path: string;
  dependencies: string[];
  createdBy: string;
  lastModified: Date;
  status: 'stable' | 'in-development' | 'needs-review';
}

interface RelationshipInfo {
  id: string;
  source: string;
  target: string;
  type: string;
  description: string;
  createdBy: string;
  lastModified: Date;
}

interface DependencyInfo {
  id: string;
  component: string;
  dependency: string;
  type: string;
  version: string;
  status: 'active' | 'outdated' | 'conflict';
}

export class AgentCollaborationService {
  private ws: Socket;
  private projectId: string;
  private agents: Map<string, Agent> = new Map();
  private tasks: Map<string, AgentTask> = new Map();
  private codebaseMap: CodebaseMap;
  private sessionId: string;

  constructor(config: { ws: Socket; projectId: string }) {
    this.ws = config.ws;
    this.projectId = config.projectId;
    this.sessionId = uuidv4();
    this.codebaseMap = {
      components: new Map(),
      relationships: new Map(),
      dependencies: new Map(),
      lastUpdate: new Date()
    };
  }

  public async initialize() {
    this.setupEventListeners();
    this.registerAgents();
    await this.initializeCodebaseMap();
  }

  private setupEventListeners() {
    // Agent status updates
    this.ws.on('agent:status-update', (data: { agentId: string; status: Agent['status'] }) => {
      const agent = this.agents.get(data.agentId);
      if (agent) {
        agent.status = data.status;
        this.updateAgentStatus(agent);
      }
    });

    // Task updates
    this.ws.on('task:update', (data: { taskId: string; updates: Partial<AgentTask> }) => {
      const task = this.tasks.get(data.taskId);
      if (task) {
        Object.assign(task, data.updates);
        this.updateTaskStatus(task);
      }
    });

    // Codebase changes
    this.ws.on('codebase:change', (data: { componentId: string; changes: any }) => {
      this.handleCodebaseChange(data);
    });

    // Agent communication
    this.ws.on('agent:message', (data: { from: string; to: string; message: any }) => {
      this.handleAgentMessage(data);
    });
  }

  private async registerAgents() {
    const agentTypes: AgentType[] = [
      'project-manager',
      'code-implementer',
      'designer',
      'architect',
      'reviewer',
      'tester',
      'documentation',
      'integration'
    ];

    for (const type of agentTypes) {
      const agent: Agent = {
        id: uuidv4(),
        type,
        name: this.getAgentName(type),
        status: 'idle',
        capabilities: this.getAgentCapabilities(type),
        lastUpdate: new Date()
      };

      this.agents.set(agent.id, agent);
      this.ws.emit('agent:register', {
        projectId: this.projectId,
        agent
      });
    }
  }

  private getAgentName(type: AgentType): string {
    const names: Record<AgentType, string> = {
      'project-manager': 'Project Manager',
      'code-implementer': 'Code Implementer',
      'designer': 'UI/UX Designer',
      'architect': 'System Architect',
      'reviewer': 'Code Reviewer',
      'tester': 'Quality Assurance',
      'documentation': 'Documentation Specialist',
      'integration': 'Integration Specialist'
    };
    return names[type];
  }

  private getAgentCapabilities(type: AgentType): string[] {
    const capabilities: Record<AgentType, string[]> = {
      'project-manager': ['task-management', 'coordination', 'progress-tracking'],
      'code-implementer': ['coding', 'refactoring', 'bug-fixing'],
      'designer': ['ui-design', 'ux-design', 'prototyping'],
      'architect': ['system-design', 'architecture-planning', 'scalability'],
      'reviewer': ['code-review', 'best-practices', 'security'],
      'tester': ['testing', 'qa', 'performance'],
      'documentation': ['documentation', 'api-docs', 'user-guides'],
      'integration': ['integration', 'deployment', 'ci-cd']
    };
    return capabilities[type];
  }

  private async initializeCodebaseMap() {
    this.ws.emit('codebase:initialize', {
      projectId: this.projectId,
      sessionId: this.sessionId
    }, (data: any) => {
      this.updateCodebaseMap(data);
    });
  }

  private updateCodebaseMap(data: any) {
    // Update components
    data.components.forEach((comp: ComponentInfo) => {
      this.codebaseMap.components.set(comp.id, comp);
    });

    // Update relationships
    data.relationships.forEach((rel: RelationshipInfo) => {
      this.codebaseMap.relationships.set(rel.id, rel);
    });

    // Update dependencies
    data.dependencies.forEach((dep: DependencyInfo) => {
      this.codebaseMap.dependencies.set(dep.id, dep);
    });

    this.codebaseMap.lastUpdate = new Date();
  }

  private handleCodebaseChange(data: { componentId: string; changes: any }) {
    const component = this.codebaseMap.components.get(data.componentId);
    if (component) {
      // Update component
      Object.assign(component, data.changes);
      component.lastModified = new Date();

      // Notify relevant agents
      this.notifyRelevantAgents(component);
    }
  }

  private notifyRelevantAgents(component: ComponentInfo) {
    const relevantAgents = Array.from(this.agents.values()).filter(agent => {
      switch (agent.type) {
        case 'architect':
          return component.type === 'system' || component.type === 'architecture';
        case 'reviewer':
          return true; // Reviewers should be notified of all changes
        case 'tester':
          return component.type === 'feature' || component.type === 'bug-fix';
        case 'documentation':
          return component.type === 'api' || component.type === 'feature';
        default:
          return false;
      }
    });

    relevantAgents.forEach(agent => {
      this.ws.emit('agent:notification', {
        projectId: this.projectId,
        agentId: agent.id,
        type: 'codebase-change',
        data: {
          componentId: component.id,
          changes: component
        }
      });
    });
  }

  private handleAgentMessage(data: { from: string; to: string; message: any }) {
    const fromAgent = this.agents.get(data.from);
    const toAgent = this.agents.get(data.to);

    if (fromAgent && toAgent) {
      // Process message based on type
      switch (data.message.type) {
        case 'task-assignment':
          this.handleTaskAssignment(data.message);
          break;
        case 'code-review-request':
          this.handleCodeReviewRequest(data.message);
          break;
        case 'design-review-request':
          this.handleDesignReviewRequest(data.message);
          break;
        case 'integration-request':
          this.handleIntegrationRequest(data.message);
          break;
      }
    }
  }

  private handleTaskAssignment(message: any) {
    const task: AgentTask = {
      id: uuidv4(),
      type: message.taskType,
      description: message.description,
      assignedTo: message.assignedTo,
      status: 'pending',
      dependencies: message.dependencies || [],
      priority: message.priority || 'medium',
      createdAt: new Date(),
      updatedAt: new Date()
    };

    this.tasks.set(task.id, task);
    this.ws.emit('task:created', {
      projectId: this.projectId,
      task
    });
  }

  private handleCodeReviewRequest(message: any) {
    const reviewer = Array.from(this.agents.values())
      .find(agent => agent.type === 'reviewer' && agent.status === 'idle');

    if (reviewer) {
      this.ws.emit('agent:message', {
        projectId: this.projectId,
        from: message.from,
        to: reviewer.id,
        message: {
          type: 'code-review-request',
          data: message.data
        }
      });
    }
  }

  private handleDesignReviewRequest(message: any) {
    const designer = Array.from(this.agents.values())
      .find(agent => agent.type === 'designer' && agent.status === 'idle');

    if (designer) {
      this.ws.emit('agent:message', {
        projectId: this.projectId,
        from: message.from,
        to: designer.id,
        message: {
          type: 'design-review-request',
          data: message.data
        }
      });
    }
  }

  private handleIntegrationRequest(message: any) {
    const integrator = Array.from(this.agents.values())
      .find(agent => agent.type === 'integration' && agent.status === 'idle');

    if (integrator) {
      this.ws.emit('agent:message', {
        projectId: this.projectId,
        from: message.from,
        to: integrator.id,
        message: {
          type: 'integration-request',
          data: message.data
        }
      });
    }
  }

  private updateAgentStatus(agent: Agent) {
    this.ws.emit('agent:status-updated', {
      projectId: this.projectId,
      agentId: agent.id,
      status: agent.status
    });
  }

  private updateTaskStatus(task: AgentTask) {
    this.ws.emit('task:status-updated', {
      projectId: this.projectId,
      taskId: task.id,
      status: task.status
    });
  }

  public dispose() {
    this.ws.emit('agent:dispose', {
      projectId: this.projectId,
      sessionId: this.sessionId
    });
    this.agents.clear();
    this.tasks.clear();
    this.codebaseMap.components.clear();
    this.codebaseMap.relationships.clear();
    this.codebaseMap.dependencies.clear();
  }
} 