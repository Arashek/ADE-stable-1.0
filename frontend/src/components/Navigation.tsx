import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
  Divider,
  Box
} from '@mui/material';
import { styled } from '@mui/material/styles';
import {
  Home as HomeIcon,
  Settings as SettingsIcon,
  School as SchoolIcon,
  Psychology as PsychologyIcon,
  SettingsEthernet as PipelineIcon,
} from '@mui/icons-material';

const drawerWidth = 240;

const StyledDrawer = styled(Drawer)(({ theme }) => ({
  width: drawerWidth,
  flexShrink: 0,
  '& .MuiDrawer-paper': {
    width: drawerWidth,
    backgroundColor: theme.palette.background.default,
  },
}));

const StyledListItem = styled(ListItem)(({ theme }) => ({
  borderRadius: theme.shape.borderRadius,
  margin: theme.spacing(0.5, 1),
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

const StyledListItemIcon = styled(ListItemIcon)(({ theme }) => ({
  minWidth: 40,
}));

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
  const location = useLocation();

  return (
    <StyledDrawer variant="permanent" anchor="left">
      <List>
        {navigationItems.map((item) => (
          <Tooltip key={item.path} title={item.tooltip} placement="right">
            <StyledListItem
              button
              component={Link}
              to={item.path}
              sx={{
                backgroundColor:
                  location.pathname === item.path
                    ? (theme) => theme.palette.action.selected
                    : 'none',
              }}
            >
              <StyledListItemIcon>
                {item.icon}
              </StyledListItemIcon>
              <ListItemText primary={item.label} />
            </StyledListItem>
          </Tooltip>
        ))}
      </List>
    </StyledDrawer>
  );
};

export default Navigation;