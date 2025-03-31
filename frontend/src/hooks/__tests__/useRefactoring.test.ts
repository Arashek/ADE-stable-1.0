import { renderHook, act } from '@testing-library/react';
import { useRefactoring } from '../useRefactoring';
import { RefactoringService } from '../../services/refactoring/RefactoringService';
import { RefactoringOperation, RefactoringType } from '../../types/refactoring';

// Mock the RefactoringService
jest.mock('../../services/refactoring/RefactoringService');

describe('useRefactoring', () => {
  let mockRefactoringService: jest.Mocked<RefactoringService>;

  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();

    // Create a mock instance of RefactoringService
    mockRefactoringService = {
      getInstance: jest.fn(),
      applyRefactoring: jest.fn(),
      previewRefactoring: jest.fn(),
      undo: jest.fn(),
      redo: jest.fn(),
      getHistory: jest.fn(),
      getCurrentIndex: jest.fn()
    } as any;

    // Set up the mock instance
    (RefactoringService.getInstance as jest.Mock).mockReturnValue(mockRefactoringService);
  });

  it('should initialize with default values', () => {
    const { result } = renderHook(() => useRefactoring());

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should apply refactoring successfully', async () => {
    const operation: RefactoringOperation = {
      id: '1',
      type: 'extract-method' as RefactoringType,
      description: 'Test operation',
      file: 'test.ts',
      line: 1,
      status: 'pending'
    };

    mockRefactoringService.applyRefactoring.mockResolvedValue(undefined);

    const { result } = renderHook(() => useRefactoring());

    await act(async () => {
      await result.current.applyRefactoring(operation);
    });

    expect(mockRefactoringService.applyRefactoring).toHaveBeenCalledWith(operation);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should handle refactoring errors', async () => {
    const operation: RefactoringOperation = {
      id: '1',
      type: 'extract-method' as RefactoringType,
      description: 'Test operation',
      file: 'test.ts',
      line: 1,
      status: 'pending'
    };

    const error = new Error('Refactoring failed');
    mockRefactoringService.applyRefactoring.mockRejectedValue(error);

    const { result } = renderHook(() => useRefactoring());

    await act(async () => {
      await expect(result.current.applyRefactoring(operation)).rejects.toThrow(error);
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe('Refactoring failed');
  });

  it('should preview refactoring successfully', async () => {
    const operation: RefactoringOperation = {
      id: '1',
      type: 'extract-method' as RefactoringType,
      description: 'Test operation',
      file: 'test.ts',
      line: 1,
      status: 'pending'
    };

    const preview = '// Preview of refactored code';
    mockRefactoringService.previewRefactoring.mockResolvedValue(preview);

    const { result } = renderHook(() => useRefactoring());

    let previewResult;
    await act(async () => {
      previewResult = await result.current.previewRefactoring(operation);
    });

    expect(mockRefactoringService.previewRefactoring).toHaveBeenCalledWith(operation);
    expect(previewResult).toBe(preview);
    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('should handle preview errors', async () => {
    const operation: RefactoringOperation = {
      id: '1',
      type: 'extract-method' as RefactoringType,
      description: 'Test operation',
      file: 'test.ts',
      line: 1,
      status: 'pending'
    };

    const error = new Error('Preview failed');
    mockRefactoringService.previewRefactoring.mockRejectedValue(error);

    const { result } = renderHook(() => useRefactoring());

    await act(async () => {
      await expect(result.current.previewRefactoring(operation)).rejects.toThrow(error);
    });

    expect(result.current.isLoading).toBe(false);
    expect(result.current.error).toBe('Preview failed');
  });

  it('should handle undo and redo operations', () => {
    const { result } = renderHook(() => useRefactoring());

    act(() => {
      result.current.undo();
    });
    expect(mockRefactoringService.undo).toHaveBeenCalled();

    act(() => {
      result.current.redo();
    });
    expect(mockRefactoringService.redo).toHaveBeenCalled();
  });

  it('should get history and current index', () => {
    const history: RefactoringOperation[] = [
      {
        id: '1',
        type: 'extract-method' as RefactoringType,
        description: 'Operation 1',
        file: 'test.ts',
        line: 1,
        status: 'applied'
      }
    ];
    const currentIndex = 0;

    mockRefactoringService.getHistory.mockReturnValue(history);
    mockRefactoringService.getCurrentIndex.mockReturnValue(currentIndex);

    const { result } = renderHook(() => useRefactoring());

    expect(result.current.getHistory()).toBe(history);
    expect(result.current.getCurrentIndex()).toBe(currentIndex);
  });
}); 