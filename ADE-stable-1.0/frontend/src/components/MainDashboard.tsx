import React, { useState, useEffect } from 'react';
import { Box } from '@mui/material';
import { LayoutToggle, LayoutType } from './LayoutToggle';
import { LayoutComponents } from './layouts/LayoutComponents';
import { WebIDE } from './WebIDE';

interface MainDashboardProps {
  projectId: string;
}

export const MainDashboard: React.FC<MainDashboardProps> = ({ projectId }) => {
  const [currentLayout, setCurrentLayout] = useState<LayoutType>(() => {
    const savedLayout = localStorage.getItem('preferredLayout');
    return (savedLayout as LayoutType) || 'grid-matrix';
  });

  useEffect(() => {
    localStorage.setItem('preferredLayout', currentLayout);
  }, [currentLayout]);

  const handleLayoutChange = (newLayout: LayoutType) => {
    setCurrentLayout(newLayout);
  };

  return (
    <Box sx={{ height: '100vh', overflow: 'hidden' }}>
      <LayoutToggle
        currentLayout={currentLayout}
        onLayoutChange={handleLayoutChange}
      />
      <LayoutComponents layout={currentLayout}>
        <WebIDE projectId={projectId} />
      </LayoutComponents>
    </Box>
  );
}; 