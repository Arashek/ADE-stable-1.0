import { Socket } from 'socket.io-client';
import { DesignAgentService, DesignSpec, DesignComponent } from '../DesignAgentService';
import { DefaultEventsMap } from 'socket.io/dist/typed-events';

describe('DesignAgentService', () => {
  let mockSocket: jest.Mocked<Socket<DefaultEventsMap, DefaultEventsMap>>;
  let service: DesignAgentService;
  const projectId = 'test-project-id';

  beforeEach(() => {
    mockSocket = {
      on: jest.fn(),
      emit: jest.fn().mockReturnThis(),
    } as unknown as jest.Mocked<Socket<DefaultEventsMap, DefaultEventsMap>>;

    service = new DesignAgentService({ ws: mockSocket, projectId });
  });

  describe('initialization', () => {
    it('should set up event listeners on initialize', async () => {
      await service.initialize();

      expect(mockSocket.on).toHaveBeenCalledWith('design:update', expect.any(Function));
      expect(mockSocket.on).toHaveBeenCalledWith('design:feedback', expect.any(Function));
      expect(mockSocket.on).toHaveBeenCalledWith('design:system-update', expect.any(Function));
      expect(mockSocket.on).toHaveBeenCalledWith('design:preview-update', expect.any(Function));
      expect(mockSocket.emit).toHaveBeenCalledWith('design:connect', expect.any(Object));
    });
  });

  describe('design operations', () => {
    const mockDesign: DesignSpec = {
      id: 'test-design-id',
      projectId,
      name: 'Test Design',
      description: 'Test Description',
      components: [],
      createdAt: new Date(),
      updatedAt: new Date(),
      status: 'draft',
    };

    it('should save a design', async () => {
      const successResponse = { success: true };
      mockSocket.emit.mockImplementation((event, data, callback) => {
        callback(successResponse);
        return mockSocket;
      });

      const result = await service.saveDesign(mockDesign);

      expect(mockSocket.emit).toHaveBeenCalledWith(
        'design:save',
        expect.objectContaining({
          projectId,
          design: mockDesign,
        }),
        expect.any(Function)
      );
      expect(result).toEqual(successResponse);
    });

    it('should update a design', async () => {
      const updates = { name: 'Updated Design' };
      const successResponse = { success: true };
      mockSocket.emit.mockImplementation((event, data, callback) => {
        callback(successResponse);
        return mockSocket;
      });

      const result = await service.updateDesign(mockDesign.id, updates);

      expect(mockSocket.emit).toHaveBeenCalledWith(
        'design:update',
        expect.objectContaining({
          projectId,
          designId: mockDesign.id,
          updates,
        }),
        expect.any(Function)
      );
      expect(result).toEqual(successResponse);
    });

    it('should add feedback to a design', async () => {
      const feedback = {
        from: 'test-user',
        comment: 'Test feedback',
      };
      const successResponse = { success: true };
      mockSocket.emit.mockImplementation((event, data, callback) => {
        callback(successResponse);
        return mockSocket;
      });

      const result = await service.addFeedback(mockDesign.id, feedback);

      expect(mockSocket.emit).toHaveBeenCalledWith(
        'design:add-feedback',
        expect.objectContaining({
          projectId,
          designId: mockDesign.id,
          feedback,
        }),
        expect.any(Function)
      );
      expect(result).toEqual(successResponse);
    });

    it('should generate a preview', async () => {
      const previewResponse = {
        success: true,
        preview: 'data:image/png;base64,test-preview',
      };
      mockSocket.emit.mockImplementation((event, data, callback) => {
        callback(previewResponse);
        return mockSocket;
      });

      const result = await service.generatePreview(mockDesign.id);

      expect(mockSocket.emit).toHaveBeenCalledWith(
        'design:generate-preview',
        expect.objectContaining({
          projectId,
          designId: mockDesign.id,
        }),
        expect.any(Function)
      );
      expect(result).toBe(previewResponse.preview);
    });

    it('should implement a design', async () => {
      const successResponse = { success: true };
      mockSocket.emit.mockImplementation((event, data, callback) => {
        callback(successResponse);
        return mockSocket;
      });

      const result = await service.implementDesign(mockDesign.id);

      expect(mockSocket.emit).toHaveBeenCalledWith(
        'design:implement',
        expect.objectContaining({
          projectId,
          designId: mockDesign.id,
        }),
        expect.any(Function)
      );
      expect(result).toEqual(successResponse);
    });
  });

  describe('error handling', () => {
    it('should reject with error message on failure', async () => {
      const errorResponse = {
        success: false,
        error: 'Test error message',
      };
      mockSocket.emit.mockImplementation((event, data, callback) => {
        callback(errorResponse);
        return mockSocket;
      });

      await expect(service.saveDesign({} as DesignSpec)).rejects.toThrow('Test error message');
    });
  });

  describe('disposal', () => {
    it('should emit disconnect event on dispose', () => {
      service.dispose();

      expect(mockSocket.emit).toHaveBeenCalledWith(
        'design:disconnect',
        expect.objectContaining({
          projectId,
        })
      );
    });
  });
}); 