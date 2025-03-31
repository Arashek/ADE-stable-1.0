import { Socket } from 'socket.io-client';
import { DefaultEventsMap } from 'socket.io/dist/typed-events';
import { IDECommunicationService } from '../IDECommunicationService';

describe('IDECommunicationService', () => {
  let mockSocket: jest.Mocked<Socket<DefaultEventsMap, DefaultEventsMap>>;
  let service: IDECommunicationService;

  beforeEach(() => {
    mockSocket = {
      emit: jest.fn(),
      on: jest.fn(),
      off: jest.fn(),
    } as unknown as jest.Mocked<Socket<DefaultEventsMap, DefaultEventsMap>>;

    service = new IDECommunicationService({
      ws: mockSocket,
      projectId: 'test-project',
      ideConfig: {
        type: 'vscode',
        version: '1.0.0',
        capabilities: [],
      },
    });
  });

  afterEach(() => {
    service.dispose();
  });

  describe('initialization', () => {
    it('should set up event listeners on initialize', async () => {
      await service.initialize();

      expect(mockSocket.on).toHaveBeenCalledWith('ide:connected', expect.any(Function));
      expect(mockSocket.on).toHaveBeenCalledWith('ide:disconnected', expect.any(Function));
      expect(mockSocket.on).toHaveBeenCalledWith('ide:message', expect.any(Function));
      expect(mockSocket.on).toHaveBeenCalledWith('ide:capability-update', expect.any(Function));
      expect(mockSocket.on).toHaveBeenCalledWith('ide:extension-update', expect.any(Function));
    });

    it('should emit connection message on initialize', async () => {
      await service.initialize();

      expect(mockSocket.emit).toHaveBeenCalledWith('ide:connect', expect.objectContaining({
        projectId: 'test-project',
        config: expect.any(Object),
      }));
    });
  });

  describe('message handling', () => {
    it('should queue messages when disconnected', async () => {
      const message = {
        type: 'test',
        payload: { data: 'test' },
        metadata: {
          timestamp: new Date(),
          source: 'test',
          target: 'test',
        },
      };

      await service.sendMessage(message);
      expect(mockSocket.emit).not.toHaveBeenCalled();
    });

    it('should process queued messages when connected', async () => {
      const message = {
        type: 'test',
        payload: { data: 'test' },
        metadata: {
          timestamp: new Date(),
          source: 'test',
          target: 'test',
        },
      };

      await service.sendMessage(message);
      
      // Find the connected callback and call it
      const connectedCallback = mockSocket.on.mock.calls.find(call => call[0] === 'ide:connected')?.[1];
      if (connectedCallback) {
        connectedCallback();
      }
      
      await service.initialize();

      expect(mockSocket.emit).toHaveBeenCalledWith('ide:message', expect.objectContaining({
        projectId: 'test-project',
        ...message,
      }));
    });
  });

  describe('capability handling', () => {
    it('should set up VSCode capabilities', async () => {
      service = new IDECommunicationService({
        ws: mockSocket,
        projectId: 'test-project',
        ideConfig: {
          type: 'vscode',
          version: '1.0.0',
          capabilities: [],
        },
      });

      await service.initialize();

      expect(mockSocket.emit).toHaveBeenCalledWith('ide:capability-setup', expect.objectContaining({
        capabilities: expect.arrayContaining([
          'file:open',
          'file:save',
          'file:close',
          'command:execute',
          'debug:start',
          'debug:stop',
          'completion:provide',
          'hover:provide',
          'definition:provide',
          'reference:provide',
        ]),
      }));
    });

    it('should set up JetBrains capabilities', async () => {
      service = new IDECommunicationService({
        ws: mockSocket,
        projectId: 'test-project',
        ideConfig: {
          type: 'jetbrains',
          version: '1.0.0',
          capabilities: [],
        },
      });

      await service.initialize();

      expect(mockSocket.emit).toHaveBeenCalledWith('ide:capability-setup', expect.objectContaining({
        capabilities: expect.arrayContaining([
          'refactoring:provide',
          'intention:provide',
          'quickfix:provide',
        ]),
      }));
    });

    it('should set up web IDE capabilities', async () => {
      service = new IDECommunicationService({
        ws: mockSocket,
        projectId: 'test-project',
        ideConfig: {
          type: 'web',
          version: '1.0.0',
          capabilities: [],
        },
      });

      await service.initialize();

      expect(mockSocket.emit).toHaveBeenCalledWith('ide:capability-setup', expect.objectContaining({
        capabilities: expect.arrayContaining([
          'collaboration:provide',
          'preview:provide',
        ]),
      }));
    });
  });

  describe('disposal', () => {
    it('should clean up resources on dispose', () => {
      service.dispose();
      expect(mockSocket.emit).toHaveBeenCalledWith('ide:disconnect', expect.objectContaining({
        projectId: 'test-project',
      }));
    });
  });
}); 