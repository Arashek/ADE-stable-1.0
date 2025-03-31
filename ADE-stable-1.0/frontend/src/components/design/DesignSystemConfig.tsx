import React, { useState } from 'react';
import { DesignSystem } from '../../types/design';

interface DesignSystemConfigProps {
  currentDesign: DesignSystem;
  onDesignUpdate: (design: Partial<DesignSystem>) => void;
}

export const DesignSystemConfig: React.FC<DesignSystemConfigProps> = ({
  currentDesign,
  onDesignUpdate,
}) => {
  const [showAdvancedSettings, setShowAdvancedSettings] = useState(false);
  const [figmaEnabled, setFigmaEnabled] = useState(false);
  const [figmaToken, setFigmaToken] = useState('');

  const handleFigmaToggle = () => {
    const newEnabled = !figmaEnabled;
    setFigmaEnabled(newEnabled);
    
    onDesignUpdate({
      metadata: {
        ...currentDesign.metadata,
        integrations: {
          ...currentDesign.metadata.integrations,
          figma: {
            enabled: newEnabled,
            token: newEnabled ? figmaToken : '',
          },
        },
      },
    });
  };

  const handleFigmaTokenChange = (token: string) => {
    setFigmaToken(token);
    onDesignUpdate({
      metadata: {
        ...currentDesign.metadata,
        integrations: {
          ...currentDesign.metadata.integrations,
          figma: {
            enabled: figmaEnabled,
            token,
          },
        },
      },
    });
  };

  return (
    <div className="p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-medium text-gray-900">Design System Settings</h2>
        <button
          onClick={() => setShowAdvancedSettings(!showAdvancedSettings)}
          className="text-sm text-gray-500 hover:text-gray-700"
        >
          {showAdvancedSettings ? 'Hide Advanced Settings' : 'Show Advanced Settings'}
        </button>
      </div>

      {/* Basic Settings */}
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            System Name
          </label>
          <input
            type="text"
            value={currentDesign.metadata.name || ''}
            onChange={e =>
              onDesignUpdate({
                metadata: {
                  ...currentDesign.metadata,
                  name: e.target.value,
                },
              })
            }
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description
          </label>
          <textarea
            value={currentDesign.metadata.description || ''}
            onChange={e =>
              onDesignUpdate({
                metadata: {
                  ...currentDesign.metadata,
                  description: e.target.value,
                },
              })
            }
            className="w-full px-3 py-2 border rounded-md"
            rows={3}
          />
        </div>
      </div>

      {/* Advanced Settings */}
      {showAdvancedSettings && (
        <div className="space-y-4 pt-4 border-t">
          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-2">Integrations</h3>
            
            {/* Figma Integration */}
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <label className="text-sm text-gray-700">Figma Integration</label>
                <button
                  onClick={handleFigmaToggle}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full ${
                    figmaEnabled ? 'bg-blue-500' : 'bg-gray-200'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                      figmaEnabled ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
              </div>

              {figmaEnabled && (
                <div className="mt-2">
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Figma Access Token
                  </label>
                  <input
                    type="password"
                    value={figmaToken}
                    onChange={e => handleFigmaTokenChange(e.target.value)}
                    className="w-full px-3 py-2 border rounded-md"
                    placeholder="Enter your Figma access token"
                  />
                  <p className="mt-1 text-xs text-gray-500">
                    Optional: Enable Figma integration for importing designs and syncing components.
                    Your token is stored securely and only used when explicitly requested.
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Grid Settings */}
          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-2">Grid Settings</h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Grid Size
                </label>
                <input
                  type="number"
                  value={currentDesign.metadata.gridSize || 8}
                  onChange={e =>
                    onDesignUpdate({
                      metadata: {
                        ...currentDesign.metadata,
                        gridSize: parseInt(e.target.value),
                      },
                    })
                  }
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Snap Threshold
                </label>
                <input
                  type="number"
                  value={currentDesign.metadata.snapThreshold || 4}
                  onChange={e =>
                    onDesignUpdate({
                      metadata: {
                        ...currentDesign.metadata,
                        snapThreshold: parseInt(e.target.value),
                      },
                    })
                  }
                  className="w-full px-3 py-2 border rounded-md"
                />
              </div>
            </div>
          </div>

          {/* Export Settings */}
          <div>
            <h3 className="text-sm font-medium text-gray-900 mb-2">Export Settings</h3>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={currentDesign.metadata.exportWithComments || false}
                  onChange={e =>
                    onDesignUpdate({
                      metadata: {
                        ...currentDesign.metadata,
                        exportWithComments: e.target.checked,
                      },
                    })
                  }
                  className="rounded border-gray-300 text-blue-500 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Include comments in exported code
                </span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={currentDesign.metadata.exportWithStyles || true}
                  onChange={e =>
                    onDesignUpdate({
                      metadata: {
                        ...currentDesign.metadata,
                        exportWithStyles: e.target.checked,
                      },
                    })
                  }
                  className="rounded border-gray-300 text-blue-500 focus:ring-blue-500"
                />
                <span className="ml-2 text-sm text-gray-700">
                  Include styles in exported code
                </span>
              </label>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}; 