import { codeCompletionService } from '../CodeCompletionService';
import { cache } from '../../../utils/cache';
import { performanceMonitor } from '../../../utils/performance';

// Mock dependencies
jest.mock('../../../utils/cache');
jest.mock('../../../utils/performance');
jest.mock('../../../utils/errorHandling', () => ({
  errorHandler: {
    handleError: jest.fn(),
  },
  ErrorSeverity: {
    LOW: 'low',
    MEDIUM: 'medium',
    HIGH: 'high',
  },
}));

describe('CodeCompletionService', () => {
  const mockContext = {
    code: 'function calculateTotal(items) {\n  return items.reduce((sum, item) => sum + item.price, 0);\n}',
    cursorPosition: 45,
    language: 'typescript',
    filePath: 'src/utils/calculations.ts',
    projectContext: {
      imports: ['import { Item } from "./types";'],
      dependencies: ['lodash'],
      relatedFiles: ['src/types.ts'],
    },
  };

  const mockSuggestions = [
    {
      text: 'reduce',
      kind: 'function',
      detail: 'Array.prototype.reduce',
      documentation: 'Reduces an array to a single value',
      relevance: 0.9,
    },
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (cache.get as jest.Mock).mockReturnValue(null);
    (performanceMonitor.measure as jest.Mock).mockImplementation((fn) => fn);
  });

  describe('getCompletions', () => {
    it('should return cached suggestions if available', async () => {
      (cache.get as jest.Mock).mockReturnValue(mockSuggestions);

      const result = await codeCompletionService.getCompletions(mockContext);

      expect(result).toEqual(mockSuggestions);
      expect(cache.get).toHaveBeenCalled();
      expect(fetch).not.toHaveBeenCalled();
    });

    it('should fetch suggestions from AI service when cache is empty', async () => {
      const mockResponse = { ok: true, json: () => Promise.resolve(mockSuggestions) };
      (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

      const result = await codeCompletionService.getCompletions(mockContext);

      expect(result).toEqual(mockSuggestions);
      expect(fetch).toHaveBeenCalledWith('/api/ai/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(mockContext),
      });
      expect(cache.set).toHaveBeenCalled();
    });

    it('should handle API errors gracefully', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({ ok: false, statusText: 'Not Found' });

      const result = await codeCompletionService.getCompletions(mockContext);

      expect(result).toEqual([]);
    });
  });

  describe('analyzeCode', () => {
    it('should analyze code and return results', async () => {
      const mockAnalysis = {
        complexity: 2,
        dependencies: ['lodash'],
        potentialIssues: [
          {
            type: 'complexity',
            message: 'Function is too complex',
            line: 1,
            severity: 'medium',
          },
        ],
      };

      const mockResponse = { ok: true, json: () => Promise.resolve(mockAnalysis) };
      (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

      const result = await codeCompletionService.analyzeCode('test code', 'typescript');

      expect(result).toEqual(mockAnalysis);
      expect(fetch).toHaveBeenCalledWith('/api/ai/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: 'test code', language: 'typescript' }),
      });
    });

    it('should handle API errors gracefully', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({ ok: false, statusText: 'Not Found' });

      const result = await codeCompletionService.analyzeCode('test code', 'typescript');

      expect(result).toEqual({
        complexity: 0,
        dependencies: [],
        potentialIssues: [],
      });
    });
  });

  describe('generateCodeVisualization', () => {
    it('should generate code visualization', async () => {
      const mockVisualization = {
        ast: { type: 'Program' },
        dependencies: { imports: [] },
        flow: { nodes: [] },
      };

      const mockResponse = { ok: true, json: () => Promise.resolve(mockVisualization) };
      (global.fetch as jest.Mock).mockResolvedValue(mockResponse);

      const result = await codeCompletionService.generateCodeVisualization('test code', 'typescript');

      expect(result).toEqual(mockVisualization);
      expect(fetch).toHaveBeenCalledWith('/api/ai/visualize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ code: 'test code', language: 'typescript' }),
      });
    });

    it('should handle API errors gracefully', async () => {
      (global.fetch as jest.Mock).mockResolvedValue({ ok: false, statusText: 'Not Found' });

      const result = await codeCompletionService.generateCodeVisualization('test code', 'typescript');

      expect(result).toEqual({
        ast: null,
        dependencies: null,
        flow: null,
      });
    });
  });
}); 