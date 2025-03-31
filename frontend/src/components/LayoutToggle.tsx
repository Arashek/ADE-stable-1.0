import React, { useState } from 'react';
import {
  IconButton,
  Menu,
  MenuItem,
  ListItemIcon,
  ListItemText,
  Tooltip,
} from '@mui/material';
import {
  GridView as GridViewIcon,
  ViewQuilt as ViewQuiltIcon,
  ViewSidebar as ViewSidebarIcon,
  Preview as PreviewIcon,
  Chat as ChatIcon,
  ViewStream as ViewStreamIcon,
  ViewModule as ViewModuleIcon,
} from '@mui/icons-material';

export type LayoutType = 
  | 'grid-matrix'
  | 'command-first'
  | 'agent-centric'
  | 'preview-focused'
  | 'chat-driven'
  | 'dynamic-flow';

interface LayoutOption {
  id: LayoutType;
  label: string;
  icon: React.ReactElement;
  description: string;
}

interface LayoutToggleProps {
  currentLayout: LayoutType;
  onLayoutChange: (layout: LayoutType) => void;
}

const layoutOptions: LayoutOption[] = [
  {
    id: 'grid-matrix',
    label: 'Grid Matrix',
    icon: <GridViewIcon />,
    description: 'Equal-sized panels for balanced multitasking',
  },
  {
    id: 'command-first',
    label: 'Command First',
    icon: <ViewQuiltIcon />,
    description: 'Prioritizes command center with strategic panel arrangement',
  },
  {
    id: 'agent-centric',
    label: 'Agent Centric',
    icon: <ViewSidebarIcon />,
    description: 'Focuses on agent activities with optimal monitoring space',
  },
  {
    id: 'preview-focused',
    label: 'Preview Focused',
    icon: <PreviewIcon />,
    description: 'Emphasizes preview window while maintaining IDE access',
  },
  {
    id: 'chat-driven',
    label: 'Chat Driven',
    icon: <ChatIcon />,
    description: 'Optimized for chat-based development workflow',
  },
  {
    id: 'dynamic-flow',
    label: 'Dynamic Flow',
    icon: <ViewStreamIcon />,
    description: 'Flexible layout adapting to your workflow needs',
  },
];

export const LayoutToggle: React.FC<LayoutToggleProps> = ({
  currentLayout,
  onLayoutChange,
}) => {
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);

  const handleClick = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLayoutSelect = (layout: LayoutType) => {
    onLayoutChange(layout);
    handleClose();
  };

  const currentLayoutOption = layoutOptions.find(
    (option) => option.id === currentLayout
  );

  return (
    <>
      <Tooltip title="Change Layout">
        <IconButton
          onClick={handleClick}
          size="large"
          sx={{
            position: 'fixed',
            top: '1rem',
            right: '1rem',
            bgcolor: 'background.paper',
            boxShadow: 2,
            '&:hover': {
              bgcolor: 'action.hover',
            },
          }}
        >
          {currentLayoutOption?.icon || <ViewModuleIcon />}
        </IconButton>
      </Tooltip>
      <Menu
        anchorEl={anchorEl}
        open={Boolean(anchorEl)}
        onClose={handleClose}
        anchorOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        {layoutOptions.map((option) => (
          <MenuItem
            key={option.id}
            onClick={() => handleLayoutSelect(option.id)}
            selected={currentLayout === option.id}
          >
            <ListItemIcon>{option.icon}</ListItemIcon>
            <ListItemText
              primary={option.label}
              secondary={option.description}
              sx={{
                '& .MuiListItemText-secondary': {
                  fontSize: '0.75rem',
                },
              }}
            />
          </MenuItem>
        ))}
      </Menu>
    </>
  );
}; 