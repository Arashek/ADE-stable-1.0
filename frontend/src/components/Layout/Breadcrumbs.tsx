import React from 'react';
import {
  Box,
  Breadcrumbs as MUIBreadcrumbs,
  Link,
  Typography,
  useTheme,
} from '@mui/material';
import {
  NavigateNext as NavigateNextIcon,
  Home as HomeIcon,
} from '@mui/icons-material';
import { Link as RouterLink, useLocation } from 'react-router-dom';

interface BreadcrumbItem {
  label: string;
  path: string;
}

const pathToBreadcrumbs = (pathname: string): BreadcrumbItem[] => {
  const paths = pathname.split('/').filter(Boolean);
  
  return paths.map((path, index) => {
    const fullPath = '/' + paths.slice(0, index + 1).join('/');
    const label = path
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
    
    return {
      label,
      path: fullPath,
    };
  });
};

const Breadcrumbs: React.FC = () => {
  const theme = useTheme();
  const location = useLocation();
  const items = pathToBreadcrumbs(location.pathname);

  return (
    <Box sx={{ p: 2, backgroundColor: theme.palette.background.paper }}>
      <MUIBreadcrumbs
        separator={<NavigateNextIcon fontSize="small" />}
        aria-label="breadcrumb"
        sx={{
          '& .MuiBreadcrumbs-separator': {
            mx: 1,
          },
        }}
      >
        <Link
          component={RouterLink}
          to="/"
          color="inherit"
          sx={{
            display: 'flex',
            alignItems: 'center',
            textDecoration: 'none',
            '&:hover': {
              textDecoration: 'underline',
            },
          }}
        >
          <HomeIcon sx={{ mr: 0.5 }} fontSize="inherit" />
          Home
        </Link>
        {items.map((item, index) => (
          <Link
            key={item.path}
            component={RouterLink}
            to={item.path}
            color={index === items.length - 1 ? 'text.primary' : 'inherit'}
            sx={{
              textDecoration: 'none',
              '&:hover': {
                textDecoration: 'underline',
              },
            }}
          >
            {item.label}
          </Link>
        ))}
      </MUIBreadcrumbs>
    </Box>
  );
};

export default Breadcrumbs; 