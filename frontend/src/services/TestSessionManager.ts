import { v4 as uuidv4 } from 'uuid';
import { AgentCollaborationService } from './AgentCollaborationService';
import { TrainingManager, TrainingScenario, TrainingResult, ValidationResult } from './TrainingManager';
import { Socket } from '../types/socket';

export interface TestSession {
  id: string;
  startTime: Date;
  endTime?: Date;
  status: 'running' | 'paused' | 'completed' | 'failed';
  scenario: TrainingScenario;
  currentIteration: number;
  responses: Array<{
    promptId: string;
    response: string;
    timestamp: Date;
    validationResults: ValidationResult[];
  }>;
  agentService: AgentCollaborationService;
}

export interface TestLoopConfig {
  maxIterations: number;
  pauseInterval: number;
  timeout: number;
  autoRestart: boolean;
  isolationLevel: 'strict' | 'moderate' | 'none';
}

export class TestSessionManager {
  private sessions: Map<string, TestSession> = new Map();
  private trainingManager: TrainingManager;
  private config: TestLoopConfig;
  private ws: Socket;

  constructor(
    trainingManager: TrainingManager,
    ws: Socket,
    config: TestLoopConfig = {
      maxIterations: 10,
      pauseInterval: 5000,
      timeout: 30000,
      autoRestart: false,
      isolationLevel: 'strict'
    }
  ) {
    this.trainingManager = trainingManager;
    this.ws = ws;
    this.config = config;
  }

  private createAgentService(): AgentCollaborationService {
    return new AgentCollaborationService({
      ws: this.ws,
      projectId: `test-${uuidv4()}`
    });
  }

  public async startNewSession(scenarioId: string): Promise<TestSession> {
    const scenario = this.trainingManager.getScenario(scenarioId);
    if (!scenario) {
      throw new Error(`Scenario ${scenarioId} not found`);
    }

    const agentService = this.createAgentService();
    await agentService.initialize();

    const session: TestSession = {
      id: uuidv4(),
      startTime: new Date(),
      status: 'running',
      scenario,
      currentIteration: 0,
      responses: [],
      agentService
    };

    this.sessions.set(session.id, session);
    await this.startTestLoop(session.id);
    return session;
  }

  private async isolateContext(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (!session) return;

    switch (this.config.isolationLevel) {
      case 'strict':
        // Reset agent service completely
        await session.agentService.dispose();
        session.agentService = this.createAgentService();
        await session.agentService.initialize();
        break;
      case 'moderate':
        // Clear conversation history but keep agent state
        await session.agentService.dispose();
        session.agentService = this.createAgentService();
        await session.agentService.initialize();
        break;
      case 'none':
        // No isolation
        break;
    }
  }

  private async startTestLoop(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (!session) return;

    while (session.status === 'running' && session.currentIteration < this.config.maxIterations) {
      try {
        // Generate and send initial prompt
        const prompt = this.trainingManager.generatePrompt(session.scenario.id, 'initial');
        if (!prompt) {
          throw new Error('No initial prompt found for scenario');
        }

        const response = await session.agentService.sendMessage(prompt.content);
        
        // Validate response
        const validationResults = await this.trainingManager.validateResponse(
          session.scenario.id,
          prompt.id,
          response
        );

        // Record response
        session.responses.push({
          promptId: prompt.id,
          response,
          timestamp: new Date(),
          validationResults
        });

        // Check if we've met success criteria
        const success = await this.trainingManager.evaluateSuccess(
          session.scenario.id,
          session.responses
        );

        if (success) {
          await this.completeSession(sessionId);
          break;
        }

        // Increment iteration and pause if needed
        session.currentIteration++;
        if (session.currentIteration < this.config.maxIterations) {
          await new Promise(resolve => setTimeout(resolve, this.config.pauseInterval));
          await this.isolateContext(sessionId);
        }

      } catch (error) {
        console.error(`Error in test loop for session ${sessionId}:`, error);
        await this.failSession(sessionId, error as Error);
        break;
      }
    }

    if (session.status === 'running' && session.currentIteration >= this.config.maxIterations) {
      await this.failSession(sessionId, new Error('Maximum iterations reached'));
    }
  }

  public async pauseSession(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.status = 'paused';
      await session.agentService.dispose();
    }
  }

  public async resumeSession(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.status = 'running';
      session.agentService = this.createAgentService();
      await session.agentService.initialize();
      await this.startTestLoop(sessionId);
    }
  }

  public async endSession(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.status = 'completed';
      session.endTime = new Date();
      await session.agentService.dispose();
    }
  }

  public async failSession(sessionId: string, error: Error): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.status = 'failed';
      session.endTime = new Date();
      
      // Record failure result
      const result: TrainingResult = {
        scenarioId: session.scenario.id,
        sessionId: session.id,
        startTime: session.startTime,
        endTime: session.endTime,
        status: 'failure',
        attempts: session.currentIteration,
        responses: session.responses,
        metrics: {
          responseTime: 0, // Calculate based on timestamps
          tokenUsage: 0, // Get from agent service
          errorCount: 1
        }
      };
      
      this.trainingManager.recordResult(result);
      await session.agentService.dispose();
    }
  }

  private async completeSession(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (session) {
      session.status = 'completed';
      session.endTime = new Date();
      
      // Record success result
      const result: TrainingResult = {
        scenarioId: session.scenario.id,
        sessionId: session.id,
        startTime: session.startTime,
        endTime: session.endTime,
        status: 'success',
        attempts: session.currentIteration,
        responses: session.responses,
        metrics: {
          responseTime: 0, // Calculate based on timestamps
          tokenUsage: 0, // Get from agent service
          errorCount: 0
        }
      };
      
      this.trainingManager.recordResult(result);
      await session.agentService.dispose();
    }
  }

  public getSession(sessionId: string): TestSession | undefined {
    return this.sessions.get(sessionId);
  }

  public getAllSessions(): TestSession[] {
    return Array.from(this.sessions.values());
  }

  public getActiveSessions(): TestSession[] {
    return this.getAllSessions().filter(session => 
      session.status === 'running' || session.status === 'paused'
    );
  }
} 