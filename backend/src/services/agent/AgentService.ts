import { singleton } from 'tsyringe';
import { Logger } from '../logger/Logger';
import { ConfigService } from '../config/ConfigService';
import { CORE_CAPABILITIES, validateCapabilityDependencies, getRequiredLLMs } from './AgentCapabilities';

export interface AgentCapability {
  id: string;
  name: string;
  description: string;
  requiredLLMs: string[];
  supportedActions: string[];
  parameters: Record<string, any>;
}

export interface AgentConfig {
  id: string;
  name: string;
  description: string;
  capabilities: AgentCapability[];
  defaultLLM: string;
  fallbackLLMs: string[];
  isActive: boolean;
  parameters?: Record<string, any>;
}

export interface AgentInventory {
  agents: Record<string, AgentConfig>;
  llmMappings: Record<string, string[]>;
  lastUpdated: Date;
  capabilityStats: Record<string, {
    totalAgents: number;
    activeAgents: number;
    verifiedAgents: number;
  }>;
}

export interface CapabilityVerificationResult {
  agentId: string;
  capabilities: Record<string, {
    verified: boolean;
    missingDependencies?: string[];
    missingLLMs?: string[];
    errors?: string[];
  }>;
  overallStatus: 'verified' | 'partial' | 'failed';
}

@singleton()
export class AgentService {
  private static instance: AgentService;
  private inventory: AgentInventory;
  private logger: Logger;
  private config: ConfigService;

  constructor(logger: Logger, config: ConfigService) {
    this.logger = logger;
    this.config = config;
    this.inventory = {
      agents: {},
      llmMappings: {},
      lastUpdated: new Date(),
      capabilityStats: {}
    };
    this.initializeCapabilityStats();
  }

  private initializeCapabilityStats(): void {
    Object.keys(CORE_CAPABILITIES).forEach(capId => {
      this.inventory.capabilityStats[capId] = {
        totalAgents: 0,
        activeAgents: 0,
        verifiedAgents: 0
      };
    });
  }

  public static getInstance(logger: Logger, config: ConfigService): AgentService {
    if (!AgentService.instance) {
      AgentService.instance = new AgentService(logger, config);
    }
    return AgentService.instance;
  }

  public async registerAgent(config: AgentConfig): Promise<void> {
    try {
      // Validate capabilities and their dependencies
      const verificationResult = await this.verifyAgentCapabilities(config.id);
      if (verificationResult.overallStatus === 'failed') {
        throw new Error(`Agent ${config.id} failed capability verification`);
      }

      this.inventory.agents[config.id] = config;
      await this.updateLLMMappings(config);
      await this.updateCapabilityStats();
      this.inventory.lastUpdated = new Date();
      this.logger.info(`Agent ${config.id} registered successfully`);
    } catch (error) {
      this.logger.error(`Failed to register agent ${config.id}:`, error);
      throw error;
    }
  }

  public async unregisterAgent(agentId: string): Promise<void> {
    try {
      delete this.inventory.agents[agentId];
      await this.rebuildLLMMappings();
      await this.updateCapabilityStats();
      this.inventory.lastUpdated = new Date();
      this.logger.info(`Agent ${agentId} unregistered successfully`);
    } catch (error) {
      this.logger.error(`Failed to unregister agent ${agentId}:`, error);
      throw error;
    }
  }

  public getAgentInventory(): AgentInventory {
    return this.inventory;
  }

  public getAgent(agentId: string): AgentConfig | undefined {
    return this.inventory.agents[agentId];
  }

  public async verifyAgentCapabilities(agentId: string): Promise<CapabilityVerificationResult> {
    const agent = this.inventory.agents[agentId];
    if (!agent) {
      throw new Error(`Agent ${agentId} not found`);
    }

    const result: CapabilityVerificationResult = {
      agentId,
      capabilities: {},
      overallStatus: 'verified'
    };

    try {
      // Verify each capability
      for (const capability of agent.capabilities) {
        result.capabilities[capability.id] = {
          verified: true
        };

        // Check capability dependencies
        const dependencies = this.getCapabilityDependencies(capability.id);
        const missingDependencies = dependencies.filter(
          dep => !agent.capabilities.some(cap => cap.id === dep)
        );

        if (missingDependencies.length > 0) {
          result.capabilities[capability.id].verified = false;
          result.capabilities[capability.id].missingDependencies = missingDependencies;
        }

        // Check LLM availability
        const requiredLLMs = capability.requiredLLMs;
        const availableLLMs = this.getAvailableLLMs(agent);
        const missingLLMs = requiredLLMs.filter(llm => !availableLLMs.includes(llm));

        if (missingLLMs.length > 0) {
          result.capabilities[capability.id].verified = false;
          result.capabilities[capability.id].missingLLMs = missingLLMs;
        }

        // If any verification failed, mark overall status as partial or failed
        if (!result.capabilities[capability.id].verified) {
          result.overallStatus = result.overallStatus === 'verified' ? 'partial' : 'failed';
        }
      }

      return result;
    } catch (error) {
      this.logger.error(`Failed to verify capabilities for agent ${agentId}:`, error);
      return {
        agentId,
        capabilities: {},
        overallStatus: 'failed'
      };
    }
  }

  private getCapabilityDependencies(capabilityId: string): string[] {
    const capability = CORE_CAPABILITIES[capabilityId];
    return capability ? (capability.parameters.dependencies || []) : [];
  }

  private getAvailableLLMs(agent: AgentConfig): string[] {
    const llms = new Set<string>();
    llms.add(agent.defaultLLM);
    agent.fallbackLLMs.forEach(llm => llms.add(llm));
    return Array.from(llms);
  }

  public async updateLLMMapping(llmId: string, endpoints: string[]): Promise<void> {
    try {
      this.inventory.llmMappings[llmId] = endpoints;
      this.inventory.lastUpdated = new Date();
      await this.updateCapabilityStats();
      this.logger.info(`LLM mapping updated for ${llmId}`);
    } catch (error) {
      this.logger.error(`Failed to update LLM mapping for ${llmId}:`, error);
      throw error;
    }
  }

  private async updateLLMMappings(config: AgentConfig): Promise<void> {
    const llms = getRequiredLLMs(config.capabilities.map(cap => cap.id));
    llms.forEach(llm => {
      if (!this.inventory.llmMappings[llm]) {
        this.inventory.llmMappings[llm] = [];
      }
    });
  }

  private async rebuildLLMMappings(): Promise<void> {
    const newMappings: Record<string, string[]> = {};
    
    Object.values(this.inventory.agents).forEach(agent => {
      const llms = getRequiredLLMs(agent.capabilities.map(cap => cap.id));
      llms.forEach(llm => {
        if (!newMappings[llm]) {
          newMappings[llm] = this.inventory.llmMappings[llm] || [];
        }
      });
    });

    this.inventory.llmMappings = newMappings;
  }

  private async updateCapabilityStats(): Promise<void> {
    // Reset stats
    this.initializeCapabilityStats();

    // Update stats based on current agents
    Object.values(this.inventory.agents).forEach(agent => {
      agent.capabilities.forEach(cap => {
        const stats = this.inventory.capabilityStats[cap.id];
        if (stats) {
          stats.totalAgents++;
          if (agent.isActive) {
            stats.activeAgents++;
          }
          // Check if capability is verified
          const verificationResult = this.verifyAgentCapabilities(agent.id);
          if (verificationResult.capabilities[cap.id]?.verified) {
            stats.verifiedAgents++;
          }
        }
      });
    });
  }

  public getCapabilityStats(): Record<string, {
    totalAgents: number;
    activeAgents: number;
    verifiedAgents: number;
  }> {
    return this.inventory.capabilityStats;
  }
} 