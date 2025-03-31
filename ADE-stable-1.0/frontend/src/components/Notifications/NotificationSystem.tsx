import React, { useState, useEffect } from 'react';
import {
  Box,
  Badge,
  IconButton,
  Popover,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Typography,
  Button,
  Divider,
  Snackbar,
  Alert,
} from '@mui/material';
import {
  Notifications as NotificationsIcon,
  Code as CodeIcon,
  Comment as CommentIcon,
  PullRequest as PullRequestIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Build as BuildIcon,
  Security as SecurityIcon,
} from '@mui/icons-material';

export interface Notification {
  id: string;
  type: 'pr_review' | 'comment' | 'mention' | 'build' | 'security' | 'system';
  title: string;
  message: string;
  timestamp: string;
  read: boolean;
  actionUrl?: string;
  metadata?: {
    pullRequestId?: string;
    commentId?: string;
    buildId?: string;
    severity?: 'info' | 'warning' | 'error';
  };
}

interface NotificationSystemProps {
  notifications: Notification[];
  onMarkAsRead: (notificationId: string) => void;
  onMarkAllAsRead: () => void;
  onNotificationClick: (notification: Notification) => void;
  onDismiss: (notificationId: string) => void;
}

const NotificationSystem: React.FC<NotificationSystemProps> = ({
  notifications,
  onMarkAsRead,
  onMarkAllAsRead,
  onNotificationClick,
  onDismiss,
}) => {
  const [anchorEl, setAnchorEl] = useState<HTMLElement | null>(null);
  const [showSnackbar, setShowSnackbar] = useState(false);
  const [currentSnackbar, setCurrentSnackbar] = useState<Notification | null>(null);

  const unreadCount = notifications.filter((n) => !n.read).length;

  useEffect(() => {
    // Show snackbar for new notifications
    const latestUnread = notifications.find((n) => !n.read);
    if (latestUnread && (!currentSnackbar || latestUnread.id !== currentSnackbar.id)) {
      setCurrentSnackbar(latestUnread);
      setShowSnackbar(true);
    }
  }, [notifications]);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleNotificationClick = (notification: Notification) => {
    onNotificationClick(notification);
    onMarkAsRead(notification.id);
    handleClose();
  };

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'pr_review':
        return <PullRequestIcon color="primary" />;
      case 'comment':
        return <CommentIcon color="info" />;
      case 'build':
        return <BuildIcon color="warning" />;
      case 'security':
        return <SecurityIcon color="error" />;
      case 'mention':
        return <CodeIcon color="secondary" />;
      default:
        return <NotificationsIcon />;
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);

    if (minutes < 60) {
      return `${minutes}m ago`;
    } else if (hours < 24) {
      return `${hours}h ago`;
    } else if (days < 7) {
      return `${days}d ago`;
    } else {
      return date.toLocaleDateString();
    }
  };

  const open = Boolean(anchorEl);
  const id = open ? 'notifications-popover' : undefined;

  return (
    <>
      <IconButton
        aria-describedby={id}
        onClick={handleClick}
        sx={{ position: 'relative' }}
      >
        <Badge badgeContent={unreadCount} color="error">
          <NotificationsIcon />
        </Badge>
      </IconButton>

      <Popover
        id={id}
        open={open}
        anchorEl={anchorEl}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <Box sx={{ width: 360 }}>
          <Box
            sx={{
              p: 2,
              display: 'flex',
              justifyContent: 'space-between',
              alignItems: 'center',
              borderBottom: 1,
              borderColor: 'divider',
            }}
          >
            <Typography variant="h6">Notifications</Typography>
            {unreadCount > 0 && (
              <Button size="small" onClick={onMarkAllAsRead}>
                Mark all as read
              </Button>
            )}
          </Box>

          <List sx={{ maxHeight: 400, overflow: 'auto' }}>
            {notifications.length === 0 ? (
              <ListItem>
                <ListItemText
                  primary="No notifications"
                  secondary="You're all caught up!"
                />
              </ListItem>
            ) : (
              notifications.map((notification, index) => (
                <React.Fragment key={notification.id}>
                  {index > 0 && <Divider />}
                  <ListItem
                    button
                    onClick={() => handleNotificationClick(notification)}
                    sx={{
                      backgroundColor: notification.read
                        ? 'transparent'
                        : 'action.hover',
                    }}
                  >
                    <ListItemIcon>
                      {getNotificationIcon(notification.type)}
                    </ListItemIcon>
                    <ListItemText
                      primary={notification.title}
                      secondary={
                        <Box
                          component="span"
                          sx={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            alignItems: 'center',
                          }}
                        >
                          <Typography
                            variant="body2"
                            color="text.secondary"
                            sx={{
                              overflow: 'hidden',
                              textOverflow: 'ellipsis',
                              whiteSpace: 'nowrap',
                            }}
                          >
                            {notification.message}
                          </Typography>
                          <Typography
                            variant="caption"
                            color="text.secondary"
                            sx={{ ml: 1, flexShrink: 0 }}
                          >
                            {formatTimestamp(notification.timestamp)}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                </React.Fragment>
              ))
            )}
          </List>
        </Box>
      </Popover>

      <Snackbar
        open={showSnackbar}
        autoHideDuration={6000}
        onClose={() => setShowSnackbar(false)}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'right' }}
      >
        {currentSnackbar && (
          <Alert
            severity={currentSnackbar.metadata?.severity || 'info'}
            onClose={() => setShowSnackbar(false)}
            action={
              <Button
                color="inherit"
                size="small"
                onClick={() => {
                  handleNotificationClick(currentSnackbar);
                  setShowSnackbar(false);
                }}
              >
                View
              </Button>
            }
          >
            <Typography variant="subtitle2">{currentSnackbar.title}</Typography>
            <Typography variant="body2">{currentSnackbar.message}</Typography>
          </Alert>
        )}
      </Snackbar>
    </>
  );
};

export default NotificationSystem; 