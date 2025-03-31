import React, { useState, useEffect } from 'react';
import { DesignSystem, DesignComponent, DesignStyle } from '../../types/design';

interface DesignPropertiesPanelProps {
  currentDesign: DesignSystem;
  selectedComponent?: DesignComponent;
  selectedStyle?: DesignStyle;
  onDesignUpdate: (design: Partial<DesignSystem>) => void;
}

export const DesignPropertiesPanel: React.FC<DesignPropertiesPanelProps> = ({
  currentDesign,
  selectedComponent,
  selectedStyle,
  onDesignUpdate,
}) => {
  const [activeTab, setActiveTab] = useState<'component' | 'style'>('component');
  const [editForm, setEditForm] = useState<Partial<DesignComponent | DesignStyle>>({});

  useEffect(() => {
    if (selectedComponent) {
      setEditForm(selectedComponent);
      setActiveTab('component');
    } else if (selectedStyle) {
      setEditForm(selectedStyle);
      setActiveTab('style');
    }
  }, [selectedComponent, selectedStyle]);

  const handlePropertyChange = (key: string, value: any) => {
    setEditForm(prev => ({ ...prev, [key]: value }));
  };

  const handleSave = () => {
    if (activeTab === 'component' && selectedComponent) {
      const updatedComponents = currentDesign.components?.map(comp =>
        comp.id === selectedComponent.id ? { ...comp, ...editForm } : comp
      );
      onDesignUpdate({ components: updatedComponents });
    } else if (activeTab === 'style' && selectedStyle) {
      const updatedStyles = currentDesign.styles?.map(style =>
        style.id === selectedStyle.id ? { ...style, ...editForm } : style
      );
      onDesignUpdate({ styles: updatedStyles });
    }
  };

  const renderComponentProperties = () => {
    if (!selectedComponent) {
      return (
        <div className="text-gray-500 text-center py-4">
          Select a component to edit its properties
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
          <input
            type="text"
            value={editForm.name || ''}
            onChange={e => handlePropertyChange('name', e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select
            value={editForm.type || ''}
            onChange={e => handlePropertyChange('type', e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
          >
            <option value="rectangle">Rectangle</option>
            <option value="text">Text</option>
            <option value="image">Image</option>
            <option value="button">Button</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Properties</label>
          <textarea
            value={JSON.stringify(editForm.properties || {}, null, 2)}
            onChange={e => {
              try {
                handlePropertyChange('properties', JSON.parse(e.target.value));
              } catch (error) {
                // Handle invalid JSON
              }
            }}
            className="w-full px-3 py-2 border rounded-md font-mono text-sm"
            rows={4}
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Styles</label>
          <textarea
            value={JSON.stringify(editForm.styles || {}, null, 2)}
            onChange={e => {
              try {
                handlePropertyChange('styles', JSON.parse(e.target.value));
              } catch (error) {
                // Handle invalid JSON
              }
            }}
            className="w-full px-3 py-2 border rounded-md font-mono text-sm"
            rows={4}
          />
        </div>
      </div>
    );
  };

  const renderStyleProperties = () => {
    if (!selectedStyle) {
      return (
        <div className="text-gray-500 text-center py-4">
          Select a style to edit its properties
        </div>
      );
    }

    return (
      <div className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
          <input
            type="text"
            value={editForm.name || ''}
            onChange={e => handlePropertyChange('name', e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
          <select
            value={editForm.type || ''}
            onChange={e => handlePropertyChange('type', e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
          >
            <option value="FILL">Fill</option>
            <option value="TEXT">Text</option>
            <option value="EFFECT">Effect</option>
            <option value="GRID">Grid</option>
          </select>
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Value</label>
          <input
            type="text"
            value={editForm.value || ''}
            onChange={e => handlePropertyChange('value', e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
          />
        </div>
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Scope</label>
          <select
            value={editForm.scope || ''}
            onChange={e => handlePropertyChange('scope', e.target.value)}
            className="w-full px-3 py-2 border rounded-md"
          >
            <option value="global">Global</option>
            <option value="page">Page</option>
            <option value="component">Component</option>
          </select>
        </div>
      </div>
    );
  };

  return (
    <div className="h-full flex flex-col">
      {/* Tabs */}
      <div className="flex border-b">
        <button
          onClick={() => setActiveTab('component')}
          className={`px-4 py-2 ${
            activeTab === 'component'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Component Properties
        </button>
        <button
          onClick={() => setActiveTab('style')}
          className={`px-4 py-2 ${
            activeTab === 'style'
              ? 'border-b-2 border-blue-500 text-blue-500'
              : 'text-gray-500 hover:text-gray-700'
          }`}
        >
          Style Properties
        </button>
      </div>

      {/* Content */}
      <div className="flex-1 p-4 overflow-y-auto">
        {activeTab === 'component' ? renderComponentProperties() : renderStyleProperties()}
      </div>

      {/* Save Button */}
      <div className="p-4 border-t">
        <button
          onClick={handleSave}
          className="w-full px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
        >
          Save Changes
        </button>
      </div>
    </div>
  );
}; 