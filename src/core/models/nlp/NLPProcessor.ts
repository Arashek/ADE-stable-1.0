import { UserPreferences, TechnicalPreferences, QualityPreferences } from '../chat/ChatInteractionManager';

export class NLPProcessor {
  async processInput(input: string): Promise<ProcessedInput> {
    // Process input to extract topic, intent, and other information
    const topic = this.extractTopic(input);
    const intent = this.extractIntent(input);
    const entities = this.extractEntities(input);
    const sentiment = this.analyzeSentiment(input);
    const confidence = this.calculateConfidence(input);

    return {
      topic,
      intent,
      confidence,
      entities,
      sentiment,
      text: input
    };
  }

  async extractPreferences(input: string): Promise<Partial<UserPreferences>> {
    const preferences: Partial<UserPreferences> = {
      technicalPreferences: this.extractTechnicalPreferences(input),
      qualityPreferences: this.extractQualityPreferences(input)
    };

    return preferences;
  }

  private extractTopic(input: string): string {
    // Extract main topic from input
    const topics = ['design', 'development', 'testing', 'security', 'performance', 'documentation'];
    const words = input.toLowerCase().split(' ');
    
    for (const topic of topics) {
      if (words.includes(topic)) {
        return topic;
      }
    }

    return 'general';
  }

  private extractIntent(input: string): string {
    // Extract user intent from input
    const intents = {
      question: ['what', 'how', 'why', 'when', 'where', 'which'],
      request: ['can', 'could', 'would', 'should', 'please'],
      statement: ['is', 'are', 'was', 'were', 'have', 'has'],
      preference: ['prefer', 'like', 'want', 'need', 'should']
    };

    const words = input.toLowerCase().split(' ');
    
    for (const [intent, keywords] of Object.entries(intents)) {
      if (keywords.some(keyword => words.includes(keyword))) {
        return intent;
      }
    }

    return 'unknown';
  }

  private extractEntities(input: string): any[] {
    // Extract named entities and technical terms
    const entities: any[] = [];
    
    // Look for technical terms
    const technicalTerms = [
      'react', 'typescript', 'javascript', 'node', 'python', 'java',
      'docker', 'kubernetes', 'aws', 'azure', 'gcp',
      'rest', 'graphql', 'sql', 'nosql', 'redis',
      'jest', 'cypress', 'selenium', 'jenkins', 'git'
    ];

    const words = input.toLowerCase().split(' ');
    
    for (const term of technicalTerms) {
      if (words.includes(term)) {
        entities.push({
          type: 'technical_term',
          value: term
        });
      }
    }

    return entities;
  }

  private analyzeSentiment(input: string): 'positive' | 'negative' | 'neutral' {
    // Simple sentiment analysis
    const positiveWords = ['good', 'great', 'excellent', 'perfect', 'like', 'love', 'want', 'need'];
    const negativeWords = ['bad', 'poor', 'terrible', 'hate', 'dislike', 'don\'t', 'not'];
    
    const words = input.toLowerCase().split(' ');
    
    let positiveCount = 0;
    let negativeCount = 0;
    
    for (const word of words) {
      if (positiveWords.includes(word)) positiveCount++;
      if (negativeWords.includes(word)) negativeCount++;
    }
    
    if (positiveCount > negativeCount) return 'positive';
    if (negativeCount > positiveCount) return 'negative';
    return 'neutral';
  }

  private calculateConfidence(input: string): number {
    // Calculate confidence score based on input clarity and completeness
    let confidence = 0.5; // Base confidence

    // Check for technical terms
    const technicalTerms = this.extractEntities(input);
    if (technicalTerms.length > 0) {
      confidence += 0.2;
    }

    // Check for clear intent
    const intent = this.extractIntent(input);
    if (intent !== 'unknown') {
      confidence += 0.2;
    }

    // Check for specific topic
    const topic = this.extractTopic(input);
    if (topic !== 'general') {
      confidence += 0.1;
    }

    return Math.min(confidence, 1.0);
  }

  private extractTechnicalPreferences(input: string): TechnicalPreferences {
    const preferences: TechnicalPreferences = {
      frameworks: [],
      languages: [],
      tools: [],
      architecture: null
    };

    // Extract framework preferences
    const frameworks = ['react', 'angular', 'vue', 'express', 'django', 'flask'];
    const words = input.toLowerCase().split(' ');
    
    for (const framework of frameworks) {
      if (words.includes(framework)) {
        preferences.frameworks.push(framework);
      }
    }

    // Extract language preferences
    const languages = ['typescript', 'javascript', 'python', 'java', 'c#', 'go'];
    for (const language of languages) {
      if (words.includes(language)) {
        preferences.languages.push(language);
      }
    }

    // Extract tool preferences
    const tools = ['docker', 'kubernetes', 'jenkins', 'git', 'aws', 'azure'];
    for (const tool of tools) {
      if (words.includes(tool)) {
        preferences.tools.push(tool);
      }
    }

    // Extract architecture preferences
    const architectures = ['microservices', 'monolithic', 'serverless', 'event-driven'];
    for (const architecture of architectures) {
      if (words.includes(architecture)) {
        preferences.architecture = architecture;
        break;
      }
    }

    return preferences;
  }

  private extractQualityPreferences(input: string): QualityPreferences {
    const preferences: QualityPreferences = {
      testing: null,
      documentation: null,
      performance: null,
      security: null
    };

    const words = input.toLowerCase().split(' ');

    // Extract testing preferences
    if (words.includes('test') || words.includes('testing')) {
      preferences.testing = 'comprehensive';
    }

    // Extract documentation preferences
    if (words.includes('document') || words.includes('documentation')) {
      preferences.documentation = 'detailed';
    }

    // Extract performance preferences
    if (words.includes('performance') || words.includes('speed') || words.includes('fast')) {
      preferences.performance = 'optimized';
    }

    // Extract security preferences
    if (words.includes('security') || words.includes('secure') || words.includes('safe')) {
      preferences.security = 'high';
    }

    return preferences;
  }
}

export interface ProcessedInput {
  topic: string;
  intent: string;
  confidence: number;
  entities: any[];
  sentiment: 'positive' | 'negative' | 'neutral';
  text: string;
} 