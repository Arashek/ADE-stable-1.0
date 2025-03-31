import React from 'react';
import {
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Collapse,
  Box,
  Typography,
  Divider,
  Tooltip,
  useTheme,
} from '@mui/material';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Extension as ExtensionIcon,
  Link as LinkIcon,
  Store as StoreIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
  Lock as LockIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUser, RequirePermission } from '../context/UserContext';

const navigationItems = [
  {
    id: 'dashboard',
    title: 'Dashboard',
    icon: <DashboardIcon />,
    path: '/admin/owner',
    permission: 'dashboard.view',
  },
  {
    id: 'operations',
    title: 'Operations',
    icon: <PeopleIcon />,
    permission: 'operations.view',
    children: [
      {
        id: 'users',
        title: 'User Management',
        path: '/admin/owner/operations/users',
        permission: 'operations.users.view',
      },
      {
        id: 'deployments',
        title: 'Deployment Manager',
        path: '/admin/owner/operations/deployments',
        permission: 'operations.deployments.view',
      },
    ],
  },
  {
    id: 'security',
    title: 'Security',
    icon: <SecurityIcon />,
    permission: 'security.view',
    children: [
      {
        id: 'access',
        title: 'Access Control',
        path: '/admin/owner/security/access',
        permission: 'security.access.view',
      },
      {
        id: 'data',
        title: 'Data Protection',
        path: '/admin/owner/security/data',
        permission: 'security.data.view',
      },
    ],
  },
  {
    id: 'architecture',
    title: 'Architecture',
    icon: <StorageIcon />,
    permission: 'architecture.view',
    children: [
      {
        id: 'components',
        title: 'Component Manager',
        path: '/admin/owner/architecture/components',
        permission: 'architecture.components.view',
      },
      {
        id: 'models',
        title: 'Model Management',
        path: '/admin/owner/architecture/models',
        permission: 'architecture.models.view',
      },
    ],
  },
  {
    id: 'integrations',
    title: 'Integrations',
    icon: <LinkIcon />,
    permission: 'integrations.view',
    children: [
      {
        id: 'services',
        title: 'External Services',
        path: '/admin/owner/integrations/services',
        permission: 'integrations.services.view',
      },
      {
        id: 'marketplace',
        title: 'Marketplace',
        path: '/admin/owner/integrations/marketplace',
        permission: 'integrations.marketplace.view',
      },
    ],
  },
];

const OwnerNavigation = ({ expandedSections, onToggleSection }) => {
  const theme = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const { hasPermission, logAuditEvent } = useUser();

  const isActive = (path) => {
    return location.pathname === path;
  };

  const handleNavigation = (path, permission) => {
    logAuditEvent('NAVIGATION', {
      path,
      permission,
    });
    navigate(path);
  };

  const renderNavigationItem = (item) => {
    if (!hasPermission(item.permission)) return null;

    if (item.children) {
      const hasAnyChildPermission = item.children.some(child => hasPermission(child.permission));
      if (!hasAnyChildPermission) return null;

      return (
        <Box key={item.id}>
          <ListItem
            button
            onClick={() => onToggleSection(item.id)}
            sx={{
              backgroundColor: expandedSections[item.id] ? 'action.selected' : 'inherit',
              '&:hover': {
                backgroundColor: 'action.hover',
              },
            }}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.title} />
            {expandedSections[item.id] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </ListItem>
          <Collapse in={expandedSections[item.id]} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              {item.children.map((child) => {
                if (!hasPermission(child.permission)) return null;
                return (
                  <ListItem
                    key={child.id}
                    button
                    onClick={() => handleNavigation(child.path, child.permission)}
                    sx={{
                      pl: 4,
                      backgroundColor: isActive(child.path) ? 'action.selected' : 'inherit',
                      '&:hover': {
                        backgroundColor: 'action.hover',
                      },
                    }}
                  >
                    <ListItemText
                      primary={child.title}
                      primaryTypographyProps={{
                        color: isActive(child.path) ? 'primary' : 'inherit',
                      }}
                    />
                    {!hasPermission(child.permission) && (
                      <Tooltip title="No permission">
                        <LockIcon fontSize="small" color="disabled" />
                      </Tooltip>
                    )}
                  </ListItem>
                );
              })}
            </List>
          </Collapse>
        </Box>
      );
    }

    return (
      <ListItem
        key={item.id}
        button
        onClick={() => handleNavigation(item.path, item.permission)}
        sx={{
          backgroundColor: isActive(item.path) ? 'action.selected' : 'inherit',
          '&:hover': {
            backgroundColor: 'action.hover',
          },
        }}
      >
        <ListItemIcon>{item.icon}</ListItemIcon>
        <ListItemText
          primary={item.title}
          primaryTypographyProps={{
            color: isActive(item.path) ? 'primary' : 'inherit',
          }}
        />
      </ListItem>
    );
  };

  return (
    <Box>
      <Box sx={{ p: 2 }}>
        <Typography variant="h6" noWrap component="div">
          Owner Panel
        </Typography>
      </Box>
      <Divider />
      <List>
        {navigationItems.map(renderNavigationItem)}
      </List>
    </Box>
  );
};

export default OwnerNavigation; 