import React, { useState } from 'react';
import { DesignSystem, DesignPage, DesignSuggestion, DesignNotification } from '../../types/design';
import { DesignAgent } from '../../services/DesignAgent';
import { DesignChat } from './DesignChat';
import { FigmaIntegration } from './FigmaIntegration';
import { DesignToolsPanel } from './DesignToolsPanel';
import { DesignPreview } from './DesignPreview';
import { PageNavigator } from './PageNavigator';
import { ComponentLibrary } from './ComponentLibrary';
import { StyleGuide } from './StyleGuide';
import { DesignSuggestionsPanel } from './DesignSuggestionsPanel';

interface DesignCommandCenterProps {
  designAgent: DesignAgent;
  initialDesign?: Partial<DesignSystem>;
}

type TabType = 'chat' | 'tools' | 'figma' | 'preview' | 'pages' | 'components' | 'styles' | 'suggestions';
type ModificationMode = 'natural' | 'tools' | 'hybrid';

export const DesignCommandCenter: React.FC<DesignCommandCenterProps> = ({
  designAgent,
  initialDesign,
}) => {
  const [currentTab, setCurrentTab] = useState<TabType>('chat');
  const [modificationMode, setModificationMode] = useState<ModificationMode>('hybrid');
  const [currentDesign, setCurrentDesign] = useState<Partial<DesignSystem>>(initialDesign || {});
  const [currentPage, setCurrentPage] = useState<string>('home');
  const [isModifying, setIsModifying] = useState(false);
  const [modificationHistory, setModificationHistory] = useState<Array<{
    timestamp: Date;
    type: 'update' | 'finalize' | 'modify';
    changes: Partial<DesignSystem>;
  }>>([]);

  const handleDesignUpdate = (design: Partial<DesignSystem>) => {
    setCurrentDesign(prev => ({ ...prev, ...design }));
    setModificationHistory(prev => [...prev, {
      timestamp: new Date(),
      type: 'update',
      changes: design,
    }]);
  };

  const handlePageChange = (pageId: string) => {
    setCurrentPage(pageId);
    // Load page-specific design data
    const pageDesign = currentDesign.pages?.find(p => p.id === pageId);
    if (pageDesign) {
      setCurrentDesign(prev => ({
        ...prev,
        currentPage: pageId,
      }));
    }
  };

  const handleModify = async () => {
    setIsModifying(true);
    // Enable modification mode with current context
  };

  const handleUpdate = async () => {
    try {
      // Save current modifications
      await designAgent.updateDesign(currentDesign);
      setModificationHistory(prev => [...prev, {
        timestamp: new Date(),
        type: 'update',
        changes: currentDesign,
      }]);
      setIsModifying(false);
    } catch (error) {
      console.error('Failed to update design:', error);
    }
  };

  const handleFinalize = async (design: DesignSystem) => {
    try {
      await designAgent.finalizeDesign(design);
      setModificationHistory(prev => [...prev, {
        timestamp: new Date(),
        type: 'finalize',
        changes: design,
      }]);
      setIsModifying(false);
    } catch (error) {
      console.error('Failed to finalize design:', error);
    }
  };

  const handleSuggestionApply = (suggestion: DesignSuggestion) => {
    if (suggestion.changes) {
      handleDesignUpdate(suggestion.changes);
    }
  };

  const handleSuggestionReject = (suggestion: DesignSuggestion) => {
    // Handle rejected suggestions
    console.log('Rejected suggestion:', suggestion);
  };

  const handleNotificationAction = (notification: DesignNotification) => {
    if (notification.action) {
      switch (notification.action.type) {
        case 'review':
          setCurrentTab('preview');
          break;
        case 'update':
          handleDesignUpdate(notification.action.data);
          break;
        case 'finalize':
          handleFinalize(notification.action.data);
          break;
        default:
          console.log('Unknown notification action:', notification.action);
      }
    }
  };

  const renderTabContent = () => {
    switch (currentTab) {
      case 'chat':
        return (
          <DesignChat
            designAgent={designAgent}
            currentDesign={currentDesign}
            onDesignUpdate={handleDesignUpdate}
            modificationMode={modificationMode}
            onModeChange={setModificationMode}
          />
        );
      case 'tools':
        return (
          <DesignToolsPanel
            currentDesign={currentDesign}
            onDesignUpdate={handleDesignUpdate}
            modificationMode={modificationMode}
          />
        );
      case 'figma':
        return (
          <FigmaIntegration
            onFileSelect={() => {}}
            onComponentSelect={() => {}}
            onStyleSelect={() => {}}
            onDesignUpdate={handleDesignUpdate}
            onFinalize={handleFinalize}
            designAgent={designAgent}
          />
        );
      case 'preview':
        return (
          <DesignPreview
            design={currentDesign}
            onUpdate={handleDesignUpdate}
            currentPage={currentPage}
          />
        );
      case 'pages':
        return (
          <PageNavigator
            pages={currentDesign.pages || []}
            currentPage={currentPage}
            onPageChange={handlePageChange}
            onDesignUpdate={handleDesignUpdate}
          />
        );
      case 'components':
        return (
          <ComponentLibrary
            components={currentDesign.components || []}
            onDesignUpdate={handleDesignUpdate}
          />
        );
      case 'styles':
        return (
          <StyleGuide
            styles={currentDesign.styles || []}
            onDesignUpdate={handleDesignUpdate}
          />
        );
      case 'suggestions':
        return (
          <DesignSuggestionsPanel
            designAgent={designAgent}
            onSuggestionApply={handleSuggestionApply}
            onSuggestionReject={handleSuggestionReject}
            onNotificationAction={handleNotificationAction}
          />
        );
      default:
        return null;
    }
  };

  return (
    <div className="flex flex-col h-full">
      {/* Main Navigation */}
      <div className="flex border-b">
        <button
          onClick={() => setCurrentTab('chat')}
          className={`px-4 py-2 ${
            currentTab === 'chat'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Design Chat
        </button>
        <button
          onClick={() => setCurrentTab('tools')}
          className={`px-4 py-2 ${
            currentTab === 'tools'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Design Tools
        </button>
        <button
          onClick={() => setCurrentTab('figma')}
          className={`px-4 py-2 ${
            currentTab === 'figma'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Figma Integration
        </button>
        <button
          onClick={() => setCurrentTab('preview')}
          className={`px-4 py-2 ${
            currentTab === 'preview'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Live Preview
        </button>
        <button
          onClick={() => setCurrentTab('pages')}
          className={`px-4 py-2 ${
            currentTab === 'pages'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Pages
        </button>
        <button
          onClick={() => setCurrentTab('components')}
          className={`px-4 py-2 ${
            currentTab === 'components'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Components
        </button>
        <button
          onClick={() => setCurrentTab('styles')}
          className={`px-4 py-2 ${
            currentTab === 'styles'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Styles
        </button>
        <button
          onClick={() => setCurrentTab('suggestions')}
          className={`px-4 py-2 ${
            currentTab === 'suggestions'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Design Suggestions
          {designAgent.getSuggestions().length > 0 && (
            <span className="ml-2 px-2 py-0.5 text-xs bg-blue-500 text-white rounded-full">
              {designAgent.getSuggestions().length}
            </span>
          )}
        </button>
      </div>

      {/* Modification Mode Selector */}
      <div className="flex items-center gap-2 p-2 border-b">
        <span className="text-sm font-medium">Modification Mode:</span>
        <select
          value={modificationMode}
          onChange={(e) => setModificationMode(e.target.value as ModificationMode)}
          className="px-2 py-1 border rounded"
        >
          <option value="natural">Natural Language</option>
          <option value="tools">Design Tools</option>
          <option value="hybrid">Hybrid Mode</option>
        </select>
      </div>

      {/* Tab Content */}
      <div className="flex-1 overflow-hidden">
        {renderTabContent()}
      </div>

      {/* Action Buttons */}
      <div className="border-t p-4 flex gap-2">
        {!isModifying ? (
          <button
            onClick={handleModify}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Modify Design
          </button>
        ) : (
          <>
            <button
              onClick={handleUpdate}
              className="px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
            >
              Update Changes
            </button>
            <button
              onClick={() => handleFinalize(currentDesign as DesignSystem)}
              className="px-4 py-2 bg-purple-500 text-white rounded hover:bg-purple-600"
            >
              Finalize Design
            </button>
          </>
        )}
      </div>

      {/* Modification History */}
      <div className="border-t p-2">
        <div className="text-sm font-medium mb-1">Modification History</div>
        <div className="text-xs space-y-1">
          {modificationHistory.map((entry, index) => (
            <div key={index} className="flex justify-between">
              <span>{entry.type}</span>
              <span>{entry.timestamp.toLocaleTimeString()}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}; 