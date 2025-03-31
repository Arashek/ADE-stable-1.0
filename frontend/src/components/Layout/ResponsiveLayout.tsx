import React, { useState, useCallback, KeyboardEvent } from 'react';
import {
  Box,
  IconButton,
  useTheme,
  useMediaQuery,
  Drawer,
  SwipeableDrawer,
  Fab,
  Tooltip,
  Collapse,
  Paper,
} from '@mui/material';
import {
  ChevronLeft as ChevronLeftIcon,
  ChevronRight as ChevronRightIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
  Menu as MenuIcon,
} from '@mui/icons-material';

interface ResponsiveLayoutProps {
  leftPanel?: React.ReactNode;
  mainContent: React.ReactNode;
  rightPanel?: React.ReactNode;
  bottomPanel?: React.ReactNode;
  initialLeftWidth?: number;
  initialRightWidth?: number;
  initialBottomHeight?: number;
  minLeftWidth?: number;
  maxLeftWidth?: number;
  minRightWidth?: number;
  maxRightWidth?: number;
  minBottomHeight?: number;
  maxBottomHeight?: number;
}

export const ResponsiveLayout: React.FC<ResponsiveLayoutProps> = ({
  leftPanel,
  mainContent,
  rightPanel,
  bottomPanel,
  initialLeftWidth = 300,
  initialRightWidth = 300,
  initialBottomHeight = 200,
  minLeftWidth = 200,
  maxLeftWidth = 600,
  minRightWidth = 200,
  maxRightWidth = 600,
  minBottomHeight = 100,
  maxBottomHeight = 400,
}) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));

  const [leftWidth, setLeftWidth] = useState(initialLeftWidth);
  const [rightWidth, setRightWidth] = useState(initialRightWidth);
  const [bottomHeight, setBottomHeight] = useState(initialBottomHeight);
  
  const [isLeftOpen, setIsLeftOpen] = useState(!isMobile);
  const [isRightOpen, setIsRightOpen] = useState(!isMobile);
  const [isBottomOpen, setIsBottomOpen] = useState(!isMobile);
  
  const [isResizing, setIsResizing] = useState(false);
  const [resizeType, setResizeType] = useState<'left' | 'right' | 'bottom' | null>(null);
  const [startX, setStartX] = useState(0);
  const [startY, setStartY] = useState(0);
  const [startWidth, setStartWidth] = useState(0);
  const [startHeight, setStartHeight] = useState(0);

  const handleResizeStart = useCallback((
    event: React.MouseEvent | React.TouchEvent,
    type: 'left' | 'right' | 'bottom'
  ) => {
    event.preventDefault();
    setIsResizing(true);
    setResizeType(type);
    
    const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX;
    const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY;
    
    setStartX(clientX);
    setStartY(clientY);
    
    switch (type) {
      case 'left':
        setStartWidth(leftWidth);
        break;
      case 'right':
        setStartWidth(rightWidth);
        break;
      case 'bottom':
        setStartHeight(bottomHeight);
        break;
    }
  }, [leftWidth, rightWidth, bottomHeight]);

  const handleResizeMove = useCallback((event: MouseEvent | TouchEvent) => {
    if (!isResizing) return;

    const clientX = 'touches' in event ? event.touches[0].clientX : event.clientX;
    const clientY = 'touches' in event ? event.touches[0].clientY : event.clientY;

    switch (resizeType) {
      case 'left': {
        const delta = clientX - startX;
        const newWidth = Math.max(
          minLeftWidth,
          Math.min(maxLeftWidth, startWidth + delta)
        );
        setLeftWidth(newWidth);
        break;
      }
      case 'right': {
        const delta = startX - clientX;
        const newWidth = Math.max(
          minRightWidth,
          Math.min(maxRightWidth, startWidth + delta)
        );
        setRightWidth(newWidth);
        break;
      }
      case 'bottom': {
        const delta = startY - clientY;
        const newHeight = Math.max(
          minBottomHeight,
          Math.min(maxBottomHeight, startHeight + delta)
        );
        setBottomHeight(newHeight);
        break;
      }
    }
  }, [
    isResizing,
    resizeType,
    startX,
    startY,
    startWidth,
    startHeight,
    minLeftWidth,
    maxLeftWidth,
    minRightWidth,
    maxRightWidth,
    minBottomHeight,
    maxBottomHeight,
  ]);

  const handleResizeEnd = useCallback(() => {
    setIsResizing(false);
    setResizeType(null);
  }, []);

  const handleKeyDown = useCallback((
    event: KeyboardEvent,
    type: 'left' | 'right' | 'bottom'
  ) => {
    if (event.key === 'Enter' || event.key === ' ') {
      event.preventDefault();
      switch (type) {
        case 'left':
          setIsLeftOpen(!isLeftOpen);
          break;
        case 'right':
          setIsRightOpen(!isRightOpen);
          break;
        case 'bottom':
          setIsBottomOpen(!isBottomOpen);
          break;
      }
    }
  }, [isLeftOpen, isRightOpen, isBottomOpen]);

  React.useEffect(() => {
    if (isResizing) {
      window.addEventListener('mousemove', handleResizeMove);
      window.addEventListener('mouseup', handleResizeEnd);
      window.addEventListener('touchmove', handleResizeMove);
      window.addEventListener('touchend', handleResizeEnd);
    }

    return () => {
      window.removeEventListener('mousemove', handleResizeMove);
      window.removeEventListener('mouseup', handleResizeEnd);
      window.removeEventListener('touchmove', handleResizeMove);
      window.removeEventListener('touchend', handleResizeEnd);
    };
  }, [isResizing, handleResizeMove, handleResizeEnd]);

  const renderMobileDrawer = (
    content: React.ReactNode,
    open: boolean,
    onClose: () => void,
    onOpen: () => void,
    anchor: 'left' | 'right'
  ) => (
    <SwipeableDrawer
      anchor={anchor}
      open={open}
      onClose={onClose}
      onOpen={onOpen}
      swipeAreaWidth={20}
      disableBackdropTransition={!isMobile}
      disableDiscovery={isMobile}
      aria-label={`${anchor} panel`}
      role="complementary"
      sx={{
        '& .MuiDrawer-paper': {
          width: '80%',
          maxWidth: 360,
        },
      }}
    >
      {content}
    </SwipeableDrawer>
  );

  const renderDesktopPanel = (
    content: React.ReactNode,
    width: number,
    isOpen: boolean,
    onResize: (event: React.MouseEvent | React.TouchEvent) => void,
    position: 'left' | 'right'
  ) => (
    <>
      <Paper
        elevation={1}
        role="complementary"
        aria-label={`${position} panel`}
        sx={{
          width: isOpen ? width : 0,
          transition: theme.transitions.create('width', {
            easing: theme.transitions.easing.sharp,
            duration: theme.transitions.duration.enteringScreen,
          }),
          overflow: 'hidden',
          height: '100%',
          position: 'relative',
        }}
      >
        {content}
      </Paper>
      {isOpen && (
        <Box
          role="separator"
          aria-label={`Resize ${position} panel`}
          tabIndex={0}
          sx={{
            width: 8,
            bgcolor: 'divider',
            cursor: 'col-resize',
            transition: theme.transitions.create('background-color'),
            '&:hover': {
              bgcolor: 'primary.main',
            },
            '&:active': {
              bgcolor: 'primary.dark',
            },
            '&:focus': {
              outline: `2px solid ${theme.palette.primary.main}`,
              outlineOffset: -2,
            },
          }}
          onMouseDown={(e) => onResize(e)}
          onTouchStart={(e) => onResize(e)}
          onKeyDown={(e) => handleKeyDown(e, position)}
        />
      )}
    </>
  );

  return (
    <Box
      role="main"
      sx={{
        display: 'flex',
        flexDirection: 'column',
        height: '100vh',
        overflow: 'hidden',
      }}
    >
      <Box
        role="region"
        aria-label="Main content area"
        sx={{
          display: 'flex',
          flex: 1,
          overflow: 'hidden',
        }}
      >
        {isMobile ? (
          leftPanel &&
          renderMobileDrawer(
            leftPanel,
            isLeftOpen,
            () => setIsLeftOpen(false),
            () => setIsLeftOpen(true),
            'left'
          )
        ) : (
          leftPanel &&
          renderDesktopPanel(
            leftPanel,
            leftWidth,
            isLeftOpen,
            (e) => handleResizeStart(e, 'left'),
            'left'
          )
        )}

        <Box
          role="main"
          aria-label="Main content"
          sx={{
            flex: 1,
            overflow: 'hidden',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <Box 
            role="region"
            aria-label="Content area"
            sx={{ flex: 1, overflow: 'auto' }}
          >
            {mainContent}
          </Box>

          {bottomPanel && (
            <>
              <Box
                role="separator"
                aria-label="Resize bottom panel"
                tabIndex={0}
                sx={{
                  height: 8,
                  bgcolor: 'divider',
                  cursor: 'row-resize',
                  transition: theme.transitions.create('background-color'),
                  '&:hover': {
                    bgcolor: 'primary.main',
                  },
                  '&:active': {
                    bgcolor: 'primary.dark',
                  },
                  '&:focus': {
                    outline: `2px solid ${theme.palette.primary.main}`,
                    outlineOffset: -2,
                  },
                }}
                onMouseDown={(e) => handleResizeStart(e, 'bottom')}
                onTouchStart={(e) => handleResizeStart(e, 'bottom')}
                onKeyDown={(e) => handleKeyDown(e, 'bottom')}
              />
              <Collapse in={isBottomOpen}>
                <Paper
                  elevation={1}
                  role="complementary"
                  aria-label="Bottom panel"
                  sx={{
                    height: bottomHeight,
                    overflow: 'hidden',
                  }}
                >
                  {bottomPanel}
                </Paper>
              </Collapse>
            </>
          )}
        </Box>

        {isMobile ? (
          rightPanel &&
          renderMobileDrawer(
            rightPanel,
            isRightOpen,
            () => setIsRightOpen(false),
            () => setIsRightOpen(true),
            'right'
          )
        ) : (
          rightPanel &&
          renderDesktopPanel(
            rightPanel,
            rightWidth,
            isRightOpen,
            (e) => handleResizeStart(e, 'right'),
            'right'
          )
        )}
      </Box>

      {isMobile && (
        <Box
          role="toolbar"
          aria-label="Panel controls"
          sx={{
            position: 'fixed',
            bottom: theme.spacing(2),
            right: theme.spacing(2),
            display: 'flex',
            flexDirection: 'column',
            gap: 1,
          }}
        >
          {bottomPanel && (
            <Tooltip title={isBottomOpen ? 'Hide bottom panel' : 'Show bottom panel'}>
              <Fab
                size="small"
                color="primary"
                onClick={() => setIsBottomOpen(!isBottomOpen)}
                aria-label={isBottomOpen ? 'Hide bottom panel' : 'Show bottom panel'}
                aria-expanded={isBottomOpen}
              >
                {isBottomOpen ? <ExpandMoreIcon /> : <ExpandLessIcon />}
              </Fab>
            </Tooltip>
          )}
          {leftPanel && (
            <Tooltip title={isLeftOpen ? 'Hide left panel' : 'Show left panel'}>
              <Fab
                size="small"
                color="primary"
                onClick={() => setIsLeftOpen(!isLeftOpen)}
                aria-label={isLeftOpen ? 'Hide left panel' : 'Show left panel'}
                aria-expanded={isLeftOpen}
              >
                <MenuIcon />
              </Fab>
            </Tooltip>
          )}
          {rightPanel && (
            <Tooltip title={isRightOpen ? 'Hide right panel' : 'Show right panel'}>
              <Fab
                size="small"
                color="primary"
                onClick={() => setIsRightOpen(!isRightOpen)}
                aria-label={isRightOpen ? 'Hide right panel' : 'Show right panel'}
                aria-expanded={isRightOpen}
              >
                {isRightOpen ? <ChevronRightIcon /> : <ChevronLeftIcon />}
              </Fab>
            </Tooltip>
          )}
        </Box>
      )}
    </Box>
  );
}; 