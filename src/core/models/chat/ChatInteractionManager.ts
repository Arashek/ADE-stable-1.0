import { CodebaseAnalysisManager } from '../analysis/CodebaseAnalysisManager';
import { CodebaseInsights, ImplementationOption, ImplementationPlan } from '../analysis/types';
import { NLPProcessor, ProcessedInput } from '../nlp/NLPProcessor';

export interface ChatResponse {
  type: 'question' | 'clarification' | 'suggestions' | 'options' | 'plan' | 'transition' | 'error';
  content: string;
  suggestions?: string[];
  options?: ImplementationOption[];
  plan?: ImplementationPlan;
  nextPhase: string;
}

export class ChatInteractionManager {
  private analysisManager: CodebaseAnalysisManager;
  private currentInsights: CodebaseInsights | null;
  private userPreferences: UserPreferences;
  private chatState: ChatState;
  private nlpProcessor: NLPProcessor;
  private conversationContext: ConversationContext;

  constructor() {
    this.analysisManager = new CodebaseAnalysisManager();
    this.currentInsights = null;
    this.nlpProcessor = new NLPProcessor();
    this.userPreferences = {
      goals: [],
      requirements: [],
      painPoints: [],
      successCriteria: [],
      timeline: null,
      priorities: [],
      technicalPreferences: {
        frameworks: [],
        languages: [],
        tools: [],
        architecture: null
      },
      qualityPreferences: {
        testing: null,
        documentation: null,
        performance: null,
        security: null
      }
    };
    this.chatState = {
      currentPhase: 'initial',
      lastUserInput: null,
      pendingQuestions: [],
      completedSteps: [],
      contextStack: [],
      activeTopics: new Set()
    };
    this.conversationContext = {
      currentTopic: null,
      topicHistory: [],
      userIntent: null,
      confidence: 0,
      relevantInsights: []
    };
  }

  async handleCodebaseUpload(codebasePath: string): Promise<void> {
    // Start background analysis
    this.currentInsights = await this.analysisManager.analyzeCodebase(codebasePath);
    
    // Initialize chat with contextual questions
    this.initializeChat();
  }

  private initializeChat(): void {
    this.chatState.currentPhase = 'understanding';
    
    // Generate contextual questions based on codebase analysis
    const contextualQuestions = this.generateContextualQuestions();
    
    // Add standard questions
    const standardQuestions = [
      "What are your main goals for this project?",
      "Are there any specific requirements or constraints I should be aware of?",
      "What are the biggest pain points you'd like to address?",
      "How would you define success for this project?",
      "Do you have any timeline expectations?"
    ];
    
    this.chatState.pendingQuestions = [...contextualQuestions, ...standardQuestions];
  }

  private generateContextualQuestions(): string[] {
    const questions: string[] = [];
    
    if (!this.currentInsights) return questions;

    // Design-related questions
    if (this.currentInsights.design) {
      const design = this.currentInsights.design;
      if (design.usesReact) {
        questions.push("I notice your frontend uses React. Would you like to modernize the component structure?");
      }
      if (design.hasAccessibilityIssues) {
        questions.push("I've identified some accessibility concerns. Would you like to address these?");
      }
      if (design.componentStructure.complexity === 'high') {
        questions.push("Your component structure is quite complex. Would you like to simplify it?");
      }
    }

    // Development-related questions
    if (this.currentInsights.development) {
      const dev = this.currentInsights.development;
      if (dev.hasPerformanceBottlenecks) {
        questions.push("I see potential performance bottlenecks in the data fetching layer. Should we optimize that?");
      }
      if (dev.hasAuthIssues) {
        questions.push("Your authentication system could be enhanced. Would you like to implement OAuth2?");
      }
      if (dev.dependencies.outdated.length > 0) {
        questions.push(`I found ${dev.dependencies.outdated.length} outdated dependencies. Should we update them?`);
      }
    }

    // Testing-related questions
    if (this.currentInsights.testing) {
      const testing = this.currentInsights.testing;
      if (testing.coverage < 80) {
        questions.push(`Your test coverage is ${testing.coverage}%. Would you like to improve this?`);
      }
      if (testing.gaps.untestedComponents.length > 0) {
        questions.push(`I found ${testing.gaps.untestedComponents.length} untested components. Should we add tests for these?`);
      }
    }

    // Security-related questions
    if (this.currentInsights.security) {
      const security = this.currentInsights.security;
      if (security.vulnerabilities.critical > 0) {
        questions.push(`I found ${security.vulnerabilities.critical} critical security vulnerabilities. Should we address these first?`);
      }
    }

    return questions;
  }

  async handleUserInput(input: string): Promise<ChatResponse> {
    // Update chat state
    this.chatState.lastUserInput = input;
    
    // Process user input with NLP
    const processedInput = await this.nlpProcessor.processInput(input);
    
    // Update conversation context
    this.updateConversationContext(processedInput);
    
    // Process user input based on current phase
    switch (this.chatState.currentPhase) {
      case 'understanding':
        return this.handleUnderstandingPhase(processedInput);
      case 'clarification':
        return this.handleClarificationPhase(processedInput);
      case 'suggestion':
        return this.handleSuggestionPhase(processedInput);
      case 'decision':
        return this.handleDecisionPhase(processedInput);
      case 'implementation':
        return this.handleImplementationPhase(processedInput);
      default:
        return this.handleDefaultPhase(processedInput);
    }
  }

  private updateConversationContext(processedInput: ProcessedInput): void {
    // Update current topic
    this.conversationContext.currentTopic = processedInput.topic;
    
    // Update topic history
    this.conversationContext.topicHistory.push(processedInput.topic);
    
    // Update user intent
    this.conversationContext.userIntent = processedInput.intent;
    
    // Update confidence
    this.conversationContext.confidence = processedInput.confidence;
    
    // Find relevant insights
    this.conversationContext.relevantInsights = this.findRelevantInsights(processedInput);
  }

  private findRelevantInsights(processedInput: ProcessedInput): any[] {
    const relevantInsights: any[] = [];
    
    if (!this.currentInsights) return relevantInsights;
    
    // Find insights based on topic and intent
    switch (processedInput.topic) {
      case 'design':
        if (this.currentInsights.design) {
          relevantInsights.push(this.currentInsights.design);
        }
        break;
      case 'development':
        if (this.currentInsights.development) {
          relevantInsights.push(this.currentInsights.development);
        }
        break;
      case 'testing':
        if (this.currentInsights.testing) {
          relevantInsights.push(this.currentInsights.testing);
        }
        break;
      case 'security':
        if (this.currentInsights.security) {
          relevantInsights.push(this.currentInsights.security);
        }
        break;
    }
    
    return relevantInsights;
  }

  private async handleUnderstandingPhase(input: ProcessedInput): Promise<ChatResponse> {
    // Update user preferences based on input
    await this.updateUserPreferences(input.text);
    
    // Check if we have enough information
    if (this.hasEnoughInformation()) {
      this.chatState.currentPhase = 'suggestion';
      return {
        type: 'transition',
        content: this.generateTransitionMessage(),
        nextPhase: 'suggestion'
      };
    }
    
    // Get next contextual question
    const nextQuestion = this.getNextContextualQuestion(input);
    return {
      type: 'question',
      content: nextQuestion,
      nextPhase: 'understanding'
    };
  }

  private async updateUserPreferences(input: string): Promise<void> {
    // Extract preferences using NLP
    const preferences = await this.nlpProcessor.extractPreferences(input);
    
    // Update user preferences
    this.userPreferences = {
      ...this.userPreferences,
      ...preferences
    };
  }

  private getNextContextualQuestion(input: ProcessedInput): string {
    // Get next question from pending questions
    const nextQuestion = this.chatState.pendingQuestions.shift();
    
    if (!nextQuestion) {
      // Generate follow-up question based on current topic
      return this.generateFollowUpQuestion(input);
    }
    
    return nextQuestion;
  }

  private generateFollowUpQuestion(input: ProcessedInput): string {
    // Generate follow-up question based on current topic and context
    switch (input.topic) {
      case 'design':
        return "Would you like to focus on improving the user interface or component architecture?";
      case 'development':
        return "Should we prioritize performance optimization or code quality improvements?";
      case 'testing':
        return "Would you prefer to focus on unit tests or end-to-end testing?";
      case 'security':
        return "Should we address critical vulnerabilities first or implement comprehensive security measures?";
      default:
        return "Is there anything specific you'd like to focus on?";
    }
  }

  private generateTransitionMessage(): string {
    const topics = Array.from(this.chatState.activeTopics);
    return `Based on your input, I understand you want to focus on ${topics.join(', ')}. I have some suggestions for improvements. Would you like to hear them?`;
  }

  private async handleClarificationPhase(input: ProcessedInput): Promise<ChatResponse> {
    // Process clarification questions
    const clarification = this.generateClarification(input.text);
    return {
      type: 'clarification',
      content: clarification,
      nextPhase: 'clarification'
    };
  }

  private async handleSuggestionPhase(input: ProcessedInput): Promise<ChatResponse> {
    if (input.text.toLowerCase().includes('yes')) {
      // Present suggestions based on insights
      const suggestions = this.currentInsights?.suggestions || [];
      return {
        type: 'suggestions',
        content: "Here are my suggestions based on the codebase analysis:",
        suggestions,
        nextPhase: 'decision'
      };
    }
    
    return {
      type: 'question',
      content: "Would you like to hear my suggestions for improvements?",
      nextPhase: 'suggestion'
    };
  }

  private async handleDecisionPhase(input: ProcessedInput): Promise<ChatResponse> {
    // Present implementation options
    const options = this.analysisManager.getImplementationOptions();
    return {
      type: 'options',
      content: "Here are the implementation options:",
      options,
      nextPhase: 'implementation'
    };
  }

  private async handleImplementationPhase(input: ProcessedInput): Promise<ChatResponse> {
    // Process implementation decision
    const selectedOption = this.parseImplementationOption(input.text);
    if (selectedOption) {
      const plan = this.analysisManager.createImplementationPlan(selectedOption);
      return {
        type: 'plan',
        content: "Here's the implementation plan:",
        plan,
        nextPhase: 'execution'
      };
    }
    
    return {
      type: 'clarification',
      content: "Could you please select one of the implementation options?",
      nextPhase: 'implementation'
    };
  }

  private handleDefaultPhase(input: ProcessedInput): Promise<ChatResponse> {
    return {
      type: 'error',
      content: "I'm not sure how to process that input. Could you please rephrase?",
      nextPhase: this.chatState.currentPhase
    };
  }

  private hasEnoughInformation(): boolean {
    return (
      this.userPreferences.goals.length > 0 &&
      this.userPreferences.requirements.length > 0 &&
      this.userPreferences.painPoints.length > 0 &&
      this.userPreferences.successCriteria.length > 0
    );
  }

  private generateClarification(input: string): string {
    // Generate clarification questions based on input
    return "Could you please clarify...";
  }

  private parseImplementationOption(input: string): ImplementationOption | null {
    // Parse user input to determine selected implementation option
    return null;
  }
}

interface ConversationContext {
  currentTopic: string | null;
  topicHistory: string[];
  userIntent: string | null;
  confidence: number;
  relevantInsights: any[];
}

export interface TechnicalPreferences {
  frameworks: string[];
  languages: string[];
  tools: string[];
  architecture: string | null;
}

export interface QualityPreferences {
  testing: string | null;
  documentation: string | null;
  performance: string | null;
  security: string | null;
}

export interface UserPreferences {
  goals: string[];
  requirements: string[];
  painPoints: string[];
  successCriteria: string[];
  timeline: string | null;
  priorities: string[];
  technicalPreferences: TechnicalPreferences;
  qualityPreferences: QualityPreferences;
}

interface ChatState {
  currentPhase: 'initial' | 'understanding' | 'clarification' | 'suggestion' | 'decision' | 'implementation' | 'execution';
  lastUserInput: string | null;
  pendingQuestions: string[];
  completedSteps: string[];
  contextStack: any[];
  activeTopics: Set<string>;
} 