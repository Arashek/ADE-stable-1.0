import { monitoringService } from './monitoring.service';

interface LLMConfig {
  model: 'llama2' | 'mistral';
  temperature?: number;
  maxTokens?: number;
  topP?: number;
  presencePenalty?: number;
  frequencyPenalty?: number;
}

interface LLMResponse {
  text: string;
  model: string;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  latency: number;
}

class LLMService {
  private static instance: LLMService;
  private readonly API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
  private readonly WS_URL = process.env.REACT_APP_WS_URL || 'ws://localhost:8000/ws';

  private constructor() {}

  public static getInstance(): LLMService {
    if (!LLMService.instance) {
      LLMService.instance = new LLMService();
    }
    return LLMService.instance;
  }

  async generateCompletion(
    prompt: string,
    config: LLMConfig
  ): Promise<LLMResponse> {
    const startTime = performance.now();

    try {
      const response = await fetch(`${this.API_BASE_URL}/api/llm/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          prompt,
          ...config,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      const latency = performance.now() - startTime;

      // Track performance metrics
      monitoringService.trackPerformance({
        name: 'llm_generation',
        value: latency,
        tags: {
          model: config.model,
          promptLength: prompt.length.toString(),
        },
      });

      return {
        text: data.text,
        model: config.model,
        usage: data.usage,
        latency,
      };
    } catch (error) {
      // Track error
      const err = error as Error;
      monitoringService.trackError({
        message: err.message || 'LLM generation error',
        stack: err.stack,
        severity: 'error'
      }, {
        context: 'llm_generation',
        model: config.model,
      });
      throw error;
    }
  }

  async streamCompletion(
    prompt: string,
    config: LLMConfig,
    onToken: (token: string) => void
  ): Promise<void> {
    const startTime = performance.now();
    const ws = new WebSocket(this.WS_URL);

    return new Promise((resolve, reject) => {
      ws.onopen = () => {
        ws.send(JSON.stringify({
          type: 'generate',
          prompt,
          ...config,
        }));
      };

      ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        
        if (data.type === 'token') {
          onToken(data.token);
        } else if (data.type === 'complete') {
          const latency = performance.now() - startTime;
          
          // Track performance metrics
          monitoringService.trackPerformance({
            name: 'llm_streaming',
            value: latency,
            tags: {
              model: config.model,
              promptLength: prompt.length.toString(),
            },
          });

          ws.close();
          resolve();
        }
      };

      ws.onerror = (event: Event) => {
        // Track error
        const errorObj = event instanceof ErrorEvent ? event.error : new Error('WebSocket error');
        monitoringService.trackError({
          message: errorObj.message || 'WebSocket error',
          stack: errorObj.stack,
          severity: 'error'
        }, {
          context: 'llm_streaming',
          model: config.model,
        });
        reject(errorObj);
      };
    });
  }

  async compareModels(
    prompt: string,
    configs: LLMConfig[]
  ): Promise<Record<string, LLMResponse>> {
    const results: Record<string, LLMResponse> = {};

    for (const config of configs) {
      try {
        results[config.model] = await this.generateCompletion(prompt, config);
      } catch (error) {
        console.error(`Error generating completion for ${config.model}:`, error);
      }
    }

    return results;
  }
}

export const llmService = LLMService.getInstance(); 