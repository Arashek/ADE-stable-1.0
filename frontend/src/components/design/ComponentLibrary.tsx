import React, { useState } from 'react';
import { DesignSystem, DesignComponent } from '../../types/design';

interface ComponentLibraryProps {
  components: DesignComponent[];
  onDesignUpdate: (design: Partial<DesignSystem>) => void;
}

export const ComponentLibrary: React.FC<ComponentLibraryProps> = ({
  components,
  onDesignUpdate,
}) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedComponent, setSelectedComponent] = useState<DesignComponent | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState<Partial<DesignComponent>>({});

  const filteredComponents = components.filter(component =>
    component.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    component.type.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const handleCreateComponent = () => {
    const newComponent: DesignComponent = {
      id: `component-${Date.now()}`,
      name: 'New Component',
      type: 'rectangle',
      properties: {},
      styles: {
        backgroundColor: '#ffffff',
        borderColor: '#d1d5db',
        borderWidth: '1px',
      },
    };

    onDesignUpdate({
      components: [...components, newComponent],
    });

    setSelectedComponent(newComponent);
    setIsEditing(true);
    setEditForm(newComponent);
  };

  const handleEditComponent = (component: DesignComponent) => {
    setSelectedComponent(component);
    setIsEditing(true);
    setEditForm(component);
  };

  const handleSaveComponent = () => {
    if (!selectedComponent || !editForm.name) return;

    const updatedComponents = components.map(component =>
      component.id === selectedComponent.id
        ? { ...component, ...editForm }
        : component
    );

    onDesignUpdate({
      components: updatedComponents,
    });

    setIsEditing(false);
    setSelectedComponent(null);
    setEditForm({});
  };

  const handleDeleteComponent = (componentId: string) => {
    if (!confirm('Are you sure you want to delete this component?')) return;

    onDesignUpdate({
      components: components.filter(c => c.id !== componentId),
    });

    if (selectedComponent?.id === componentId) {
      setSelectedComponent(null);
      setIsEditing(false);
      setEditForm({});
    }
  };

  const renderComponentPreview = (component: DesignComponent) => {
    return (
      <div
        className="w-full h-24 border rounded-lg p-2"
        style={{
          backgroundColor: component.styles.backgroundColor || '#ffffff',
          borderColor: component.styles.borderColor || '#d1d5db',
          borderWidth: component.styles.borderWidth || '1px',
        }}
      >
        <div className="text-xs text-gray-500 mb-1">{component.name}</div>
        <div className="w-full h-full bg-white rounded">
          {component.type === 'rectangle' && (
            <div className="w-full h-full rounded" />
          )}
          {component.type === 'text' && (
            <div
              className="w-full h-full flex items-center justify-center"
              style={{
                color: component.styles.color || '#000000',
                fontSize: component.styles.fontSize || '16px',
                fontFamily: component.styles.fontFamily || 'sans-serif',
              }}
            >
              {component.properties.text || 'Text Component'}
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-full">
      {/* Component List */}
      <div className="w-1/3 border-r p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Components</h2>
          <button
            onClick={handleCreateComponent}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            New Component
          </button>
        </div>

        <input
          type="text"
          placeholder="Search components..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full px-3 py-2 border rounded mb-4"
        />

        <div className="space-y-4">
          {filteredComponents.map(component => (
            <div
              key={component.id}
              className={`p-2 border rounded cursor-pointer ${
                selectedComponent?.id === component.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'hover:border-gray-300'
              }`}
              onClick={() => handleEditComponent(component)}
            >
              {renderComponentPreview(component)}
            </div>
          ))}
        </div>
      </div>

      {/* Component Editor */}
      <div className="flex-1 p-4">
        {selectedComponent ? (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">Edit Component</h2>
              <button
                onClick={() => handleDeleteComponent(selectedComponent.id)}
                className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
              >
                Delete
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Name</label>
                <input
                  type="text"
                  value={editForm.name || ''}
                  onChange={(e) => setEditForm(prev => ({ ...prev, name: e.target.value }))}
                  className="w-full px-3 py-2 border rounded"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Type</label>
                <select
                  value={editForm.type || ''}
                  onChange={(e) => setEditForm(prev => ({ ...prev, type: e.target.value }))}
                  className="w-full px-3 py-2 border rounded"
                >
                  <option value="rectangle">Rectangle</option>
                  <option value="text">Text</option>
                  <option value="circle">Circle</option>
                  <option value="image">Image</option>
                </select>
              </div>

              {/* Style Editor */}
              <div>
                <label className="block text-sm font-medium mb-1">Styles</label>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Background Color</label>
                    <input
                      type="color"
                      value={editForm.styles?.backgroundColor || '#ffffff'}
                      onChange={(e) => setEditForm(prev => ({
                        ...prev,
                        styles: { ...prev.styles, backgroundColor: e.target.value },
                      }))}
                      className="w-full h-8"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Border Color</label>
                    <input
                      type="color"
                      value={editForm.styles?.borderColor || '#d1d5db'}
                      onChange={(e) => setEditForm(prev => ({
                        ...prev,
                        styles: { ...prev.styles, borderColor: e.target.value },
                      }))}
                      className="w-full h-8"
                    />
                  </div>
                </div>
              </div>

              <button
                onClick={handleSaveComponent}
                className="w-full px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                Save Changes
              </button>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-500">Select a component to edit</div>
          </div>
        )}
      </div>
    </div>
  );
}; 