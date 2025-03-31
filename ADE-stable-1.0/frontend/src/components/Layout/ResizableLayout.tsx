import React, { useState, useCallback } from 'react';
import { Box, IconButton, useTheme } from '@mui/material';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';

interface ResizableLayoutProps {
  leftPanel: React.ReactNode;
  rightPanel: React.ReactNode;
  initialLeftWidth?: number;
  minLeftWidth?: number;
  maxLeftWidth?: number;
}

const ResizableLayout: React.FC<ResizableLayoutProps> = ({
  leftPanel,
  rightPanel,
  initialLeftWidth = 600,
  minLeftWidth = 300,
  maxLeftWidth = 1200,
}) => {
  const theme = useTheme();
  const [leftWidth, setLeftWidth] = useState(initialLeftWidth);
  const [isResizing, setIsResizing] = useState(false);
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [startX, setStartX] = useState(0);
  const [startWidth, setStartWidth] = useState(0);

  const handleMouseDown = useCallback((e: React.MouseEvent) => {
    setIsResizing(true);
    setStartX(e.clientX);
    setStartWidth(leftWidth);
  }, [leftWidth]);

  const handleMouseMove = useCallback((e: MouseEvent) => {
    if (!isResizing) return;

    const newWidth = startWidth + (e.clientX - startX);
    if (newWidth >= minLeftWidth && newWidth <= maxLeftWidth) {
      setLeftWidth(newWidth);
    }
  }, [isResizing, startX, startWidth, minLeftWidth, maxLeftWidth]);

  const handleMouseUp = useCallback(() => {
    setIsResizing(false);
  }, []);

  React.useEffect(() => {
    if (isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
    }

    return () => {
      document.removeEventListener('mousemove', handleMouseMove);
      document.removeEventListener('mouseup', handleMouseUp);
    };
  }, [isResizing, handleMouseMove, handleMouseUp]);

  const toggleCollapse = () => {
    setIsCollapsed(!isCollapsed);
  };

  return (
    <Box
      sx={{
        display: 'flex',
        width: '100%',
        height: '100%',
        overflow: 'hidden',
        bgcolor: 'background.default',
      }}
    >
      <Box
        sx={{
          width: isCollapsed ? '0px' : `${leftWidth}px`,
          flexShrink: 0,
          transition: isResizing ? 'none' : 'width 0.3s ease',
          overflow: 'hidden',
          position: 'relative',
        }}
      >
        {leftPanel}
      </Box>

      <Box
        sx={{
          width: '8px',
          cursor: 'col-resize',
          backgroundColor: theme.palette.divider,
          '&:hover': {
            backgroundColor: theme.palette.primary.main,
          },
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
        onMouseDown={handleMouseDown}
      >
        <IconButton
          size="small"
          onClick={toggleCollapse}
          sx={{
            position: 'absolute',
            top: '50%',
            transform: 'translateY(-50%)',
            bgcolor: 'background.paper',
            '&:hover': {
              bgcolor: 'action.hover',
            },
          }}
        >
          {isCollapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
        </IconButton>
      </Box>

      <Box
        sx={{
          flexGrow: 1,
          overflow: 'hidden',
        }}
      >
        {rightPanel}
      </Box>
    </Box>
  );
};

export default ResizableLayout; 