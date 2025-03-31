import { v4 as uuidv4 } from 'uuid';

export interface TrainingScenario {
  id: string;
  name: string;
  description: string;
  prompts: TrainingPrompt[];
  context: Record<string, any>;
  successCriteria: SuccessCriteria[];
  maxAttempts: number;
  timeout: number;
}

export interface TrainingPrompt {
  id: string;
  content: string;
  type: 'initial' | 'follow-up' | 'error-handling' | 'completion';
  context?: Record<string, any>;
  expectedResponse?: string;
  validationRules?: ValidationRule[];
}

export interface SuccessCriteria {
  type: 'response-match' | 'code-quality' | 'performance' | 'security' | 'custom';
  description: string;
  validator: (response: any) => boolean;
}

export interface ValidationRule {
  type: 'contains' | 'not-contains' | 'matches' | 'custom';
  value: string | RegExp | ((value: any) => boolean);
  message: string;
}

export interface TrainingResult {
  scenarioId: string;
  sessionId: string;
  startTime: Date;
  endTime: Date;
  status: 'success' | 'failure' | 'timeout';
  attempts: number;
  responses: Array<{
    promptId: string;
    response: string;
    timestamp: Date;
    validationResults: ValidationResult[];
  }>;
  metrics: {
    responseTime: number;
    tokenUsage: number;
    errorCount: number;
  };
}

export interface ValidationResult {
  rule: ValidationRule;
  passed: boolean;
  message?: string;
}

export class TrainingManager {
  private scenarios: Map<string, TrainingScenario> = new Map();
  private results: Map<string, TrainingResult> = new Map();

  constructor() {
    this.loadDefaultScenarios();
  }

  private loadDefaultScenarios() {
    // Add some default training scenarios
    this.addScenario({
      id: uuidv4(),
      name: 'Basic Code Generation',
      description: 'Test basic code generation capabilities',
      prompts: [
        {
          id: uuidv4(),
          content: 'Generate a simple function to calculate the factorial of a number',
          type: 'initial',
          validationRules: [
            {
              type: 'contains',
              value: 'function',
              message: 'Response should contain a function definition'
            }
          ]
        }
      ],
      context: {},
      successCriteria: [
        {
          type: 'code-quality',
          description: 'Code should be well-formatted and documented',
          validator: (response: string) => {
            return response.includes('function') && 
                   response.includes('//') && 
                   response.includes('return');
          }
        }
      ],
      maxAttempts: 3,
      timeout: 30000
    });
  }

  public addScenario(scenario: TrainingScenario): void {
    this.scenarios.set(scenario.id, scenario);
  }

  public getScenario(id: string): TrainingScenario | undefined {
    return this.scenarios.get(id);
  }

  public getAllScenarios(): TrainingScenario[] {
    return Array.from(this.scenarios.values());
  }

  public async validateResponse(
    scenarioId: string,
    promptId: string,
    response: string
  ): Promise<ValidationResult[]> {
    const scenario = this.scenarios.get(scenarioId);
    if (!scenario) {
      throw new Error(`Scenario ${scenarioId} not found`);
    }

    const prompt = scenario.prompts.find(p => p.id === promptId);
    if (!prompt) {
      throw new Error(`Prompt ${promptId} not found in scenario ${scenarioId}`);
    }

    const results: ValidationResult[] = [];

    if (prompt.validationRules) {
      for (const rule of prompt.validationRules) {
        const passed = this.validateRule(rule, response);
        results.push({
          rule,
          passed,
          message: passed ? undefined : rule.message
        });
      }
    }

    return results;
  }

  private validateRule(rule: ValidationRule, value: string): boolean {
    switch (rule.type) {
      case 'contains':
        return value.includes(rule.value as string);
      case 'not-contains':
        return !value.includes(rule.value as string);
      case 'matches':
        return (rule.value as RegExp).test(value);
      case 'custom':
        return (rule.value as (value: any) => boolean)(value);
      default:
        return false;
    }
  }

  public recordResult(result: TrainingResult): void {
    this.results.set(result.sessionId, result);
  }

  public getResult(sessionId: string): TrainingResult | undefined {
    return this.results.get(sessionId);
  }

  public getAllResults(): TrainingResult[] {
    return Array.from(this.results.values());
  }

  public getScenarioResults(scenarioId: string): TrainingResult[] {
    return this.getAllResults().filter(result => result.scenarioId === scenarioId);
  }

  public generatePrompt(scenarioId: string, type: TrainingPrompt['type']): TrainingPrompt | undefined {
    const scenario = this.scenarios.get(scenarioId);
    if (!scenario) {
      return undefined;
    }

    return scenario.prompts.find(prompt => prompt.type === type);
  }

  public async evaluateSuccess(
    scenarioId: string,
    responses: Array<{ promptId: string; response: string }>
  ): Promise<boolean> {
    const scenario = this.scenarios.get(scenarioId);
    if (!scenario) {
      return false;
    }

    for (const criteria of scenario.successCriteria) {
      const lastResponse = responses[responses.length - 1];
      if (!criteria.validator(lastResponse.response)) {
        return false;
      }
    }

    return true;
  }
} 