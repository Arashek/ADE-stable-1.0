import { create } from 'zustand';

interface CommandHistoryItem {
  command: string;
  timestamp: Date;
  status: 'success' | 'error' | 'pending';
  output?: string;
}

interface CommandStore {
  history: CommandHistoryItem[];
  addToHistory: (item: CommandHistoryItem) => void;
  clearHistory: () => void;
}

export const useCommandStore = create<CommandStore>((set) => ({
  history: [],
  addToHistory: (item) =>
    set((state) => ({
      history: [...state.history, item],
    })),
  clearHistory: () => set({ history: [] }),
})); 