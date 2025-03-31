import React, { useState } from 'react';
import { DesignPage, DesignSystem } from '../../types/design';

interface PageNavigatorProps {
  pages: DesignPage[];
  currentPage: string;
  onPageChange: (pageId: string) => void;
  onDesignUpdate: (design: Partial<DesignSystem>) => void;
}

export const PageNavigator: React.FC<PageNavigatorProps> = ({
  pages,
  currentPage,
  onPageChange,
  onDesignUpdate,
}) => {
  const [isAddingPage, setIsAddingPage] = useState(false);
  const [newPageName, setNewPageName] = useState('');
  const [newPagePath, setNewPagePath] = useState('');

  const handleAddPage = () => {
    if (!newPageName.trim() || !newPagePath.trim()) return;

    const newPage: DesignPage = {
      id: `page-${Date.now()}`,
      name: newPageName,
      path: newPagePath,
      components: [],
      styles: [],
      layout: {
        type: 'default',
        properties: {},
      },
    };

    onDesignUpdate({
      pages: [...pages, newPage],
    });

    setIsAddingPage(false);
    setNewPageName('');
    setNewPagePath('');
  };

  const handleDeletePage = (pageId: string) => {
    if (pageId === 'home') return; // Prevent deleting home page

    onDesignUpdate({
      pages: pages.filter(p => p.id !== pageId),
    });

    if (currentPage === pageId) {
      onPageChange('home');
    }
  };

  const handleDuplicatePage = (page: DesignPage) => {
    const newPage: DesignPage = {
      ...page,
      id: `page-${Date.now()}`,
      name: `${page.name} (Copy)`,
      path: `${page.path}-copy`,
    };

    onDesignUpdate({
      pages: [...pages, newPage],
    });
  };

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold">Pages</h2>
        <button
          onClick={() => setIsAddingPage(true)}
          className="px-3 py-1 bg-blue-500 text-white rounded hover:bg-blue-600"
        >
          Add Page
        </button>
      </div>

      {isAddingPage && (
        <div className="mb-4 p-4 border rounded">
          <h3 className="text-md font-medium mb-2">New Page</h3>
          <div className="space-y-2">
            <input
              type="text"
              placeholder="Page Name"
              value={newPageName}
              onChange={(e) => setNewPageName(e.target.value)}
              className="w-full px-3 py-2 border rounded"
            />
            <input
              type="text"
              placeholder="Page Path"
              value={newPagePath}
              onChange={(e) => setNewPagePath(e.target.value)}
              className="w-full px-3 py-2 border rounded"
            />
            <div className="flex gap-2">
              <button
                onClick={handleAddPage}
                className="px-3 py-1 bg-green-500 text-white rounded hover:bg-green-600"
              >
                Create
              </button>
              <button
                onClick={() => setIsAddingPage(false)}
                className="px-3 py-1 bg-gray-500 text-white rounded hover:bg-gray-600"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="space-y-2">
        {pages.map((page) => (
          <div
            key={page.id}
            className={`p-3 border rounded flex justify-between items-center ${
              currentPage === page.id ? 'bg-blue-50 border-blue-500' : ''
            }`}
          >
            <div className="flex items-center gap-2">
              <button
                onClick={() => onPageChange(page.id)}
                className="text-left hover:text-blue-500"
              >
                {page.name}
              </button>
              <span className="text-sm text-gray-500">({page.path})</span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => handleDuplicatePage(page)}
                className="px-2 py-1 text-sm bg-gray-100 rounded hover:bg-gray-200"
              >
                Duplicate
              </button>
              {page.id !== 'home' && (
                <button
                  onClick={() => handleDeletePage(page.id)}
                  className="px-2 py-1 text-sm bg-red-100 text-red-600 rounded hover:bg-red-200"
                >
                  Delete
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}; 