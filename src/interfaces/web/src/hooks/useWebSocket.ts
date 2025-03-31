import { useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { websocketService } from '../services/websocketService';

export function useWebSocket(type: 'activity' | 'project' | 'agent' | 'task') {
  const queryClient = useQueryClient();

  useEffect(() => {
    // Subscribe to WebSocket messages
    const unsubscribe = websocketService.subscribe((message) => {
      if (message.type !== type) return;

      // Update React Query cache based on the action
      switch (message.action) {
        case 'create':
          queryClient.setQueryData([`${type}s`], (oldData: any[] = []) => {
            return [...oldData, message.data];
          });
          break;

        case 'update':
          queryClient.setQueryData([`${type}s`], (oldData: any[] = []) => {
            return oldData.map((item) =>
              item.id === (message.data as any).id ? message.data : item
            );
          });
          break;

        case 'delete':
          queryClient.setQueryData([`${type}s`], (oldData: any[] = []) => {
            return oldData.filter((item) => item.id !== (message.data as any).id);
          });
          break;
      }
    });

    // Cleanup subscription on unmount
    return () => {
      unsubscribe();
    };
  }, [type, queryClient]);
} 