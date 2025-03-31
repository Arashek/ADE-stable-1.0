import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  makeStyles,
  Theme,
  createStyles,
} from '@material-ui/core';
import {
  Home as HomeIcon,
  Settings as SettingsIcon,
  School as SchoolIcon,
  Psychology as PsychologyIcon,
  SettingsEthernet as PipelineIcon,
} from '@material-ui/icons';

const drawerWidth = 240;

const useStyles = makeStyles((theme: Theme) =>
  createStyles({
    drawer: {
      width: drawerWidth,
      flexShrink: 0,
    },
    drawerPaper: {
      width: drawerWidth,
      backgroundColor: theme.palette.background.default,
    },
    active: {
      backgroundColor: theme.palette.action.selected,
    },
    listItem: {
      borderRadius: theme.shape.borderRadius,
      margin: theme.spacing(0.5, 1),
      '&:hover': {
        backgroundColor: theme.palette.action.hover,
      },
    },
    listItemIcon: {
      minWidth: 40,
    },
  })
);

interface NavigationItem {
  path: string;
  label: string;
  icon: React.ReactNode;
  tooltip: string;
}

const navigationItems: NavigationItem[] = [
  {
    path: '/',
    label: 'Dashboard',
    icon: <HomeIcon />,
    tooltip: 'System overview and metrics',
  },
  {
    path: '/pipeline',
    label: 'Pipeline',
    icon: <PipelineIcon />,
    tooltip: 'Pipeline monitoring and configuration',
  },
  {
    path: '/models',
    label: 'Models',
    icon: <PsychologyIcon />,
    tooltip: 'Model integration and coordination',
  },
  {
    path: '/learning',
    label: 'Learning',
    icon: <SchoolIcon />,
    tooltip: 'Learning system and feedback',
  },
  {
    path: '/settings',
    label: 'Settings',
    icon: <SettingsIcon />,
    tooltip: 'System configuration',
  },
];

const Navigation: React.FC = () => {
  const classes = useStyles();
  const location = useLocation();

  return (
    <Drawer
      className={classes.drawer}
      variant="permanent"
      classes={{
        paper: classes.drawerPaper,
      }}
      anchor="left"
    >
      <List>
        {navigationItems.map((item) => (
          <Tooltip key={item.path} title={item.tooltip} placement="right">
            <ListItem
              button
              component={Link}
              to={item.path}
              className={`${classes.listItem} ${
                location.pathname === item.path ? classes.active : ''
              }`}
            >
              <ListItemIcon className={classes.listItemIcon}>
                {item.icon}
              </ListItemIcon>
              <ListItemText primary={item.label} />
            </ListItem>
          </Tooltip>
        ))}
      </List>
    </Drawer>
  );
};

export default Navigation; 