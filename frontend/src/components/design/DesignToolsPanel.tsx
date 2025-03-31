import React, { useState } from 'react';
import { DesignSystem, DesignComponent, DesignStyle, DesignPage } from '../../types/design';

interface DesignToolsPanelProps {
  currentDesign: DesignSystem;
  onDesignUpdate: (design: Partial<DesignSystem>) => void;
}

export const DesignToolsPanel: React.FC<DesignToolsPanelProps> = ({
  currentDesign,
  onDesignUpdate,
}) => {
  const [activeTab, setActiveTab] = useState<'components' | 'styles' | 'layout'>('components');
  const [selectedTool, setSelectedTool] = useState<string | null>(null);

  const handleToolSelect = (tool: string) => {
    setSelectedTool(tool);
  };

  const handleComponentAdd = (component: DesignComponent) => {
    const currentPage = currentDesign.pages?.find(p => p.id === currentDesign.currentPage);
    if (!currentPage) return;

    const updatedPages = currentDesign.pages?.map(page =>
      page.id === currentPage.id
        ? {
            ...page,
            components: [...(page.components || []), component.id],
          }
        : page
    );

    onDesignUpdate({
      pages: updatedPages,
    });
  };

  const handleStyleApply = (style: DesignStyle) => {
    const currentPage = currentDesign.pages?.find(p => p.id === currentDesign.currentPage);
    if (!currentPage) return;

    const updatedPages = currentDesign.pages?.map(page =>
      page.id === currentPage.id
        ? {
            ...page,
            styles: [...(page.styles || []), style.id],
          }
        : page
    );

    onDesignUpdate({
      pages: updatedPages,
    });
  };

  const renderComponentTools = () => {
    return (
      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={() => handleToolSelect('rectangle')}
          className={`p-4 border rounded-lg text-center ${
            selectedTool === 'rectangle' ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'
          }`}
        >
          <div className="w-full h-16 bg-white border rounded mb-2" />
          <div className="text-sm">Rectangle</div>
        </button>
        <button
          onClick={() => handleToolSelect('text')}
          className={`p-4 border rounded-lg text-center ${
            selectedTool === 'text' ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'
          }`}
        >
          <div className="w-full h-16 bg-white border rounded mb-2 flex items-center justify-center">
            <span className="text-gray-500">Text</span>
          </div>
          <div className="text-sm">Text</div>
        </button>
        <button
          onClick={() => handleToolSelect('image')}
          className={`p-4 border rounded-lg text-center ${
            selectedTool === 'image' ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'
          }`}
        >
          <div className="w-full h-16 bg-white border rounded mb-2 flex items-center justify-center">
            <span className="text-gray-500">Image</span>
          </div>
          <div className="text-sm">Image</div>
        </button>
        <button
          onClick={() => handleToolSelect('button')}
          className={`p-4 border rounded-lg text-center ${
            selectedTool === 'button' ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'
          }`}
        >
          <div className="w-full h-16 bg-white border rounded mb-2 flex items-center justify-center">
            <span className="text-gray-500">Button</span>
          </div>
          <div className="text-sm">Button</div>
        </button>
      </div>
    );
  };

  const renderStyleTools = () => {
    return (
      <div className="space-y-4">
        {currentDesign.styles?.map(style => (
          <button
            key={style.id}
            onClick={() => handleStyleApply(style)}
            className="w-full p-4 border rounded-lg text-left hover:border-gray-300"
          >
            <div className="text-sm font-medium mb-1">{style.name}</div>
            <div
              className="w-full h-8 rounded"
              style={{
                backgroundColor: style.type === 'FILL' ? style.value : '#ffffff',
                borderColor: '#d1d5db',
                borderWidth: '1px',
              }}
            />
          </button>
        ))}
      </div>
    );
  };

  const renderLayoutTools = () => {
    return (
      <div className="space-y-4">
        <button
          onClick={() => handleToolSelect('grid')}
          className={`w-full p-4 border rounded-lg text-left ${
            selectedTool === 'grid' ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'
          }`}
        >
          <div className="text-sm font-medium mb-1">Grid Layout</div>
          <div className="w-full h-16 bg-white border rounded grid grid-cols-3 gap-1 p-1">
            {[...Array(6)].map((_, i) => (
              <div key={i} className="bg-gray-100 rounded" />
            ))}
          </div>
        </button>
        <button
          onClick={() => handleToolSelect('flex')}
          className={`w-full p-4 border rounded-lg text-left ${
            selectedTool === 'flex' ? 'border-blue-500 bg-blue-50' : 'hover:border-gray-300'
          }`}
        >
          <div className="text-sm font-medium mb-1">Flex Layout</div>
          <div className="w-full h-16 bg-white border rounded flex gap-1 p-1">
            {[...Array(3)].map((_, i) => (
              <div key={i} className="flex-1 bg-gray-100 rounded" />
            ))}
          </div>
        </button>
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col">
      {/* Tool Tabs */}
      <div className="flex border-b">
        <button
          onClick={() => setActiveTab('components')}
          className={`px-4 py-2 ${
            activeTab === 'components'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Components
        </button>
        <button
          onClick={() => setActiveTab('styles')}
          className={`px-4 py-2 ${
            activeTab === 'styles'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Styles
        </button>
        <button
          onClick={() => setActiveTab('layout')}
          className={`px-4 py-2 ${
            activeTab === 'layout'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Layout
        </button>
      </div>

      {/* Tool Content */}
      <div className="flex-1 p-4 overflow-y-auto">
        {activeTab === 'components' && renderComponentTools()}
        {activeTab === 'styles' && renderStyleTools()}
        {activeTab === 'layout' && renderLayoutTools()}
      </div>
    </div>
  );
}; 