import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const initialState = {
  activeProject: null,
  team: [],
  conversations: [],
  tasks: [],
  preferences: {
    theme: 'light',
    notifications: true,
    panelLayout: {
      top: 0.6,
      bottom: 0.4
    }
  }
};

const useCommandCenterStore = create(
  persist(
    (set, get) => ({
      ...initialState,

      // Project Management
      setActiveProject: (project) => set({ activeProject: project }),
      updateProjectData: (data) => set((state) => ({
        activeProject: state.activeProject ? { ...state.activeProject, ...data } : null
      })),

      // Team Management
      setTeam: (team) => set({ team }),
      addTeamMember: (member) => set((state) => ({
        team: [...state.team, member]
      })),
      removeTeamMember: (memberId) => set((state) => ({
        team: state.team.filter(member => member.id !== memberId)
      })),

      // Conversation Management
      addConversation: (conversation) => set((state) => ({
        conversations: [...state.conversations, conversation]
      })),
      updateConversation: (conversationId, updates) => set((state) => ({
        conversations: state.conversations.map(conv =>
          conv.id === conversationId ? { ...conv, ...updates } : conv
        )
      })),
      clearConversations: () => set({ conversations: [] }),

      // Task Management
      setTasks: (tasks) => set({ tasks }),
      addTask: (task) => set((state) => ({
        tasks: [...state.tasks, task]
      })),
      updateTask: (taskId, updates) => set((state) => ({
        tasks: state.tasks.map(task =>
          task.id === taskId ? { ...task, ...updates } : task
        )
      })),
      removeTask: (taskId) => set((state) => ({
        tasks: state.tasks.filter(task => task.id !== taskId)
      })),

      // Preferences Management
      updatePreferences: (preferences) => set((state) => ({
        preferences: { ...state.preferences, ...preferences }
      })),
      resetPreferences: () => set((state) => ({
        preferences: initialState.preferences
      })),

      // Utility Functions
      getTaskById: (taskId) => {
        const state = get();
        return state.tasks.find(task => task.id === taskId);
      },
      getConversationById: (conversationId) => {
        const state = get();
        return state.conversations.find(conv => conv.id === conversationId);
      },
      getTeamMemberById: (memberId) => {
        const state = get();
        return state.team.find(member => member.id === memberId);
      },

      // Reset Store
      resetStore: () => set(initialState)
    }),
    {
      name: 'command-center-storage',
      partialize: (state) => ({
        preferences: state.preferences,
        activeProject: state.activeProject
      })
    }
  )
);

export default useCommandCenterStore; 