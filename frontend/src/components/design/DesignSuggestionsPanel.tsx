import React, { useState, useEffect } from 'react';
import { DesignAgent, DesignSuggestion, DesignNotification } from '../../services/DesignAgent';

interface DesignSuggestionsPanelProps {
  designAgent: DesignAgent;
  onSuggestionApply: (suggestion: DesignSuggestion) => void;
  onSuggestionReject: (suggestion: DesignSuggestion) => void;
  onNotificationAction: (notification: DesignNotification) => void;
}

export const DesignSuggestionsPanel: React.FC<DesignSuggestionsPanelProps> = ({
  designAgent,
  onSuggestionApply,
  onSuggestionReject,
  onNotificationAction,
}) => {
  const [suggestions, setSuggestions] = useState<DesignSuggestion[]>([]);
  const [notifications, setNotifications] = useState<DesignNotification[]>([]);
  const [activeTab, setActiveTab] = useState<'suggestions' | 'notifications'>('suggestions');
  const [isBlinking, setIsBlinking] = useState(false);

  useEffect(() => {
    // Initial load
    setSuggestions(designAgent.getSuggestions());
    setNotifications(designAgent.getNotifications());

    // Listen for updates
    const handleSuggestion = (suggestion: DesignSuggestion) => {
      setSuggestions(prev => [...prev, suggestion]);
      setIsBlinking(true);
      setTimeout(() => setIsBlinking(false), 2000);
    };

    const handleNotification = (notification: DesignNotification) => {
      setNotifications(prev => [...prev, notification]);
      setIsBlinking(true);
      setTimeout(() => setIsBlinking(false), 2000);
    };

    designAgent.on('design:suggestion', handleSuggestion);
    designAgent.on('design:notification', handleNotification);

    return () => {
      designAgent.off('design:suggestion', handleSuggestion);
      designAgent.off('design:notification', handleNotification);
    };
  }, [designAgent]);

  const handleApplySuggestion = async (suggestion: DesignSuggestion) => {
    const success = await designAgent.applySuggestion(suggestion.id);
    if (success) {
      setSuggestions(prev => prev.filter(s => s.id !== suggestion.id));
      onSuggestionApply(suggestion);
    }
  };

  const handleRejectSuggestion = async (suggestion: DesignSuggestion) => {
    await designAgent.rejectSuggestion(suggestion.id);
    setSuggestions(prev => prev.filter(s => s.id !== suggestion.id));
    onSuggestionReject(suggestion);
  };

  const handleNotificationClick = (notification: DesignNotification) => {
    if (notification.action) {
      onNotificationAction(notification);
    }
  };

  const renderSuggestion = (suggestion: DesignSuggestion) => (
    <div key={suggestion.id} className="p-4 border rounded-lg mb-2">
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-medium">{suggestion.type}</h3>
          <p className="text-sm text-gray-600">{suggestion.description}</p>
        </div>
        <span className={`px-2 py-1 text-xs rounded ${
          suggestion.priority === 'high' ? 'bg-red-100 text-red-800' :
          suggestion.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
          'bg-green-100 text-green-800'
        }`}>
          {suggestion.priority}
        </span>
      </div>
      
      {suggestion.preview && (
        <div className="mb-2">
          <img src={suggestion.preview} alt="Preview" className="max-w-full h-auto rounded" />
        </div>
      )}

      <div className="flex gap-2">
        <button
          onClick={() => handleApplySuggestion(suggestion)}
          className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Apply
        </button>
        <button
          onClick={() => handleRejectSuggestion(suggestion)}
          className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600"
        >
          Reject
        </button>
      </div>
    </div>
  );

  const renderNotification = (notification: DesignNotification) => (
    <div
      key={notification.id}
      onClick={() => handleNotificationClick(notification)}
      className="p-4 border rounded-lg mb-2 cursor-pointer hover:bg-gray-50"
    >
      <div className="flex justify-between items-start mb-2">
        <div>
          <h3 className="font-medium">{notification.title}</h3>
          <p className="text-sm text-gray-600">{notification.message}</p>
        </div>
        <span className={`px-2 py-1 text-xs rounded ${
          notification.priority === 'high' ? 'bg-red-100 text-red-800' :
          notification.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
          'bg-green-100 text-green-800'
        }`}>
          {notification.priority}
        </span>
      </div>
      
      {notification.action && (
        <div className="text-sm text-blue-500">
          Click to {notification.action.type}
        </div>
      )}
    </div>
  );

  return (
    <div className="flex flex-col h-full">
      {/* Tabs */}
      <div className="flex border-b">
        <button
          onClick={() => setActiveTab('suggestions')}
          className={`px-4 py-2 ${
            activeTab === 'suggestions'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Suggestions
          {suggestions.length > 0 && (
            <span className="ml-2 px-2 py-0.5 text-xs bg-blue-500 text-white rounded-full">
              {suggestions.length}
            </span>
          )}
        </button>
        <button
          onClick={() => setActiveTab('notifications')}
          className={`px-4 py-2 ${
            activeTab === 'notifications'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Notifications
          {notifications.length > 0 && (
            <span className="ml-2 px-2 py-0.5 text-xs bg-blue-500 text-white rounded-full">
              {notifications.length}
            </span>
          )}
        </button>
      </div>

      {/* Content */}
      <div className={`flex-1 overflow-y-auto p-4 ${isBlinking ? 'animate-pulse' : ''}`}>
        {activeTab === 'suggestions' ? (
          suggestions.length > 0 ? (
            suggestions.map(renderSuggestion)
          ) : (
            <div className="text-center text-gray-500 py-8">
              No suggestions available
            </div>
          )
        ) : (
          notifications.length > 0 ? (
            notifications.map(renderNotification)
          ) : (
            <div className="text-center text-gray-500 py-8">
              No notifications
            </div>
          )
        )}
      </div>
    </div>
  );
}; 