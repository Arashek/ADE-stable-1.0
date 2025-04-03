import React, { useCallback, useEffect, useState } from 'react';
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
    if (!socket) {
      console.warn('Socket not connected - cannot analyze file');
      return { path, content, dependencies: [], symbols: [] };
    }
    
    return new Promise((resolve, reject) => {
      try {
        socket.timeout(8000).emit('codebase:analyze', { path, content }, (err: Error | null, context: FileContext) => {
          if (err) {
            console.error('Error analyzing file:', err);
            reject(err);
            return;
          }
          resolve(context || { path, content, dependencies: [], symbols: [] });
        });
      } catch (error) {
        console.error('Exception while analyzing file:', error);
        resolve({ path, content, dependencies: [], symbols: [] });
      }
    });
  }, [socket]);

  const getDependencies = useCallback(async (path: string): Promise<string[]> => {
    if (!socket) {
      console.warn('Socket not connected - cannot get dependencies');
      return [];
    }
    
    return new Promise((resolve, reject) => {
      try {
        socket.timeout(5000).emit('codebase:dependencies', { path }, (err: Error | null, dependencies: string[]) => {
          if (err) {
            console.error('Error getting dependencies:', err);
            reject(err);
            return;
          }
          resolve(dependencies || []);
        });
      } catch (error) {
        console.error('Exception while getting dependencies:', error);
        resolve([]);
      }
    });
  }, [socket]);

  const getSymbols = useCallback(async (path: string): Promise<Symbol[]> => {
    if (!socket) {
      console.warn('Socket not connected - cannot get symbols');
      return [];
    }
    
    return new Promise((resolve, reject) => {
      try {
        socket.timeout(5000).emit('codebase:symbols', { path }, (err: Error | null, symbols: Symbol[]) => {
          if (err) {
            console.error('Error getting symbols:', err);
            reject(err);
            return;
          }
          resolve(symbols || []);
        });
      } catch (error) {
        console.error('Exception while getting symbols:', error);
        resolve([]);
      }
    });
  }, [socket]);

  const resolveSymbol = useCallback(async (symbol: Symbol): Promise<FileContext> => {
    if (!socket) {
      console.warn('Socket not connected - cannot resolve symbol');
      return { path: '', content: '', dependencies: [], symbols: [] };
    }
    
    return new Promise((resolve, reject) => {
      try {
        socket.timeout(5000).emit('codebase:resolve-symbol', { symbol }, (err: Error | null, context: FileContext) => {
          if (err) {
            console.error('Error resolving symbol:', err);
            reject(err);
            return;
          }
          resolve(context || { path: '', content: '', dependencies: [], symbols: [] });
        });
      } catch (error) {
        console.error('Exception while resolving symbol:', error);
        resolve({ path: '', content: '', dependencies: [], symbols: [] });
      }
    });
  }, [socket]);

  const subscribeToFileChanges = useCallback((callback: (changes: FileChange[]) => void) => {
    if (!socket) {
      console.warn('Socket not connected - cannot subscribe to file changes');
      return () => {};
    }

    const safeCallback = (changes: FileChange[]) => {
      try {
        callback(changes || []);
      } catch (error) {
        console.error('Error in file changes callback:', error);
      }
    };

    socket.on('codebase:changes', safeCallback);

    return () => {
      socket.off('codebase:changes', safeCallback);
    };
  }, [socket]);

  const getProjectStructure = useCallback(async (): Promise<any> => {
    if (!socket) {
      console.warn('Socket not connected - cannot get project structure');
      return { directories: [], files: [] };
    }
    
    return new Promise((resolve, reject) => {
      try {
        socket.timeout(10000).emit('codebase:structure', (err: Error | null, structure: any) => {
          if (err) {
            console.error('Error getting project structure:', err);
            reject(err);
            return;
          }
          resolve(structure || { directories: [], files: [] });
        });
      } catch (error) {
        console.error('Exception while getting project structure:', error);
        resolve({ directories: [], files: [] });
      }
    });
  }, [socket]);

  const findReferences = useCallback(async (symbol: Symbol): Promise<Symbol[]> => {
    if (!socket) {
      console.warn('Socket not connected - cannot find references');
      return [];
    }
    
    return new Promise((resolve, reject) => {
      try {
        socket.timeout(8000).emit('codebase:find-references', { symbol }, (err: Error | null, references: Symbol[]) => {
          if (err) {
            console.error('Error finding references:', err);
            reject(err);
            return;
          }
          resolve(references || []);
        });
      } catch (error) {
        console.error('Exception while finding references:', error);
        resolve([]);
      }
    });
  }, [socket]);

  return {
    analyzeFile,
    getDependencies,
    getSymbols,
    resolveSymbol,
    subscribeToFileChanges,
    getProjectStructure,
    findReferences,
    isConnected: !!socket && socket.connected
  };
};