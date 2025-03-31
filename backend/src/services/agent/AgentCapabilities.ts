import { AgentCapability } from './AgentService';

export const CORE_CAPABILITIES: Record<string, AgentCapability> = {
  CODE_AWARENESS: {
    id: 'code-awareness',
    name: 'Code Awareness',
    description: 'Ability to understand, analyze, and modify code across multiple programming languages',
    requiredLLMs: ['claude-3-opus', 'gpt-4-turbo'],
    supportedActions: [
      'analyze_code',
      'suggest_improvements',
      'detect_patterns',
      'explain_code',
      'find_bugs'
    ],
    parameters: {
      supportedLanguages: [
        'typescript',
        'javascript',
        'python',
        'java',
        'c++',
        'rust',
        'go'
      ],
      maxFileSize: 10485760, // 10MB
      contextWindow: 16000
    }
  },

  PERSISTENT_MEMORY: {
    id: 'persistent-memory',
    name: 'Persistent Memory',
    description: 'Long-term storage and recall of project context, decisions, and interactions',
    requiredLLMs: ['claude-3-opus', 'gpt-4'],
    supportedActions: [
      'store_context',
      'retrieve_context',
      'update_memory',
      'analyze_history',
      'summarize_interactions'
    ],
    parameters: {
      storageType: 'vector',
      maxHistorySize: 1000000,
      retentionPeriod: 30 // days
    }
  },

  PROJECT_AWARENESS: {
    id: 'project-awareness',
    name: 'Project Awareness',
    description: 'Access and understanding of project structure, dependencies, and documentation',
    requiredLLMs: ['claude-3-opus', 'gpt-4-turbo'],
    supportedActions: [
      'analyze_structure',
      'track_dependencies',
      'monitor_changes',
      'generate_documentation',
      'suggest_architecture'
    ],
    parameters: {
      maxProjectSize: 1073741824, // 1GB
      supportedVCS: ['git'],
      monitoredAspects: ['dependencies', 'structure', 'documentation']
    }
  },

  INTELLIGENT_CHAT: {
    id: 'intelligent-chat',
    name: 'Intelligent Chat',
    description: 'Context-aware communication with users about project specifics',
    requiredLLMs: ['claude-3-opus', 'claude-3-sonnet', 'gpt-4'],
    supportedActions: [
      'context_aware_response',
      'clarify_requirements',
      'provide_explanations',
      'suggest_solutions',
      'answer_queries'
    ],
    parameters: {
      contextRetention: true,
      multilingualSupport: true,
      maxResponseTime: 5000 // ms
    }
  },

  TOOL_EXECUTION: {
    id: 'tool-execution',
    name: 'Tool Execution',
    description: 'Ability to execute and manage development tools and scripts',
    requiredLLMs: ['claude-3-opus', 'gpt-4-turbo'],
    supportedActions: [
      'execute_script',
      'manage_tools',
      'validate_output',
      'handle_errors',
      'suggest_commands'
    ],
    parameters: {
      securityLevel: 'high',
      allowedTools: ['npm', 'git', 'docker', 'vscode'],
      timeoutSeconds: 300
    }
  },

  TERMINAL_ACCESS: {
    id: 'terminal-access',
    name: 'Terminal Access',
    description: 'Direct terminal interaction for multiple programming environments',
    requiredLLMs: ['claude-3-opus', 'gpt-4'],
    supportedActions: [
      'execute_command',
      'manage_processes',
      'handle_io',
      'monitor_output',
      'suggest_commands'
    ],
    parameters: {
      supportedShells: ['bash', 'powershell', 'zsh'],
      maxConcurrentSessions: 5,
      timeoutSeconds: 600
    }
  },

  AGENT_COLLABORATION: {
    id: 'agent-collaboration',
    name: 'Agent Collaboration',
    description: 'Ability to work with other agents and share context/results',
    requiredLLMs: ['claude-3-opus', 'gpt-4'],
    supportedActions: [
      'share_context',
      'delegate_tasks',
      'merge_results',
      'coordinate_actions',
      'resolve_conflicts'
    ],
    parameters: {
      maxCollaborators: 10,
      syncInterval: 1000, // ms
      conflictResolution: 'automatic'
    }
  },

  LLM_FALLBACK: {
    id: 'llm-fallback',
    name: 'LLM Fallback',
    description: 'Dynamic switching between different LLM providers based on availability and task requirements',
    requiredLLMs: ['claude-3-sonnet', 'gpt-3.5-turbo', 'gpt-4'],
    supportedActions: [
      'switch_provider',
      'optimize_selection',
      'handle_failure',
      'balance_load',
      'monitor_performance'
    ],
    parameters: {
      failoverStrategy: 'cascade',
      performanceThreshold: 2000, // ms
      costOptimization: true
    }
  }
};

export const CAPABILITY_DEPENDENCIES: Record<string, string[]> = {
  'code-awareness': ['persistent-memory', 'project-awareness'],
  'intelligent-chat': ['persistent-memory', 'project-awareness'],
  'tool-execution': ['terminal-access', 'code-awareness'],
  'agent-collaboration': ['persistent-memory', 'intelligent-chat'],
  'llm-fallback': ['persistent-memory']
};

export function validateCapabilityDependencies(capabilities: string[]): boolean {
  for (const capability of capabilities) {
    const dependencies = CAPABILITY_DEPENDENCIES[capability] || [];
    if (!dependencies.every(dep => capabilities.includes(dep))) {
      return false;
    }
  }
  return true;
}

export function getRequiredLLMs(capabilities: string[]): string[] {
  const llms = new Set<string>();
  capabilities.forEach(capId => {
    const capability = CORE_CAPABILITIES[capId];
    if (capability) {
      capability.requiredLLMs.forEach(llm => llms.add(llm));
    }
  });
  return Array.from(llms);
}

export function validateCapabilityParameters(
  capabilityId: string,
  parameters: Record<string, any>
): boolean {
  const capability = CORE_CAPABILITIES[capabilityId];
  if (!capability) return false;

  const requiredParams = Object.keys(capability.parameters);
  return requiredParams.every(param => 
    parameters.hasOwnProperty(param) && 
    typeof parameters[param] === typeof capability.parameters[param]
  );
} 