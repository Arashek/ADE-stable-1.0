import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Box,
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  IconButton,
  Typography,
  Divider,
  styled,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  Code as CodeIcon,
  Terminal as TerminalIcon,
  Settings as SettingsIcon,
  ChevronLeft as ChevronLeftIcon,
} from '@mui/icons-material';

interface SidebarProps {
  open: boolean;
  onToggle: () => void;
}

const DRAWER_WIDTH = 260;

const StyledDrawer = styled(Drawer)(({ theme }) => ({
  width: DRAWER_WIDTH,
  flexShrink: 0,
  '& .MuiDrawer-paper': {
    width: DRAWER_WIDTH,
    boxSizing: 'border-box',
    backgroundColor: '#212936',
    color: '#ffffff',
  },
}));

const Logo = styled(Box)(({ theme }) => ({
  display: 'flex',
  alignItems: 'center',
  padding: theme.spacing(2),
  color: '#ffffff',
  gap: theme.spacing(2),
}));

const StyledListItem = styled(ListItem)<{ active?: boolean }>(({ theme, active }) => ({
  margin: theme.spacing(0.5, 1),
  borderRadius: '8px',
  backgroundColor: active ? 'rgba(74, 123, 255, 0.1)' : 'transparent',
  color: active ? '#4a7bff' : '#ffffff',
  '&:hover': {
    backgroundColor: active ? 'rgba(74, 123, 255, 0.2)' : 'rgba(255, 255, 255, 0.1)',
  },
  '& .MuiListItemIcon-root': {
    color: active ? '#4a7bff' : '#ffffff',
  },
}));

const menuItems = [
  { path: '/', label: 'Dashboard', icon: <DashboardIcon /> },
  { path: '/code', label: 'Code Editor', icon: <CodeIcon /> },
  { path: '/terminal', label: 'Terminal', icon: <TerminalIcon /> },
  { path: '/settings', label: 'Settings', icon: <SettingsIcon /> },
];

const Sidebar: React.FC<SidebarProps> = ({ open, onToggle }) => {
  const location = useLocation();
  const navigate = useNavigate();

  const handleNavigation = (path: string) => {
    navigate(path);
  };

  return (
    <StyledDrawer variant="permanent" open={open}>
      <Logo>
        <IconButton color="inherit" onClick={onToggle}>
          {open ? <ChevronLeftIcon /> : <MenuIcon />}
        </IconButton>
        {open && (
          <Typography variant="h6" noWrap>
            ADE Platform
          </Typography>
        )}
      </Logo>

      <Divider sx={{ backgroundColor: 'rgba(255, 255, 255, 0.1)' }} />

      <List>
        {menuItems.map((item) => (
          <StyledListItem
            key={item.path}
            button
            active={location.pathname === item.path}
            onClick={() => handleNavigation(item.path)}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            {open && <ListItemText primary={item.label} />}
          </StyledListItem>
        ))}
      </List>
    </StyledDrawer>
  );
};

export default Sidebar; 