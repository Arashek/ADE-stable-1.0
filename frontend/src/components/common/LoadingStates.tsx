import React from 'react';
import {
  Box,
  CircularProgress,
  LinearProgress,
  Typography,
  Fade,
  styled,
} from '@mui/material';

const StyledBox = styled(Box)(({ theme }) => ({
  display: 'flex',
  flexDirection: 'column',
  alignItems: 'center',
  justifyContent: 'center',
  padding: theme.spacing(2),
}));

const StyledCircularProgress = styled(CircularProgress)(({ theme }) => ({
  marginBottom: theme.spacing(2),
}));

const StyledLinearProgress = styled(LinearProgress)(({ theme }) => ({
  width: '100%',
  maxWidth: 400,
  marginBottom: theme.spacing(2),
}));

const StyledTypography = styled(Typography)(({ theme }) => ({
  marginTop: theme.spacing(1),
  color: theme.palette.text.secondary,
}));

interface LoadingStatesProps {
  type?: 'circular' | 'linear';
  message?: string;
  show?: boolean;
  variant?: 'determinate' | 'indeterminate';
  value?: number;
}

export const LoadingStates: React.FC<LoadingStatesProps> = ({
  type = 'circular',
  message = 'Loading...',
  show = true,
  variant = 'indeterminate',
  value,
}) => {
  return (
    <Fade in={show}>
      <StyledBox>
        {type === 'circular' ? (
          <StyledCircularProgress
            variant={variant}
            value={value}
            sx={{
              animation: 'pulse 1.5s ease-in-out infinite',
              '@keyframes pulse': {
                '0%': {
                  transform: 'scale(1)',
                  opacity: 1,
                },
                '50%': {
                  transform: 'scale(1.1)',
                  opacity: 0.8,
                },
                '100%': {
                  transform: 'scale(1)',
                  opacity: 1,
                },
              },
            }}
          />
        ) : (
          <StyledLinearProgress
            variant={variant}
            value={value}
          />
        )}
        <StyledTypography variant="body2">
          {message}
        </StyledTypography>
      </StyledBox>
    </Fade>
  );
}; 