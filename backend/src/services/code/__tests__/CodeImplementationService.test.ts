import { CodeImplementationService } from '../CodeImplementationService';
import { CodeAnalyzer } from '../CodeAnalyzer';
import { CodeCompiler } from '../CodeCompiler';
import { CodeValidator } from '../CodeValidator';
import { DatabaseService } from '../../DatabaseService';
import { FileService } from '../../FileService';
import { Server, Socket } from 'socket.io';
import { CodeImplementation, CodeFile } from '../../../../frontend/src/services/CodeImplementationService';

jest.mock('socket.io');
jest.mock('../../DatabaseService');
jest.mock('../../FileService');
jest.mock('../CodeAnalyzer');
jest.mock('../CodeCompiler');
jest.mock('../CodeValidator');

describe('CodeImplementationService', () => {
  let service: CodeImplementationService;
  let mockIo: jest.Mocked<Server>;
  let mockSocket: jest.Mocked<Socket>;
  let mockDb: jest.Mocked<DatabaseService>;
  let mockFileService: jest.Mocked<FileService>;
  let mockAnalyzer: jest.Mocked<CodeAnalyzer>;
  let mockCompiler: jest.Mocked<CodeCompiler>;
  let mockValidator: jest.Mocked<CodeValidator>;

  beforeEach(() => {
    mockIo = new Server() as jest.Mocked<Server>;
    mockSocket = {
      on: jest.fn(),
      emit: jest.fn(),
    } as unknown as jest.Mocked<Socket>;

    mockDb = {
      getCodeImplementations: jest.fn(),
      saveCodeImplementation: jest.fn(),
      getCodeImplementation: jest.fn(),
    } as unknown as jest.Mocked<DatabaseService>;

    mockFileService = {
      saveFile: jest.fn(),
    } as unknown as jest.Mocked<FileService>;

    mockAnalyzer = {
      analyzeFile: jest.fn(),
    } as unknown as jest.Mocked<CodeAnalyzer>;

    mockCompiler = {
      compileImplementation: jest.fn(),
    } as unknown as jest.Mocked<CodeCompiler>;

    mockValidator = {
      validateImplementation: jest.fn(),
    } as unknown as jest.Mocked<CodeValidator>;

    service = new CodeImplementationService(
      mockIo,
      mockDb,
      mockFileService,
      mockAnalyzer,
      mockCompiler,
      mockValidator
    );
  });

  describe('handleConnect', () => {
    it('should set up session and load implementations', async () => {
      const projectId = 'test-project';
      const sessionId = 'test-session';
      const mockImplementation: CodeImplementation = {
        id: 'test-impl',
        projectId,
        name: 'Test Implementation',
        description: 'Test Description',
        files: [],
        status: 'draft',
      };

      mockDb.getCodeImplementations.mockResolvedValue([mockImplementation]);

      await service['handleConnect'](mockSocket, { projectId, sessionId });

      expect(mockSocket.emit).toHaveBeenCalledWith('code:update', {
        implementation: mockImplementation,
      });
    });
  });

  describe('handleSave', () => {
    it('should save implementation and analyze code', async () => {
      const projectId = 'test-project';
      const sessionId = 'test-session';
      const mockImplementation: CodeImplementation = {
        id: 'test-impl',
        projectId,
        name: 'Test Implementation',
        description: 'Test Description',
        files: [
          {
            id: 'test-file',
            path: 'test.ts',
            content: 'console.log("test")',
            language: 'typescript',
            dependencies: [],
            lastModified: new Date(),
          },
        ],
        status: 'draft',
      };

      mockValidator.validateImplementation.mockResolvedValue({ isValid: true, errors: [] });
      mockDb.saveCodeImplementation.mockResolvedValue(undefined);
      mockAnalyzer.analyzeFile.mockResolvedValue({
        complexity: 1,
        maintainability: 80,
        testCoverage: 100,
        issues: [],
      });

      await service['handleSave'](mockSocket, {
        projectId,
        sessionId,
        implementation: mockImplementation,
      });

      expect(mockValidator.validateImplementation).toHaveBeenCalledWith(mockImplementation);
      expect(mockDb.saveCodeImplementation).toHaveBeenCalledWith(projectId, mockImplementation);
      expect(mockFileService.saveFile).toHaveBeenCalledWith(
        'test.ts',
        'console.log("test")'
      );
      expect(mockAnalyzer.analyzeFile).toHaveBeenCalledWith(mockImplementation.files[0]);
    });

    it('should handle validation errors', async () => {
      const projectId = 'test-project';
      const sessionId = 'test-session';
      const mockImplementation: CodeImplementation = {
        id: 'test-impl',
        projectId,
        name: 'Test Implementation',
        description: 'Test Description',
        files: [],
        status: 'draft',
      };

      mockValidator.validateImplementation.mockResolvedValue({
        isValid: false,
        errors: ['Invalid implementation'],
      });

      await service['handleSave'](mockSocket, {
        projectId,
        sessionId,
        implementation: mockImplementation,
      });

      expect(mockSocket.emit).toHaveBeenCalledWith('code:error', {
        error: 'Invalid implementation',
      });
    });
  });

  describe('handleUpdateFile', () => {
    it('should update file and analyze changes', async () => {
      const projectId = 'test-project';
      const sessionId = 'test-session';
      const fileId = 'test-file';
      const updates = {
        content: 'console.log("updated")',
      };

      const mockImplementation: CodeImplementation = {
        id: 'test-impl',
        projectId,
        name: 'Test Implementation',
        description: 'Test Description',
        files: [
          {
            id: fileId,
            path: 'test.ts',
            content: 'console.log("test")',
            language: 'typescript',
            dependencies: [],
            lastModified: new Date(),
          },
        ],
        status: 'draft',
      };

      mockDb.getCodeImplementation.mockResolvedValue(mockImplementation);
      mockValidator.validateImplementation.mockResolvedValue({ isValid: true, errors: [] });
      mockDb.saveCodeImplementation.mockResolvedValue(undefined);
      mockAnalyzer.analyzeFile.mockResolvedValue({
        complexity: 1,
        maintainability: 80,
        testCoverage: 100,
        issues: [],
      });

      await service['handleUpdateFile'](mockSocket, {
        projectId,
        sessionId,
        fileId,
        updates,
      });

      expect(mockFileService.saveFile).toHaveBeenCalledWith(
        'test.ts',
        'console.log("updated")'
      );
      expect(mockAnalyzer.analyzeFile).toHaveBeenCalled();
    });

    it('should handle file not found', async () => {
      const projectId = 'test-project';
      const sessionId = 'test-session';
      const fileId = 'non-existent';

      const mockImplementation: CodeImplementation = {
        id: 'test-impl',
        projectId,
        name: 'Test Implementation',
        description: 'Test Description',
        files: [],
        status: 'draft',
      };

      mockDb.getCodeImplementation.mockResolvedValue(mockImplementation);

      await service['handleUpdateFile'](mockSocket, {
        projectId,
        sessionId,
        fileId,
        updates: {},
      });

      expect(mockSocket.emit).toHaveBeenCalledWith('code:error', {
        error: 'File not found',
      });
    });
  });

  describe('handleCompile', () => {
    it('should compile implementation and update status', async () => {
      const projectId = 'test-project';
      const sessionId = 'test-session';
      const implementationId = 'test-impl';

      const mockImplementation: CodeImplementation = {
        id: implementationId,
        projectId,
        name: 'Test Implementation',
        description: 'Test Description',
        files: [],
        status: 'draft',
      };

      mockDb.getCodeImplementation.mockResolvedValue(mockImplementation);
      mockCompiler.compileImplementation.mockResolvedValue({
        success: true,
        output: 'Compilation successful',
      });

      await service['handleCompile'](mockSocket, {
        projectId,
        sessionId,
        implementationId,
      });

      expect(mockCompiler.compileImplementation).toHaveBeenCalledWith(mockImplementation);
      expect(mockSocket.emit).toHaveBeenCalledWith('code:compilation', {
        success: true,
        output: 'Compilation successful',
      });
      expect(mockDb.saveCodeImplementation).toHaveBeenCalledWith(projectId, {
        ...mockImplementation,
        status: 'implemented',
      });
    });

    it('should handle compilation failure', async () => {
      const projectId = 'test-project';
      const sessionId = 'test-session';
      const implementationId = 'test-impl';

      const mockImplementation: CodeImplementation = {
        id: implementationId,
        projectId,
        name: 'Test Implementation',
        description: 'Test Description',
        files: [],
        status: 'draft',
      };

      mockDb.getCodeImplementation.mockResolvedValue(mockImplementation);
      mockCompiler.compileImplementation.mockResolvedValue({
        success: false,
        error: 'Compilation failed',
      });

      await service['handleCompile'](mockSocket, {
        projectId,
        sessionId,
        implementationId,
      });

      expect(mockSocket.emit).toHaveBeenCalledWith('code:compilation', {
        success: false,
        error: 'Compilation failed',
      });
      expect(mockDb.saveCodeImplementation).not.toHaveBeenCalled();
    });
  });

  describe('handleAddFeedback', () => {
    it('should add feedback to implementation', async () => {
      const projectId = 'test-project';
      const sessionId = 'test-session';
      const implementationId = 'test-impl';
      const feedback = {
        from: 'test-user',
        comment: 'Test feedback',
      };

      const mockImplementation: CodeImplementation = {
        id: implementationId,
        projectId,
        name: 'Test Implementation',
        description: 'Test Description',
        files: [],
        status: 'draft',
      };

      mockDb.getCodeImplementation.mockResolvedValue(mockImplementation);

      await service['handleAddFeedback'](mockSocket, {
        projectId,
        sessionId,
        implementationId,
        feedback,
      });

      expect(mockDb.saveCodeImplementation).toHaveBeenCalledWith(projectId, {
        ...mockImplementation,
        feedback: [
          {
            id: expect.any(String),
            from: feedback.from,
            comment: feedback.comment,
            timestamp: expect.any(Date),
            status: 'pending',
          },
        ],
      });
    });
  });
}); 