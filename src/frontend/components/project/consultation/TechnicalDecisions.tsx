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
  Alert
} from '@mui/material';
import { ProjectSpecification, UserPreferences } from '../../../../core/models/agent/types';

interface TechnicalDecisionsProps {
  specification: ProjectSpecification;
  onUpdate: (updates: Partial<UserPreferences>) => void;
}

export const TechnicalDecisions: React.FC<TechnicalDecisionsProps> = ({
  specification,
  onUpdate
}) => {
  const handleTechnologyStackUpdate = (technologies: string[]) => {
    onUpdate({ technologyStack: technologies });
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>
        Technical Decisions Overview
      </Typography>

      <Grid container spacing={3}>
        {/* Architecture Overview */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Architecture Overview" />
            <CardContent>
              <Typography variant="body1" paragraph>
                The system architecture has been designed with the following components:
              </Typography>
              <List>
                {specification.architecture.components.map((component) => (
                  <ListItem key={component.name}>
                    <ListItemText
                      primary={component.name}
                      secondary={
                        <Box>
                          <Typography variant="body2" color="text.secondary">
                            Type: {component.type}
                          </Typography>
                          <Typography variant="body2" color="text.secondary">
                            Responsibilities: {component.responsibilities.join(', ')}
                          </Typography>
                        </Box>
                      }
                    />
                  </ListItem>
                ))}
              </List>
            </CardContent>
          </Card>
        </Grid>

        {/* Technology Stack */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Technology Stack" />
            <CardContent>
              <Typography variant="body1" paragraph>
                The following technologies have been selected for the project:
              </Typography>
              <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {specification.architecture.technologies.map((tech) => (
                  <Chip
                    key={tech.name}
                    label={`${tech.name} ${tech.version}`}
                    color="primary"
                    variant="outlined"
                    onClick={() => handleTechnologyStackUpdate([tech.name])}
                  />
                ))}
              </Box>
              <Alert severity="info" sx={{ mt: 2 }}>
                Click on technologies to customize your stack
              </Alert>
            </CardContent>
          </Card>
        </Grid>

        {/* Development Workflow */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Development Workflow" />
            <CardContent>
              <Typography variant="body1" paragraph>
                The development process will follow these workflows:
              </Typography>
              <List>
                {specification.development.workflows.map((workflow) => (
                  <React.Fragment key={workflow.name}>
                    <ListItem>
                      <ListItemText
                        primary={workflow.name}
                        secondary={
                          <Box>
                            <Typography variant="body2" color="text.secondary">
                              Steps: {workflow.steps.join(' → ')}
                            </Typography>
                            <Typography variant="body2" color="text.secondary">
                              Triggers: {workflow.triggers.join(', ')}
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

        {/* Testing Strategy */}
        <Grid item xs={12}>
          <Card>
            <CardHeader title="Testing Strategy" />
            <CardContent>
              <Typography variant="body1" paragraph>
                The following testing approaches will be implemented:
              </Typography>
              <List>
                <ListItem>
                  <ListItemText
                    primary="Test Types"
                    secondary={specification.development.testing.types.join(', ')}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Frameworks"
                    secondary={specification.development.testing.frameworks.join(', ')}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Coverage Target"
                    secondary={`${specification.development.testing.coverage}%`}
                  />
                </ListItem>
                <ListItem>
                  <ListItemText
                    primary="Automation"
                    secondary={specification.development.testing.automation ? 'Enabled' : 'Disabled'}
                  />
                </ListItem>
              </List>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
}; 