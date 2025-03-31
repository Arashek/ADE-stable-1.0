import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { useLocation } from 'react-router-dom';

// Action types
const ActionTypes = {
  SET_CURRENT_FILE: 'SET_CURRENT_FILE',
  SET_SELECTED_CODE: 'SET_SELECTED_CODE',
  UPDATE_PROJECT_STRUCTURE: 'UPDATE_PROJECT_STRUCTURE',
  SET_DEBUG_STATE: 'SET_DEBUG_STATE',
  SET_GIT_STATE: 'SET_GIT_STATE',
  SET_TEST_RESULTS: 'SET_TEST_RESULTS',
  SET_TERMINAL_OUTPUT: 'SET_TERMINAL_OUTPUT',
  SET_ERRORS: 'SET_ERRORS',
  TOGGLE_COMMAND_CENTER: 'TOGGLE_COMMAND_CENTER',
  SET_USER_PREFERENCES: 'SET_USER_PREFERENCES',
  UPDATE_SESSION: 'UPDATE_SESSION'
};

// Initial state
const initialState = {
  currentFile: null,
  selectedCode: null,
  projectStructure: null,
  debugState: null,
  gitState: null,
  testResults: null,
  terminalOutput: null,
  errors: [],
  isCommandCenterOpen: false,
  userPreferences: {
    theme: 'light',
    fontSize: 14,
    keyboardShortcuts: {
      toggleCommandCenter: 'ctrl+shift+c',
      askAboutCode: 'ctrl+shift+a',
      jumpToFile: 'ctrl+shift+j'
    },
    commandCenterPosition: 'right',
    autoOpenOnError: true
  },
  activeSession: null
};

// Reducer
const reducer = (state, action) => {
  switch (action.type) {
    case ActionTypes.SET_CURRENT_FILE:
      return { ...state, currentFile: action.payload };
    case ActionTypes.SET_SELECTED_CODE:
      return { ...state, selectedCode: action.payload };
    case ActionTypes.UPDATE_PROJECT_STRUCTURE:
      return { ...state, projectStructure: action.payload };
    case ActionTypes.SET_DEBUG_STATE:
      return { ...state, debugState: action.payload };
    case ActionTypes.SET_GIT_STATE:
      return { ...state, gitState: action.payload };
    case ActionTypes.SET_TEST_RESULTS:
      return { ...state, testResults: action.payload };
    case ActionTypes.SET_TERMINAL_OUTPUT:
      return { ...state, terminalOutput: action.payload };
    case ActionTypes.SET_ERRORS:
      return { ...state, errors: action.payload };
    case ActionTypes.TOGGLE_COMMAND_CENTER:
      return { ...state, isCommandCenterOpen: !state.isCommandCenterOpen };
    case ActionTypes.SET_USER_PREFERENCES:
      return { ...state, userPreferences: { ...state.userPreferences, ...action.payload } };
    case ActionTypes.UPDATE_SESSION:
      return { ...state, activeSession: action.payload };
    default:
      return state;
  }
};

// Create context
const GlobalContext = createContext();

// Provider component
export const GlobalProvider = ({ children }) => {
  const [state, dispatch] = useReducer(reducer, initialState);
  const location = useLocation();

  // Load user preferences from localStorage
  useEffect(() => {
    const savedPreferences = localStorage.getItem('userPreferences');
    if (savedPreferences) {
      dispatch({ type: ActionTypes.SET_USER_PREFERENCES, payload: JSON.parse(savedPreferences) });
    }
  }, []);

  // Save user preferences to localStorage
  useEffect(() => {
    localStorage.setItem('userPreferences', JSON.stringify(state.userPreferences));
  }, [state.userPreferences]);

  // Handle keyboard shortcuts
  useEffect(() => {
    const handleKeyPress = (event) => {
      const { keyboardShortcuts } = state.userPreferences;
      
      // Check for Command Center toggle shortcut
      if (event.ctrlKey && event.shiftKey && event.key === 'C') {
        dispatch({ type: ActionTypes.TOGGLE_COMMAND_CENTER });
      }
      
      // Check for "Ask about code" shortcut
      if (event.ctrlKey && event.shiftKey && event.key === 'A') {
        // Trigger "Ask about code" action
        if (state.selectedCode) {
          // Implement ask about code functionality
        }
      }
      
      // Check for "Jump to file" shortcut
      if (event.ctrlKey && event.shiftKey && event.key === 'J') {
        // Trigger "Jump to file" action
        // Implement jump to file functionality
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [state.userPreferences, state.selectedCode]);

  // Update current file based on location
  useEffect(() => {
    const filePath = location.pathname.split('/').pop();
    if (filePath) {
      dispatch({ type: ActionTypes.SET_CURRENT_FILE, payload: filePath });
    }
  }, [location]);

  return (
    <GlobalContext.Provider value={{ state, dispatch, ActionTypes }}>
      {children}
    </GlobalContext.Provider>
  );
};

// Custom hook for using the global context
export const useGlobal = () => {
  const context = useContext(GlobalContext);
  if (!context) {
    throw new Error('useGlobal must be used within a GlobalProvider');
  }
  return context;
}; 