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
  Chip,
  Alert,
  FormControl,
  InputLabel,
  Select,
  MenuItem
} from '@mui/material';
import { SecuritySpec, UserPreferences } from '../../../../core/models/agent/types';

interface SecurityImplicationsProps {
  security: SecuritySpec;
  onUpdate: (updates: Partial<UserPreferences>) => void;
}

export const SecurityImplications: React.FC<SecurityImplicationsProps> = ({
  security,
  onUpdate
}) => {
  const handleSecurityLevelUpdate = (level: 'high' | 'medium' | 'low') => {
    onUpdate({ securityLevel: level });
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Security Implications
      </Typography>

      <Grid container spacing={3}>
        {/* Security Level Selection */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Security Level" />
            <CardContent>
              <Typography variant="body1" paragraph>
                Select the desired security level for your project:
              </Typography>
              <FormControl fullWidth>
                <InputLabel>Security Level</InputLabel>
                <Select
                  label="Security Level"
                  defaultValue="medium"
                  onChange={(e) => handleSecurityLevelUpdate(e.target.value as 'high' | 'medium' | 'low')}
                >
                  <MenuItem value="high">High Security</MenuItem>
                  <MenuItem value="medium">Medium Security</MenuItem>
                  <MenuItem value="low">Low Security</MenuItem>
                </Select>
              </FormControl>
              <Alert severity="info" sx={{ mt: 2 }}>
                Higher security levels may impact development speed and resource usage
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* Security Threats */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Identified Threats" />
            <CardContent>
              <Typography variant="body1" paragraph>
                The following security threats have been identified:
              </Typography>
              <List>
                {security.threats.map((threat) => (
                  <React.Fragment key={threat.id}>
                    <ListItem>
                      <ListItemText
                        primary={threat.description}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Impact: {threat.impact}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Likelihood: {threat.likelihood}
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

        {/* Mitigation Strategies */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Mitigation Strategies" />
            <CardContent>
              <Typography variant="body1" paragraph>
                The following mitigation strategies will be implemented:
              </Typography>
              <List>
                {security.mitigations.map((mitigation) => (
                  <React.Fragment key={mitigation.threatId}>
                    <ListItem>
                      <ListItemText
                        primary={mitigation.description}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Implementation: {mitigation.implementation}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Effectiveness: {Math.round(mitigation.effectiveness * 100)}%
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

        {/* Compliance Requirements */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Compliance Requirements" />
            <CardContent>
              <Typography variant="body1" paragraph>
                The following compliance standards must be met:
              </Typography>
              <List>
                {security.compliance.map((compliance) => (
                  <React.Fragment key={compliance.standard}>
                    <ListItem>
                      <ListItemText
                        primary={compliance.standard}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Requirements: {compliance.requirements.join(', ')}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Implementation: {compliance.implementation}
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

        {/* Security Best Practices */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Security Best Practices" />
            <CardContent>
              <Typography variant="body1" paragraph>
                The following security best practices will be enforced:
              </Typography>
              <List>
                {security.bestPractices.map((practice) => (
                  <React.Fragment key={practice.category}>
                    <ListItem>
                      <ListItemText
                        primary={practice.category}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Description: {practice.description}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Implementation: {practice.implementation}
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