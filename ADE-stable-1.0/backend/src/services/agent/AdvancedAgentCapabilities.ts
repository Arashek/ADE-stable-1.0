import { AgentCapability } from './AgentCapabilities';
import { injectable } from 'tsyringe';

@injectable()
export class AdvancedAgentCapabilities {
  private advancedCapabilities: AgentCapability[] = [
    {
      id: 'code-generation',
      name: 'Code Generation',
      description: 'Generate code based on specifications and requirements',
      requiredLLMs: ['claude-3-opus', 'gpt-4-turbo'],
      supportedActions: [
        'generate-code',
        'refactor-code',
        'optimize-code',
        'document-code'
      ],
      parameters: {
        maxTokens: 4000,
        temperature: 0.7,
        topP: 0.9,
        frequencyPenalty: 0.5,
        presencePenalty: 0.5
      }
    },
    {
      id: 'code-review',
      name: 'Code Review',
      description: 'Perform automated code reviews and suggest improvements',
      requiredLLMs: ['claude-3-opus', 'gpt-4-turbo'],
      supportedActions: [
        'review-code',
        'suggest-improvements',
        'check-best-practices',
        'security-audit'
      ],
      parameters: {
        maxTokens: 2000,
        temperature: 0.3,
        topP: 0.8,
        severityLevels: ['critical', 'high', 'medium', 'low']
      }
    },
    {
      id: 'test-generation',
      name: 'Test Generation',
      description: 'Generate unit tests and integration tests for code',
      requiredLLMs: ['claude-3-opus', 'gpt-4-turbo'],
      supportedActions: [
        'generate-unit-tests',
        'generate-integration-tests',
        'generate-test-cases',
        'coverage-analysis'
      ],
      parameters: {
        maxTokens: 3000,
        temperature: 0.5,
        topP: 0.9,
        testFrameworks: ['jest', 'mocha', 'pytest']
      }
    },
    {
      id: 'documentation',
      name: 'Documentation',
      description: 'Generate and maintain code documentation',
      requiredLLMs: ['claude-3-opus', 'gpt-4-turbo'],
      supportedActions: [
        'generate-docs',
        'update-docs',
        'api-documentation',
        'code-comments'
      ],
      parameters: {
        maxTokens: 2000,
        temperature: 0.3,
        topP: 0.8,
        docFormats: ['markdown', 'html', 'pdf']
      }
    },
    {
      id: 'performance-optimization',
      name: 'Performance Optimization',
      description: 'Analyze and optimize code performance',
      requiredLLMs: ['claude-3-opus', 'gpt-4-turbo'],
      supportedActions: [
        'profile-code',
        'optimize-algorithms',
        'memory-optimization',
        'cpu-optimization'
      ],
      parameters: {
        maxTokens: 2500,
        temperature: 0.4,
        topP: 0.8,
        metrics: ['execution-time', 'memory-usage', 'cpu-usage']
      }
    },
    {
      id: 'security-analysis',
      name: 'Security Analysis',
      description: 'Perform security analysis and vulnerability scanning',
      requiredLLMs: ['claude-3-opus', 'gpt-4-turbo'],
      supportedActions: [
        'vulnerability-scan',
        'security-audit',
        'compliance-check',
        'threat-modeling'
      ],
      parameters: {
        maxTokens: 2000,
        temperature: 0.2,
        topP: 0.7,
        securityLevels: ['critical', 'high', 'medium', 'low']
      }
    },
    {
      id: 'dependency-management',
      name: 'Dependency Management',
      description: 'Manage and optimize project dependencies',
      requiredLLMs: ['claude-3-opus', 'gpt-4-turbo'],
      supportedActions: [
        'update-dependencies',
        'security-audit',
        'version-compatibility',
        'dependency-optimization'
      ],
      parameters: {
        maxTokens: 1500,
        temperature: 0.3,
        topP: 0.8,
        packageManagers: ['npm', 'pip', 'maven', 'gradle']
      }
    },
    {
      id: 'deployment-automation',
      name: 'Deployment Automation',
      description: 'Automate deployment processes and infrastructure',
      requiredLLMs: ['claude-3-opus', 'gpt-4-turbo'],
      supportedActions: [
        'generate-deployment-scripts',
        'infrastructure-as-code',
        'ci-cd-pipeline',
        'containerization'
      ],
      parameters: {
        maxTokens: 3000,
        temperature: 0.4,
        topP: 0.8,
        platforms: ['aws', 'azure', 'gcp', 'kubernetes']
      }
    }
  ];

  public getCapabilities(): AgentCapability[] {
    return this.advancedCapabilities;
  }

  public getCapabilityById(id: string): AgentCapability | undefined {
    return this.advancedCapabilities.find(cap => cap.id === id);
  }

  public getCapabilitiesByLLM(llmId: string): AgentCapability[] {
    return this.advancedCapabilities.filter(cap => 
      cap.requiredLLMs.includes(llmId)
    );
  }

  public getCapabilitiesByAction(action: string): AgentCapability[] {
    return this.advancedCapabilities.filter(cap => 
      cap.supportedActions.includes(action)
    );
  }
} 