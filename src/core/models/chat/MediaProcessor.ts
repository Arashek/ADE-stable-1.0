import { Logger } from '../logging/Logger';
import { MediaMetadata, MessageType } from './types';
import { v4 as uuidv4 } from 'uuid';
import * as path from 'path';
import * as fs from 'fs';
import sharp from 'sharp';
import { AgentManager } from '../agent/AgentManager';
import { createHash } from 'crypto';

interface CacheEntry {
  text: string;
  metadata: MediaMetadata;
  analysis: any;
  timestamp: number;
}

export class MediaProcessor {
  private logger: Logger;
  private agentManager: AgentManager;
  private tempDir: string;
  private cacheDir: string;
  private cache: Map<string, CacheEntry>;
  private cacheTimeout: number = 24 * 60 * 60 * 1000; // 24 hours

  constructor(agentManager: AgentManager) {
    this.logger = new Logger('MediaProcessor');
    this.agentManager = agentManager;
    this.tempDir = path.join(process.cwd(), 'temp', 'media');
    this.cacheDir = path.join(process.cwd(), 'cache', 'media');
    this.cache = new Map();
    this.ensureDirectories();
    this.loadCache();
  }

  private ensureDirectories(): void {
    [this.tempDir, this.cacheDir].forEach(dir => {
      if (!fs.existsSync(dir)) {
        fs.mkdirSync(dir, { recursive: true });
      }
    });
  }

  private generateCacheKey(file: Express.Multer.File, type: MessageType, context: any): string {
    const content = `${file.buffer.toString('base64')}-${type}-${JSON.stringify(context)}`;
    return createHash('sha256').update(content).digest('hex');
  }

  private async loadCache(): Promise<void> {
    try {
      const cacheFiles = await fs.promises.readdir(this.cacheDir);
      for (const file of cacheFiles) {
        if (file.endsWith('.json')) {
          const content = await fs.promises.readFile(path.join(this.cacheDir, file), 'utf-8');
          const entry: CacheEntry = JSON.parse(content);
          
          // Check if cache entry is expired
          if (Date.now() - entry.timestamp < this.cacheTimeout) {
            this.cache.set(file.replace('.json', ''), entry);
          } else {
            await fs.promises.unlink(path.join(this.cacheDir, file));
          }
        }
      }
    } catch (error) {
      this.logger.error('Failed to load cache', error);
    }
  }

  private async saveToCache(key: string, entry: CacheEntry): Promise<void> {
    try {
      const cachePath = path.join(this.cacheDir, `${key}.json`);
      await fs.promises.writeFile(cachePath, JSON.stringify(entry));
      this.cache.set(key, entry);
    } catch (error) {
      this.logger.error('Failed to save to cache', error);
    }
  }

  async processMedia(
    file: Express.Multer.File,
    type: MessageType,
    context: {
      projectId: string;
      userId: string;
      conversationId: string;
    }
  ): Promise<{
    text: string;
    metadata: MediaMetadata;
    analysis: any;
  }> {
    try {
      const cacheKey = this.generateCacheKey(file, type, context);
      const cachedResult = this.cache.get(cacheKey);

      if (cachedResult && Date.now() - cachedResult.timestamp < this.cacheTimeout) {
        this.logger.info('Using cached result');
        return {
          text: cachedResult.text,
          metadata: cachedResult.metadata,
          analysis: cachedResult.analysis
        };
      }

      const tempPath = path.join(this.tempDir, `${uuidv4()}${path.extname(file.originalname)}`);
      await fs.promises.writeFile(tempPath, file.buffer);

      let result;
      switch (type) {
        case MessageType.IMAGE:
          result = await this.processImage(tempPath, context);
          break;
        case MessageType.VOICE:
          result = await this.processVoice(tempPath, context);
          break;
        case MessageType.FILE:
          result = await this.processFile(tempPath, context);
          break;
        default:
          throw new Error(`Unsupported media type: ${type}`);
      }

      // Clean up temp file
      await fs.promises.unlink(tempPath);

      // Save to cache
      await this.saveToCache(cacheKey, {
        ...result,
        timestamp: Date.now()
      });

      return result;
    } catch (error) {
      this.logger.error('Failed to process media', error);
      throw error;
    }
  }

  private async processImage(
    filePath: string,
    context: { projectId: string; userId: string; conversationId: string }
  ): Promise<{
    text: string;
    metadata: MediaMetadata;
    analysis: any;
  }> {
    const image = sharp(filePath);
    const metadata = await image.metadata();

    // Use vision agent to analyze image
    const visionAgent = this.agentManager.getAgent('vision');
    const analysis = await visionAgent.analyzeImage(filePath, {
      projectId: context.projectId,
      userId: context.userId,
      conversationId: context.conversationId
    });

    return {
      text: analysis.description,
      metadata: {
        fileName: path.basename(filePath),
        fileSize: fs.statSync(filePath).size,
        mimeType: 'image/jpeg',
        width: metadata.width,
        height: metadata.height
      },
      analysis
    };
  }

  private async processVoice(
    filePath: string,
    context: { projectId: string; userId: string; conversationId: string }
  ): Promise<{
    text: string;
    metadata: MediaMetadata;
    analysis: any;
  }> {
    // Use speech-to-text agent to convert voice to text
    const speechAgent = this.agentManager.getAgent('speech');
    const transcription = await speechAgent.transcribeAudio(filePath, {
      projectId: context.projectId,
      userId: context.userId,
      conversationId: context.conversationId
    });

    return {
      text: transcription.text,
      metadata: {
        fileName: path.basename(filePath),
        fileSize: fs.statSync(filePath).size,
        mimeType: 'audio/webm',
        duration: transcription.duration
      },
      analysis: transcription
    };
  }

  private async processFile(
    filePath: string,
    context: { projectId: string; userId: string; conversationId: string }
  ): Promise<{
    text: string;
    metadata: MediaMetadata;
    analysis: any;
  }> {
    // Use document analysis agent to process file
    const documentAgent = this.agentManager.getAgent('document');
    const analysis = await documentAgent.analyzeDocument(filePath, {
      projectId: context.projectId,
      userId: context.userId,
      conversationId: context.conversationId
    });

    return {
      text: analysis.summary,
      metadata: {
        fileName: path.basename(filePath),
        fileSize: fs.statSync(filePath).size,
        mimeType: 'application/octet-stream'
      },
      analysis
    };
  }
} 