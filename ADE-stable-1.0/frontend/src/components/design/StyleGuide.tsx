import React, { useState } from 'react';
import { DesignSystem, DesignStyle } from '../../types/design';

interface StyleGuideProps {
  styles: DesignStyle[];
  onDesignUpdate: (design: Partial<DesignSystem>) => void;
}

export const StyleGuide: React.FC<StyleGuideProps> = ({
  styles,
  onDesignUpdate,
}) => {
  const [selectedStyle, setSelectedStyle] = useState<DesignStyle | null>(null);
  const [editForm, setEditForm] = useState<Partial<DesignStyle>>({});
  const [isCreating, setIsCreating] = useState(false);

  const handleCreateStyle = () => {
    const newStyle: DesignStyle = {
      id: `style-${Date.now()}`,
      name: 'New Style',
      type: 'class',
      properties: {},
      scope: 'global',
    };

    onDesignUpdate({
      styles: [...styles, newStyle],
    });

    setSelectedStyle(newStyle);
    setEditForm(newStyle);
    setIsCreating(true);
  };

  const handleEditStyle = (style: DesignStyle) => {
    setSelectedStyle(style);
    setEditForm(style);
    setIsCreating(false);
  };

  const handleSaveStyle = () => {
    if (!editForm.name) return;

    const updatedStyles = styles.map(style =>
      style.id === selectedStyle?.id
        ? { ...style, ...editForm }
        : style
    );

    onDesignUpdate({
      styles: updatedStyles,
    });

    setSelectedStyle(null);
    setEditForm({});
    setIsCreating(false);
  };

  const handleDeleteStyle = (styleId: string) => {
    const updatedStyles = styles.filter(s => s.id !== styleId);
    onDesignUpdate({
      styles: updatedStyles,
    });

    if (selectedStyle?.id === styleId) {
      setSelectedStyle(null);
      setEditForm({});
      setIsCreating(false);
    }
  };

  const renderStylePreview = (style: DesignStyle) => {
    return (
      <div
        className="w-full h-24 border rounded-lg p-2"
        style={{
          backgroundColor: style.properties.backgroundColor || '#ffffff',
          borderColor: style.properties.borderColor || '#d1d5db',
          borderWidth: style.properties.borderWidth || '1px',
        }}
      >
        <div className="text-xs text-gray-500 mb-1">{style.name}</div>
        <div className="w-full h-full bg-white rounded">
          <div
            className="w-full h-full flex items-center justify-center"
            style={{
              color: style.properties.color || '#000000',
              fontSize: style.properties.fontSize || '16px',
              fontFamily: style.properties.fontFamily || 'sans-serif',
            }}
          >
            {style.properties.text || 'Style Preview'}
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="flex h-full">
      {/* Style List */}
      <div className="w-1/3 border-r p-4">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">Style Guide</h2>
          <button
            onClick={handleCreateStyle}
            className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            New Style
          </button>
        </div>

        <div className="space-y-4">
          {styles.map(style => (
            <div
              key={style.id}
              className={`p-2 border rounded cursor-pointer ${
                selectedStyle?.id === style.id
                  ? 'border-blue-500 bg-blue-50'
                  : 'hover:border-gray-300'
              }`}
              onClick={() => handleEditStyle(style)}
            >
              {renderStylePreview(style)}
            </div>
          ))}
        </div>
      </div>

      {/* Style Editor */}
      <div className="flex-1 p-4">
        {selectedStyle ? (
          <div>
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-lg font-semibold">
                {isCreating ? 'Create Style' : 'Edit Style'}
              </h2>
              {!isCreating && (
                <button
                  onClick={() => handleDeleteStyle(selectedStyle.id)}
                  className="px-3 py-1 bg-red-500 text-white rounded hover:bg-red-600"
                >
                  Delete
                </button>
              )}
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
                  <option value="class">Class</option>
                  <option value="id">ID</option>
                  <option value="element">Element</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Scope</label>
                <select
                  value={editForm.scope || 'global'}
                  onChange={(e) => setEditForm(prev => ({ ...prev, scope: e.target.value }))}
                  className="w-full px-3 py-2 border rounded"
                >
                  <option value="global">Global</option>
                  <option value="component">Component</option>
                  <option value="page">Page</option>
                </select>
              </div>

              {/* Style Properties Editor */}
              <div>
                <label className="block text-sm font-medium mb-1">Properties</label>
                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Background Color</label>
                    <input
                      type="color"
                      value={editForm.properties?.backgroundColor || '#ffffff'}
                      onChange={(e) => setEditForm(prev => ({
                        ...prev,
                        properties: { ...prev.properties, backgroundColor: e.target.value },
                      }))}
                      className="w-full h-8"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Text Color</label>
                    <input
                      type="color"
                      value={editForm.properties?.color || '#000000'}
                      onChange={(e) => setEditForm(prev => ({
                        ...prev,
                        properties: { ...prev.properties, color: e.target.value },
                      }))}
                      className="w-full h-8"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Font Size</label>
                    <input
                      type="text"
                      value={editForm.properties?.fontSize || '16px'}
                      onChange={(e) => setEditForm(prev => ({
                        ...prev,
                        properties: { ...prev.properties, fontSize: e.target.value },
                      }))}
                      className="w-full px-3 py-2 border rounded"
                    />
                  </div>
                  <div>
                    <label className="block text-xs text-gray-500 mb-1">Font Family</label>
                    <input
                      type="text"
                      value={editForm.properties?.fontFamily || 'sans-serif'}
                      onChange={(e) => setEditForm(prev => ({
                        ...prev,
                        properties: { ...prev.properties, fontFamily: e.target.value },
                      }))}
                      className="w-full px-3 py-2 border rounded"
                    />
                  </div>
                </div>
              </div>

              <button
                onClick={handleSaveStyle}
                className="w-full px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600"
              >
                {isCreating ? 'Create Style' : 'Save Changes'}
              </button>
            </div>
          </div>
        ) : (
          <div className="flex items-center justify-center h-full">
            <div className="text-gray-500">Select a style to edit</div>
          </div>
        )}
      </div>
    </div>
  );
}; 