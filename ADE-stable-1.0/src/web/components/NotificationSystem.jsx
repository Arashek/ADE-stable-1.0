import React from 'react';
import { Snackbar, Alert, IconButton, Badge } from '@mui/material';
import { Notifications as NotificationsIcon } from '@mui/icons-material';
import { useGlobal } from '../state/GlobalContext';

const NotificationSystem = () => {
  const { state, dispatch } = useGlobal();
  const [open, setOpen] = React.useState(false);
  const [notifications, setNotifications] = React.useState([]);

  // Handle new notifications
  React.useEffect(() => {
    const handleNewNotification = (event) => {
      const { message, type, action } = event.detail;
      addNotification(message, type, action);
    };

    window.addEventListener('newNotification', handleNewNotification);
    return () => window.removeEventListener('newNotification', handleNewNotification);
  }, []);

  const addNotification = (message, type = 'info', action = null) => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, message, type, action }]);
    setOpen(true);
  };

  const handleClose = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }
    setOpen(false);
  };

  const handleNotificationAction = (action) => {
    if (action) {
      // Handle different action types
      switch (action.type) {
        case 'openFile':
          // Implement file opening logic
          break;
        case 'showError':
          // Implement error display logic
          break;
        case 'runCommand':
          // Implement command execution logic
          break;
        default:
          break;
      }
    }
  };

  const clearNotifications = () => {
    setNotifications([]);
  };

  return (
    <>
      <IconButton
        color="inherit"
        onClick={() => setOpen(true)}
        sx={{ position: 'fixed', top: 16, right: 16, zIndex: 1300 }}
      >
        <Badge badgeContent={notifications.length} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Snackbar
        open={open}
        autoHideDuration={6000}
        onClose={handleClose}
        anchorOrigin={{ vertical: 'top', horizontal: 'right' }}
      >
        <Alert
          onClose={handleClose}
          severity={notifications[0]?.type || 'info'}
          sx={{ width: '100%' }}
          action={
            notifications[0]?.action && (
              <IconButton
                size="small"
                aria-label="close"
                color="inherit"
                onClick={() => handleNotificationAction(notifications[0].action)}
              >
                {notifications[0].action.icon}
              </IconButton>
            )
          }
        >
          {notifications[0]?.message}
        </Alert>
      </Snackbar>
    </>
  );
};

export default NotificationSystem; 