import { InteractiveDesignService } from '../InteractiveDesignService';
import { DatabaseService } from '../../DatabaseService';
import { FileService } from '../../FileService';
import { Server, Socket } from 'socket.io';
import {
  DesignCanvas,
  DesignElement,
  DesignStyle,
  DesignCollaboration,
} from '../../../../frontend/src/services/InteractiveDesignService';

jest.mock('socket.io');
jest.mock('../../DatabaseService');
jest.mock('../../FileService');

describe('InteractiveDesignService', () => {
  let service: InteractiveDesignService;
  let mockIo: jest.Mocked<Server>;
  let mockSocket: jest.Mocked<Socket>;
  let mockDb: jest.Mocked<DatabaseService>;
  let mockFileService: jest.Mocked<FileService>;

  const mockCanvas: DesignCanvas = {
    id: 'test-canvas-1',
    name: 'Test Canvas',
    elements: [
      {
        id: 'elem-1',
        type: 'component',
        content: 'Test Component',
        position: { x: 100, y: 100 },
        size: { width: 200, height: 100 },
        style: {
          fill: '#ffffff',
          stroke: '#000000',
          strokeWidth: 2,
        },
        properties: {},
      },
    ],
    style: {
      fill: '#ffffff',
      stroke: '#000000',
      strokeWidth: 1,
    },
    grid: {
      enabled: true,
      size: 20,
      color: '#e0e0e0',
    },
    snap: {
      enabled: true,
      threshold: 10,
    },
    zoom: 1,
    pan: { x: 0, y: 0 },
  };

  const mockCollaboration: DesignCollaboration = {
    id: 'test-collab-1',
    projectId: 'test-project-1',
    canvasId: 'test-canvas-1',
    participants: [
      {
        id: 'user-1',
        name: 'Test User',
        role: 'editor',
      },
    ],
    history: [],
    chat: [],
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
      getCanvas: jest.fn(),
      saveCanvas: jest.fn(),
      getCollaboration: jest.fn(),
      saveCollaboration: jest.fn(),
    } as any;

    mockFileService = {
      saveFile: jest.fn(),
      readFile: jest.fn(),
    } as any;

    service = new InteractiveDesignService(mockIo, mockDb, mockFileService);
  });

  describe('handleConnect', () => {
    it('should set up session and load existing data', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        userId: 'user-1',
        role: 'editor' as const,
      };

      mockDb.getCanvas.mockResolvedValue(mockCanvas);
      mockDb.getCollaboration.mockResolvedValue(mockCollaboration);

      await service['handleConnect'](mockSocket, data);

      expect(mockDb.getCanvas).toHaveBeenCalledWith(data.projectId);
      expect(mockDb.getCollaboration).toHaveBeenCalledWith(data.projectId);
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', { canvas: mockCanvas });
      expect(mockSocket.emit).toHaveBeenCalledWith('design:collaboration', { collaboration: mockCollaboration });
    });
  });

  describe('handleCreateCanvas', () => {
    it('should create a new canvas', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        name: 'New Canvas',
      };

      mockDb.saveCanvas.mockResolvedValue(undefined);

      await service['handleCreateCanvas'](mockSocket, data);

      expect(mockDb.saveCanvas).toHaveBeenCalled();
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', expect.any(Object));
    });

    it('should handle insufficient permissions', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        name: 'New Canvas',
      };

      // Mock viewer role
      service['sessions'].set('test-session-1', {
        socket: mockSocket,
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        userId: 'user-1',
        role: 'viewer',
      });

      await service['handleCreateCanvas'](mockSocket, data);

      expect(mockSocket.emit).toHaveBeenCalledWith('design:error', {
        error: 'Insufficient permissions',
      });
    });
  });

  describe('handleAddElement', () => {
    it('should add a new element to the canvas', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        element: {
          type: 'component',
          content: 'New Component',
          position: { x: 200, y: 200 },
          size: { width: 150, height: 75 },
          style: {
            fill: '#ffffff',
            stroke: '#000000',
            strokeWidth: 2,
          },
          properties: {},
        },
      };

      mockDb.getCanvas.mockResolvedValue(mockCanvas);
      mockDb.saveCanvas.mockResolvedValue(undefined);

      await service['handleAddElement'](mockSocket, data);

      expect(mockDb.getCanvas).toHaveBeenCalledWith(data.projectId);
      expect(mockDb.saveCanvas).toHaveBeenCalled();
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', expect.any(Object));
    });

    it('should handle canvas not found', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        element: {
          type: 'component',
          content: 'New Component',
          position: { x: 200, y: 200 },
          size: { width: 150, height: 75 },
          style: {
            fill: '#ffffff',
            stroke: '#000000',
            strokeWidth: 2,
          },
          properties: {},
        },
      };

      mockDb.getCanvas.mockResolvedValue(null);

      await service['handleAddElement'](mockSocket, data);

      expect(mockSocket.emit).toHaveBeenCalledWith('design:error', {
        error: 'Canvas not found',
      });
    });
  });

  describe('handleUpdateElement', () => {
    it('should update an existing element', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        elementId: 'elem-1',
        updates: {
          content: 'Updated Component',
        },
      };

      mockDb.getCanvas.mockResolvedValue(mockCanvas);
      mockDb.saveCanvas.mockResolvedValue(undefined);

      await service['handleUpdateElement'](mockSocket, data);

      expect(mockDb.getCanvas).toHaveBeenCalledWith(data.projectId);
      expect(mockDb.saveCanvas).toHaveBeenCalled();
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', expect.any(Object));
    });

    it('should handle element not found', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        elementId: 'non-existent',
        updates: {
          content: 'Updated Component',
        },
      };

      mockDb.getCanvas.mockResolvedValue(mockCanvas);

      await service['handleUpdateElement'](mockSocket, data);

      expect(mockSocket.emit).toHaveBeenCalledWith('design:error', {
        error: 'Element not found',
      });
    });
  });

  describe('handleUpdateStyle', () => {
    it('should update element style', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        elementId: 'elem-1',
        style: {
          fill: '#f0f0f0',
          stroke: '#333333',
          strokeWidth: 3,
        },
      };

      mockDb.getCanvas.mockResolvedValue(mockCanvas);
      mockDb.saveCanvas.mockResolvedValue(undefined);

      await service['handleUpdateStyle'](mockSocket, data);

      expect(mockDb.getCanvas).toHaveBeenCalledWith(data.projectId);
      expect(mockDb.saveCanvas).toHaveBeenCalled();
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', expect.any(Object));
    });

    it('should handle invalid style properties', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        elementId: 'elem-1',
        style: {
          fill: 'invalid-color',
          strokeWidth: -1,
          opacity: 2, // Invalid opacity value
        },
      };

      mockDb.getCanvas.mockResolvedValue(mockCanvas);

      await service['handleUpdateStyle'](mockSocket, data);

      expect(mockSocket.emit).toHaveBeenCalledWith('design:error', {
        error: 'Invalid style properties',
      });
    });

    it('should handle nested style updates', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        elementId: 'elem-1',
        style: {
          shadow: {
            color: '#000000',
            blur: 10,
            offsetX: 5,
            offsetY: 5,
          },
          font: {
            family: 'Arial',
            size: 16,
            weight: 'bold',
            style: 'normal',
            color: '#000000',
          },
        },
      };

      mockDb.getCanvas.mockResolvedValue(mockCanvas);
      mockDb.saveCanvas.mockResolvedValue(undefined);

      await service['handleUpdateStyle'](mockSocket, data);

      expect(mockDb.saveCanvas).toHaveBeenCalled();
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', expect.any(Object));
    });
  });

  describe('handleGroupElements', () => {
    it('should group selected elements', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        elementIds: ['elem-1'],
      };

      mockDb.getCanvas.mockResolvedValue(mockCanvas);
      mockDb.saveCanvas.mockResolvedValue(undefined);

      await service['handleGroupElements'](mockSocket, data);

      expect(mockDb.getCanvas).toHaveBeenCalledWith(data.projectId);
      expect(mockDb.saveCanvas).toHaveBeenCalled();
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', expect.any(Object));
    });

    it('should handle grouping locked elements', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        elementIds: ['elem-1'],
      };

      const canvasWithLockedElement = {
        ...mockCanvas,
        elements: [
          {
            ...mockCanvas.elements[0],
            locked: true,
          },
        ],
      };

      mockDb.getCanvas.mockResolvedValue(canvasWithLockedElement);

      await service['handleGroupElements'](mockSocket, data);

      expect(mockSocket.emit).toHaveBeenCalledWith('design:error', {
        error: 'Cannot group locked elements',
      });
    });

    it('should handle grouping elements from different layers', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        elementIds: ['elem-1', 'elem-2'],
      };

      const canvasWithLayeredElements = {
        ...mockCanvas,
        elements: [
          {
            ...mockCanvas.elements[0],
            layer: 1,
          },
          {
            id: 'elem-2',
            type: 'component',
            content: 'Second Component',
            position: { x: 300, y: 300 },
            size: { width: 200, height: 100 },
            style: {
              fill: '#ffffff',
              stroke: '#000000',
              strokeWidth: 2,
            },
            properties: {},
            layer: 2,
          },
        ],
      };

      mockDb.getCanvas.mockResolvedValue(canvasWithLayeredElements);

      await service['handleGroupElements'](mockSocket, data);

      expect(mockSocket.emit).toHaveBeenCalledWith('design:error', {
        error: 'Cannot group elements from different layers',
      });
    });
  });

  describe('handleUngroupElements', () => {
    it('should ungroup elements', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        groupId: 'group-1',
      };

      const canvasWithGroup = {
        ...mockCanvas,
        elements: [
          {
            ...mockCanvas.elements[0],
            groupId: 'group-1',
          },
        ],
      };

      mockDb.getCanvas.mockResolvedValue(canvasWithGroup);
      mockDb.saveCanvas.mockResolvedValue(undefined);

      await service['handleUngroupElements'](mockSocket, data);

      expect(mockDb.getCanvas).toHaveBeenCalledWith(data.projectId);
      expect(mockDb.saveCanvas).toHaveBeenCalled();
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', expect.any(Object));
    });
  });

  describe('handleUpdateCanvasSettings', () => {
    it('should update canvas settings', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        settings: {
          grid: {
            enabled: false,
            size: 30,
            color: '#cccccc',
          },
        },
      };

      mockDb.getCanvas.mockResolvedValue(mockCanvas);
      mockDb.saveCanvas.mockResolvedValue(undefined);

      await service['handleUpdateCanvasSettings'](mockSocket, data);

      expect(mockDb.getCanvas).toHaveBeenCalledWith(data.projectId);
      expect(mockDb.saveCanvas).toHaveBeenCalled();
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', expect.any(Object));
    });
  });

  describe('handleChatMessage', () => {
    it('should add chat message', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        message: 'Test message',
        type: 'text' as const,
      };

      mockDb.getCollaboration.mockResolvedValue(mockCollaboration);
      mockDb.saveCollaboration.mockResolvedValue(undefined);

      await service['handleChatMessage'](mockSocket, data);

      expect(mockDb.getCollaboration).toHaveBeenCalledWith(data.projectId);
      expect(mockDb.saveCollaboration).toHaveBeenCalled();
      expect(mockSocket.emit).toHaveBeenCalledWith('design:chat', expect.any(Object));
    });

    it('should handle command messages', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        message: '/align center',
        type: 'command' as const,
      };

      mockDb.getCollaboration.mockResolvedValue(mockCollaboration);
      mockDb.saveCollaboration.mockResolvedValue(undefined);

      await service['handleChatMessage'](mockSocket, data);

      expect(mockDb.saveCollaboration).toHaveBeenCalled();
      expect(mockSocket.emit).toHaveBeenCalledWith('design:chat', expect.any(Object));
    });

    it('should handle suggestion messages', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        message: 'Consider using a different color scheme for better contrast',
        type: 'suggestion' as const,
      };

      mockDb.getCollaboration.mockResolvedValue(mockCollaboration);
      mockDb.saveCollaboration.mockResolvedValue(undefined);

      await service['handleChatMessage'](mockSocket, data);

      expect(mockDb.saveCollaboration).toHaveBeenCalled();
      expect(mockSocket.emit).toHaveBeenCalledWith('design:chat', expect.any(Object));
    });
  });

  describe('handleUpdateCursor', () => {
    it('should update user cursor position', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        position: { x: 100, y: 100 },
      };

      mockDb.getCollaboration.mockResolvedValue(mockCollaboration);
      mockDb.saveCollaboration.mockResolvedValue(undefined);

      await service['handleUpdateCursor'](mockSocket, data);

      expect(mockDb.getCollaboration).toHaveBeenCalledWith(data.projectId);
      expect(mockDb.saveCollaboration).toHaveBeenCalled();
      expect(mockSocket.emit).toHaveBeenCalledWith('design:collaboration', expect.any(Object));
    });

    it('should handle cursor updates for multiple users', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        position: { x: 100, y: 100 },
      };

      const collaborationWithMultipleUsers = {
        ...mockCollaboration,
        participants: [
          {
            id: 'user-1',
            name: 'User 1',
            role: 'editor',
            cursor: { x: 50, y: 50, color: '#FF0000' },
          },
          {
            id: 'user-2',
            name: 'User 2',
            role: 'editor',
            cursor: { x: 150, y: 150, color: '#00FF00' },
          },
        ],
      };

      mockDb.getCollaboration.mockResolvedValue(collaborationWithMultipleUsers);
      mockDb.saveCollaboration.mockResolvedValue(undefined);

      await service['handleUpdateCursor'](mockSocket, data);

      expect(mockDb.saveCollaboration).toHaveBeenCalled();
      expect(mockSocket.emit).toHaveBeenCalledWith('design:collaboration', expect.any(Object));
    });

    it('should handle cursor updates with custom colors', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
        position: { x: 100, y: 100 },
        color: '#FF00FF',
      };

      mockDb.getCollaboration.mockResolvedValue(mockCollaboration);
      mockDb.saveCollaboration.mockResolvedValue(undefined);

      await service['handleUpdateCursor'](mockSocket, data);

      expect(mockDb.saveCollaboration).toHaveBeenCalled();
      expect(mockSocket.emit).toHaveBeenCalledWith('design:collaboration', expect.any(Object));
    });
  });

  describe('handleUndo', () => {
    it('should undo last action', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
      };

      const previousState = {
        ...mockCanvas,
        elements: [],
      };

      service['undoStacks'].set(data.projectId, [previousState]);
      mockDb.getCanvas.mockResolvedValue(mockCanvas);
      mockDb.saveCanvas.mockResolvedValue(undefined);

      await service['handleUndo'](mockSocket, data);

      expect(mockDb.saveCanvas).toHaveBeenCalledWith(data.projectId, previousState);
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', { canvas: previousState });
    });

    it('should handle nothing to undo', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
      };

      await service['handleUndo'](mockSocket, data);

      expect(mockSocket.emit).toHaveBeenCalledWith('design:error', {
        error: 'Nothing to undo',
      });
    });

    it('should handle undo with multiple actions', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
      };

      const states = [
        { ...mockCanvas, elements: [] },
        { ...mockCanvas, elements: [{ ...mockCanvas.elements[0] }] },
        { ...mockCanvas, elements: [{ ...mockCanvas.elements[0] }, { ...mockCanvas.elements[0], id: 'elem-2' }] },
      ];

      service['undoStacks'].set(data.projectId, states);
      mockDb.getCanvas.mockResolvedValue(states[2]);
      mockDb.saveCanvas.mockResolvedValue(undefined);

      await service['handleUndo'](mockSocket, data);

      expect(mockDb.saveCanvas).toHaveBeenCalledWith(data.projectId, states[1]);
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', { canvas: states[1] });
    });

    it('should handle undo with style changes', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
      };

      const previousState = {
        ...mockCanvas,
        elements: [
          {
            ...mockCanvas.elements[0],
            style: {
              fill: '#000000',
              stroke: '#ffffff',
              strokeWidth: 1,
            },
          },
        ],
      };

      service['undoStacks'].set(data.projectId, [previousState]);
      mockDb.getCanvas.mockResolvedValue(mockCanvas);
      mockDb.saveCanvas.mockResolvedValue(undefined);

      await service['handleUndo'](mockSocket, data);

      expect(mockDb.saveCanvas).toHaveBeenCalledWith(data.projectId, previousState);
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', { canvas: previousState });
    });
  });

  describe('handleRedo', () => {
    it('should redo last undone action', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
      };

      const nextState = {
        ...mockCanvas,
        elements: [],
      };

      service['redoStacks'].set(data.projectId, [nextState]);
      mockDb.getCanvas.mockResolvedValue(mockCanvas);
      mockDb.saveCanvas.mockResolvedValue(undefined);

      await service['handleRedo'](mockSocket, data);

      expect(mockDb.saveCanvas).toHaveBeenCalledWith(data.projectId, nextState);
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', { canvas: nextState });
    });

    it('should handle nothing to redo', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
      };

      await service['handleRedo'](mockSocket, data);

      expect(mockSocket.emit).toHaveBeenCalledWith('design:error', {
        error: 'Nothing to redo',
      });
    });

    it('should handle redo with multiple actions', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
      };

      const states = [
        { ...mockCanvas, elements: [] },
        { ...mockCanvas, elements: [{ ...mockCanvas.elements[0] }] },
        { ...mockCanvas, elements: [{ ...mockCanvas.elements[0] }, { ...mockCanvas.elements[0], id: 'elem-2' }] },
      ];

      service['redoStacks'].set(data.projectId, states);
      mockDb.getCanvas.mockResolvedValue(states[0]);
      mockDb.saveCanvas.mockResolvedValue(undefined);

      await service['handleRedo'](mockSocket, data);

      expect(mockDb.saveCanvas).toHaveBeenCalledWith(data.projectId, states[1]);
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', { canvas: states[1] });
    });

    it('should handle redo with group operations', async () => {
      const data = {
        projectId: 'test-project-1',
        sessionId: 'test-session-1',
        canvasId: 'test-canvas-1',
      };

      const nextState = {
        ...mockCanvas,
        elements: [
          {
            ...mockCanvas.elements[0],
            groupId: 'group-1',
          },
        ],
      };

      service['redoStacks'].set(data.projectId, [nextState]);
      mockDb.getCanvas.mockResolvedValue(mockCanvas);
      mockDb.saveCanvas.mockResolvedValue(undefined);

      await service['handleRedo'](mockSocket, data);

      expect(mockDb.saveCanvas).toHaveBeenCalledWith(data.projectId, nextState);
      expect(mockSocket.emit).toHaveBeenCalledWith('design:update', { canvas: nextState });
    });
  });
}); 