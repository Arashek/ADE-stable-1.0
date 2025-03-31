import { create } from 'zustand';

const useClipboardManagerStore = create((set, get) => ({
  history: [],
  maxHistorySize: 50,
  activeContexts: new Set(),
  contextReferences: new Map(),
  selectedContent: null,
  isProcessing: false,
  error: null,

  addToHistory: (content) => {
    const { history, maxHistorySize } = get();
    const newItem = {
      id: Date.now(),
      content,
      type: get().detectContentType(content),
      timestamp: Date.now(),
      source: 'clipboard'
    };

    const updatedHistory = [newItem, ...history].slice(0, maxHistorySize);
    set({ history: updatedHistory });
  },

  detectContentType: (content) => {
    if (typeof content === 'string') {
      // Check for URLs
      if (/^https?:\/\/\S+$/.test(content)) {
        return 'url';
      }
      // Check for code snippets
      if (content.includes('function') || content.includes('class') || content.includes('const')) {
        return 'code';
      }
      // Check for file paths
      if (/^[a-zA-Z]:\\|\//.test(content)) {
        return 'filepath';
      }
      return 'text';
    }
    return typeof content;
  },

  createContextReference: (content, metadata = {}) => {
    const { contextReferences } = get();
    const reference = {
      id: Date.now(),
      content,
      type: get().detectContentType(content),
      metadata,
      timestamp: Date.now(),
      priority: metadata.priority || 0
    };

    contextReferences.set(reference.id, reference);
    set({ contextReferences });
    return reference.id;
  },

  activateContext: (contextId) => {
    const { activeContexts } = get();
    activeContexts.add(contextId);
    set({ activeContexts });
  },

  deactivateContext: (contextId) => {
    const { activeContexts } = get();
    activeContexts.delete(contextId);
    set({ activeContexts });
  },

  updateContextPriority: (contextId, priority) => {
    const { contextReferences } = get();
    const reference = contextReferences.get(contextId);
    if (reference) {
      reference.priority = priority;
      contextReferences.set(contextId, reference);
      set({ contextReferences });
    }
  },

  getActiveContexts: () => {
    const { activeContexts, contextReferences } = get();
    return Array.from(activeContexts)
      .map(id => contextReferences.get(id))
      .filter(Boolean)
      .sort((a, b) => b.priority - a.priority);
  },

  getContextById: (contextId) => {
    return get().contextReferences.get(contextId);
  },

  removeContext: (contextId) => {
    const { contextReferences, activeContexts } = get();
    contextReferences.delete(contextId);
    activeContexts.delete(contextId);
    set({ contextReferences, activeContexts });
  },

  setSelectedContent: (content) => {
    set({ selectedContent: content });
  },

  clearHistory: () => {
    set({ history: [] });
  },

  clearContexts: () => {
    set({ contextReferences: new Map(), activeContexts: new Set() });
  },

  getHistoryByType: (type) => {
    const { history } = get();
    return history.filter(item => item.type === type);
  },

  getRecentHistory: (limit = 10) => {
    const { history } = get();
    return history.slice(0, limit);
  },

  searchHistory: (query) => {
    const { history } = get();
    const searchQuery = query.toLowerCase();
    return history.filter(item => 
      item.content.toLowerCase().includes(searchQuery) ||
      item.type.toLowerCase().includes(searchQuery)
    );
  },

  exportHistory: () => {
    const { history } = get();
    return JSON.stringify(history, null, 2);
  },

  importHistory: (jsonString) => {
    try {
      const history = JSON.parse(jsonString);
      set({ history });
      return true;
    } catch (error) {
      set({ error: 'Failed to import history' });
      return false;
    }
  },

  clearError: () => {
    set({ error: null });
  }
}));

export default useClipboardManagerStore; 