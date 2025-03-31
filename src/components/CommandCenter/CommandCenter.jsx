import React, { useState, useEffect, useCallback } from 'react';
import { useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import IconButton from '@mui/material/IconButton';
import Typography from '@mui/material/Typography';
import NotificationsIcon from '@mui/icons-material/Notifications';
import ChevronLeftIcon from '@mui/icons-material/ChevronLeft';
import ChevronRightIcon from '@mui/icons-material/ChevronRight';
import { styled } from '@mui/material/styles';

// Styled components
const CommandCenterContainer = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  height: '100%',
  backgroundColor: theme.palette.background.default,
}));

const Header = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  padding: theme.spacing(1, 2),
  borderBottom: `1px solid ${theme.palette.divider}`,
  backgroundColor: theme.palette.background.paper,
}));

const SplitPanel = styled(Box)(({ theme }) => ({
  display: 'flex',
  flex: 1,
  overflow: 'hidden',
  position: 'relative',
}));

const Panel = styled(Paper)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  overflow: 'hidden',
  backgroundColor: theme.palette.background.paper,
}));

const ResizeHandle = styled(Box)(({ theme }) => ({
  width: theme.spacing(1),
  backgroundColor: theme.palette.divider,
  cursor: 'col-resize',
  '&:hover': {
    backgroundColor: theme.palette.primary.main,
  },
}));

const MiniView = styled(Paper)(({ theme, isCollapsed }) => ({
  position: 'fixed',
  bottom: theme.spacing(2),
  right: theme.spacing(2),
  padding: theme.spacing(1),
  borderRadius: theme.shape.borderRadius,
  backgroundColor: theme.palette.background.paper,
  boxShadow: theme.shadows[3],
  zIndex: theme.zIndex.speedDial,
  transform: isCollapsed ? 'translateY(100%)' : 'translateY(0)',
  transition: theme.transitions.create('transform'),
}));

const CommandCenter = () => {
  const theme = useTheme();
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [leftPanelWidth, setLeftPanelWidth] = useState(300);
  const [isResizing, setIsResizing] = useState(false);
  const [startX, setStartX] = useState(0);
  const [startWidth, setStartWidth] = useState(0);

  // State management
  const [activeConversations, setActiveConversations] = useState([]);
  const [projectContext, setProjectContext] = useState(null);
  const [notifications, setNotifications] = useState([]);

  // Handle panel resizing
  const handleResizeStart = useCallback((e) => {
    setIsResizing(true);
    setStartX(e.clientX);
    setStartWidth(leftPanelWidth);
  }, [leftPanelWidth]);

  const handleResizeEnd = useCallback(() => {
    setIsResizing(false);
  }, []);

  const handleResize = useCallback((e) => {
    if (!isResizing) return;
    
    const diff = e.clientX - startX;
    const newWidth = Math.max(200, Math.min(600, startWidth + diff));
    setLeftPanelWidth(newWidth);
  }, [isResizing, startX, startWidth]);

  // Event listeners for resizing
  useEffect(() => {
    if (isResizing) {
      window.addEventListener('mousemove', handleResize);
      window.addEventListener('mouseup', handleResizeEnd);
    }
    return () => {
      window.removeEventListener('mousemove', handleResize);
      window.removeEventListener('mouseup', handleResizeEnd);
    };
  }, [isResizing, handleResize, handleResizeEnd]);

  // Handle notifications
  const handleNotificationClick = useCallback(() => {
    setIsCollapsed(false);
    // Additional notification handling logic
  }, []);

  return (
    <CommandCenterContainer>
      <Header>
        <Typography variant="h6">Command Center</Typography>
        <Box>
          <IconButton onClick={handleNotificationClick}>
            <NotificationsIcon />
            {notifications.length > 0 && (
              <Box
                sx={{
                  position: 'absolute',
                  top: 0,
                  right: 0,
                  width: 8,
                  height: 8,
                  borderRadius: '50%',
                  backgroundColor: 'error.main',
                }}
              />
            )}
          </IconButton>
          <IconButton onClick={() => setIsCollapsed(!isCollapsed)}>
            {isCollapsed ? <ChevronRightIcon /> : <ChevronLeftIcon />}
          </IconButton>
        </Box>
      </Header>

      {!isCollapsed && (
        <SplitPanel>
          <Panel sx={{ width: leftPanelWidth }}>
            {/* Left panel content */}
          </Panel>
          <ResizeHandle
            onMouseDown={handleResizeStart}
            sx={{ cursor: isResizing ? 'col-resize' : 'default' }}
          />
          <Panel sx={{ flex: 1 }}>
            {/* Right panel content */}
          </Panel>
        </SplitPanel>
      )}

      <MiniView isCollapsed={isCollapsed}>
        <Typography variant="body2">Command Center</Typography>
        {notifications.length > 0 && (
          <Box
            sx={{
              position: 'absolute',
              top: -4,
              right: -4,
              width: 8,
              height: 8,
              borderRadius: '50%',
              backgroundColor: 'error.main',
            }}
          />
        )}
      </MiniView>
    </CommandCenterContainer>
  );
};

export default CommandCenter; 