import React from 'react';
import {
  Box,
  Typography,
  Grid,
  Card,
  CardContent,
  CardHeader,
  List,
  ListItem,
  ListItemText,
  Divider,
  TextField,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Alert,
  Switch,
  FormControlLabel
} from '@mui/material';
import { BackupSpec } from '../../../../core/models/agent/types';

interface BackupStrategyProps {
  backup: BackupSpec;
  onUpdate: (updates: { backupStrategy: Partial<BackupSpec> }) => void;
}

export const BackupStrategy: React.FC<BackupStrategyProps> = ({
  backup,
  onUpdate
}) => {
  const handleBackupUpdate = (updates: Partial<BackupSpec>) => {
    onUpdate({
      backupStrategy: {
        ...backup,
        ...updates
      }
    });
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Backup Strategy
      </Typography>

      <Grid container spacing={3}>
        {/* Backup Schedule */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Backup Schedule" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Configure your backup schedule:
              </Typography>
              <FormControl fullWidth sx={{ mb: 2 }}>
                <InputLabel>Frequency</InputLabel>
                <Select
                  label="Frequency"
                  defaultValue={backup.schedule.frequency}
                  onChange={(e) => handleBackupUpdate({
                    schedule: {
                      ...backup.schedule,
                      frequency: e.target.value as 'hourly' | 'daily' | 'weekly' | 'monthly'
                    }
                  })}
                >
                  <MenuItem value="hourly">Hourly</MenuItem>
                  <MenuItem value="daily">Daily</MenuItem>
                  <MenuItem value="weekly">Weekly</MenuItem>
                  <MenuItem value="monthly">Monthly</MenuItem>
                </Select>
              </FormControl>
              <TextField
                fullWidth
                label="Time"
                type="time"
                InputLabelProps={{ shrink: true }}
                onChange={(e) => handleBackupUpdate({
                  schedule: {
                    ...backup.schedule,
                    time: e.target.value
                  }
                })}
              />
              <Alert severity="info" sx={{ mt: 2 }}>
                More frequent backups provide better data protection but require more storage
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* Retention Policy */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Retention Policy" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Set your backup retention policy:
              </Typography>
              <TextField
                fullWidth
                label="Retention Period (days)"
                type="number"
                defaultValue={backup.retention.period}
                onChange={(e) => handleBackupUpdate({
                  retention: {
                    ...backup.retention,
                    period: parseInt(e.target.value)
                  }
                })}
                sx={{ mb: 2 }}
              />
              <FormControlLabel
                control={
                  <Switch
                    checked={backup.retention.keepLatest}
                    onChange={(e) => handleBackupUpdate({
                      retention: {
                        ...backup.retention,
                        keepLatest: e.target.checked
                      }
                    })}
                  />
                }
                label="Always keep latest backup"
              />
              <Alert severity="info" sx={{ mt: 2 }}>
                Longer retention periods require more storage space
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* Backup Locations */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Backup Locations" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Configure backup storage locations:
              </Typography>
              <List>
                {backup.locations.map((location) => (
                  <React.Fragment key={location.type}>
                    <ListItem>
                      <ListItemText
                        primary={`${location.type} Storage`}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Provider: {location.provider}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Region: {location.region}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Encryption: {location.encryption ? 'Enabled' : 'Disabled'}
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

        {/* Recovery Options */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Recovery Options" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Configure recovery settings:
              </Typography>
              <List>
                {backup.recovery.map((option) => (
                  <React.Fragment key={option.type}>
                    <ListItem>
                      <ListItemText
                        primary={`${option.type} Recovery`}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Description: {option.description}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Time Estimate: {option.timeEstimate}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Priority: {option.priority}
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

        {/* Monitoring and Alerts */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Monitoring and Alerts" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Configure backup monitoring:
              </Typography>
              <FormControlLabel
                control={
                  <Switch
                    checked={backup.monitoring.enabled}
                    onChange={(e) => handleBackupUpdate({
                      monitoring: {
                        ...backup.monitoring,
                        enabled: e.target.checked
                      }
                    })}
                  />
                }
                label="Enable monitoring"
                sx={{ mb: 2 }}
              />
              <FormControl fullWidth>
                <InputLabel>Alert Threshold</InputLabel>
                <Select
                  label="Alert Threshold"
                  defaultValue={backup.monitoring.alertThreshold}
                  onChange={(e) => handleBackupUpdate({
                    monitoring: {
                      ...backup.monitoring,
                      alertThreshold: e.target.value as 'critical' | 'warning' | 'info'
                    }
                  })}
                >
                  <MenuItem value="critical">Critical</MenuItem>
                  <MenuItem value="warning">Warning</MenuItem>
                  <MenuItem value="info">Info</MenuItem>
                </Select>
              </FormControl>
              <Alert severity="info" sx={{ mt: 2 }}>
                Monitoring helps ensure backup reliability and quick issue detection
              </Alert>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}; 