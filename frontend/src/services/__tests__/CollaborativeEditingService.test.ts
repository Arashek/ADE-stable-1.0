import { Socket } from 'socket.io-client';
import { DefaultEventsMap } from 'socket.io/dist/typed-events';
import { CollaborativeEditingService } from '../CollaborativeEditingService';
import * as monaco from 'monaco-editor';

describe('CollaborativeEditingService', () => {
  let mockSocket: jest.Mocked<Socket<DefaultEventsMap, DefaultEventsMap>>;
  let mockEditor: jest.Mocked<monaco.editor.IStandaloneCodeEditor>;
  let service: CollaborativeEditingService;

  beforeEach(() => {
    mockSocket = {
      emit: jest.fn(),
      on: jest.fn(),
      off: jest.fn(),
    } as unknown as jest.Mocked<Socket<DefaultEventsMap, DefaultEventsMap>>;

    mockEditor = {
      deltaDecorations: jest.fn(),
      getModel: jest.fn(),
      onDidChangeModelContent: jest.fn(),
      onDidChangeCursorPosition: jest.fn(),
      onDidChangeCursorSelection: jest.fn(),
    } as unknown as jest.Mocked<monaco.editor.IStandaloneCodeEditor>;

    service = new CollaborativeEditingService({
      ws: mockSocket,
      projectId: 'test-project',
      editor: mockEditor
    });
  });

  afterEach(() => {
    service.dispose();
  });

  describe('document collaboration', () => {
    it('should join and leave document', async () => {
      const uri = 'file:///test.ts';

      await service.joinDocument(uri);

      expect(mockSocket.emit).toHaveBeenCalledWith('collaboration:join-document', expect.objectContaining({
        projectId: 'test-project',
        uri
      }));

      await service.leaveDocument(uri);

      expect(mockSocket.emit).toHaveBeenCalledWith('collaboration:leave-document', expect.objectContaining({
        projectId: 'test-project',
        uri
      }));
    });

    it('should handle user presence', () => {
      const user = {
        id: 'user-1',
        name: 'Test User',
        presence: 'online' as const
      };

      const userJoinedHandler = mockSocket.on.mock.calls.find(call => call[0] === 'collaboration:user-joined')?.[1];
      if (userJoinedHandler) {
        userJoinedHandler({ user });
      }

      expect(service.getActiveUsers()).toContainEqual(user);

      const userLeftHandler = mockSocket.on.mock.calls.find(call => call[0] === 'collaboration:user-left')?.[1];
      if (userLeftHandler) {
        userLeftHandler({ userId: user.id });
      }

      expect(service.getActiveUsers()).not.toContainEqual(user);
    });

    it('should handle code changes', async () => {
      const uri = 'file:///test.ts';
      const change = {
        uri,
        version: 1,
        changes: [
          {
            range: {
              start: { line: 1, character: 1 },
              end: { line: 1, character: 5 }
            },
            text: 'test'
          }
        ],
        userId: 'user-1',
        timestamp: Date.now()
      };

      await service.applyChange(change);

      expect(mockSocket.emit).toHaveBeenCalledWith('collaboration:change', expect.objectContaining({
        projectId: 'test-project',
        change
      }));

      const changeHandler = mockSocket.on.mock.calls.find(call => call[0] === 'collaboration:change')?.[1];
      if (changeHandler) {
        changeHandler({ change });
      }

      expect(service.getChangeHistory(uri)).toContainEqual(change);
    });

    it('should handle conflicts', async () => {
      const uri = 'file:///test.ts';
      const conflict = {
        uri,
        version: 2,
        localChange: {
          uri,
          version: 1,
          changes: [
            {
              range: {
                start: { line: 1, character: 1 },
                end: { line: 1, character: 5 }
              },
              text: 'local'
            }
          ],
          userId: 'user-1',
          timestamp: Date.now()
        },
        remoteChange: {
          uri,
          version: 1,
          changes: [
            {
              range: {
                start: { line: 1, character: 1 },
                end: { line: 1, character: 5 }
              },
              text: 'remote'
            }
          ],
          userId: 'user-2',
          timestamp: Date.now()
        }
      };

      const conflictHandler = mockSocket.on.mock.calls.find(call => call[0] === 'collaboration:conflict')?.[1];
      if (conflictHandler) {
        conflictHandler({ conflict });
      }

      expect(service.getConflicts(uri)).toContainEqual(conflict);

      const resolution = {
        ...conflict,
        resolution: {
          uri,
          version: 2,
          changes: [
            {
              range: {
                start: { line: 1, character: 1 },
                end: { line: 1, character: 5 }
              },
              text: 'resolved'
            }
          ],
          userId: 'user-1',
          timestamp: Date.now()
        }
      };

      await service.resolveConflict(resolution);

      expect(mockSocket.emit).toHaveBeenCalledWith('collaboration:resolve-conflict', expect.objectContaining({
        projectId: 'test-project',
        conflict: resolution
      }));
    });
  });
}); 