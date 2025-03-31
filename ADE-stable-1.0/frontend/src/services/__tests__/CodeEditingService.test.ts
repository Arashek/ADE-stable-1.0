import { Socket } from 'socket.io-client';
import { DefaultEventsMap } from 'socket.io/dist/typed-events';
import { CodeEditingService } from '../CodeEditingService';

describe('CodeEditingService', () => {
  let mockSocket: jest.Mocked<Socket<DefaultEventsMap, DefaultEventsMap>>;
  let service: CodeEditingService;

  beforeEach(() => {
    mockSocket = {
      emit: jest.fn(),
      on: jest.fn(),
      off: jest.fn(),
    } as unknown as jest.Mocked<Socket<DefaultEventsMap, DefaultEventsMap>>;

    service = new CodeEditingService({
      ws: mockSocket,
      projectId: 'test-project'
    });
  });

  afterEach(() => {
    service.dispose();
  });

  describe('code editing', () => {
    it('should apply code edits', async () => {
      const edit = {
        uri: 'file:///test.ts',
        range: {
          start: { line: 1, character: 1 },
          end: { line: 1, character: 5 }
        },
        newText: 'test',
        editId: 'test-edit'
      };

      await service.applyEdit(edit);

      expect(mockSocket.emit).toHaveBeenCalledWith('code:edit', expect.objectContaining({
        projectId: 'test-project',
        edit
      }));
    });
  });

  describe('code completion', () => {
    it('should request and handle code completion', async () => {
      const uri = 'file:///test.ts';
      const position = { line: 1, character: 5 };
      const completionItems = [
        {
          label: 'test',
          kind: 1,
          insertText: 'test'
        }
      ];

      const completionPromise = service.requestCompletion(uri, position);

      // Simulate completion response
      const completionHandler = mockSocket.on.mock.calls.find(call => call[0] === 'code:completion')?.[1];
      if (completionHandler) {
        completionHandler({ uri, items: completionItems });
      }

      const result = await completionPromise;

      expect(mockSocket.emit).toHaveBeenCalledWith('code:completion-request', expect.objectContaining({
        projectId: 'test-project',
        uri,
        position
      }));
      expect(result).toEqual(completionItems);
    });
  });

  describe('debugging', () => {
    it('should handle breakpoints', async () => {
      const breakpoint = {
        id: 'test-breakpoint',
        uri: 'file:///test.ts',
        line: 1
      };

      await service.setBreakpoint(breakpoint);

      expect(mockSocket.emit).toHaveBeenCalledWith('debug:set-breakpoint', expect.objectContaining({
        projectId: 'test-project',
        breakpoint
      }));

      await service.removeBreakpoint(breakpoint.id);

      expect(mockSocket.emit).toHaveBeenCalledWith('debug:remove-breakpoint', expect.objectContaining({
        projectId: 'test-project',
        breakpointId: breakpoint.id
      }));
    });

    it('should handle debugging session', async () => {
      const config = {
        type: 'node',
        request: 'launch',
        program: '${workspaceFolder}/test.ts'
      };

      await service.startDebugging(config);

      expect(mockSocket.emit).toHaveBeenCalledWith('debug:start', expect.objectContaining({
        projectId: 'test-project',
        configuration: config
      }));

      await service.stopDebugging();

      expect(mockSocket.emit).toHaveBeenCalledWith('debug:stop', expect.objectContaining({
        projectId: 'test-project'
      }));
    });
  });

  describe('diagnostics', () => {
    it('should handle code diagnostics', () => {
      const diagnostics = [
        {
          range: {
            start: { line: 1, character: 1 },
            end: { line: 1, character: 5 }
          },
          message: 'Test error',
          severity: 'error'
        }
      ];

      const diagnosticsHandler = mockSocket.on.mock.calls.find(call => call[0] === 'code:diagnostics')?.[1];
      if (diagnosticsHandler) {
        diagnosticsHandler({
          uri: 'file:///test.ts',
          diagnostics
        });
      }

      expect(mockSocket.emit).toHaveBeenCalledWith('ide:diagnostics', expect.objectContaining({
        projectId: 'test-project',
        uri: 'file:///test.ts',
        diagnostics
      }));
    });
  });
}); 