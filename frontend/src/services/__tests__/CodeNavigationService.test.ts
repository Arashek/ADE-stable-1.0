import { Socket } from 'socket.io-client';
import { DefaultEventsMap } from 'socket.io/dist/typed-events';
import { CodeNavigationService } from '../CodeNavigationService';
import * as monaco from 'monaco-editor';

describe('CodeNavigationService', () => {
  let mockSocket: jest.Mocked<Socket<DefaultEventsMap, DefaultEventsMap>>;
  let mockEditor: jest.Mocked<monaco.editor.IStandaloneCodeEditor>;
  let service: CodeNavigationService;

  beforeEach(() => {
    mockSocket = {
      emit: jest.fn(),
      on: jest.fn(),
      off: jest.fn(),
    } as unknown as jest.Mocked<Socket<DefaultEventsMap, DefaultEventsMap>>;

    mockEditor = {
      deltaDecorations: jest.fn(),
      getModel: jest.fn(),
    } as unknown as jest.Mocked<monaco.editor.IStandaloneCodeEditor>;

    service = new CodeNavigationService({
      ws: mockSocket,
      projectId: 'test-project',
      editor: mockEditor
    });
  });

  afterEach(() => {
    service.dispose();
  });

  describe('code navigation', () => {
    it('should find definition', async () => {
      const uri = 'file:///test.ts';
      const position = { line: 1, character: 5 };
      const location = {
        uri: 'file:///definition.ts',
        range: {
          start: { line: 10, character: 1 },
          end: { line: 10, character: 10 }
        }
      };

      const definitionPromise = service.findDefinition(uri, position);

      // Simulate definition response
      const definitionHandler = mockSocket.on.mock.calls.find(call => call[0] === 'navigation:definition')?.[1];
      if (definitionHandler) {
        definitionHandler({ uri, location });
      }

      const result = await definitionPromise;

      expect(mockSocket.emit).toHaveBeenCalledWith('navigation:find-definition', expect.objectContaining({
        projectId: 'test-project',
        uri,
        position
      }));
      expect(result).toEqual(location);
    });

    it('should find references', async () => {
      const uri = 'file:///test.ts';
      const position = { line: 1, character: 5 };
      const references = [
        {
          uri: 'file:///reference1.ts',
          range: {
            start: { line: 1, character: 1 },
            end: { line: 1, character: 10 }
          }
        },
        {
          uri: 'file:///reference2.ts',
          range: {
            start: { line: 2, character: 1 },
            end: { line: 2, character: 10 }
          }
        }
      ];

      const referencesPromise = service.findReferences(uri, position);

      // Simulate references response
      const referencesHandler = mockSocket.on.mock.calls.find(call => call[0] === 'navigation:references')?.[1];
      if (referencesHandler) {
        referencesHandler({ uri, references });
      }

      const result = await referencesPromise;

      expect(mockSocket.emit).toHaveBeenCalledWith('navigation:find-references', expect.objectContaining({
        projectId: 'test-project',
        uri,
        position
      }));
      expect(result).toEqual(references);
    });

    it('should get document symbols', async () => {
      const uri = 'file:///test.ts';
      const symbols = [
        {
          name: 'testFunction',
          kind: 12, // Function
          location: {
            uri: 'file:///test.ts',
            range: {
              start: { line: 1, character: 1 },
              end: { line: 1, character: 20 }
            }
          }
        }
      ];

      const symbolsPromise = service.getDocumentSymbols(uri);

      // Simulate symbols response
      const symbolsHandler = mockSocket.on.mock.calls.find(call => call[0] === 'navigation:document-symbols')?.[1];
      if (symbolsHandler) {
        symbolsHandler({ uri, symbols });
      }

      const result = await symbolsPromise;

      expect(mockSocket.emit).toHaveBeenCalledWith('navigation:document-symbols', expect.objectContaining({
        projectId: 'test-project',
        uri
      }));
      expect(result).toEqual(symbols);
    });

    it('should get outline', async () => {
      const uri = 'file:///test.ts';
      const outline = [
        {
          name: 'testClass',
          kind: 5, // Class
          range: {
            start: { line: 1, character: 1 },
            end: { line: 10, character: 1 }
          },
          children: [
            {
              name: 'testMethod',
              kind: 6, // Method
              range: {
                start: { line: 2, character: 1 },
                end: { line: 5, character: 1 }
              }
            }
          ]
        }
      ];

      const outlinePromise = service.getOutline(uri);

      // Simulate outline response
      const outlineHandler = mockSocket.on.mock.calls.find(call => call[0] === 'navigation:outline')?.[1];
      if (outlineHandler) {
        outlineHandler({ uri, outline });
      }

      const result = await outlinePromise;

      expect(mockSocket.emit).toHaveBeenCalledWith('navigation:outline', expect.objectContaining({
        projectId: 'test-project',
        uri
      }));
      expect(result).toEqual(outline);
    });
  });
}); 