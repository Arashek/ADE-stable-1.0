import { useState, useCallback } from 'react';
import { RefactoringService } from '../services/refactoring/RefactoringService';
import { RefactoringOperation } from '../types/refactoring';

export const useRefactoring = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const refactoringService = RefactoringService.getInstance();

  const applyRefactoring = useCallback(async (operation: RefactoringOperation) => {
    setIsLoading(true);
    setError(null);
    try {
      await refactoringService.applyRefactoring(operation);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to apply refactoring');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const previewRefactoring = useCallback(async (operation: RefactoringOperation) => {
    setIsLoading(true);
    setError(null);
    try {
      return await refactoringService.previewRefactoring(operation);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to preview refactoring');
      throw err;
    } finally {
      setIsLoading(false);
    }
  }, []);

  const undo = useCallback(() => {
    refactoringService.undo();
  }, []);

  const redo = useCallback(() => {
    refactoringService.redo();
  }, []);

  const getHistory = useCallback(() => {
    return refactoringService.getHistory();
  }, []);

  const getCurrentIndex = useCallback(() => {
    return refactoringService.getCurrentIndex();
  }, []);

  return {
    isLoading,
    error,
    applyRefactoring,
    previewRefactoring,
    undo,
    redo,
    getHistory,
    getCurrentIndex
  };
}; 