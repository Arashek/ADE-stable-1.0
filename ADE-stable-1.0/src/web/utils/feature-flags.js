import { create } from 'zustand';

// Feature flag store
const useFeatureFlags = create((set, get) => ({
  // Feature flags
  flags: {
    commandCenter: {
      enabled: true,
      rolloutPercentage: 100,
      variant: 'control',
      startDate: '2024-01-01',
      endDate: null
    },
    voiceProcessing: {
      enabled: true,
      rolloutPercentage: 50,
      variant: 'control',
      startDate: '2024-01-01',
      endDate: null
    },
    imageProcessing: {
      enabled: true,
      rolloutPercentage: 75,
      variant: 'control',
      startDate: '2024-01-01',
      endDate: null
    },
    aiSuggestions: {
      enabled: false,
      rolloutPercentage: 0,
      variant: 'control',
      startDate: null,
      endDate: null
    }
  },

  // Analytics data
  analytics: {
    featureUsage: {},
    userFeedback: [],
    performanceMetrics: {},
    errorRates: {}
  },

  // Methods
  isFeatureEnabled: (featureName) => {
    const feature = get().flags[featureName];
    if (!feature) return false;
    
    const now = new Date();
    const startDate = new Date(feature.startDate);
    const endDate = feature.endDate ? new Date(feature.endDate) : null;
    
    if (endDate && now > endDate) return false;
    if (now < startDate) return false;
    
    return feature.enabled;
  },

  getFeatureVariant: (featureName) => {
    const feature = get().flags[featureName];
    if (!feature) return 'control';
    
    // A/B testing logic
    const userId = localStorage.getItem('userId');
    if (!userId) return 'control';
    
    const hash = userId.split('').reduce((acc, char) => {
      return char.charCodeAt(0) + ((acc << 5) - acc);
    }, 0);
    
    const percentage = Math.abs(hash % 100);
    return percentage < feature.rolloutPercentage ? feature.variant : 'control';
  },

  updateFeatureFlag: (featureName, updates) => {
    set((state) => ({
      flags: {
        ...state.flags,
        [featureName]: {
          ...state.flags[featureName],
          ...updates
        }
      }
    }));
  },

  trackFeatureUsage: (featureName, action, metadata = {}) => {
    set((state) => ({
      analytics: {
        ...state.analytics,
        featureUsage: {
          ...state.analytics.featureUsage,
          [featureName]: {
            ...state.analytics.featureUsage[featureName],
            [action]: (state.analytics.featureUsage[featureName]?.[action] || 0) + 1,
            lastUsed: new Date().toISOString(),
            metadata: {
              ...state.analytics.featureUsage[featureName]?.metadata,
              [new Date().toISOString()]: metadata
            }
          }
        }
      }
    }));
  },

  collectUserFeedback: (featureName, feedback, rating) => {
    set((state) => ({
      analytics: {
        ...state.analytics,
        userFeedback: [
          ...state.analytics.userFeedback,
          {
            feature: featureName,
            feedback,
            rating,
            timestamp: new Date().toISOString()
          }
        ]
      }
    }));
  },

  trackPerformanceMetric: (metricName, value) => {
    set((state) => ({
      analytics: {
        ...state.analytics,
        performanceMetrics: {
          ...state.analytics.performanceMetrics,
          [metricName]: [
            ...(state.analytics.performanceMetrics[metricName] || []),
            {
              value,
              timestamp: new Date().toISOString()
            }
          ]
        }
      }
    }));
  },

  trackError: (featureName, error) => {
    set((state) => ({
      analytics: {
        ...state.analytics,
        errorRates: {
          ...state.analytics.errorRates,
          [featureName]: {
            ...state.analytics.errorRates[featureName],
            count: (state.analytics.errorRates[featureName]?.count || 0) + 1,
            lastError: {
              message: error.message,
              stack: error.stack,
              timestamp: new Date().toISOString()
            }
          }
        }
      }
    }));
  },

  // Export analytics data
  exportAnalytics: () => {
    const analytics = get().analytics;
    const blob = new Blob([JSON.stringify(analytics, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `analytics-${new Date().toISOString()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  }
}));

export default useFeatureFlags; 