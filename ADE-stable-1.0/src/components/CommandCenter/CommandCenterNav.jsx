import React from 'react';
import { useTheme } from '@mui/material/styles';
import Box from '@mui/material/Box';
import IconButton from '@mui/material/IconButton';
import Badge from '@mui/material/Badge';
import Tooltip from '@mui/material/Tooltip';
import { styled } from '@mui/material/styles';
import CommandCenterIcon from '@mui/icons-material/Dashboard';

const NavButton = styled(IconButton)(({ theme }) => ({
  position: 'relative',
  margin: theme.spacing(0, 1),
  '&:hover': {
    backgroundColor: theme.palette.action.hover,
  },
}));

const CommandCenterNav = ({ notifications, onClick }) => {
  const theme = useTheme();

  return (
    <Box sx={{ display: 'flex', alignItems: 'center' }}>
      <Tooltip title="Command Center">
        <NavButton
          onClick={onClick}
          color="primary"
          size="large"
          aria-label="command center"
        >
          <Badge
            badgeContent={notifications.length}
            color="error"
            invisible={notifications.length === 0}
          >
            <CommandCenterIcon />
          </Badge>
        </NavButton>
      </Tooltip>
    </Box>
  );
};

export default CommandCenterNav; 