import React from 'react';
import { useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import Paper from '@mui/material/Paper';
import Typography from '@mui/material/Typography';
import IconButton from '@mui/material/IconButton';
import Badge from '@mui/material/Badge';
import { styled } from '@mui/material/styles';
import ExpandMoreIcon from '@mui/icons-material/ExpandMore';
import NotificationsIcon from '@mui/icons-material/Notifications';
import SpeedIcon from '@mui/icons-material/Speed';
import ErrorIcon from '@mui/icons-material/Error';

const MiniViewContainer = styled(Paper)(({ theme }) => ({
  position: 'fixed',
  bottom: theme.spacing(2),
  right: theme.spacing(2),
  width: 300,
  maxHeight: 400,
  display: 'flex',
  flexDirection: 'column',
  zIndex: theme.zIndex.speedDial,
  boxShadow: theme.shadows[4],
}));

const MiniViewHeader = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1),
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'space-between',
  borderBottom: `1px solid ${theme.palette.divider}`,
}));

const MiniViewContent = styled(Box)(({ theme }) => ({
  padding: theme.spacing(1),
  overflow: 'auto',
  flex: 1,
}));

const StatusItem = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(0.5),
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

const MiniView = ({
  notifications,
  agentStatus,
  metrics,
  onExpand,
  onNotificationClick,
}) => {
  const theme = useTheme();

  const getStatusColor = (status) => {
    switch (status) {
      case 'active':
        return theme.palette.success.main;
      case 'error':
        return theme.palette.error.main;
      default:
        return theme.palette.grey[400];
    }
  };

  const getMetricValue = (metric) => {
    if (metric >= 90) return 'High';
    if (metric >= 70) return 'Medium';
    return 'Low';
  };

  const getMetricColor = (metric) => {
    if (metric >= 90) return theme.palette.error.main;
    if (metric >= 70) return theme.palette.warning.main;
    return theme.palette.success.main;
  };

  return (
    <MiniViewContainer>
      <MiniViewHeader>
        <Typography variant="subtitle2">Command Center</Typography>
        <Box>
          <IconButton size="small" onClick={onNotificationClick}>
            <Badge badgeContent={notifications.length} color="error">
              <NotificationsIcon />
            </Badge>
          </IconButton>
          <IconButton size="small" onClick={onExpand}>
            <ExpandMoreIcon />
          </IconButton>
        </Box>
      </MiniViewHeader>

      <MiniViewContent>
        {/* Agent Status Summary */}
        <Typography variant="caption" color="text.secondary" sx={{ px: 1, py: 0.5, display: 'block' }}>
          Agent Status
        </Typography>
        {Object.entries(agentStatus).map(([agent, status]) => (
          <StatusItem key={agent}>
            <Box
              sx={{
                width: 8,
                height: 8,
                borderRadius: '50%',
                backgroundColor: getStatusColor(status),
                mr: 1,
              }}
            />
            <Typography variant="body2" sx={{ flex: 1 }}>
              {agent}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {status}
            </Typography>
          </StatusItem>
        ))}

        {/* System Metrics */}
        <Typography variant="caption" color="text.secondary" sx={{ px: 1, py: 0.5, display: 'block', mt: 1 }}>
          System Metrics
        </Typography>
        {Object.entries(metrics).map(([metric, value]) => (
          <StatusItem key={metric}>
            <SpeedIcon sx={{ mr: 1, color: getMetricColor(value) }} />
            <Typography variant="body2" sx={{ flex: 1 }}>
              {metric}
            </Typography>
            <Typography variant="caption" color="text.secondary">
              {getMetricValue(value)}
            </Typography>
          </StatusItem>
        ))}

        {/* Error Summary */}
        {notifications.filter(n => n.type === 'error').length > 0 && (
          <>
            <Typography variant="caption" color="text.secondary" sx={{ px: 1, py: 0.5, display: 'block', mt: 1 }}>
              Active Errors
            </Typography>
            {notifications
              .filter(n => n.type === 'error')
              .slice(0, 3)
              .map((notification, index) => (
                <StatusItem key={index}>
                  <ErrorIcon sx={{ mr: 1, color: theme.palette.error.main }} />
                  <Typography variant="body2" sx={{ flex: 1 }}>
                    {notification.message}
                  </Typography>
                </StatusItem>
              ))}
          </>
        )}
      </MiniViewContent>
    </MiniViewContainer>
  );
};

export default MiniView; 