import React, { useState, useRef, useEffect } from 'react';
import { DesignSystem, DesignComponent, DesignStyle, DesignPage } from '../../types/design';

interface DesignCanvasProps {
  currentDesign: DesignSystem;
  onDesignUpdate: (design: Partial<DesignSystem>) => void;
  onComponentSelect: (component: DesignComponent) => void;
  onStyleSelect: (style: DesignStyle) => void;
}

export const DesignCanvas: React.FC<DesignCanvasProps> = ({
  currentDesign,
  onDesignUpdate,
  onComponentSelect,
  onStyleSelect,
}) => {
  const canvasRef = useRef<HTMLDivElement>(null);
  const [scale, setScale] = useState(1);
  const [isDragging, setIsDragging] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [position, setPosition] = useState({ x: 0, y: 0 });
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null);

  const currentPage = currentDesign.pages?.find(p => p.id === currentDesign.currentPage);
  const pageComponents = currentPage?.components
    .map(id => currentDesign.components?.find(c => c.id === id))
    .filter((c): c is DesignComponent => c !== undefined);

  const handleMouseDown = (e: React.MouseEvent) => {
    if (e.button === 2) { // Middle click
      setIsDragging(true);
      setDragStart({ x: e.clientX - position.x, y: e.clientY - position.y });
    }
  };

  const handleMouseMove = (e: React.MouseEvent) => {
    if (isDragging) {
      setPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y,
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  const handleWheel = (e: React.WheelEvent) => {
    if (e.ctrlKey) {
      e.preventDefault();
      const delta = e.deltaY > 0 ? 0.9 : 1.1;
      setScale(prev => Math.min(Math.max(prev * delta, 0.1), 3));
    }
  };

  const handleComponentClick = (component: DesignComponent) => {
    setSelectedComponent(component.id);
    onComponentSelect(component);
  };

  const handleStyleClick = (style: DesignStyle) => {
    onStyleSelect(style);
  };

  const renderComponent = (component: DesignComponent) => {
    const isSelected = selectedComponent === component.id;
    const componentStyles = {
      ...component.styles,
      position: 'absolute',
      left: `${component.properties.x || 0}px`,
      top: `${component.properties.y || 0}px`,
      width: `${component.properties.width || 100}px`,
      height: `${component.properties.height || 100}px`,
      cursor: 'pointer',
      outline: isSelected ? '2px solid #3b82f6' : 'none',
    };

    switch (component.type) {
      case 'rectangle':
        return (
          <div
            key={component.id}
            style={componentStyles}
            onClick={() => handleComponentClick(component)}
          />
        );
      case 'text':
        return (
          <div
            key={component.id}
            style={componentStyles}
            onClick={() => handleComponentClick(component)}
          >
            {component.properties.text || 'Text'}
          </div>
        );
      case 'image':
        return (
          <div
            key={component.id}
            style={componentStyles}
            onClick={() => handleComponentClick(component)}
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
            onClick={() => handleComponentClick(component)}
          >
            {component.properties.text || 'Button'}
          </button>
        );
      default:
        return null;
    }
  };

  return (
    <div
      ref={canvasRef}
      className="flex-1 bg-gray-100 overflow-hidden"
      onMouseDown={handleMouseDown}
      onMouseMove={handleMouseMove}
      onMouseUp={handleMouseUp}
      onMouseLeave={handleMouseUp}
      onWheel={handleWheel}
    >
      {currentPage ? (
        <div
          className="relative bg-white shadow-lg"
          style={{
            transform: `scale(${scale}) translate(${position.x}px, ${position.y}px)`,
            transformOrigin: '0 0',
            width: `${currentPage.properties.width || 1920}px`,
            height: `${currentPage.properties.height || 1080}px`,
            margin: '20px',
          }}
        >
          {/* Page Background */}
          <div
            className="absolute inset-0"
            style={{
              backgroundColor: currentPage.properties.backgroundColor || '#ffffff',
            }}
          />

          {/* Components */}
          {pageComponents?.map(renderComponent)}

          {/* Grid Overlay */}
          <div
            className="absolute inset-0 pointer-events-none"
            style={{
              backgroundImage: 'linear-gradient(to right, #e5e7eb 1px, transparent 1px), linear-gradient(to bottom, #e5e7eb 1px, transparent 1px)',
              backgroundSize: '20px 20px',
              opacity: 0.5,
            }}
          />
        </div>
      ) : (
        <div className="flex items-center justify-center h-full">
          <div className="text-gray-500">Select a page to start designing</div>
        </div>
      )}
    </div>
  );
}; 