import { FigmaService } from '../FigmaService';
import { DatabaseService } from '../../../DatabaseService';
import { FileService } from '../../../FileService';
import axios from 'axios';

jest.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('FigmaService', () => {
  let service: FigmaService;
  let mockDb: jest.Mocked<DatabaseService>;
  let mockFileService: jest.Mocked<FileService>;

  const mockConfig = {
    accessToken: 'test-token',
    teamId: 'test-team',
    projectId: 'test-project',
  };

  beforeEach(() => {
    mockDb = {
      saveComponents: jest.fn(),
      saveStyles: jest.fn(),
    } as any;

    mockFileService = {
      saveFile: jest.fn(),
    } as any;

    service = new FigmaService(mockConfig, mockDb, mockFileService);
  });

  describe('validateAccessToken', () => {
    it('should return true when token is valid', async () => {
      mockedAxios.create.mockReturnValue({
        get: jest.fn().mockResolvedValue({ data: {} }),
      } as any);

      const result = await service.validateAccessToken();
      expect(result).toBe(true);
    });

    it('should return false when token is invalid', async () => {
      mockedAxios.create.mockReturnValue({
        get: jest.fn().mockRejectedValue(new Error('Invalid token')),
      } as any);

      const result = await service.validateAccessToken();
      expect(result).toBe(false);
    });
  });

  describe('getFile', () => {
    it('should fetch file data', async () => {
      const mockFile = {
        key: 'test-key',
        name: 'Test File',
        lastModified: '2024-01-01',
      };

      mockedAxios.create.mockReturnValue({
        get: jest.fn().mockResolvedValue({ data: mockFile }),
      } as any);

      const result = await service.getFile('test-key');
      expect(result).toEqual(mockFile);
    });
  });

  describe('getTeamComponents', () => {
    it('should fetch team components', async () => {
      const mockComponents = [
        {
          key: 'test-component',
          name: 'Test Component',
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
        },
      ];

      mockedAxios.create.mockReturnValue({
        get: jest.fn().mockResolvedValue({
          data: { meta: { components: mockComponents } },
        }),
      } as any);

      const result = await service.getTeamComponents('test-team');
      expect(result).toEqual(mockComponents);
    });
  });

  describe('syncComponents', () => {
    it('should sync components with database', async () => {
      const mockComponents = [
        {
          key: 'test-component',
          name: 'Test Component',
          created_at: '2024-01-01',
          updated_at: '2024-01-01',
        },
      ];

      mockedAxios.create.mockReturnValue({
        get: jest.fn().mockResolvedValue({
          data: { meta: { components: mockComponents } },
        }),
      } as any);

      await service.syncComponents('test-team');
      expect(mockDb.saveComponents).toHaveBeenCalledWith(mockComponents);
    });
  });

  describe('getTeamStyles', () => {
    it('should fetch team styles', async () => {
      const mockStyles = [
        {
          key: 'test-style',
          name: 'Test Style',
          remote: true,
          styleType: 'FILL',
        },
      ];

      mockedAxios.create.mockReturnValue({
        get: jest.fn().mockResolvedValue({
          data: { meta: { styles: mockStyles } },
        }),
      } as any);

      const result = await service.getTeamStyles('test-team');
      expect(result).toEqual(mockStyles);
    });
  });

  describe('syncStyles', () => {
    it('should sync styles with database', async () => {
      const mockStyles = [
        {
          key: 'test-style',
          name: 'Test Style',
          remote: true,
          styleType: 'FILL',
        },
      ];

      mockedAxios.create.mockReturnValue({
        get: jest.fn().mockResolvedValue({
          data: { meta: { styles: mockStyles } },
        }),
      } as any);

      await service.syncStyles('test-team');
      expect(mockDb.saveStyles).toHaveBeenCalledWith(mockStyles);
    });
  });

  describe('exportNode', () => {
    it('should export node as image', async () => {
      const mockImageUrl = 'https://example.com/image.png';
      const mockImageData = Buffer.from('test-image-data');

      mockedAxios.create.mockReturnValue({
        get: jest.fn()
          .mockResolvedValueOnce({ data: { images: { 'test-node': mockImageUrl } } })
          .mockResolvedValueOnce({ data: mockImageData }),
      } as any);

      await service.exportNode('test-file', 'test-node');
      expect(mockFileService.saveFile).toHaveBeenCalledWith(
        'exports/test-node.png',
        mockImageData
      );
    });
  });
}); 