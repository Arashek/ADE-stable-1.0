import React from 'react';
import { Paper, Box, Typography, PaperProps, styled } from '@mui/material';

interface CardProps extends Omit<PaperProps, 'title'> {
  title?: React.ReactNode;
  subtitle?: React.ReactNode;
  headerAction?: React.ReactNode;
  noPadding?: boolean;
}

const StyledPaper = styled(Paper)(({ theme }) => ({
  backgroundColor: '#ffffff',
  borderRadius: '12px',
  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.05)',
  overflow: 'hidden',
}));

const Card: React.FC<CardProps> = ({
  title,
  subtitle,
  headerAction,
  children,
  noPadding = false,
  ...props
}) => {
  return (
    <StyledPaper {...props}>
      {(title || subtitle || headerAction) && (
        <Box
          sx={{
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'flex-start',
            p: 3,
            pb: noPadding ? 3 : 0,
          }}
        >
          <Box>
            {title && (
              <Typography variant="h6" gutterBottom={!!subtitle}>
                {title}
              </Typography>
            )}
            {subtitle && (
              <Typography variant="body2" color="text.secondary">
                {subtitle}
              </Typography>
            )}
          </Box>
          {headerAction && <Box>{headerAction}</Box>}
        </Box>
      )}
      <Box sx={{ p: noPadding ? 0 : 3 }}>{children}</Box>
    </StyledPaper>
  );
};

export default Card; 