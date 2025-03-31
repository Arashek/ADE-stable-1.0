import { MediaUploader } from '../MediaUploader';
import * as fs from 'fs';
import * as path from 'path';
import { MessageType } from '../types';

jest.mock('fs');
jest.mock('path');
jest.mock('sharp');

describe('MediaUploader', () => {
  let mediaUploader: MediaUploader;
  const mockUploadDir = '/mock/upload/dir';
  const mockSettings = {
    maxFileSize: 10 * 1024 * 1024, // 10MB
    allowedFileTypes: ['image/jpeg', 'image/png', 'audio/mp3', 'application/pdf'],
    maxImageDimension: 1920,
    maxVoiceDuration: 300, // 5 minutes
    storageQuota: 100 * 1024 * 1024, // 100MB
    compressionEnabled: true
  };

  beforeEach(() => {
    jest.clearAllMocks();
    mediaUploader = new MediaUploader(mockUploadDir, mockSettings);
  });

  describe('uploadFile', () => {
    const mockFile = {
      originalname: 'test.jpg',
      mimetype: 'image/jpeg',
      size: 5 * 1024 * 1024, // 5MB
      buffer: Buffer.from('test image data')
    };

    it('should upload and process an image file', async () => {
      const mockSharp = {
        metadata: jest.fn().mockResolvedValue({
          width: 2000,
          height: 1500
        }),
        resize: jest.fn().mockReturnThis(),
        toFile: jest.fn().mockResolvedValue(undefined),
        jpeg: jest.fn().mockReturnThis()
      };

      require('sharp').mockImplementation(() => mockSharp);

      const result = await mediaUploader.uploadFile(mockFile as any, 'user123');

      expect(result.type).toBe(MessageType.IMAGE);
      expect(result.metadata).toMatchObject({
        fileName: mockFile.originalname,
        fileSize: mockFile.size,
        mimeType: mockFile.mimetype,
        width: 2000,
        height: 1500
      });
      expect(result.url).toMatch(/^\/uploads\/image-.*\.jpg$/);
      expect(mockSharp.resize).toHaveBeenCalledWith(
        mockSettings.maxImageDimension,
        null,
        expect.any(Object)
      );
    });

    it('should upload a voice file', async () => {
      const mockVoiceFile = {
        ...mockFile,
        mimetype: 'audio/mp3'
      };

      const result = await mediaUploader.uploadFile(mockVoiceFile as any, 'user123');

      expect(result.type).toBe(MessageType.VOICE);
      expect(result.metadata).toMatchObject({
        fileName: mockVoiceFile.originalname,
        fileSize: mockVoiceFile.size,
        mimeType: mockVoiceFile.mimetype
      });
      expect(result.url).toMatch(/^\/uploads\/voice-.*\.mp3$/);
    });

    it('should upload a regular file', async () => {
      const mockRegularFile = {
        ...mockFile,
        mimetype: 'application/pdf'
      };

      const result = await mediaUploader.uploadFile(mockRegularFile as any, 'user123');

      expect(result.type).toBe(MessageType.FILE);
      expect(result.metadata).toMatchObject({
        fileName: mockRegularFile.originalname,
        fileSize: mockRegularFile.size,
        mimeType: mockRegularFile.mimetype
      });
      expect(result.url).toMatch(/^\/uploads\/file-.*\.pdf$/);
    });

    it('should throw error for file size exceeding limit', async () => {
      const largeFile = {
        ...mockFile,
        size: 15 * 1024 * 1024 // 15MB
      };

      await expect(mediaUploader.uploadFile(largeFile as any, 'user123'))
        .rejects.toThrow(/File size exceeds maximum allowed size/);
    });

    it('should throw error for unsupported file type', async () => {
      const unsupportedFile = {
        ...mockFile,
        mimetype: 'application/x-unsupported'
      };

      await expect(mediaUploader.uploadFile(unsupportedFile as any, 'user123'))
        .rejects.toThrow(/File type .* is not allowed/);
    });
  });

  describe('deleteFile', () => {
    it('should delete file and its thumbnail', async () => {
      const fileUrl = '/uploads/test-image.jpg';
      const mockUnlink = jest.fn().mockResolvedValue(undefined);
      (fs.promises.unlink as jest.Mock).mockImplementation(mockUnlink);

      await mediaUploader.deleteFile(fileUrl);

      expect(mockUnlink).toHaveBeenCalledTimes(2);
      expect(mockUnlink).toHaveBeenCalledWith(
        expect.stringContaining('test-image.jpg')
      );
      expect(mockUnlink).toHaveBeenCalledWith(
        expect.stringContaining('test-image-thumb.jpg')
      );
    });

    it('should handle errors when deleting files', async () => {
      const fileUrl = '/uploads/test-image.jpg';
      const mockUnlink = jest.fn().mockRejectedValue(new Error('Delete failed'));
      (fs.promises.unlink as jest.Mock).mockImplementation(mockUnlink);

      await expect(mediaUploader.deleteFile(fileUrl))
        .rejects.toThrow('Delete failed');
    });
  });
}); 