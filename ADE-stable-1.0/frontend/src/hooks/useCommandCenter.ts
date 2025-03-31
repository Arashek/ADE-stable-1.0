import { useCallback } from 'react';
import { Socket } from 'socket.io-client';

export interface Task {
  id: string;
  title: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  priority: 'low' | 'medium' | 'high';
  assignedAgent?: string;
  progress: number;
  timestamp: string;
}

export interface TaskUpdate {
  status?: Task['status'];
  progress?: number;
  assignedAgent?: string;
}

export const useCommandCenter = (socket: Socket | null) => {
  const getTasks = useCallback(async (): Promise<Task[]> => {
    if (!socket) throw new Error('Socket not connected');
    return new Promise((resolve) => {
      socket.emit('command-center:get-tasks', (tasks: Task[]) => {
        resolve(tasks);
      });
    });
  }, [socket]);

  const updateTask = useCallback(async (taskId: string, update: TaskUpdate): Promise<Task> => {
    if (!socket) throw new Error('Socket not connected');
    return new Promise((resolve) => {
      socket.emit('command-center:update-task', { taskId, update }, (task: Task) => {
        resolve(task);
      });
    });
  }, [socket]);

  const createTask = useCallback(async (task: Omit<Task, 'id' | 'timestamp'>): Promise<Task> => {
    if (!socket) throw new Error('Socket not connected');
    return new Promise((resolve) => {
      socket.emit('command-center:create-task', task, (newTask: Task) => {
        resolve(newTask);
      });
    });
  }, [socket]);

  const deleteTask = useCallback(async (taskId: string): Promise<void> => {
    if (!socket) throw new Error('Socket not connected');
    return new Promise((resolve) => {
      socket.emit('command-center:delete-task', { taskId }, () => {
        resolve();
      });
    });
  }, [socket]);

  return {
    getTasks,
    updateTask,
    createTask,
    deleteTask
  };
}; 