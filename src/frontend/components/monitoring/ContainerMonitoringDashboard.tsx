import React, { useEffect, useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  LinearProgress,
  Chip,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  IconButton,
  Tooltip,
  Divider,
  Alert,
  AlertTitle
} from '@mui/material';
import {
  Memory,
  Storage,
  Speed,
  Assessment,
  Warning,
  CheckCircle,
  Error,
  Info,
  Refresh
} from '@mui/icons-material';
import { ContainerMetrics, HealthStatus, Alert as AlertType } from '../../../core/monitoring/types';

interface ContainerMonitoringDashboardProps {
  containerId: string;
  metrics: ContainerMetrics;
  healthStatus: HealthStatus;
  alerts: AlertType[];
  onRefresh: () => void;
  onResolveAlert: (alertId: string) => void;
}

const MetricCard: React.FC<{
  title: string;
  value: number;
  unit: string;
  icon: React.ReactNode;
  color: 'primary' | 'secondary' | 'error' | 'success';
}> = ({ title, value, unit, icon, color }) => (
  <Card>
    <CardContent>
      <Box display="flex" alignItems="center" mb={2}>
        <Box color={`${color}.main`} mr={1}>
          {icon}
        </Box>
        <Typography variant="h6">{title}</Typography>
      </Box>
      <Typography variant="h4" component="div">
        {value.toFixed(1)} {unit}
      </Typography>
      <LinearProgress
        variant="determinate"
        value={value}
        color={color}
        sx={{ mt: 1, height: 8, borderRadius: 4 }}
      />
    </CardContent>
  </Card>
);

const AlertCard: React.FC<{
  alert: AlertType;
  onResolve: (id: string) => void;
}> = ({ alert, onResolve }) => {
  const getSeverityColor = (severity: AlertType['severity']) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const getSeverityIcon = (severity: AlertType['severity']) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <Error color="error" />;
      case 'medium':
        return <Warning color="warning" />;
      case 'low':
        return <Info color="info" />;
      default:
        return <Info />;
    }
  };

  return (
    <Alert
      severity={getSeverityColor(alert.severity)}
      action={
        !alert.resolved && (
          <IconButton
            aria-label="resolve"
            color="inherit"
            size="small"
            onClick={() => onResolve(alert.id)}
          >
            <CheckCircle />
          </IconButton>
        )
      }
      sx={{ mb: 2 }}
    >
      <AlertTitle>
        <Box display="flex" alignItems="center">
          {getSeverityIcon(alert.severity)}
          <Typography variant="subtitle1" sx={{ ml: 1 }}>
            {alert.title}
          </Typography>
        </Box>
      </AlertTitle>
      <Typography variant="body2">{alert.message}</Typography>
      {alert.metadata && (
        <Typography variant="caption" color="text.secondary">
          {JSON.stringify(alert.metadata)}
        </Typography>
      )}
    </Alert>
  );
};

export const ContainerMonitoringDashboard: React.FC<ContainerMonitoringDashboardProps> = ({
  containerId,
  metrics,
  healthStatus,
  alerts,
  onRefresh,
  onResolveAlert
}) => {
  const [autoRefresh, setAutoRefresh] = useState(true);

  useEffect(() => {
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(onRefresh, 30000); // Refresh every 30 seconds
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, onRefresh]);

  return (
    <Box>
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4">Container Monitoring</Typography>
        <Box>
          <Tooltip title={autoRefresh ? 'Auto-refresh enabled' : 'Auto-refresh disabled'}>
            <IconButton onClick={() => setAutoRefresh(!autoRefresh)}>
              <Refresh className={autoRefresh ? 'rotating' : ''} />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      <Grid container spacing={3}>
        {/* Health Status */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Assessment sx={{ mr: 1 }} />
                <Typography variant="h6">Health Status</Typography>
              </Box>
              <Box display="flex" alignItems="center" gap={2}>
                <Chip
                  label={healthStatus.status.toUpperCase()}
                  color={
                    healthStatus.status === 'healthy'
                      ? 'success'
                      : healthStatus.status === 'unhealthy'
                      ? 'error'
                      : 'warning'
                  }
                />
                <Typography variant="body2" color="text.secondary">
                  Last Updated: {healthStatus.lastUpdated.toLocaleString()}
                </Typography>
              </Box>
              <List>
                {Object.entries(healthStatus.checks).map(([name, check]) => (
                  <React.Fragment key={name}>
                    <ListItem>
                      <ListItemIcon>
                        {check.status === 'pass' ? (
                          <CheckCircle color="success" />
                        ) : check.status === 'fail' ? (
                          <Error color="error" />
                        ) : (
                          <Info color="info" />
                        )}
                      </ListItemIcon>
                      <ListItemText
                        primary={name}
                        secondary={
                          check.status === 'fail'
                            ? `Last Error: ${check.lastError}`
                            : `Last Check: ${check.lastCheck.toLocaleString()}`
                        }
                      />
                    </ListItem>
                    <Divider />
                  </React.Fragment>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Metrics */}
        <Grid item xs={12} md={3}>
          <MetricCard
            title="CPU Usage"
            value={metrics.cpu.usage}
            unit="%"
            icon={<Speed />}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Memory Usage"
            value={metrics.memory.usage}
            unit="%"
            icon={<Memory />}
            color="secondary"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Disk Usage"
            value={metrics.disk.usage}
            unit="%"
            icon={<Storage />}
            color="error"
          />
        </Grid>
        <Grid item xs={12} md={3}>
          <MetricCard
            title="Network I/O"
            value={(metrics.network.rxBytes + metrics.network.txBytes) / 1024 / 1024}
            unit="MB/s"
            icon={<Speed />}
            color="success"
          />
        </Grid>

        {/* Alerts */}
        <Grid item xs={12}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Warning sx={{ mr: 1 }} />
                <Typography variant="h6">Active Alerts</Typography>
              </Box>
              {alerts.filter(alert => !alert.resolved).length === 0 ? (
                <Typography color="text.secondary">No active alerts</Typography>
              ) : (
                alerts
                  .filter(alert => !alert.resolved)
                  .map(alert => (
                    <AlertCard
                      key={alert.id}
                      alert={alert}
                      onResolve={onResolveAlert}
                    />
                  ))
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <style jsx>{`
        .rotating {
          animation: rotate 1s linear infinite;
        }

        @keyframes rotate {
          from {
            transform: rotate(0deg);
          }
          to {
            transform: rotate(360deg);
          }
        }
      `}</style>
    </Box>
  );
}; 