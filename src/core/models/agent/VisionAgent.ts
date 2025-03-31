import { BaseAgent } from './BaseAgent';
import { AgentContext } from './AgentManager';
import OpenAI from 'openai';
import * as fs from 'fs';

export class VisionAgent extends BaseAgent {
  private openai: OpenAI;

  constructor() {
    super('VisionAgent');
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
  }

  async analyzeImage(filePath: string, context: AgentContext): Promise<{
    description: string;
    objects: string[];
    text?: string;
    confidence: number;
  }> {
    await this.validateContext(context);

    try {
      const imageBuffer = await fs.promises.readFile(filePath);
      const base64Image = imageBuffer.toString('base64');

      const response = await this.openai.chat.completions.create({
        model: "gpt-4-vision-preview",
        messages: [
          {
            role: "user",
            content: [
              {
                type: "text",
                text: "Analyze this image and provide a detailed description, list of objects, and any text visible in the image."
              },
              {
                type: "image_url",
                image_url: {
                  url: `data:image/jpeg;base64,${base64Image}`
                }
              }
            ]
          }
        ],
        max_tokens: 500
      });

      const analysis = response.choices[0].message.content;
      
      // Parse the analysis into structured data
      // This is a simple example - you might want to use more sophisticated parsing
      const description = analysis.split('\n')[0];
      const objects = analysis.match(/Objects: (.*)/)?.[1].split(', ') || [];
      const text = analysis.match(/Text: (.*)/)?.[1];

      return {
        description,
        objects,
        text,
        confidence: 0.95 // GPT-4 Vision doesn't provide confidence scores
      };
    } catch (error) {
      this.logger.error('Failed to analyze image', error);
      throw error;
    }
  }
} 