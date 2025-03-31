import React from 'react';
import { DesignSystem } from '../../types/design';

interface DesignToolbarProps {
  currentDesign: DesignSystem;
  onDesignUpdate: (design: Partial<DesignSystem>) => void;
  onUndo: () => void;
  onRedo: () => void;
  onSave: () => void;
  onPreview: () => void;
  onExport: () => void;
  onConfig: () => void;
  onGenerateCode: () => void;
  onDeploy: () => void;
  onTest: () => void;
  canUndo: boolean;
  canRedo: boolean;
}

export const DesignToolbar: React.FC<DesignToolbarProps> = ({
  currentDesign,
  onDesignUpdate,
  onUndo,
  onRedo,
  onSave,
  onPreview,
  onExport,
  onConfig,
  onGenerateCode,
  onDeploy,
  onTest,
  canUndo,
  canRedo,
}) => {
  const handleZoomChange = (value: number) => {
    onDesignUpdate({
      metadata: {
        ...currentDesign.metadata,
        zoom: value,
      },
    });
  };

  const handleGridToggle = () => {
    onDesignUpdate({
      metadata: {
        ...currentDesign.metadata,
        showGrid: !currentDesign.metadata.showGrid,
      },
    });
  };

  const handleSnapToggle = () => {
    onDesignUpdate({
      metadata: {
        ...currentDesign.metadata,
        snapToGrid: !currentDesign.metadata.snapToGrid,
      },
    });
  };

  return (
    <div className="h-12 border-b bg-white flex items-center px-4 space-x-4">
      {/* History Controls */}
      <div className="flex items-center space-x-2">
        <button
          onClick={onUndo}
          disabled={!canUndo}
          className="p-2 text-gray-700 hover:bg-gray-100 rounded-md disabled:opacity-50"
          title="Undo"
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
              d="M3 10h10a8 8 0 018 8v2M3 10l6 6m-6-6l6-6"
            />
          </svg>
        </button>
        <button
          onClick={onRedo}
          disabled={!canRedo}
          className="p-2 text-gray-700 hover:bg-gray-100 rounded-md disabled:opacity-50"
          title="Redo"
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
              d="M21 10H11a8 8 0 00-8 8v2M21 10l-6 6m6-6l-6-6"
            />
          </svg>
        </button>
      </div>

      {/* Development Actions */}
      <div className="flex items-center space-x-2 border-l pl-4">
        <button
          onClick={onGenerateCode}
          className="px-4 py-2 text-sm font-medium text-white bg-green-500 rounded-md hover:bg-green-600"
          title="Generate Code"
        >
          Generate Code
        </button>
        <button
          onClick={onTest}
          className="px-4 py-2 text-sm font-medium text-white bg-yellow-500 rounded-md hover:bg-yellow-600"
          title="Run Tests"
        >
          Test
        </button>
        <button
          onClick={onDeploy}
          className="px-4 py-2 text-sm font-medium text-white bg-purple-500 rounded-md hover:bg-purple-600"
          title="Deploy"
        >
          Deploy
        </button>
      </div>

      {/* Design Actions */}
      <div className="flex items-center space-x-2 border-l pl-4">
        <button
          onClick={onConfig}
          className="p-2 text-gray-700 hover:bg-gray-100 rounded-md"
          title="Settings"
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
              d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
            />
          </svg>
        </button>
        <button
          onClick={onPreview}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Preview
        </button>
        <button
          onClick={onSave}
          className="px-4 py-2 text-sm font-medium text-white bg-blue-500 rounded-md hover:bg-blue-600"
        >
          Save
        </button>
        <button
          onClick={onExport}
          className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
        >
          Export
        </button>
      </div>
    </div>
  );
}; 