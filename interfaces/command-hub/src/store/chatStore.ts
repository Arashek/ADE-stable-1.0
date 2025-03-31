import { create } from 'zustand';

interface Message {
  id: string;
  content: string;
  sender: {
    id: string;
    name: string;
    type: 'agent' | 'user';
    avatar?: string;
  };
  timestamp: Date;
  type: 'text' | 'code' | 'file';
  metadata?: {
    language?: string;
    fileName?: string;
    fileSize?: number;
  };
}

interface ChatStore {
  messages: Message[];
  addMessage: (message: Message) => void;
  clearMessages: () => void;
  setMessages: (messages: Message[]) => void;
}

export const useChatStore = create<ChatStore>((set) => ({
  messages: [],
  addMessage: (message) =>
    set((state) => ({
      messages: [...state.messages, message],
    })),
  clearMessages: () => set({ messages: [] }),
  setMessages: (messages) => set({ messages }),
})); 