import { AICodeAnalysisService, CodeSnippet, AnalysisResult } from '../AICodeAnalysisService';

describe('AICodeAnalysisService', () => {
  let service: AICodeAnalysisService;

  beforeEach(() => {
    service = AICodeAnalysisService.getInstance();
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  const mockCodeSnippet: CodeSnippet = {
    content: 'function example() { return true; }',
    language: 'typescript',
    file: 'test.ts',
  };

  const mockAnalysisResult: AnalysisResult = {
    suggestions: [
      {
        type: 'improvement',
        message: 'Consider adding a return type annotation',
        line: 1,
        confidence: 0.9,
      },
      {
        type: 'warning',
        message: 'Function lacks documentation',
        line: 1,
        confidence: 0.8,
      },
    ],
    metrics: {
      complexity: 1,
      maintainability: 85,
      testability: 90,
    },
  };

  it('should be a singleton', () => {
    const instance1 = AICodeAnalysisService.getInstance();
    const instance2 = AICodeAnalysisService.getInstance();
    expect(instance1).toBe(instance2);
  });

  it('should analyze code and return suggestions', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockAnalysisResult),
    });

    const result = await service.analyzeCode(mockCodeSnippet);

    expect(global.fetch).toHaveBeenCalledWith('/api/ai/analyze', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(mockCodeSnippet),
    });

    expect(result).toEqual(mockAnalysisResult);
  });

  it('should handle analysis errors', async () => {
    const errorMessage = 'Analysis failed';
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error(errorMessage));

    await expect(service.analyzeCode(mockCodeSnippet)).rejects.toThrow(errorMessage);
  });

  it('should handle non-ok responses', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 500,
      statusText: 'Internal Server Error',
    });

    await expect(service.analyzeCode(mockCodeSnippet)).rejects.toThrow('Failed to analyze code');
  });

  it('should cache analysis results', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: () => Promise.resolve(mockAnalysisResult),
    });

    // First call should make an API request
    await service.analyzeCode(mockCodeSnippet);
    expect(global.fetch).toHaveBeenCalledTimes(1);

    // Second call with same code should use cache
    await service.analyzeCode(mockCodeSnippet);
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });

  it('should clear cache when requested', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockAnalysisResult),
    });

    // First call
    await service.analyzeCode(mockCodeSnippet);
    expect(global.fetch).toHaveBeenCalledTimes(1);

    // Clear cache
    service.clearCache();

    // Second call should make a new request
    await service.analyzeCode(mockCodeSnippet);
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  it('should handle different code snippets separately in cache', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockAnalysisResult),
    });

    const mockCodeSnippet2: CodeSnippet = {
      ...mockCodeSnippet,
      content: 'function example2() { return false; }',
    };

    // First snippet
    await service.analyzeCode(mockCodeSnippet);
    expect(global.fetch).toHaveBeenCalledTimes(1);

    // Different snippet should make new request
    await service.analyzeCode(mockCodeSnippet2);
    expect(global.fetch).toHaveBeenCalledTimes(2);

    // Original snippet should use cache
    await service.analyzeCode(mockCodeSnippet);
    expect(global.fetch).toHaveBeenCalledTimes(2);
  });

  it('should generate cache key correctly', () => {
    const key1 = service.generateCacheKey(mockCodeSnippet);
    const key2 = service.generateCacheKey({
      ...mockCodeSnippet,
      content: 'different content',
    });

    expect(key1).not.toBe(key2);
  });

  it('should handle concurrent requests for same code', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve(mockAnalysisResult),
    });

    // Make multiple concurrent requests
    const promises = Array(3).fill(null).map(() => service.analyzeCode(mockCodeSnippet));

    // Wait for all requests to complete
    await Promise.all(promises);

    // Should only make one API call
    expect(global.fetch).toHaveBeenCalledTimes(1);
  });
}); 