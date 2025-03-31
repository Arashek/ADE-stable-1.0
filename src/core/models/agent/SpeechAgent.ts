import { BaseAgent } from './BaseAgent';
import { AgentContext } from './AgentManager';
import OpenAI from 'openai';
import * as fs from 'fs';

export class SpeechAgent extends BaseAgent {
  private openai: OpenAI;

  constructor() {
    super('SpeechAgent');
    this.openai = new OpenAI({
      apiKey: process.env.OPENAI_API_KEY
    });
  }

  async transcribeAudio(filePath: string, context: AgentContext): Promise<{
    text: string;
    duration: number;
    confidence: number;
    segments: Array<{
      text: string;
      start: number;
      end: number;
      confidence: number;
    }>;
  }> {
    await this.validateContext(context);

    try {
      const audioFile = await fs.promises.readFile(filePath);
      
      const transcription = await this.openai.audio.transcriptions.create({
        file: new File([audioFile], 'audio.webm', { type: 'audio/webm' }),
        model: "whisper-1",
        response_format: "verbose_json",
        timestamp_granularities: ["segment"]
      });

      return {
        text: transcription.text,
        duration: transcription.duration || 0,
        confidence: transcription.segments.reduce((acc, seg) => acc + seg.confidence, 0) / transcription.segments.length,
        segments: transcription.segments.map(seg => ({
          text: seg.text,
          start: seg.start,
          end: seg.end,
          confidence: seg.confidence
        }))
      };
    } catch (error) {
      this.logger.error('Failed to transcribe audio', error);
      throw error;
    }
  }
} 