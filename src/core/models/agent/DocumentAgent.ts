import { BaseAgent } from './BaseAgent';
import { AgentContext } from './AgentManager';
import OpenAI from 'openai';
import * as fs from 'fs';

export class DocumentAgent extends BaseAgent {
  private openai: OpenAI;

  constructor() {
    super('DocumentAgent');
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
  }

  async analyzeDocument(filePath: string, context: AgentContext): Promise<{
    summary: string;
    keyPoints: string[];
    entities: Array<{
      text: string;
      type: string;
      confidence: number;
    }>;
    sentiment?: {
      score: number;
      label: string;
    };
  }> {
    await this.validateContext(context);

    try {
      const documentContent = await fs.promises.readFile(filePath, 'utf-8');

      const response = await this.openai.chat.completions.create({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: "You are a document analysis assistant. Analyze the provided document and extract key information."
          },
          {
            role: "user",
            content: `Please analyze this document and provide:
            1. A concise summary
            2. Key points
            3. Named entities with their types
            4. Sentiment analysis
            
            Document content:
            ${documentContent}`
          }
        ],
        response_format: { type: "json_object" },
        max_tokens: 1000
      });

      const analysis = JSON.parse(response.choices[0].message.content || '{}');

      return {
        summary: analysis.summary || '',
        keyPoints: analysis.keyPoints || [],
        entities: analysis.entities || [],
        sentiment: analysis.sentiment
      };
    } catch (error) {
      this.logger.error('Failed to analyze document', error);
      throw error;
    }
  }
} 