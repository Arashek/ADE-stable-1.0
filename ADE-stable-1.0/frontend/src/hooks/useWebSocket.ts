import { useState, useEffect } from 'react';
import { Socket, io } from 'socket.io-client';

export const useWebSocket = (projectId: string): Socket | null => {
  const [socket, setSocket] = useState<Socket | null>(null);

  useEffect(() => {
    const newSocket = io(`ws://localhost:3000/project/${projectId}`);
    setSocket(newSocket);

    newSocket.on('connect', () => {
      console.log('Connected to WebSocket server');
    });

    newSocket.on('disconnect', () => {
      console.log('Disconnected from WebSocket server');
    });

    return () => {
      newSocket.close();
    };
  }, [projectId]);

  return socket;
}; 