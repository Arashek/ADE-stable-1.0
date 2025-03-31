import React from 'react';
import {
  Paper,
  Typography,
  List,
  ListItem,
  ListItemText,
  ListItemIcon,
  Chip
} from '@mui/material';
import {
  Code as CodeIcon,
  Build as BuildIcon,
  BugReport as DebugIcon,
  Assessment as AnalysisIcon,
  Security as SecurityIcon
} from '@mui/icons-material';

interface AgentActivity {
  id: string;
  type: string;
  timestamp: string;
  details: any;
}

interface AgentActivityPanelProps {
  activities: AgentActivity[];
}

const getActivityIcon = (type: string) => {
  switch (type) {
    case 'code':
      return <CodeIcon />;
    case 'build':
      return <BuildIcon />;
    case 'debug':
      return <DebugIcon />;
    case 'analysis':
      return <AnalysisIcon />;
    case 'security':
      return <SecurityIcon />;
    default:
      return <CodeIcon />;
  }
};

const formatTimestamp = (timestamp: string) => {
  return new Date(timestamp).toLocaleTimeString();
};

export const AgentActivityPanel: React.FC<AgentActivityPanelProps> = ({
  activities
}) => {
  return (
    <Paper sx={{ p: 2, height: '100%', overflow: 'auto' }}>
      <Typography variant="h6" gutterBottom>
        Agent Activities
      </Typography>
      <List>
        {activities.map((activity) => (
          <ListItem key={activity.id}>
            <ListItemIcon>
              {getActivityIcon(activity.type)}
            </ListItemIcon>
            <ListItemText
              primary={
                <>
                  <Typography variant="body2" component="span">
                    {activity.type}
                  </Typography>
                  <Chip
                    size="small"
                    label={formatTimestamp(activity.timestamp)}
                    variant="outlined"
                    sx={{ ml: 1 }}
                  />
                </>
              }
              secondary={
                <Typography variant="body2" color="text.secondary">
                  {JSON.stringify(activity.details, null, 2)}
                </Typography>
              }
            />
          </ListItem>
        ))}
      </List>
    </Paper>
  );
}; 