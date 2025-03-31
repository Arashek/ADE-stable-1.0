import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  activeProject: null,
  teamComposition: [],
  conversations: [],
  tasks: [],
  userPreferences: {
    theme: 'light',
    layout: 'split',
    notifications: true,
    autoCollapse: false,
  },
  notifications: [],
  agentStatus: {
    codeAnalysis: 'idle',
    resourceManagement: 'idle',
    errorHandling: 'idle',
    taskPlanning: 'idle',
  },
};

const commandCenterSlice = createSlice({
  name: 'commandCenter',
  initialState,
  reducers: {
    setActiveProject: (state, action) => {
      state.activeProject = action.payload;
    },
    updateTeamComposition: (state, action) => {
      state.teamComposition = action.payload;
    },
    addConversation: (state, action) => {
      state.conversations.push(action.payload);
    },
    updateConversation: (state, action) => {
      const index = state.conversations.findIndex(
        conv => conv.id === action.payload.id
      );
      if (index !== -1) {
        state.conversations[index] = action.payload;
      }
    },
    addTask: (state, action) => {
      state.tasks.push(action.payload);
    },
    updateTaskStatus: (state, action) => {
      const task = state.tasks.find(t => t.id === action.payload.id);
      if (task) {
        task.status = action.payload.status;
      }
    },
    updateUserPreferences: (state, action) => {
      state.userPreferences = {
        ...state.userPreferences,
        ...action.payload,
      };
    },
    addNotification: (state, action) => {
      state.notifications.push(action.payload);
    },
    clearNotification: (state, action) => {
      state.notifications = state.notifications.filter(
        n => n.id !== action.payload
      );
    },
    updateAgentStatus: (state, action) => {
      const { agent, status } = action.payload;
      state.agentStatus[agent] = status;
    },
    resetCommandCenter: (state) => {
      return initialState;
    },
  },
});

export const {
  setActiveProject,
  updateTeamComposition,
  addConversation,
  updateConversation,
  addTask,
  updateTaskStatus,
  updateUserPreferences,
  addNotification,
  clearNotification,
  updateAgentStatus,
  resetCommandCenter,
} = commandCenterSlice.actions;

export default commandCenterSlice.reducer; 