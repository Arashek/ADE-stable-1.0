import { AgentConfig, AgentCapability } from '../services/agent/AgentService';
import { LLMEndpoint } from '../services/agent/LLMProviderService';

export function validateAgentConfig(config: Partial<AgentConfig>): string | null {
  // Check required fields
  if (!config.id) {
    return 'Agent ID is required';
  }
  if (!config.name) {
    return 'Agent name is required';
  }
  if (!config.description) {
    return 'Agent description is required';
  }
  if (!config.capabilities || !Array.isArray(config.capabilities)) {
    return 'Agent capabilities must be an array';
  }
  if (!config.defaultLLM) {
    return 'Default LLM is required';
  }
  if (!config.fallbackLLMs || !Array.isArray(config.fallbackLLMs)) {
    return 'Fallback LLMs must be an array';
  }

  // Validate capabilities
  for (const capability of config.capabilities) {
    const capabilityError = validateAgentCapability(capability);
    if (capabilityError) {
      return `Invalid capability: ${capabilityError}`;
    }
  }

  // Validate ID format (alphanumeric with hyphens and underscores)
  if (!/^[a-zA-Z0-9-_]+$/.test(config.id)) {
    return 'Agent ID must contain only alphanumeric characters, hyphens, and underscores';
  }

  // Validate name length
  if (config.name.length < 3 || config.name.length > 50) {
    return 'Agent name must be between 3 and 50 characters';
  }

  // Validate description length
  if (config.description.length < 10 || config.description.length > 500) {
    return 'Agent description must be between 10 and 500 characters';
  }

  // Validate capabilities array is not empty
  if (config.capabilities.length === 0) {
    return 'Agent must have at least one capability';
  }

  // Validate fallback LLMs don't include default LLM
  if (config.fallbackLLMs.includes(config.defaultLLM)) {
    return 'Fallback LLMs should not include the default LLM';
  }

  return null;
}

function validateAgentCapability(capability: Partial<AgentCapability>): string | null {
  // Check required fields
  if (!capability.id) {
    return 'Capability ID is required';
  }
  if (!capability.name) {
    return 'Capability name is required';
  }
  if (!capability.description) {
    return 'Capability description is required';
  }
  if (!capability.requiredLLMs || !Array.isArray(capability.requiredLLMs)) {
    return 'Required LLMs must be an array';
  }
  if (!capability.supportedActions || !Array.isArray(capability.supportedActions)) {
    return 'Supported actions must be an array';
  }

  // Validate ID format
  if (!/^[a-zA-Z0-9-_]+$/.test(capability.id)) {
    return 'Capability ID must contain only alphanumeric characters, hyphens, and underscores';
  }

  // Validate name length
  if (capability.name.length < 3 || capability.name.length > 50) {
    return 'Capability name must be between 3 and 50 characters';
  }

  // Validate description length
  if (capability.description.length < 10 || capability.description.length > 200) {
    return 'Capability description must be between 10 and 200 characters';
  }

  // Validate required LLMs array is not empty
  if (capability.requiredLLMs.length === 0) {
    return 'Capability must require at least one LLM';
  }

  // Validate supported actions array is not empty
  if (capability.supportedActions.length === 0) {
    return 'Capability must support at least one action';
  }

  // Validate parameters if present
  if (capability.parameters) {
    if (typeof capability.parameters !== 'object' || Array.isArray(capability.parameters)) {
      return 'Capability parameters must be an object';
    }
  }

  return null;
}

export function validateLLMEndpoint(endpoint: Partial<LLMEndpoint>): string | null {
  // Check required fields
  if (!endpoint.id) {
    return 'Endpoint ID is required';
  }
  if (!endpoint.url) {
    return 'Endpoint URL is required';
  }
  if (!endpoint.apiKey) {
    return 'API key is required';
  }
  if (!endpoint.model) {
    return 'Model name is required';
  }
  if (!endpoint.provider) {
    return 'Provider name is required';
  }
  if (typeof endpoint.maxTokens !== 'number') {
    return 'Max tokens must be a number';
  }
  if (typeof endpoint.temperature !== 'number') {
    return 'Temperature must be a number';
  }

  // Validate ID format
  if (!/^[a-zA-Z0-9-_]+$/.test(endpoint.id)) {
    return 'Endpoint ID must contain only alphanumeric characters, hyphens, and underscores';
  }

  // Validate URL format
  try {
    new URL(endpoint.url);
  } catch {
    return 'Invalid URL format';
  }

  // Validate API key format (non-empty string)
  if (typeof endpoint.apiKey !== 'string' || endpoint.apiKey.trim().length === 0) {
    return 'Invalid API key format';
  }

  // Validate model name format
  if (!/^[a-zA-Z0-9-]+$/.test(endpoint.model)) {
    return 'Model name must contain only alphanumeric characters and hyphens';
  }

  // Validate provider name format
  if (!/^[a-zA-Z0-9-]+$/.test(endpoint.provider)) {
    return 'Provider name must contain only alphanumeric characters and hyphens';
  }

  // Validate max tokens range
  if (endpoint.maxTokens < 1 || endpoint.maxTokens > 32000) {
    return 'Max tokens must be between 1 and 32000';
  }

  // Validate temperature range
  if (endpoint.temperature < 0 || endpoint.temperature > 1) {
    return 'Temperature must be between 0 and 1';
  }

  return null;
}