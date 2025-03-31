import React, { useEffect, useState } from 'react';
import {
  Box,
  Paper,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip,
  CircularProgress,
  Alert,
  Divider,
  Button,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
} from '@mui/material';
import {
  Security,
  Error,
  Warning,
  Info,
  Shield,
  Lock,
  NetworkCheck,
  Storage,
  Speed,
  Timeline,
  Assessment,
} from '@mui/icons-material';
import { SecurityAlert, SecurityPattern } from '../../../core/models/project/SecurityEventCorrelator';
import { SecurityEvent } from '../../../core/models/project/SecurityAuditLogger';

interface SecurityAlertsDashboardProps {
  alerts: SecurityAlert[];
  patterns: SecurityPattern[];
  events: SecurityEvent[];
  onClearAlerts: () => void;
  onDismissAlert: (alertId: string) => void;
}

const severityColors = {
  critical: 'error',
  high: 'error',
  medium: 'warning',
  low: 'info',
} as const;

const severityIcons = {
  critical: <Error color="error" />,
  high: <Error color="error" />,
  medium: <Warning color="warning" />,
  low: <Info color="info" />,
} as const;

export const SecurityAlertsDashboard: React.FC<SecurityAlertsDashboardProps> = ({
  alerts,
  patterns,
  events,
  onClearAlerts,
  onDismissAlert,
}) => {
  const [selectedAlert, setSelectedAlert] = useState<SecurityAlert | null>(null);
  const [alertDialogOpen, setAlertDialogOpen] = useState(false);
  const [filteredAlerts, setFilteredAlerts] = useState<SecurityAlert[]>(alerts);

  useEffect(() => {
    setFilteredAlerts(alerts);
  }, [alerts]);

  const handleAlertClick = (alert: SecurityAlert) => {
    setSelectedAlert(alert);
    setAlertDialogOpen(true);
  };

  const handleDialogClose = () => {
    setAlertDialogOpen(false);
    setSelectedAlert(null);
  };

  const handleDismissAlert = () => {
    if (selectedAlert) {
      onDismissAlert(selectedAlert.id);
      handleDialogClose();
    }
  };

  const getAlertSummary = () => {
    const total = alerts.length;
    const critical = alerts.filter(a => a.severity === 'critical').length;
    const high = alerts.filter(a => a.severity === 'high').length;
    const medium = alerts.filter(a => a.severity === 'medium').length;
    const low = alerts.filter(a => a.severity === 'low').length;

    return {
      total,
      critical,
      high,
      medium,
      low,
    };
  };

  const getPatternSummary = () => {
    return patterns.map(pattern => ({
      ...pattern,
      alertCount: alerts.filter(a => a.patternId === pattern.id).length,
    }));
  };

  const getRecentEvents = () => {
    return events
      .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime())
      .slice(0, 5);
  };

  const summary = getAlertSummary();
  const patternSummary = getPatternSummary();
  const recentEvents = getRecentEvents();

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom>
        Security Alerts Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Alert Summary */}
        <Grid item xs={12} md={4}>
          <Card>
            <CardContent>
              <Box display="flex" alignItems="center" mb={2}>
                <Shield sx={{ fontSize: 40, mr: 2, color: 'primary.main' }} />
                <Box>
                  <Typography variant="h6">Alert Summary</Typography>
                  <Typography variant="h3" color="primary">
                    {summary.total}
                  </Typography>
                </Box>
              </Box>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="h4" color="error">
                    {summary.critical}
                  </Typography>
                  <Typography variant="body2">Critical</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h4" color="error">
                    {summary.high}
                  </Typography>
                  <Typography variant="body2">High</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h4" color="warning">
                    {summary.medium}
                  </Typography>
                  <Typography variant="body2">Medium</Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="h4" color="info">
                    {summary.low}
                  </Typography>
                  <Typography variant="body2">Low</Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Pattern Summary */}
        <Grid item xs={12} md={8}>
          <Card>
            <CardHeader title="Security Patterns" />
            <CardContent>
              <List>
                {patternSummary.map((pattern) => (
                  <React.Fragment key={pattern.id}>
                    <ListItem>
                      <ListItemIcon>
                        {severityIcons[pattern.severity]}
                      </ListItemIcon>
                      <ListItemText
                        primary={pattern.name}
                        secondary={
                          <Box display="flex" alignItems="center" mt={1}>
                            <Chip
                              label={`${pattern.alertCount} alerts`}
                              color={pattern.alertCount > 0 ? severityColors[pattern.severity] : 'default'}
                              size="small"
                              sx={{ mr: 1 }}
                            />
                            <Typography variant="caption" color="text.secondary">
                              {pattern.description}
                            </Typography>
                          </Box>
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

        {/* Recent Alerts */}
        <Grid item xs={12}>
          <Card>
            <CardHeader
              title="Recent Alerts"
              action={
                <Button
                  variant="outlined"
                  color="primary"
                  onClick={onClearAlerts}
                >
                  Clear All
                </Button>
              }
            />
            <CardContent>
              <List>
                {filteredAlerts.map((alert) => (
                  <React.Fragment key={alert.id}>
                    <ListItem
                      button
                      onClick={() => handleAlertClick(alert)}
                    >
                      <ListItemIcon>
                        {severityIcons[alert.severity]}
                      </ListItemIcon>
                      <ListItemText
                        primary={alert.description}
                        secondary={
                          <Box display="flex" alignItems="center" mt={1}>
                            <Chip
                              label={alert.severity}
                              color={severityColors[alert.severity]}
                              size="small"
                              sx={{ mr: 1 }}
                            />
                            <Typography variant="caption" color="text.secondary">
                              {new Date(alert.timestamp).toLocaleString()}
                            </Typography>
                          </Box>
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

        {/* Recent Events */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Recent Security Events" />
            <CardContent>
              <List>
                {recentEvents.map((event) => (
                  <React.Fragment key={`${event.timestamp}-${event.eventType}`}>
                    <ListItem>
                      <ListItemIcon>
                        {severityIcons[event.severity]}
                      </ListItemIcon>
                      <ListItemText
                        primary={event.action}
                        secondary={
                          <Box display="flex" alignItems="center" mt={1}>
                            <Chip
                              label={event.eventType}
                              size="small"
                              sx={{ mr: 1 }}
                            />
                            <Typography variant="caption" color="text.secondary">
                              {new Date(event.timestamp).toLocaleString()}
                            </Typography>
                          </Box>
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
      </Grid>

      {/* Alert Details Dialog */}
      <Dialog
        open={alertDialogOpen}
        onClose={handleDialogClose}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box display="flex" alignItems="center">
            {selectedAlert && severityIcons[selectedAlert.severity]}
            <Typography variant="h6" sx={{ ml: 1 }}>
              {selectedAlert?.description}
            </Typography>
          </Box>
        </DialogTitle>
        <DialogContent>
          {selectedAlert && (
            <Box>
              <Typography variant="subtitle1" gutterBottom>
                Details
              </Typography>
              <Typography variant="body2" paragraph>
                {selectedAlert.description}
              </Typography>
              <Typography variant="subtitle1" gutterBottom>
                Recommendations
              </Typography>
              <List>
                {selectedAlert.recommendations.map((rec, index) => (
                  <ListItem key={index}>
                    <ListItemIcon>
                      <Assessment color="primary" />
                    </ListItemIcon>
                    <ListItemText primary={rec} />
                  </ListItem>
                ))}
              </List>
              <Typography variant="subtitle1" gutterBottom>
                Related Events
              </Typography>
              <List>
                {selectedAlert.events.map((event) => (
                  <ListItem key={event.id}>
                    <ListItemIcon>
                      {severityIcons[event.severity]}
                    </ListItemIcon>
                    <ListItemText
                      primary={event.action}
                      secondary={
                        <Box display="flex" alignItems="center" mt={1}>
                          <Chip
                            label={event.eventType}
                            size="small"
                            sx={{ mr: 1 }}
                          />
                          <Typography variant="caption" color="text.secondary">
                            {new Date(event.timestamp).toLocaleString()}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={handleDialogClose}>Close</Button>
          <Button onClick={handleDismissAlert} color="primary">
            Dismiss Alert
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}; 