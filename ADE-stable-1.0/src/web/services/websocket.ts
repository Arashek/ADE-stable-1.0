import { create } from 'zustand';

interface WebSocketState {
  socket: WebSocket | null;
  isConnected: boolean;
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: any) => void;
}

interface RealTimeEvent {
  type: 'agent_update' | 'code_change' | 'task_update' | 'resource_update' | 'chat_message';
  data: any;
  timestamp: number;
}

const useWebSocketStore = create<WebSocketState>((set, get) => ({
  socket: null,
  isConnected: false,
  connect: () => {
    const socket = new WebSocket(process.env.REACT_APP_WS_URL || 'ws://localhost:8080/ws');
    
    socket.onopen = () => {
      set({ isConnected: true });
      console.log('WebSocket connected');
    };

    socket.onclose = () => {
      set({ isConnected: false });
      console.log('WebSocket disconnected');
    };

    socket.onerror = (error) => {
      console.error('WebSocket error:', error);
      set({ isConnected: false });
    };

    set({ socket });
  },
  disconnect: () => {
    const { socket } = get();
    if (socket) {
      socket.close();
      set({ socket: null, isConnected: false });
    }
  },
  sendMessage: (message: any) => {
    const { socket, isConnected } = get();
    if (isConnected && socket) {
      socket.send(JSON.stringify(message));
    }
  },
}));

export const useWebSocket = useWebSocketStore;

export const subscribeToEvents = (callback: (event: RealTimeEvent) => void) => {
  const { socket } = useWebSocketStore.getState();
  
  if (socket) {
    socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      callback(data);
    };
  }
};

export const emitEvent = (type: RealTimeEvent['type'], data: any) => {
  const { sendMessage } = useWebSocketStore.getState();
  
  sendMessage({
    type,
    data,
    timestamp: Date.now(),
  });
}; 