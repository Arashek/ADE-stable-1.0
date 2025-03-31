import React, { useState } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  IconButton,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Divider,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Menu as MenuIcon,
  Code as CodeIcon,
  AccountTree as BranchIcon,
  Settings as SettingsIcon,
  Preview as PreviewIcon,
  Notifications as NotificationsIcon,
  Chat as ChatIcon,
} from '@mui/icons-material';
import CodeReviewPanel from '../CodeReview/CodeReviewPanel';
import BranchCommitViewer from '../Git/BranchCommitViewer';
import ProjectConfig from '../Project/ProjectConfig';
import PreviewPanel from '../Preview/PreviewPanel';
import NotificationSystem from '../Notifications/NotificationSystem';
import UnifiedChat from '../shared/UnifiedChat';

const drawerWidth = 240;

interface DashboardProps {
  // Add any necessary props
}

const Dashboard: React.FC<DashboardProps> = () => {
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const [mobileOpen, setMobileOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('code');

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleTabChange = (tab: string) => {
    setActiveTab(tab);
    if (isMobile) {
      setMobileOpen(false);
    }
  };

  const drawer = (
    <Box>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          ADE Platform
        </Typography>
      </Toolbar>
      <Divider />
      <List>
        <ListItem button onClick={() => handleTabChange('code')}>
          <ListItemIcon>
            <CodeIcon />
          </ListItemIcon>
          <ListItemText primary="Code Review" />
        </ListItem>
        <ListItem button onClick={() => handleTabChange('git')}>
          <ListItemIcon>
            <BranchIcon />
          </ListItemIcon>
          <ListItemText primary="Git History" />
        </ListItem>
        <ListItem button onClick={() => handleTabChange('preview')}>
          <ListItemIcon>
            <PreviewIcon />
          </ListItemIcon>
          <ListItemText primary="Preview" />
        </ListItem>
        <ListItem button onClick={() => handleTabChange('chat')}>
          <ListItemIcon>
            <ChatIcon />
          </ListItemIcon>
          <ListItemText primary="Chat" />
        </ListItem>
        <ListItem button onClick={() => handleTabChange('notifications')}>
          <ListItemIcon>
            <NotificationsIcon />
          </ListItemIcon>
          <ListItemText primary="Notifications" />
        </ListItem>
      </List>
      <Divider />
      <List>
        <ListItem button onClick={() => handleTabChange('settings')}>
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary="Project Settings" />
        </ListItem>
      </List>
    </Box>
  );

  const renderContent = () => {
    switch (activeTab) {
      case 'code':
        return (
          <CodeReviewPanel
            pullRequestId="123"
            changes={[]}
            comments={[]}
            onAddComment={() => {}}
            onUpdateComment={() => {}}
            onDeleteComment={() => {}}
            onResolveComment={() => {}}
            onApprove={() => {}}
            onRequestChanges={() => {}}
          />
        );
      case 'git':
        return (
          <BranchCommitViewer
            branches={[]}
            commits={[]}
            onCheckout={() => {}}
            onCreateBranch={() => {}}
            onDeleteBranch={() => {}}
            onMerge={() => {}}
            onCompare={() => {}}
            onPush={() => {}}
            onPull={() => {}}
            onRebase={() => {}}
            onReset={() => {}}
            onCreateTag={() => {}}
            onStash={() => {}}
            onApplyStash={() => {}}
          />
        );
      case 'preview':
        return (
          <PreviewPanel
            url="http://localhost:3000"
            onRefresh={() => {}}
            onOpenInNewWindow={() => {}}
            onDeviceChange={() => {}}
            onZoomChange={() => {}}
            onFullscreenToggle={() => {}}
            onSettingsChange={() => {}}
          />
        );
      case 'chat':
        return <UnifiedChat />;
      case 'notifications':
        return <NotificationSystem />;
      case 'settings':
        return (
          <ProjectConfig
            config={{
              name: 'Project Name',
              description: 'Project Description',
              version: '1.0.0',
              environmentVariables: [],
              dependencies: [],
              settings: {
                autoSave: true,
                formatOnSave: true,
                lintOnSave: true,
                useGitHooks: true,
              },
              buildConfig: {
                buildCommand: 'npm run build',
                outputDirectory: 'dist',
                environment: 'development',
                optimizationLevel: 'basic',
                sourceMaps: true,
              },
              deploymentConfig: {
                platform: 'aws',
                region: 'us-east-1',
                environment: 'staging',
                autoDeploy: true,
                deploymentBranch: 'main',
                buildCommand: 'npm run build',
                envVars: [],
              },
              securityConfig: {
                ssl: true,
                cors: {
                  enabled: true,
                  allowedOrigins: [],
                },
                rateLimit: {
                  enabled: true,
                  maxRequests: 100,
                  windowMs: 60000,
                },
                authentication: {
                  type: 'jwt',
                  config: {},
                },
              },
              template: null,
              scripts: {},
              engines: {
                node: '>=14.0.0',
              },
            }}
            onSave={() => {}}
            onRefresh={() => {}}
          />
        );
      default:
        return null;
    }
  };

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
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
          <Typography variant="h6" noWrap component="div">
            {activeTab.charAt(0).toUpperCase() + activeTab.slice(1)}
          </Typography>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        {isMobile ? (
          <Drawer
            variant="temporary"
            open={mobileOpen}
            onClose={handleDrawerToggle}
            ModalProps={{
              keepMounted: true, // Better open performance on mobile.
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
            variant="permanent"
            sx={{
              display: { xs: 'none', sm: 'block' },
              '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
            }}
            open
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
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          height: '100vh',
          overflow: 'hidden',
        }}
      >
        <Toolbar />
        {renderContent()}
      </Box>
    </Box>
  );
};

export default Dashboard; 