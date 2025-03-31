import React from 'react';
import {
  Drawer,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  Box,
  IconButton,
  useTheme,
} from '@mui/material';
import {
  Code,
  AccountTree,
  GitHub,
  Settings,
  ChevronLeft,
  ChevronRight,
  Analytics,
  Speed,
  Architecture,
} from '@mui/icons-material';

interface MainNavigationProps {
  open: boolean;
  onClose: () => void;
  onNavigate: (route: string) => void;
}

export const MainNavigation: React.FC<MainNavigationProps> = ({
  open,
  onClose,
  onNavigate,
}) => {
  const theme = useTheme();

  const menuItems = [
    { text: 'Code Editor', icon: <Code />, route: '/editor' },
    { text: 'File Explorer', icon: <AccountTree />, route: '/explorer' },
    { text: 'Git Integration', icon: <GitHub />, route: '/git' },
    { text: 'Settings', icon: <Settings />, route: '/settings' },
  ];

  const advancedFeatures = [
    { text: 'Code Analysis', icon: <Analytics />, route: '/analysis' },
    { text: 'Performance', icon: <Speed />, route: '/performance' },
    { text: 'Architecture', icon: <Architecture />, route: '/architecture' },
  ];

  return (
    <Drawer
      variant="persistent"
      anchor="left"
      open={open}
      sx={{
        width: 240,
        flexShrink: 0,
        '& .MuiDrawer-paper': {
          width: 240,
          boxSizing: 'border-box',
        },
      }}
    >
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'flex-end',
          p: 1,
        }}
      >
        <IconButton onClick={onClose}>
          {theme.direction === 'ltr' ? <ChevronLeft /> : <ChevronRight />}
        </IconButton>
      </Box>
      <Divider />
      <List>
        {menuItems.map((item) => (
          <ListItem
            button
            key={item.text}
            onClick={() => onNavigate(item.route)}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
      <Divider />
      <List>
        <ListItem>
          <ListItemText
            primary="Advanced Features"
            primaryTypographyProps={{ variant: 'overline' }}
          />
        </ListItem>
        {advancedFeatures.map((item) => (
          <ListItem
            button
            key={item.text}
            onClick={() => onNavigate(item.route)}
          >
            <ListItemIcon>{item.icon}</ListItemIcon>
            <ListItemText primary={item.text} />
          </ListItem>
        ))}
      </List>
    </Drawer>
  );
}; 