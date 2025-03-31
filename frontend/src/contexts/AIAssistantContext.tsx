import React, { createContext, useContext, useReducer, useCallback } from 'react';
import { AIAssistantState, AIAssistantHistory, AIAssistantSuggestion, AIAssistantSettings, AIAssistantAnalytics } from '../interfaces/ai-assistant';
import { AIAssistantService } from '../services/ai-assistant.service';
import { AIAgentConfig } from '../interfaces/ai';

interface AIAssistantContextType extends AIAssistantState {
    analytics: AIAssistantAnalytics;
    sendMessage: (message: string) => Promise<void>;
    applySuggestion: (suggestion: AIAssistantSuggestion) => void;
    rejectSuggestion: (suggestion: AIAssistantSuggestion) => void;
    toggleExpand: () => void;
    provideFeedback: (suggestionId: string, rating: 'helpful' | 'not_helpful') => void;
    updateSettings: (settings: AIAssistantSettings) => void;
    saveHistory: () => Promise<void>;
    getProjectHistory: (projectId: string) => AIAssistantHistory[];
    getAllProjectIds: () => string[];
    clearProjectHistory: (projectId: string) => void;
}

const initialState: AIAssistantState = {
    isActive: true,
    isProcessing: false,
    history: [],
    suggestions: [],
    settings: {
        model: {
            model: 'sonnet-3.7',
            temperature: 0.7,
            maxTokens: 2000,
            apiKey: process.env.REACT_APP_AI_API_KEY || '',
        },
        features: {
            codeCompletion: true,
            commandSuggestions: true,
            errorExplanations: true,
            refactoring: true,
            documentation: true,
        },
        preferences: {
            language: 'typescript',
            style: 'concise',
            suggestions: 'inline',
            autoComplete: true,
            autoExplain: true,
        },
        shortcuts: {},
    },
    context: {
        currentFile: null,
        selection: {
            start: 0,
            end: 0,
            text: '',
        },
        cursor: {
            line: 0,
            column: 0,
        },
        projectContext: {
            files: [],
            dependencies: {},
            config: {},
        },
        systemContext: {
            os: '',
            runtime: '',
            environment: {},
        },
    },
};

const initialAnalytics: AIAssistantAnalytics = {
    totalInteractions: 0,
    successfulSuggestions: 0,
    rejectedSuggestions: 0,
    averageConfidence: 0,
    popularCommands: [],
    userFeedback: {
        helpful: 0,
        notHelpful: 0,
    },
    performance: {
        averageResponseTime: 0,
        errorRate: 0,
        suggestionAccuracy: 0,
    },
};

type AIAssistantAction =
    | { type: 'ADD_MESSAGE'; payload: AIAssistantHistory }
    | { type: 'SET_SUGGESTIONS'; payload: AIAssistantSuggestion[] }
    | { type: 'SET_PROCESSING'; payload: boolean }
    | { type: 'TOGGLE_ACTIVE' }
    | { type: 'UPDATE_SETTINGS'; payload: AIAssistantSettings }
    | { type: 'UPDATE_ANALYTICS'; payload: Partial<AIAssistantAnalytics> }
    | { type: 'UPDATE_CONTEXT'; payload: Partial<AIAssistantState['context']> };

const aiReducer = (state: AIAssistantState, action: AIAssistantAction): AIAssistantState => {
    switch (action.type) {
        case 'ADD_MESSAGE':
            return {
                ...state,
                history: [...state.history, action.payload],
            };
        case 'SET_SUGGESTIONS':
            return {
                ...state,
                suggestions: action.payload,
            };
        case 'SET_PROCESSING':
            return {
                ...state,
                isProcessing: action.payload,
            };
        case 'TOGGLE_ACTIVE':
            return {
                ...state,
                isActive: !state.isActive,
            };
        case 'UPDATE_SETTINGS':
            return {
                ...state,
                settings: action.payload,
            };
        case 'UPDATE_CONTEXT':
            return {
                ...state,
                context: {
                    ...state.context,
                    ...action.payload,
                },
            };
        default:
            return state;
    }
};

const analyticsReducer = (state: AIAssistantAnalytics, action: AIAssistantAction): AIAssistantAnalytics => {
    switch (action.type) {
        case 'UPDATE_ANALYTICS':
            return {
                ...state,
                ...action.payload,
            };
        default:
            return state;
    }
};

const AIAssistantContext = createContext<AIAssistantContextType | undefined>(undefined);

export const AIAssistantProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    const [state, dispatch] = useReducer(aiReducer, initialState);
    const [analytics, dispatchAnalytics] = useReducer(analyticsReducer, initialAnalytics);
    const aiService = AIAssistantService.getInstance();

    const sendMessage = useCallback(async (message: string) => {
        dispatch({ type: 'SET_PROCESSING', payload: true });
        try {
            const response = await aiService.sendMessage(message, state.context);
            const userMessage: AIAssistantHistory = {
                id: Date.now().toString(),
                type: 'user',
                content: message,
                timestamp: new Date().toISOString(),
                metadata: {
                    projectId: state.context.projectContext.config.projectId,
                },
            };
            dispatch({ type: 'ADD_MESSAGE', payload: userMessage });
            dispatch({ type: 'ADD_MESSAGE', payload: response.history });
            dispatch({ type: 'SET_SUGGESTIONS', payload: response.suggestions });
            dispatchAnalytics({
                type: 'UPDATE_ANALYTICS',
                payload: {
                    totalInteractions: analytics.totalInteractions + 1,
                    performance: {
                        ...analytics.performance,
                        averageResponseTime: (analytics.performance.averageResponseTime * analytics.totalInteractions + 0) / (analytics.totalInteractions + 1),
                    },
                },
            });
        } catch (error) {
            console.error('Error sending message:', error);
            dispatch({
                type: 'ADD_MESSAGE',
                payload: {
                    id: Date.now().toString(),
                    type: 'system',
                    content: 'Failed to send message. Please try again.',
                    timestamp: new Date().toISOString(),
                    metadata: {
                        projectId: state.context.projectContext.config.projectId,
                    },
                },
            });
        } finally {
            dispatch({ type: 'SET_PROCESSING', payload: false });
        }
    }, [state.context, analytics]);

    const applySuggestion = useCallback((suggestion: AIAssistantSuggestion) => {
        dispatch({ type: 'SET_SUGGESTIONS', payload: state.suggestions.filter(s => s.id !== suggestion.id) });
        dispatchAnalytics({
            type: 'UPDATE_ANALYTICS',
            payload: {
                successfulSuggestions: analytics.successfulSuggestions + 1,
                performance: {
                    ...analytics.performance,
                    suggestionAccuracy: (analytics.performance.suggestionAccuracy * analytics.totalInteractions + suggestion.confidence) / (analytics.totalInteractions + 1),
                },
            },
        });
    }, [state.suggestions, analytics]);

    const rejectSuggestion = useCallback((suggestion: AIAssistantSuggestion) => {
        dispatch({ type: 'SET_SUGGESTIONS', payload: state.suggestions.filter(s => s.id !== suggestion.id) });
        dispatchAnalytics({
            type: 'UPDATE_ANALYTICS',
            payload: {
                rejectedSuggestions: analytics.rejectedSuggestions + 1,
            },
        });
    }, [state.suggestions, analytics]);

    const toggleExpand = useCallback(() => {
        dispatch({ type: 'TOGGLE_ACTIVE' });
    }, []);

    const provideFeedback = useCallback((suggestionId: string, rating: 'helpful' | 'not_helpful') => {
        const suggestion = state.suggestions.find(s => s.id === suggestionId);
        if (suggestion) {
            dispatchAnalytics({
                type: 'UPDATE_ANALYTICS',
                payload: {
                    userFeedback: {
                        ...analytics.userFeedback,
                        [rating === 'helpful' ? 'helpful' : 'notHelpful']: analytics.userFeedback[rating === 'helpful' ? 'helpful' : 'notHelpful'] + 1,
                    },
                },
            });
        }
    }, [state.suggestions, analytics]);

    const updateSettings = useCallback((settings: AIAssistantSettings) => {
        dispatch({ type: 'UPDATE_SETTINGS', payload: settings });
    }, []);

    const saveHistory = useCallback(async () => {
        try {
            await aiService.saveHistory(state.history);
            dispatchAnalytics({
                type: 'UPDATE_ANALYTICS',
                payload: {
                    totalInteractions: state.history.length,
                },
            });
        } catch (error) {
            console.error('Error saving history:', error);
        }
    }, [state.history]);

    const getProjectHistory = useCallback((projectId: string) => {
        return aiService.getProjectHistory(projectId);
    }, []);

    const getAllProjectIds = useCallback(() => {
        return aiService.getAllProjectIds();
    }, []);

    const clearProjectHistory = useCallback((projectId: string) => {
        aiService.clearProjectHistory(projectId);
    }, []);

    const value = {
        ...state,
        analytics,
        sendMessage,
        applySuggestion,
        rejectSuggestion,
        toggleExpand,
        provideFeedback,
        updateSettings,
        saveHistory,
        getProjectHistory,
        getAllProjectIds,
        clearProjectHistory,
    };

    return (
        <AIAssistantContext.Provider value={value}>
            {children}
        </AIAssistantContext.Provider>
    );
};

export const useAIAssistant = () => {
    const context = useContext(AIAssistantContext);
    if (context === undefined) {
        throw new Error('useAIAssistant must be used within an AIAssistantProvider');
    }
    return context;
}; 