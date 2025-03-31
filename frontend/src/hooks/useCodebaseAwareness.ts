import { useCallback } from 'react';
import { Socket } from 'socket.io-client';

interface FileContext {
  path: string;
  content: string;
  dependencies: string[];
  symbols: Symbol[];
}

interface Symbol {
  name: string;
  type: string;
  location: {
    start: { line: number; column: number };
    end: { line: number; column: number };
  };
}

interface FileChange {
  path: string;
  type: 'modified' | 'created' | 'deleted';
  content?: string;
}

export const useCodebaseAwareness = (socket: Socket | null) => {
  const analyzeFile = useCallback(async (path: string, content: string): Promise<FileContext> => {
    if (!socket) throw new Error('Socket not connected');
    return new Promise((resolve) => {
      socket.emit('codebase:analyze', { path, content }, (context: FileContext) => {
        resolve(context);
      });
    });
  }, [socket]);

  const getDependencies = useCallback(async (path: string): Promise<string[]> => {
    if (!socket) throw new Error('Socket not connected');
    return new Promise((resolve) => {
      socket.emit('codebase:dependencies', { path }, (dependencies: string[]) => {
        resolve(dependencies);
      });
    });
  }, [socket]);

  const getSymbols = useCallback(async (path: string): Promise<Symbol[]> => {
    if (!socket) throw new Error('Socket not connected');
    return new Promise((resolve) => {
      socket.emit('codebase:symbols', { path }, (symbols: Symbol[]) => {
        resolve(symbols);
      });
    });
  }, [socket]);

  const resolveSymbol = useCallback(async (symbol: Symbol): Promise<FileContext> => {
    if (!socket) throw new Error('Socket not connected');
    return new Promise((resolve) => {
      socket.emit('codebase:resolve-symbol', { symbol }, (context: FileContext) => {
        resolve(context);
      });
    });
  }, [socket]);

  const subscribeToFileChanges = useCallback((callback: (changes: FileChange[]) => void) => {
    if (!socket) return () => {};

    socket.on('codebase:changes', callback);

    return () => {
      socket.off('codebase:changes', callback);
    };
  }, [socket]);

  const getProjectStructure = useCallback(async (): Promise<any> => {
    if (!socket) throw new Error('Socket not connected');
    return new Promise((resolve) => {
      socket.emit('codebase:structure', (structure: any) => {
        resolve(structure);
      });
    });
  }, [socket]);

  const findReferences = useCallback(async (symbol: Symbol): Promise<Symbol[]> => {
    if (!socket) throw new Error('Socket not connected');
    return new Promise((resolve) => {
      socket.emit('codebase:find-references', { symbol }, (references: Symbol[]) => {
        resolve(references);
      });
    });
  }, [socket]);

  return {
    analyzeFile,
    getDependencies,
    getSymbols,
    resolveSymbol,
    subscribeToFileChanges,
    getProjectStructure,
    findReferences
  };
}; 