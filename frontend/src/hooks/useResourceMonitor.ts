import { useCallback } from 'react';
import { Socket } from 'socket.io-client';
import { ResourceMetrics } from '../components/ResourceMonitor';

export const useResourceMonitor = (socket: Socket | null) => {
  const getResources = useCallback(async (): Promise<ResourceMetrics> => {
    if (!socket) throw new Error('Socket not connected');
    return new Promise((resolve) => {
      socket.emit('resource:get', (metrics: ResourceMetrics) => {
        resolve(metrics);
      });
    });
  }, [socket]);

  const startMonitoring = useCallback(() => {
    if (!socket) return;
    socket.emit('resource:start-monitoring');
  }, [socket]);

  const stopMonitoring = useCallback(() => {
    if (!socket) return;
    socket.emit('resource:stop-monitoring');
  }, [socket]);

  return {
    getResources,
    startMonitoring,
    stopMonitoring
  };
}; 