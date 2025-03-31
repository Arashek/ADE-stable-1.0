import React, { useState } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Badge,
  Breadcrumbs,
  Link,
  useTheme,
  useMediaQuery,
  Paper,
  Tooltip,
  Collapse,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
} from '@mui/material';
import {
  Menu as MenuIcon,
  ChevronLeft as ChevronLeftIcon,
  Notifications as NotificationsIcon,
  Settings as SettingsIcon,
  Person as PersonIcon,
  Logout as LogoutIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  Security as SecurityIcon,
  Storage as StorageIcon,
  Extension as ExtensionIcon,
  Link as LinkIcon,
  Store as StoreIcon,
  ExpandLess as ExpandLessIcon,
  ExpandMore as ExpandMoreIcon,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useUser, RequirePermission } from '../context/UserContext';

// Mock notifications - Replace with actual notifications
const mockNotifications = [
  {
    id: 1,
    title: 'New Extension Submission',
    message: 'Advanced Analytics extension submitted for review',
    time: '5 minutes ago',
    read: false,
  },
  {
    id: 2,
    title: 'Service Health Alert',
    message: 'AWS S3 service showing increased latency',
    time: '1 hour ago',
    read: false,
  },
  {
    id: 3,
    title: 'System Update',
    message: 'System maintenance scheduled for tonight',
    time: '2 hours ago',
    read: true,
  },
];

const drawerWidth = 240;

const OwnerPanelLayout = ({ children }) => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  const navigate = useNavigate();
  const location = useLocation();
  const { user, logout, logAuditEvent, hasPermission } = useUser();
  const [open, setOpen] = useState(!isMobile);
  const [anchorEl, setAnchorEl] = useState(null);
  const [notificationAnchor, setNotificationAnchor] = useState(null);
  const [notifications, setNotifications] = useState(mockNotifications);
  const [expandedSections, setExpandedSections] = useState({});
  const [showLogoutDialog, setShowLogoutDialog] = useState(false);

  const handleDrawerToggle = () => {
    setOpen(!open);
    logAuditEvent('DRAWER_TOGGLE', { isOpen: !open });
  };

  const handleProfileMenuOpen = (event) => {
    setAnchorEl(event.currentTarget);
    logAuditEvent('PROFILE_MENU_OPEN', { userId: user.id });
  };

  const handleNotificationMenuOpen = (event) => {
    setNotificationAnchor(event.currentTarget);
    logAuditEvent('NOTIFICATION_MENU_OPEN', { userId: user.id });
  };

  const handleMenuClose = () => {
    setAnchorEl(null);
    setNotificationAnchor(null);
  };

  const handleLogout = async () => {
    try {
      await logAuditEvent('LOGOUT', { userId: user.id });
      await logout();
      setShowLogoutDialog(false);
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  const handleProfileClick = () => {
    logAuditEvent('PROFILE_ACCESS', { userId: user.id });
    // Implement profile navigation
  };

  const handleSettingsClick = () => {
    logAuditEvent('SETTINGS_ACCESS', { userId: user.id });
    // Implement settings navigation
  };

  const handleNotificationClick = (notificationId) => {
    logAuditEvent('NOTIFICATION_VIEW', { 
      userId: user.id,
      notificationId 
    });
    setNotifications(notifications.map(notification =>
      notification.id === notificationId
        ? { ...notification, read: true }
        : notification
    ));
  };

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
    logAuditEvent('SECTION_TOGGLE', { section, isExpanded: !expandedSections[section] });
  };

  const getBreadcrumbs = () => {
    const paths = location.pathname.split('/').filter(Boolean);
    return paths.map((path, index) => {
      const isLast = index === paths.length - 1;
      const href = `/${paths.slice(0, index + 1).join('/')}`;
      const label = path.charAt(0).toUpperCase() + path.slice(1);

      return isLast ? (
        <Typography key={path} color="text.primary">
          {label}
        </Typography>
      ) : (
        <Link
          key={path}
          component="button"
          variant="body1"
          onClick={() => {
            logAuditEvent('BREADCRUMB_NAVIGATION', { path: href });
            navigate(href);
          }}
          underline="hover"
          color="inherit"
        >
          {label}
        </Link>
      );
    });
  };

  const drawer = (
    <Box>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Owner Panel
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        <RequirePermission permission="dashboard.view">
          <ListItem button onClick={() => navigate('/admin/owner')}>
            <ListItemIcon>
              <DashboardIcon />
            </ListItemIcon>
            <ListItemText primary="Dashboard" />
          </ListItem>
        </RequirePermission>

        <RequirePermission permission="operations.view">
          <ListItem button onClick={() => toggleSection('operations')}>
            <ListItemIcon>
              <PeopleIcon />
            </ListItemIcon>
            <ListItemText primary="Operations" />
            {expandedSections['operations'] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </ListItem>
          <Collapse in={expandedSections['operations']} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              <RequirePermission permission="operations.users.view">
                <ListItem button sx={{ pl: 4 }} onClick={() => navigate('/admin/owner/operations/users')}>
                  <ListItemText primary="User Management" />
                </ListItem>
              </RequirePermission>
              <RequirePermission permission="operations.deployments.view">
                <ListItem button sx={{ pl: 4 }} onClick={() => navigate('/admin/owner/operations/deployments')}>
                  <ListItemText primary="Deployment Manager" />
                </ListItem>
              </RequirePermission>
            </List>
          </Collapse>
        </RequirePermission>

        <RequirePermission permission="security.view">
          <ListItem button onClick={() => toggleSection('security')}>
            <ListItemIcon>
              <SecurityIcon />
            </ListItemIcon>
            <ListItemText primary="Security" />
            {expandedSections['security'] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </ListItem>
          <Collapse in={expandedSections['security']} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              <RequirePermission permission="security.access.view">
                <ListItem button sx={{ pl: 4 }} onClick={() => navigate('/admin/owner/security/access')}>
                  <ListItemText primary="Access Control" />
                </ListItem>
              </RequirePermission>
              <RequirePermission permission="security.data.view">
                <ListItem button sx={{ pl: 4 }} onClick={() => navigate('/admin/owner/security/data')}>
                  <ListItemText primary="Data Protection" />
                </ListItem>
              </RequirePermission>
            </List>
          </Collapse>
        </RequirePermission>

        <RequirePermission permission="architecture.view">
          <ListItem button onClick={() => toggleSection('architecture')}>
            <ListItemIcon>
              <StorageIcon />
            </ListItemIcon>
            <ListItemText primary="Architecture" />
            {expandedSections['architecture'] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </ListItem>
          <Collapse in={expandedSections['architecture']} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              <RequirePermission permission="architecture.components.view">
                <ListItem button sx={{ pl: 4 }} onClick={() => navigate('/admin/owner/architecture/components')}>
                  <ListItemText primary="Component Manager" />
                </ListItem>
              </RequirePermission>
              <RequirePermission permission="architecture.models.view">
                <ListItem button sx={{ pl: 4 }} onClick={() => navigate('/admin/owner/architecture/models')}>
                  <ListItemText primary="Model Management" />
                </ListItem>
              </RequirePermission>
            </List>
          </Collapse>
        </RequirePermission>

        <RequirePermission permission="integrations.view">
          <ListItem button onClick={() => toggleSection('integrations')}>
            <ListItemIcon>
              <LinkIcon />
            </ListItemIcon>
            <ListItemText primary="Integrations" />
            {expandedSections['integrations'] ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </ListItem>
          <Collapse in={expandedSections['integrations']} timeout="auto" unmountOnExit>
            <List component="div" disablePadding>
              <RequirePermission permission="integrations.services.view">
                <ListItem button sx={{ pl: 4 }} onClick={() => navigate('/admin/owner/integrations/services')}>
                  <ListItemText primary="External Services" />
                </ListItem>
              </RequirePermission>
              <RequirePermission permission="integrations.marketplace.view">
                <ListItem button sx={{ pl: 4 }} onClick={() => navigate('/admin/owner/integrations/marketplace')}>
                  <ListItemText primary="Marketplace" />
                </ListItem>
              </RequirePermission>
            </List>
          </Collapse>
        </RequirePermission>
      </List>
    </Box>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${open ? drawerWidth : 0}px)` },
          ml: { sm: `${open ? drawerWidth : 0}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Breadcrumbs aria-label="breadcrumb" sx={{ flexGrow: 1 }}>
            {getBreadcrumbs()}
          </Breadcrumbs>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Tooltip title="Notifications">
              <IconButton color="inherit" onClick={handleNotificationMenuOpen}>
                <Badge badgeContent={notifications.filter(n => !n.read).length} color="error">
                  <NotificationsIcon />
                </Badge>
              </IconButton>
            </Tooltip>
            <Tooltip title="Account settings">
              <IconButton
                edge="end"
                aria-label="account of current user"
                aria-haspopup="true"
                onClick={handleProfileMenuOpen}
                color="inherit"
              >
                <Avatar sx={{ width: 32, height: 32 }}>
                  {user?.avatar ? (
                    <img src={user.avatar} alt={user.name} />
                  ) : (
                    <PersonIcon />
                  )}
                </Avatar>
              </IconButton>
            </Tooltip>
          </Box>
        </Toolbar>
      </AppBar>

      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        {isMobile ? (
          <Drawer
            variant="temporary"
            open={open}
            onClose={handleDrawerToggle}
            ModalProps={{
              keepMounted: true,
            }}
            sx={{
              display: { xs: 'block', sm: 'none' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
          >
            {drawer}
          </Drawer>
        ) : (
          <Drawer
            variant="persistent"
            open={open}
            sx={{
              display: { xs: 'none', sm: 'block' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
          >
            {drawer}
          </Drawer>
        )}
      </Box>

      <Box
        component="main"
        sx={{
          flexGrow: 1,
          p: 3,
          width: { sm: `calc(100% - ${open ? drawerWidth : 0}px)` },
          mt: '64px',
        }}
      >
        {children}
      </Box>

      {/* Profile Menu */}
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleMenuClose}
        onClick={handleMenuClose}
      >
        <MenuItem onClick={handleProfileClick}>
          <ListItemIcon>
            <PersonIcon fontSize="small" />
          </ListItemIcon>
          Profile
        </MenuItem>
        <RequirePermission permission="settings.access">
          <MenuItem onClick={handleSettingsClick}>
            <ListItemIcon>
              <SettingsIcon fontSize="small" />
            </ListItemIcon>
            Settings
          </MenuItem>
        </RequirePermission>
        <Divider />
        <MenuItem onClick={() => setShowLogoutDialog(true)}>
          <ListItemIcon>
            <LogoutIcon fontSize="small" />
          </ListItemIcon>
          Logout
        </MenuItem>
      </Menu>

      {/* Logout Confirmation Dialog */}
      <Dialog
        open={showLogoutDialog}
        onClose={() => setShowLogoutDialog(false)}
      >
        <DialogTitle>Confirm Logout</DialogTitle>
        <DialogContent>
          <Typography>
            Are you sure you want to logout? Any unsaved changes will be lost.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowLogoutDialog(false)}>
            Cancel
          </Button>
          <Button onClick={handleLogout} color="primary" variant="contained">
            Logout
          </Button>
        </DialogActions>
      </Dialog>

      {/* Notifications Menu */}
      <Menu
        anchorEl={notificationAnchor}
        open={Boolean(notificationAnchor)}
        onClose={handleMenuClose}
        onClick={handleMenuClose}
      >
        <Box sx={{ width: 360, maxHeight: 400, overflow: 'auto' }}>
          {notifications.map((notification) => (
            <MenuItem
              key={notification.id}
              onClick={() => handleNotificationClick(notification.id)}
              sx={{
                backgroundColor: notification.read ? 'inherit' : 'action.hover',
                '&:hover': {
                  backgroundColor: 'action.selected',
                },
              }}
            >
              <Box sx={{ width: '100%' }}>
                <Typography variant="subtitle2">{notification.title}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {notification.message}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {notification.time}
                </Typography>
              </Box>
            </MenuItem>
          ))}
        </Box>
      </Menu>
    </Box>
  );
};

export default OwnerPanelLayout; 