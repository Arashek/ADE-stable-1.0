import { singleton } from 'tsyringe';
import { Logger } from '../logger/Logger';
import { ConfigService } from '../config/ConfigService';

export interface LLMEndpoint {
  id: string;
  url: string;
  apiKey: string;
  model: string;
  provider: string;
  maxTokens: number;
  temperature: number;
  isActive: boolean;
}

export interface LLMProvider {
  name: string;
  models: string[];
  baseUrl: string;
  defaultHeaders: Record<string, string>;
  rateLimit: {
    requests: number;
    window: number;  // in seconds
  };
}

@singleton()
export class LLMProviderService {
  private static instance: LLMProviderService;
  private endpoints: Map<string, LLMEndpoint>;
  private providers: Map<string, LLMProvider>;
  private logger: Logger;
  private config: ConfigService;

  constructor(logger: Logger, config: ConfigService) {
    this.logger = logger;
    this.config = config;
    this.endpoints = new Map();
    this.providers = new Map();
    this.initializeDefaultProviders();
  }

  public static getInstance(logger: Logger, config: ConfigService): LLMProviderService {
    if (!LLMProviderService.instance) {
      LLMProviderService.instance = new LLMProviderService(logger, config);
    }
    return LLMProviderService.instance;
  }

  private initializeDefaultProviders(): void {
    // Initialize Anthropic (Claude) provider
    this.providers.set('anthropic', {
      name: 'Anthropic',
      models: ['claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku'],
      baseUrl: 'https://api.anthropic.com/v1',
      defaultHeaders: {
        'anthropic-version': '2023-06-01'
      },
      rateLimit: {
        requests: 50,
        window: 60
      }
    });

    // Initialize OpenAI provider
    this.providers.set('openai', {
      name: 'OpenAI',
      models: ['gpt-4-turbo', 'gpt-4', 'gpt-3.5-turbo'],
      baseUrl: 'https://api.openai.com/v1',
      defaultHeaders: {},
      rateLimit: {
        requests: 60,
        window: 60
      }
    });

    // Initialize Azure OpenAI provider
    this.providers.set('azure', {
      name: 'Azure OpenAI',
      models: ['gpt-4', 'gpt-35-turbo'],
      baseUrl: 'https://{resource}.openai.azure.com',
      defaultHeaders: {
        'api-version': '2023-05-15'
      },
      rateLimit: {
        requests: 100,
        window: 60
      }
    });
  }

  public async registerEndpoint(endpoint: LLMEndpoint): Promise<void> {
    try {
      const provider = this.providers.get(endpoint.provider);
      if (!provider) {
        throw new Error(`Provider ${endpoint.provider} not found`);
      }

      if (!provider.models.includes(endpoint.model)) {
        throw new Error(`Model ${endpoint.model} not supported by provider ${endpoint.provider}`);
      }

      this.endpoints.set(endpoint.id, endpoint);
      this.logger.info(`Registered LLM endpoint ${endpoint.id} for provider ${endpoint.provider}`);
    } catch (error) {
      this.logger.error(`Failed to register LLM endpoint ${endpoint.id}:`, error);
      throw error;
    }
  }

  public async unregisterEndpoint(endpointId: string): Promise<void> {
    try {
      this.endpoints.delete(endpointId);
      this.logger.info(`Unregistered LLM endpoint ${endpointId}`);
    } catch (error) {
      this.logger.error(`Failed to unregister LLM endpoint ${endpointId}:`, error);
      throw error;
    }
  }

  public getEndpoint(endpointId: string): LLMEndpoint | undefined {
    return this.endpoints.get(endpointId);
  }

  public getActiveEndpoints(): LLMEndpoint[] {
    return Array.from(this.endpoints.values()).filter(endpoint => endpoint.isActive);
  }

  public getEndpointsByProvider(provider: string): LLMEndpoint[] {
    return Array.from(this.endpoints.values())
      .filter(endpoint => endpoint.provider === provider && endpoint.isActive);
  }

  public getEndpointsByModel(model: string): LLMEndpoint[] {
    return Array.from(this.endpoints.values())
      .filter(endpoint => endpoint.model === model && endpoint.isActive);
  }

  public getProvider(providerName: string): LLMProvider | undefined {
    return this.providers.get(providerName);
  }

  public getAllProviders(): LLMProvider[] {
    return Array.from(this.providers.values());
  }

  public async updateEndpointStatus(endpointId: string, isActive: boolean): Promise<void> {
    const endpoint = this.endpoints.get(endpointId);
    if (!endpoint) {
      throw new Error(`Endpoint ${endpointId} not found`);
    }

    endpoint.isActive = isActive;
    this.logger.info(`Updated status for endpoint ${endpointId} to ${isActive ? 'active' : 'inactive'}`);
  }

  public async validateEndpoint(endpoint: LLMEndpoint): Promise<boolean> {
    try {
      const provider = this.providers.get(endpoint.provider);
      if (!provider) {
        return false;
      }

      // Validate URL format
      try {
        new URL(endpoint.url);
      } catch {
        return false;
      }

      // Validate model compatibility
      if (!provider.models.includes(endpoint.model)) {
        return false;
      }

      // Validate token limits
      if (endpoint.maxTokens <= 0) {
        return false;
      }

      // Validate temperature range
      if (endpoint.temperature < 0 || endpoint.temperature > 1) {
        return false;
      }

      return true;
    } catch (error) {
      this.logger.error(`Failed to validate endpoint ${endpoint.id}:`, error);
      return false;
    }
  }
} 