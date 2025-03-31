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
  Alert
} from '@mui/material';
import { PerformanceSpec } from '../../../../core/models/agent/types';

interface ResourceAllocationProps {
  performance: PerformanceSpec;
  onUpdate: (updates: { performanceRequirements: Partial<PerformanceSpec> }) => void;
}

export const ResourceAllocation: React.FC<ResourceAllocationProps> = ({
  performance,
  onUpdate
}) => {
  const handlePerformanceUpdate = (updates: Partial<PerformanceSpec>) => {
    onUpdate({
      performanceRequirements: {
        ...performance,
        ...updates
      }
    });
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Resource Allocation
      </Typography>

      <Grid container spacing={3}>
        {/* Performance Metrics */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Performance Metrics" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Configure the following performance metrics:
              </Typography>
              <List>
                {performance.metrics.map((metric) => (
                  <React.Fragment key={metric.name}>
                    <ListItem>
                      <ListItemText
                        primary={metric.name}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Type: {metric.type}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Target: {metric.target}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Measurement: {metric.measurement}
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

        {/* Response Time Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Response Time" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Set the target response time for your application:
              </Typography>
              <TextField
                fullWidth
                label="Response Time"
                placeholder="e.g., 100ms"
                defaultValue={performance.responseTime}
                onChange={(e) => handlePerformanceUpdate({ responseTime: e.target.value })}
              />
              <Alert severity="info" sx={{ mt: 2 }}>
                Lower response times may require more resources
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* Throughput Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Throughput" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Set the target throughput for your application:
              </Typography>
              <TextField
                fullWidth
                label="Throughput"
                placeholder="e.g., 1000 req/s"
                defaultValue={performance.throughput}
                onChange={(e) => handlePerformanceUpdate({ throughput: e.target.value })}
              />
              <Alert severity="info" sx={{ mt: 2 }}>
                Higher throughput may require more resources
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* Scalability Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Scalability" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Configure the scaling behavior:
              </Typography>
              <FormControl fullWidth>
                <InputLabel>Scaling Mode</InputLabel>
                <Select
                  label="Scaling Mode"
                  defaultValue={performance.scalability}
                  onChange={(e) => handlePerformanceUpdate({ scalability: e.target.value })}
                >
                  <MenuItem value="auto">Automatic</MenuItem>
                  <MenuItem value="manual">Manual</MenuItem>
                  <MenuItem value="fixed">Fixed</MenuItem>
                </Select>
              </FormControl>
              <Alert severity="info" sx={{ mt: 2 }}>
                Automatic scaling may incur additional costs
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* Availability Configuration */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardHeader title="Availability" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Set the target availability:
              </Typography>
              <TextField
                fullWidth
                label="Availability"
                placeholder="e.g., 99.9%"
                defaultValue={performance.availability}
                onChange={(e) => handlePerformanceUpdate({ availability: e.target.value })}
              />
              <Alert severity="info" sx={{ mt: 2 }}>
                Higher availability requires more redundancy
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* Resource Optimization */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Resource Optimization" />
            <CardContent>
              <Typography variant="body1" paragraph>
                The following optimizations will be applied:
              </Typography>
              <List>
                {performance.optimizations.map((optimization) => (
                  <React.Fragment key={optimization.area}>
                    <ListItem>
                      <ListItemText
                        primary={optimization.area}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Description: {optimization.description}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Implementation: {optimization.implementation}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Impact: {optimization.impact}
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

        {/* Scaling Configuration */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Scaling Configuration" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Configure the scaling behavior:
              </Typography>
              <List>
                {performance.scaling.map((config) => (
                  <React.Fragment key={config.type}>
                    <ListItem>
                      <ListItemText
                        primary={`${config.type} Scaling`}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Trigger: {config.trigger}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Action: {config.action}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Limits: {config.limits.min} - {config.limits.max}
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
    </Box>
  );
}; 