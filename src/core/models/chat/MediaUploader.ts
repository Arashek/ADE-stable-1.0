import { Logger } from '../logging/Logger';
import { MediaMetadata, MessageType } from './types';
import * as fs from 'fs';
import * as path from 'path';
import sharp from 'sharp';
import { v4 as uuidv4 } from 'uuid';
import { MediaProcessor } from './MediaProcessor';
import { AgentManager } from '../agent/AgentManager';

export class MediaUploader {
  private logger: Logger;
  private uploadDir: string;
  private mediaProcessor: MediaProcessor;
  private settings: {
    maxFileSize: number;
    allowedFileTypes: string[];
    maxImageDimension: number;
    maxVoiceDuration: number;
    storageQuota: number;
    compressionEnabled: boolean;
  };

  constructor(uploadDir: string, settings: any) {
    this.logger = new Logger('MediaUploader');
    this.uploadDir = uploadDir;
    this.settings = settings;
    this.mediaProcessor = new MediaProcessor(new AgentManager());
    this.ensureUploadDirectory();
  }

  private ensureUploadDirectory(): void {
    if (!fs.existsSync(this.uploadDir)) {
      fs.mkdirSync(this.uploadDir, { recursive: true });
    }
  }

  async uploadFile(
    file: Express.Multer.File,
    userId: string,
    context: {
      projectId: string;
      conversationId: string;
    }
  ): Promise<{
    url: string;
    metadata: MediaMetadata;
    type: MessageType;
    text: string;
    analysis: any;
  }> {
    try {
      this.validateFile(file);

      const fileType = this.getFileType(file.mimetype);
      const fileName = this.generateFileName(file.originalname, fileType);
      const filePath = path.join(this.uploadDir, fileName);

      // Process file based on type
      let metadata: MediaMetadata;
      switch (fileType) {
        case MessageType.IMAGE:
          metadata = await this.processImage(file, filePath);
          break;
        case MessageType.VOICE:
          metadata = await this.processVoice(file, filePath);
          break;
        default:
          metadata = await this.processFile(file, filePath);
      }

      // Process media with LLM agents
      const { text, analysis } = await this.mediaProcessor.processMedia(file, fileType, {
        projectId: context.projectId,
        userId,
        conversationId: context.conversationId
      });

      return {
        url: `/uploads/${fileName}`,
        metadata,
        type: fileType,
        text,
        analysis
      };
    } catch (error) {
      this.logger.error('Failed to upload file', error);
      throw error;
    }
  }

  private validateFile(file: Express.Multer.File): void {
    if (file.size > this.settings.maxFileSize) {
      throw new Error(`File size exceeds maximum allowed size of ${this.settings.maxFileSize} bytes`);
    }

    if (!this.settings.allowedFileTypes.includes(file.mimetype)) {
      throw new Error(`File type ${file.mimetype} is not allowed`);
    }
  }

  private getFileType(mimeType: string): MessageType {
    if (mimeType.startsWith('image/')) {
      return MessageType.IMAGE;
    } else if (mimeType.startsWith('audio/')) {
      return MessageType.VOICE;
    } else {
      return MessageType.FILE;
    }
  }

  private generateFileName(originalName: string, type: MessageType): string {
    const extension = path.extname(originalName);
    const timestamp = new Date().getTime();
    const uniqueId = uuidv4();
    return `${type}-${timestamp}-${uniqueId}${extension}`;
  }

  private async processImage(file: Express.Multer.File, filePath: string): Promise<MediaMetadata> {
    const image = sharp(file.buffer);
    const metadata = await image.metadata();

    // Resize if needed
    if (metadata.width && metadata.width > this.settings.maxImageDimension) {
      await image
        .resize(this.settings.maxImageDimension, null, {
          fit: 'inside',
          withoutEnlargement: true
        })
        .toFile(filePath);
    } else {
      await fs.promises.writeFile(filePath, file.buffer);
    }

    // Generate thumbnail
    const thumbnailPath = filePath.replace(/\.[^/.]+$/, '-thumb.jpg');
    await image
      .resize(200, 200, {
        fit: 'cover',
        position: 'center'
      })
      .jpeg({ quality: 80 })
      .toFile(thumbnailPath);

    return {
      fileName: file.originalname,
      fileSize: file.size,
      mimeType: file.mimetype,
      width: metadata.width,
      height: metadata.height,
      thumbnailUrl: `/uploads/${path.basename(thumbnailPath)}`
    };
  }

  private async processVoice(file: Express.Multer.File, filePath: string): Promise<MediaMetadata> {
    await fs.promises.writeFile(filePath, file.buffer);

    // TODO: Implement voice duration detection
    // This would require additional audio processing libraries

    return {
      fileName: file.originalname,
      fileSize: file.size,
      mimeType: file.mimetype
    };
  }

  private async processFile(file: Express.Multer.File, filePath: string): Promise<MediaMetadata> {
    await fs.promises.writeFile(filePath, file.buffer);

    return {
      fileName: file.originalname,
      fileSize: file.size,
      mimeType: file.mimetype
    };
  }

  async deleteFile(fileUrl: string): Promise<void> {
    try {
      const fileName = path.basename(fileUrl);
      const filePath = path.join(this.uploadDir, fileName);
      const thumbnailPath = filePath.replace(/\.[^/.]+$/, '-thumb.jpg');

      await Promise.all([
        fs.promises.unlink(filePath).catch(() => {}),
        fs.promises.unlink(thumbnailPath).catch(() => {})
      ]);

      this.logger.info(`Deleted file: ${fileName}`);
    } catch (error) {
      this.logger.error('Failed to delete file', error);
      throw error;
    }
  }
} 