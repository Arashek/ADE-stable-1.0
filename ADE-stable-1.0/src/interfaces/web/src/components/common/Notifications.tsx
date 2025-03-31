import React, { useEffect, useState } from 'react';
import { Snackbar, Alert } from '@mui/material';
import { notificationService, Notification } from '../../services/notificationService';

const Notifications: React.FC = () => {
  const [notification, setNotification] = useState<Notification | null>(null);
  const [open, setOpen] = useState(false);

  useEffect(() => {
    const subscription = notificationService.onNotification().subscribe((newNotification) => {
      setNotification(newNotification);
      setOpen(true);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const handleClose = () => {
    setOpen(false);
  };

  if (!notification) return null;

  return (
    <Snackbar
      open={open}
      autoHideDuration={notification.duration}
      onClose={handleClose}
      anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
    >
      <Alert
        onClose={handleClose}
        severity={notification.severity}
        variant="filled"
        sx={{ width: '100%' }}
      >
        {notification.message}
      </Alert>
    </Snackbar>
  );
};

export default Notifications; 