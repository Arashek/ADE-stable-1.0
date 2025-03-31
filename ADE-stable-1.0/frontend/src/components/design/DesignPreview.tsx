import React, { useState } from 'react';
import { DesignSystem, DesignComponent } from '../../types/design';

interface DesignPreviewProps {
  currentDesign: DesignSystem;
  onClose: () => void;
}

export const DesignPreview: React.FC<DesignPreviewProps> = ({
  currentDesign,
  onClose,
}) => {
  const [device, setDevice] = useState<'desktop' | 'tablet' | 'mobile'>('desktop');
  const [isFullscreen, setIsFullscreen] = useState(false);

  const currentPage = currentDesign.pages?.find(p => p.id === currentDesign.currentPage);
  const pageComponents = currentPage?.components
    .map(id => currentDesign.components?.find(c => c.id === id))
    .filter((c): c is DesignComponent => c !== undefined);

  const getPreviewWidth = () => {
    switch (device) {
      case 'mobile':
        return '375px';
      case 'tablet':
        return '768px';
      default:
        return '100%';
    }
  };

  const renderComponent = (component: DesignComponent) => {
    const componentStyles = {
      ...component.styles,
      position: 'absolute',
      left: `${component.properties.x || 0}px`,
      top: `${component.properties.y || 0}px`,
      width: `${component.properties.width || 100}px`,
      height: `${component.properties.height || 100}px`,
    };

    switch (component.type) {
      case 'rectangle':
        return (
          <div
            key={component.id}
            style={componentStyles}
          />
        );
      case 'text':
        return (
          <div
            key={component.id}
            style={componentStyles}
          >
            {component.properties.text || 'Text'}
          </div>
        );
      case 'image':
        return (
          <div
            key={component.id}
            style={componentStyles}
          >
            {component.properties.src ? (
              <img
                src={component.properties.src}
                alt={component.properties.alt || ''}
                style={{ width: '100%', height: '100%', objectFit: 'cover' }}
              />
            ) : (
              <div className="w-full h-full flex items-center justify-center bg-gray-100">
                <span className="text-gray-400">Image</span>
              </div>
            )}
          </div>
        );
      case 'button':
        return (
          <button
            key={component.id}
            style={componentStyles}
          >
            {component.properties.text || 'Button'}
          </button>
        );
      default:
        return null;
    }
  };

  return (
    <div className={`fixed inset-0 bg-gray-900 ${isFullscreen ? 'z-50' : 'z-40'}`}>
      {/* Preview Header */}
      <div className="h-12 bg-white border-b flex items-center justify-between px-4">
        <div className="flex items-center space-x-4">
          <h2 className="text-lg font-medium text-gray-900">Preview</h2>
          <div className="flex items-center space-x-2">
            <button
              onClick={() => setDevice('desktop')}
              className={`px-3 py-1 rounded-md text-sm ${
                device === 'desktop'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Desktop
            </button>
            <button
              onClick={() => setDevice('tablet')}
              className={`px-3 py-1 rounded-md text-sm ${
                device === 'tablet'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Tablet
            </button>
            <button
              onClick={() => setDevice('mobile')}
              className={`px-3 py-1 rounded-md text-sm ${
                device === 'mobile'
                  ? 'bg-blue-500 text-white'
                  : 'text-gray-700 hover:bg-gray-100'
              }`}
            >
              Mobile
            </button>
          </div>
        </div>
        <div className="flex items-center space-x-2">
          <button
            onClick={() => setIsFullscreen(!isFullscreen)}
            className="p-2 text-gray-700 hover:bg-gray-100 rounded-md"
            title={isFullscreen ? 'Exit Fullscreen' : 'Enter Fullscreen'}
          >
            <svg
              className="w-5 h-5"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              {isFullscreen ? (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M9 9h6v6M15 9l-6 6"
                />
              ) : (
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M4 8V4m0 0h4M4 4l5 5m11-1V4m0 0h-4m4 0l-5 5M4 16v4m0 0h4m-4 0l5-5m11 5l-5-5m5 5v-4m0 4h-4"
                />
              )}
            </svg>
          </button>
          <button
            onClick={onClose}
            className="p-2 text-gray-700 hover:bg-gray-100 rounded-md"
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
      </div>

      {/* Preview Content */}
      <div className="h-[calc(100%-3rem)] flex items-center justify-center p-4">
        <div
          className="relative bg-white shadow-lg"
          style={{
            width: getPreviewWidth(),
            height: device === 'desktop' ? '100%' : '80%',
            maxHeight: device === 'desktop' ? 'none' : '800px',
          }}
        >
          {/* Page Background */}
          <div
            className="absolute inset-0"
            style={{
              backgroundColor: currentPage?.properties.backgroundColor || '#ffffff',
            }}
          />

          {/* Components */}
          {pageComponents?.map(renderComponent)}
        </div>
      </div>
    </div>
  );
}; 