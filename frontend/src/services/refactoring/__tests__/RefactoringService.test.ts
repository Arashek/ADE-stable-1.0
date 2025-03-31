import { RefactoringService } from '../RefactoringService';
import { RefactoringOperation } from '../../../types/refactoring';

describe('RefactoringService', () => {
  let service: RefactoringService;

  beforeEach(() => {
    // Reset the singleton instance before each test
    (RefactoringService as any).instance = null;
    service = RefactoringService.getInstance();
  });

  describe('Singleton Pattern', () => {
    it('should return the same instance when getInstance is called multiple times', () => {
      const instance1 = RefactoringService.getInstance();
      const instance2 = RefactoringService.getInstance();
      expect(instance1).toBe(instance2);
    });
  });

  describe('applyRefactoring', () => {
    it('should add operation to history and update current index', async () => {
      const operation: RefactoringOperation = {
        id: '1',
        type: 'extract-method',
        description: 'Test operation',
        file: 'test.ts',
        line: 1,
        status: 'pending'
      };

      await service.applyRefactoring(operation);
      const history = service.getHistory();
      expect(history).toHaveLength(1);
      expect(history[0]).toBe(operation);
      expect(service.getCurrentIndex()).toBe(0);
    });

    it('should handle failed operations', async () => {
      const operation: RefactoringOperation = {
        id: '1',
        type: 'invalid-type' as any,
        description: 'Test operation',
        file: 'test.ts',
        line: 1,
        status: 'pending'
      };

      await expect(service.applyRefactoring(operation)).rejects.toThrow();
      const history = service.getHistory();
      expect(history[0].status).toBe('failed');
      expect(history[0].error).toBeDefined();
    });
  });

  describe('previewRefactoring', () => {
    it('should generate preview for extract method operation', async () => {
      const operation: RefactoringOperation = {
        id: '1',
        type: 'extract-method',
        description: 'Test operation',
        file: 'test.ts',
        line: 1,
        status: 'pending'
      };

      const preview = await service.previewRefactoring(operation);
      expect(preview).toContain('function newMethod()');
    });

    it('should handle failed preview generation', async () => {
      const operation: RefactoringOperation = {
        id: '1',
        type: 'invalid-type' as any,
        description: 'Test operation',
        file: 'test.ts',
        line: 1,
        status: 'pending'
      };

      await expect(service.previewRefactoring(operation)).rejects.toThrow();
    });
  });

  describe('undo/redo', () => {
    it('should handle undo and redo operations', async () => {
      const operation1: RefactoringOperation = {
        id: '1',
        type: 'extract-method',
        description: 'Operation 1',
        file: 'test.ts',
        line: 1,
        status: 'pending'
      };

      const operation2: RefactoringOperation = {
        id: '2',
        type: 'rename-symbol',
        description: 'Operation 2',
        file: 'test.ts',
        line: 2,
        status: 'pending'
      };

      await service.applyRefactoring(operation1);
      await service.applyRefactoring(operation2);

      service.undo();
      expect(service.getCurrentIndex()).toBe(0);

      service.redo();
      expect(service.getCurrentIndex()).toBe(1);
    });

    it('should not undo when at the beginning of history', () => {
      service.undo();
      expect(service.getCurrentIndex()).toBe(-1);
    });

    it('should not redo when at the end of history', () => {
      service.redo();
      expect(service.getCurrentIndex()).toBe(-1);
    });
  });

  describe('history management', () => {
    it('should clear future operations when applying new operation after undo', async () => {
      const operation1: RefactoringOperation = {
        id: '1',
        type: 'extract-method',
        description: 'Operation 1',
        file: 'test.ts',
        line: 1,
        status: 'pending'
      };

      const operation2: RefactoringOperation = {
        id: '2',
        type: 'rename-symbol',
        description: 'Operation 2',
        file: 'test.ts',
        line: 2,
        status: 'pending'
      };

      const operation3: RefactoringOperation = {
        id: '3',
        type: 'extract-variable',
        description: 'Operation 3',
        file: 'test.ts',
        line: 3,
        status: 'pending'
      };

      await service.applyRefactoring(operation1);
      await service.applyRefactoring(operation2);
      await service.applyRefactoring(operation3);

      service.undo();
      service.undo();

      const newOperation: RefactoringOperation = {
        id: '4',
        type: 'inline-variable',
        description: 'New Operation',
        file: 'test.ts',
        line: 4,
        status: 'pending'
      };

      await service.applyRefactoring(newOperation);

      const history = service.getHistory();
      expect(history).toHaveLength(2);
      expect(history[0]).toBe(operation1);
      expect(history[1]).toBe(newOperation);
    });
  });
}); 