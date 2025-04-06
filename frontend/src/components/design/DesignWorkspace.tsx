import React, { useState, useCallback, useEffect } from 'react';
import { DesignSystem, DesignComponent, DesignStyle } from '../../types/design';
import { DesignToolsPanel } from './DesignToolsPanel';
import { DesignPropertiesPanel } from './DesignPropertiesPanel';
import { DesignCanvas } from './DesignCanvas';
import { DesignToolbar } from './DesignToolbar';
import { DesignPreview } from './DesignPreview';
import { DesignSystemConfig } from './DesignSystemConfig';

interface DesignWorkspaceProps {
  currentDesign: DesignSystem;
  onDesignUpdate: (design: Partial<DesignSystem>) => void;
  onGenerateCode?: () => void;  // New prop for code generation
  onDeploy?: () => void;        // New prop for deployment
  onTest?: () => void;          // New prop for testing
}

export const DesignWorkspace: React.FC<DesignWorkspaceProps> = ({
  currentDesign,
  onDesignUpdate,
  onGenerateCode,
  onDeploy,
  onTest,
}) => {
  const [selectedComponent, setSelectedComponent] = useState<DesignComponent | undefined>();
  const [selectedStyle, setSelectedStyle] = useState<DesignStyle | undefined>();
  const [history, setHistory] = useState<DesignSystem[]>([currentDesign]);
  const [historyIndex, setHistoryIndex] = useState(0);
  const [showPreview, setShowPreview] = useState(false);
  const [showConfig, setShowConfig] = useState(false);

  const handleComponentSelect = (component: DesignComponent) => {
    setSelectedComponent(component);
    setSelectedStyle(undefined);
  };

  const handleStyleSelect = (style: DesignStyle) => {
    setSelectedStyle(style);
    setSelectedComponent(undefined);
  };

  const handleUndo = useCallback(() => {
    if (historyIndex > 0) {
      setHistoryIndex(prev => prev - 1);
      onDesignUpdate(history[historyIndex - 1]);
    }
  }, [history, historyIndex, onDesignUpdate]);

  const handleRedo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(prev => prev + 1);
      onDesignUpdate(history[historyIndex + 1]);
    }
  }, [history, historyIndex, onDesignUpdate]);

  const handleSave = useCallback(() => {
    // Save current design state
    onDesignUpdate(currentDesign);
  }, [currentDesign, onDesignUpdate]);

  const handlePreview = useCallback(() => {
    setShowPreview(true);
  }, []);

  const handleExport = useCallback(async () => {
    // Export as regular design system
    console.log('Exporting design system...');
  }, []);

  const handleGenerateCode = useCallback(() => {
    if (onGenerateCode) {
      onGenerateCode();
    }
  }, [onGenerateCode]);

  const handleDeploy = useCallback(() => {
    if (onDeploy) {
      onDeploy();
    }
  }, [onDeploy]);

  const handleTest = useCallback(() => {
    if (onTest) {
      onTest();
    }
  }, [onTest]);

  const handleDesignUpdate = useCallback(
    (design: Partial<DesignSystem>) => {
      const updatedDesign = { ...currentDesign, ...design };
      onDesignUpdate(updatedDesign);

      // Update history
      const newHistory = history.slice(0, historyIndex + 1);
      newHistory.push(updatedDesign);
      setHistory(newHistory);
      setHistoryIndex(newHistory.length - 1);
    },
    [currentDesign, history, historyIndex, onDesignUpdate]
  );

  return (
    <div className="h-full flex flex-col">
      <DesignToolbar
        currentDesign={currentDesign}
        onDesignUpdate={handleDesignUpdate}
        onUndo={handleUndo}
        onRedo={handleRedo}
        onSave={handleSave}
        onPreview={handlePreview}
        onExport={handleExport}
        onConfig={() => setShowConfig(true)}
        onGenerateCode={handleGenerateCode}
        onDeploy={handleDeploy}
        onTest={handleTest}
        canUndo={historyIndex > 0}
        canRedo={historyIndex < history.length - 1}
      />
      <div className="flex-1 flex">
        {/* Left Panel - Tools */}
        <div className="w-64 border-r">
          <DesignToolsPanel
            currentDesign={currentDesign}
            onDesignUpdate={handleDesignUpdate}
          />
        </div>

        {/* Main Canvas */}
        <div className="flex-1">
          <DesignCanvas
            currentDesign={currentDesign}
            onDesignUpdate={handleDesignUpdate}
            onComponentSelect={handleComponentSelect}
            onStyleSelect={handleStyleSelect}
          />
        </div>

        {/* Right Panel - Properties */}
        <div className="w-80 border-l">
          <DesignPropertiesPanel
            currentDesign={currentDesign}
            selectedComponent={selectedComponent}
            selectedStyle={selectedStyle}
            onDesignUpdate={handleDesignUpdate}
          />
        </div>
      </div>

      {/* Preview Modal */}
      {showPreview && (
        <DesignPreview
          currentDesign={currentDesign}
          onClose={() => setShowPreview(false)}
        />
      )}

      {/* Configuration Modal */}
      {showConfig && (
        <div className="fixed inset-0 bg-gray-900 bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-xl w-[800px] max-h-[90vh] overflow-y-auto">
            <div className="flex items-center justify-between p-4 border-b">
              <h2 className="text-lg font-medium text-gray-900">Design System Configuration</h2>
              <button
                onClick={() => setShowConfig(false)}
                className="p-2 text-gray-500 hover:text-gray-700"
              >
                <svg
                  className="w-5 h-5"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                </svg>
              </button>
            </div>
            <DesignSystemConfig
              currentDesign={currentDesign}
              onDesignUpdate={handleDesignUpdate}
            />
          </div>
        </div>
      )}
    </div>
  );
}; 