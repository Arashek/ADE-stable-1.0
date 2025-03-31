import { ArchitectureService } from '../ArchitectureService';
import { ArchitectureAnalyzer } from '../ArchitectureAnalyzer';
import { ArchitectureValidator } from '../ArchitectureValidator';
import { ArchitectureRenderer } from '../ArchitectureRenderer';
import { DatabaseService } from '../../DatabaseService';
import { FileService } from '../../FileService';
import { Server, Socket } from 'socket.io';
import { ArchitectureSpec, ArchitectureComponent, ArchitectureConnection } from '../../../../frontend/src/services/ArchitectureService';

jest.mock('socket.io');
jest.mock('../../DatabaseService');
jest.mock('../../FileService');
jest.mock('../ArchitectureAnalyzer');
jest.mock('../ArchitectureValidator');
jest.mock('../ArchitectureRenderer');

describe('ArchitectureService', () => {
  let service: ArchitectureService;
  let mockIo: jest.Mocked<Server>;
  let mockSocket: jest.Mocked<Socket>;
  let mockDb: jest.Mocked<DatabaseService>;
  let mockFileService: jest.Mocked<FileService>;
  let mockAnalyzer: jest.Mocked<ArchitectureAnalyzer>;
  let mockValidator: jest.Mocked<ArchitectureValidator>;
  let mockRenderer: jest.Mocked<ArchitectureRenderer>;

  const mockArchitecture: ArchitectureSpec = {
    id: 'test-arch-1',
    projectId: 'test-project-1',
    name: 'Test Architecture',
    description: 'Test architecture description',
    components: [
      {
        id: 'comp-1',
        name: 'Component 1',
        type: 'service',
        description: 'Test component 1',
        position: { x: 100, y: 100 },
        size: { width: 200, height: 100 },
        style: {
          color: '#ffffff',
          borderColor: '#000000',
          borderWidth: 2,
        },
      },
      {
        id: 'comp-2',
        name: 'Component 2',
        type: 'database',
        description: 'Test component 2',
        position: { x: 400, y: 100 },
        size: { width: 200, height: 100 },
        style: {
          color: '#ffffff',
          borderColor: '#000000',
          borderWidth: 2,
        },
      },
    ],
    connections: [
      {
        id: 'conn-1',
        sourceId: 'comp-1',
        targetId: 'comp-2',
        type: 'dependency',
        style: {
          color: '#666666',
          borderWidth: 2,
        },
      },
    ],
    createdAt: new Date(),
    updatedAt: new Date(),
    status: 'draft',
  };

  beforeEach(() => {
    mockIo = {
      on: jest.fn(),
    } as any;

    mockSocket = {
      emit: jest.fn(),
      on: jest.fn(),
    } as any;

    mockDb = {
      getArchitecture: jest.fn(),
      saveArchitecture: jest.fn(),
    } as any;

    mockFileService = {
      saveFile: jest.fn(),
      readFile: jest.fn(),
    } as any;

    mockAnalyzer = {
      analyzeArchitecture: jest.fn(),
    } as any;

    mockValidator = {
      validateArchitecture: jest.fn(),
    } as any;

    mockRenderer = {
      renderArchitecture: jest.fn(),
      saveRenderings: jest.fn(),
    } as any;

    service = new ArchitectureService(
      mockIo,
      mockDb,
      mockFileService,
      mockAnalyzer,
      mockValidator,
      mockRenderer
    );
  });

  describe('handleConnect', () => {
    it('should set up session and load existing architecture', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
      };

      mockDb.getArchitecture.mockResolvedValue(mockArchitecture);

      await service['handleConnect'](mockSocket, data);

      expect(mockDb.getArchitecture).toHaveBeenCalledWith(data.projectId);
      expect(mockSocket.emit).toHaveBeenCalledWith('architecture:update', {
        architecture: mockArchitecture,
      });
    });
  });

  describe('handleSave', () => {
    it('should save and validate architecture', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        architecture: mockArchitecture,
      };

      mockValidator.validateArchitecture.mockResolvedValue({ isValid: true, errors: [] });
      mockDb.saveArchitecture.mockResolvedValue(undefined);
      mockAnalyzer.analyzeArchitecture.mockResolvedValue({
        metrics: {
          complexity: 5,
          coupling: 0.3,
          cohesion: 0.8,
          scalability: 0.7,
          maintainability: 0.8,
        },
        insights: [],
        recommendations: [],
        issues: [],
      });

      await service['handleSave'](mockSocket, data);

      expect(mockValidator.validateArchitecture).toHaveBeenCalledWith(data.architecture);
      expect(mockDb.saveArchitecture).toHaveBeenCalledWith(data.projectId, data.architecture);
      expect(mockAnalyzer.analyzeArchitecture).toHaveBeenCalledWith(data.architecture);
      expect(mockSocket.emit).toHaveBeenCalledWith('architecture:analysis', expect.any(Object));
    });

    it('should handle validation errors', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        architecture: mockArchitecture,
      };

      mockValidator.validateArchitecture.mockResolvedValue({
        isValid: false,
        errors: ['Invalid architecture'],
      });

      await service['handleSave'](mockSocket, data);

      expect(mockSocket.emit).toHaveBeenCalledWith('architecture:error', {
        error: 'Invalid architecture',
      });
    });
  });

  describe('handleUpdateComponent', () => {
    it('should update component and validate architecture', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        componentId: 'comp-1',
        updates: {
          name: 'Updated Component 1',
        },
      };

      mockDb.getArchitecture.mockResolvedValue(mockArchitecture);
      mockValidator.validateArchitecture.mockResolvedValue({ isValid: true, errors: [] });
      mockDb.saveArchitecture.mockResolvedValue(undefined);
      mockAnalyzer.analyzeArchitecture.mockResolvedValue({
        metrics: {
          complexity: 5,
          coupling: 0.3,
          cohesion: 0.8,
          scalability: 0.7,
          maintainability: 0.8,
        },
        insights: [],
        recommendations: [],
        issues: [],
      });

      await service['handleUpdateComponent'](mockSocket, data);

      expect(mockDb.getArchitecture).toHaveBeenCalledWith(data.projectId);
      expect(mockValidator.validateArchitecture).toHaveBeenCalled();
      expect(mockDb.saveArchitecture).toHaveBeenCalled();
      expect(mockAnalyzer.analyzeArchitecture).toHaveBeenCalled();
    });

    it('should handle component not found', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        componentId: 'non-existent',
        updates: {
          name: 'Updated Component',
        },
      };

      mockDb.getArchitecture.mockResolvedValue(mockArchitecture);

      await service['handleUpdateComponent'](mockSocket, data);

      expect(mockSocket.emit).toHaveBeenCalledWith('architecture:error', {
        error: 'Component not found',
      });
    });
  });

  describe('handleUpdateConnection', () => {
    it('should update connection and validate architecture', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        connectionId: 'conn-1',
        updates: {
          type: 'composition',
        },
      };

      mockDb.getArchitecture.mockResolvedValue(mockArchitecture);
      mockValidator.validateArchitecture.mockResolvedValue({ isValid: true, errors: [] });
      mockDb.saveArchitecture.mockResolvedValue(undefined);
      mockAnalyzer.analyzeArchitecture.mockResolvedValue({
        metrics: {
          complexity: 5,
          coupling: 0.3,
          cohesion: 0.8,
          scalability: 0.7,
          maintainability: 0.8,
        },
        insights: [],
        recommendations: [],
        issues: [],
      });

      await service['handleUpdateConnection'](mockSocket, data);

      expect(mockDb.getArchitecture).toHaveBeenCalledWith(data.projectId);
      expect(mockValidator.validateArchitecture).toHaveBeenCalled();
      expect(mockDb.saveArchitecture).toHaveBeenCalled();
      expect(mockAnalyzer.analyzeArchitecture).toHaveBeenCalled();
    });

    it('should handle connection not found', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        connectionId: 'non-existent',
        updates: {
          type: 'composition',
        },
      };

      mockDb.getArchitecture.mockResolvedValue(mockArchitecture);

      await service['handleUpdateConnection'](mockSocket, data);

      expect(mockSocket.emit).toHaveBeenCalledWith('architecture:error', {
        error: 'Connection not found',
      });
    });
  });

  describe('handleAnalyze', () => {
    it('should analyze architecture', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
      };

      mockDb.getArchitecture.mockResolvedValue(mockArchitecture);
      mockAnalyzer.analyzeArchitecture.mockResolvedValue({
        metrics: {
          complexity: 5,
          coupling: 0.3,
          cohesion: 0.8,
          scalability: 0.7,
          maintainability: 0.8,
        },
        insights: [],
        recommendations: [],
        issues: [],
      });

      await service['handleAnalyze'](mockSocket, data);

      expect(mockDb.getArchitecture).toHaveBeenCalledWith(data.projectId);
      expect(mockAnalyzer.analyzeArchitecture).toHaveBeenCalledWith(mockArchitecture);
      expect(mockSocket.emit).toHaveBeenCalledWith('architecture:analysis', expect.any(Object));
    });

    it('should handle architecture not found', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
      };

      mockDb.getArchitecture.mockResolvedValue(null);

      await service['handleAnalyze'](mockSocket, data);

      expect(mockSocket.emit).toHaveBeenCalledWith('architecture:error', {
        error: 'Architecture not found',
      });
    });
  });

  describe('handleValidate', () => {
    it('should validate architecture', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
      };

      mockDb.getArchitecture.mockResolvedValue(mockArchitecture);
      mockValidator.validateArchitecture.mockResolvedValue({
        isValid: true,
        errors: [],
      });

      await service['handleValidate'](mockSocket, data);

      expect(mockDb.getArchitecture).toHaveBeenCalledWith(data.projectId);
      expect(mockValidator.validateArchitecture).toHaveBeenCalledWith(mockArchitecture);
      expect(mockSocket.emit).toHaveBeenCalledWith('architecture:validation', expect.any(Object));
    });

    it('should handle architecture not found', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
      };

      mockDb.getArchitecture.mockResolvedValue(null);

      await service['handleValidate'](mockSocket, data);

      expect(mockSocket.emit).toHaveBeenCalledWith('architecture:error', {
        error: 'Architecture not found',
      });
    });
  });

  describe('handleAddFeedback', () => {
    it('should add feedback to architecture', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        architectureId: 'test-arch-1',
        feedback: {
          from: 'test-user',
          comment: 'Test feedback',
        },
      };

      mockDb.getArchitecture.mockResolvedValue(mockArchitecture);
      mockDb.saveArchitecture.mockResolvedValue(undefined);

      await service['handleAddFeedback'](mockSocket, data);

      expect(mockDb.getArchitecture).toHaveBeenCalledWith(data.projectId);
      expect(mockDb.saveArchitecture).toHaveBeenCalled();
    });

    it('should handle architecture not found', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        architectureId: 'test-arch-1',
        feedback: {
          from: 'test-user',
          comment: 'Test feedback',
        },
      };

      mockDb.getArchitecture.mockResolvedValue(null);

      await service['handleAddFeedback'](mockSocket, data);

      expect(mockSocket.emit).toHaveBeenCalledWith('architecture:error', {
        error: 'Architecture not found',
      });
    });
  });
}); 