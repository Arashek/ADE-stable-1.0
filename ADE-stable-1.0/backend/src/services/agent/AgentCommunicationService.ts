import { EventEmitter } from 'events';
import { Agent, AgentType } from './AgentRegistry';
import { MessageQueue } from '../queue/MessageQueue';
import { Redis } from 'ioredis';

interface AgentMessage {
  id: string;
  from: string;
  to: string[];
  type: 'request' | 'response' | 'notification' | 'error';
  content: any;
  metadata: {
    timestamp: number;
    priority: 'low' | 'medium' | 'high';
    requiresResponse: boolean;
    timeout?: number;
    retryCount?: number;
  };
}

interface AgentCommunicationConfig {
  redisUrl: string;
  messageQueueUrl: string;
  maxRetries: number;
  defaultTimeout: number;
}

export class AgentCommunicationService extends EventEmitter {
  private redis: Redis;
  private messageQueue: MessageQueue;
  private agents: Map<string, Agent> = new Map();
  private messageHandlers: Map<string, (message: AgentMessage) => Promise<void>> = new Map();
  private pendingResponses: Map<string, {
    resolve: (value: any) => void;
    reject: (error: Error) => void;
    timeout: NodeJS.Timeout;
  }> = new Map();

  constructor(config: AgentCommunicationConfig) {
    super();
    this.redis = new Redis(config.redisUrl);
    this.messageQueue = new MessageQueue(config.messageQueueUrl);
    this.setupMessageHandlers();
  }

  private setupMessageHandlers() {
    // Handle code analysis requests
    this.messageHandlers.set('code_analysis', async (message: AgentMessage) => {
      const codeAgent = this.getAgentByType('code-implementer');
      if (!codeAgent) {
        throw new Error('Code implementer agent not available');
      }
      return this.forwardToAgent(codeAgent, message);
    });

    // Handle design requests
    this.messageHandlers.set('design_request', async (message: AgentMessage) => {
      const designAgent = this.getAgentByType('designer');
      if (!designAgent) {
        throw new Error('Design agent not available');
      }
      return this.forwardToAgent(designAgent, message);
    });

    // Handle architecture decisions
    this.messageHandlers.set('architecture_decision', async (message: AgentMessage) => {
      const architectAgent = this.getAgentByType('architect');
      if (!architectAgent) {
        throw new Error('Architect agent not available');
      }
      return this.forwardToAgent(architectAgent, message);
    });
  }

  public async registerAgent(agent: Agent) {
    this.agents.set(agent.id, agent);
    await this.redis.sadd('active_agents', agent.id);
    await this.redis.hset(`agent:${agent.id}`, {
      type: agent.type,
      status: agent.status,
      capabilities: JSON.stringify(agent.capabilities),
      lastUpdate: Date.now()
    });
  }

  public async unregisterAgent(agentId: string) {
    this.agents.delete(agentId);
    await this.redis.srem('active_agents', agentId);
    await this.redis.del(`agent:${agentId}`);
  }

  public async sendMessage(message: AgentMessage): Promise<any> {
    if (message.metadata.requiresResponse) {
      return new Promise((resolve, reject) => {
        const timeout = setTimeout(() => {
          this.pendingResponses.delete(message.id);
          reject(new Error('Message timeout'));
        }, message.metadata.timeout || 30000);

        this.pendingResponses.set(message.id, { resolve, reject, timeout });

        this.messageQueue.publish('agent_messages', message);
      });
    } else {
      await this.messageQueue.publish('agent_messages', message);
    }
  }

  public async handleMessage(message: AgentMessage) {
    const handler = this.messageHandlers.get(message.type);
    if (handler) {
      try {
        const response = await handler(message);
        if (message.metadata.requiresResponse) {
          const pending = this.pendingResponses.get(message.id);
          if (pending) {
            pending.resolve(response);
            clearTimeout(pending.timeout);
            this.pendingResponses.delete(message.id);
          }
        }
      } catch (error) {
        if (message.metadata.requiresResponse) {
          const pending = this.pendingResponses.get(message.id);
          if (pending) {
            pending.reject(error);
            clearTimeout(pending.timeout);
            this.pendingResponses.delete(message.id);
          }
        }
        throw error;
      }
    }
  }

  private getAgentByType(type: AgentType): Agent | undefined {
    return Array.from(this.agents.values()).find(agent => agent.type === type);
  }

  private async forwardToAgent(agent: Agent, message: AgentMessage): Promise<any> {
    if (agent.status !== 'active') {
      throw new Error(`Agent ${agent.id} is not active`);
    }

    const retryCount = message.metadata.retryCount || 0;
    if (retryCount >= 3) {
      throw new Error('Max retries exceeded');
    }

    try {
      const response = await this.messageQueue.publish(`agent:${agent.id}`, message);
      return response;
    } catch (error) {
      if (message.metadata.requiresResponse) {
        message.metadata.retryCount = retryCount + 1;
        return this.forwardToAgent(agent, message);
      }
      throw error;
    }
  }

  public async getAgentStatus(agentId: string): Promise<{
    status: string;
    lastUpdate: number;
    capabilities: string[];
  } | null> {
    const agentData = await this.redis.hgetall(`agent:${agentId}`);
    if (!agentData || Object.keys(agentData).length === 0) {
      return null;
    }

    return {
      status: agentData.status,
      lastUpdate: parseInt(agentData.lastUpdate),
      capabilities: JSON.parse(agentData.capabilities)
    };
  }

  public async getActiveAgents(): Promise<Agent[]> {
    const agentIds = await this.redis.smembers('active_agents');
    return Promise.all(
      agentIds.map(async (id) => {
        const agentData = await this.redis.hgetall(`agent:${id}`);
        return {
          id,
          type: agentData.type as AgentType,
          status: agentData.status as 'active' | 'idle' | 'busy',
          capabilities: JSON.parse(agentData.capabilities),
          lastUpdate: new Date(parseInt(agentData.lastUpdate))
        };
      })
    );
  }
} 