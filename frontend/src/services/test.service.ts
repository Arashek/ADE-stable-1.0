import { MonitoringService } from './monitoring.service';

interface TestConfig {
  numIterations: number;
  learningRate?: number;
  batchSize?: number;
  maxEpochs?: number;
}

interface TestResult {
  prompt: string;
  success: boolean;
  metrics: {
    total_latency: number;
    iteration: number;
  };
  agent_metrics: Array<{
    name: string;
    latency: number;
    tokens: number;
  }>;
  error?: string;
}

interface TestHistory {
  results: TestResult[];
  total_iterations: number;
  success_rate: number;
  average_latency: number;
}

interface TestStatus {
  is_running: boolean;
  current_iteration: number;
  test_history_length: number;
}

class TestServiceImpl {
  private readonly API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';
  private readonly monitoring: MonitoringService;

  constructor(monitoring: MonitoringService) {
    this.monitoring = monitoring;
  }

  async startAutomatedTesting(config: TestConfig): Promise<void> {
    const startTime = performance.now();

    try {
      const response = await fetch(`${this.API_BASE_URL}/api/tests/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          num_iterations: config.numIterations,
          learning_rate: config.learningRate,
          batch_size: config.batchSize,
          max_epochs: config.maxEpochs,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const latency = performance.now() - startTime;
      this.monitoring.trackPerformance({
        name: 'test_start',
        value: latency,
        tags: {
          iterations: config.numIterations.toString(),
        }
      });
    } catch (error) {
      this.monitoring.trackError({
        message: (error as Error).message,
        stack: (error as Error).stack,
        severity: 'error',
        tags: {
          context: 'test_start'
        }
      });
      throw error;
    }
  }

  async stopAutomatedTesting(): Promise<void> {
    try {
      const response = await fetch(`${this.API_BASE_URL}/api/tests/stop`, {
        method: 'POST',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      this.monitoring.trackError({
        message: (error as Error).message,
        stack: (error as Error).stack,
        severity: 'error',
        tags: {
          context: 'test_stop'
        }
      });
      throw error;
    }
  }

  async getTestStatus(): Promise<TestStatus> {
    try {
      const response = await fetch(`${this.API_BASE_URL}/api/tests/status`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      this.monitoring.trackError({
        message: (error as Error).message,
        stack: (error as Error).stack,
        severity: 'error',
        tags: {
          context: 'test_status'
        }
      });
      throw error;
    }
  }

  async getTestHistory(): Promise<TestHistory> {
    try {
      const response = await fetch(`${this.API_BASE_URL}/api/tests/history`);

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error) {
      this.monitoring.trackError({
        message: (error as Error).message,
        stack: (error as Error).stack,
        severity: 'error',
        tags: {
          context: 'test_history'
        }
      });
      throw error;
    }
  }

  async savePolicies(path: string): Promise<void> {
    try {
      const response = await fetch(`${this.API_BASE_URL}/api/tests/save-policies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      this.monitoring.trackError({
        message: (error as Error).message,
        stack: (error as Error).stack,
        severity: 'error',
        tags: {
          context: 'save_policies'
        }
      });
      throw error;
    }
  }

  async loadPolicies(path: string): Promise<void> {
    try {
      const response = await fetch(`${this.API_BASE_URL}/api/tests/load-policies`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ path }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
    } catch (error) {
      this.monitoring.trackError({
        message: (error as Error).message,
        stack: (error as Error).stack,
        severity: 'error',
        tags: {
          context: 'load_policies'
        }
      });
      throw error;
    }
  }
}

export const testService = new TestServiceImpl(MonitoringService.getInstance()); 