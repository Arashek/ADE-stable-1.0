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
    if (!socket) {
      console.warn('Socket not connected - returning empty task list');
      return [];
    }
    
    return new Promise((resolve, reject) => {
      try {
        socket.timeout(5000).emit('command-center:get-tasks', (err: Error | null, tasks: Task[]) => {
          if (err) {
            console.error('Error fetching tasks:', err);
            reject(err);
            return;
          }
          resolve(tasks || []);
        });
      } catch (error) {
        console.error('Exception while fetching tasks:', error);
        resolve([]);
      }
    });
  }, [socket]);

  const updateTask = useCallback(async (taskId: string, update: TaskUpdate): Promise<Task> => {
    if (!socket) {
      const errorMsg = 'Socket not connected - cannot update task';
      console.warn(errorMsg);
      return Promise.reject(new Error(errorMsg));
    }
    
    return new Promise((resolve, reject) => {
      try {
        socket.timeout(5000).emit('command-center:update-task', { taskId, update }, (err: Error | null, task: Task) => {
          if (err) {
            console.error('Error updating task:', err);
            reject(err);
            return;
          }
          resolve(task);
        });
      } catch (error) {
        console.error('Exception while updating task:', error);
        reject(error);
      }
    });
  }, [socket]);

  const createTask = useCallback(async (task: Omit<Task, 'id' | 'timestamp'>): Promise<Task> => {
    if (!socket) {
      const errorMsg = 'Socket not connected - cannot create task';
      console.warn(errorMsg);
      return Promise.reject(new Error(errorMsg));
    }
    
    return new Promise((resolve, reject) => {
      try {
        socket.timeout(5000).emit('command-center:create-task', task, (err: Error | null, newTask: Task) => {
          if (err) {
            console.error('Error creating task:', err);
            reject(err);
            return;
          }
          resolve(newTask);
        });
      } catch (error) {
        console.error('Exception while creating task:', error);
        reject(error);
      }
    });
  }, [socket]);

  const deleteTask = useCallback(async (taskId: string): Promise<void> => {
    if (!socket) {
      const errorMsg = 'Socket not connected - cannot delete task';
      console.warn(errorMsg);
      return Promise.reject(new Error(errorMsg));
    }
    
    return new Promise((resolve, reject) => {
      try {
        socket.timeout(5000).emit('command-center:delete-task', { taskId }, (err: Error | null) => {
          if (err) {
            console.error('Error deleting task:', err);
            reject(err);
            return;
          }
          resolve();
        });
      } catch (error) {
        console.error('Exception while deleting task:', error);
        reject(error);
      }
    });
  }, [socket]);

  return {
    getTasks,
    updateTask,
    createTask,
    deleteTask,
    isConnected: !!socket && socket.connected
  };
};