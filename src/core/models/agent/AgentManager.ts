import { Logger } from '../logging/Logger';
import { VisionAgent } from './VisionAgent';
import { SpeechAgent } from './SpeechAgent';
import { DocumentAgent } from './DocumentAgent';

export interface AgentContext {
  projectId: string;
  userId: string;
  conversationId: string;
}

export class AgentManager {
  private logger: Logger;
  private agents: Map<string, any>;

  constructor() {
    this.logger = new Logger('AgentManager');
    this.agents = new Map();
    this.initializeAgents();
  }

  private initializeAgents(): void {
    this.agents.set('vision', new VisionAgent());
    this.agents.set('speech', new SpeechAgent());
    this.agents.set('document', new DocumentAgent());
  }

  getAgent(type: string): any {
    const agent = this.agents.get(type);
    if (!agent) {
      throw new Error(`Agent type ${type} not found`);
    }
    return agent;
  }
} 