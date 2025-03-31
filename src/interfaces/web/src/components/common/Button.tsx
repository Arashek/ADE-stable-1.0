import React from 'react';
import { Button as MuiButton, ButtonProps as MuiButtonProps, styled } from '@mui/material';

interface ButtonProps extends Omit<MuiButtonProps, 'variant'> {
  variant?: 'primary' | 'secondary' | 'outline' | 'text';
  size?: 'small' | 'medium' | 'large';
}

const StyledButton = styled(MuiButton)(({ theme }) => ({
  borderRadius: '8px',
  textTransform: 'none',
  fontWeight: 600,
  '&.primary': {
    backgroundColor: '#4a7bff',
    color: '#ffffff',
    '&:hover': {
      backgroundColor: '#3d63cc',
    },
  },
  '&.secondary': {
    backgroundColor: '#212936',
    color: '#ffffff',
    '&:hover': {
      backgroundColor: '#1a212c',
    },
  },
  '&.outline': {
    border: '2px solid #4a7bff',
    color: '#4a7bff',
    backgroundColor: 'transparent',
    '&:hover': {
      backgroundColor: 'rgba(74, 123, 255, 0.1)',
    },
  },
  '&.text': {
    color: '#4a7bff',
    '&:hover': {
      backgroundColor: 'rgba(74, 123, 255, 0.1)',
    },
  },
  '&.small': {
    padding: '6px 16px',
    fontSize: '0.875rem',
  },
  '&.medium': {
    padding: '8px 20px',
    fontSize: '1rem',
  },
  '&.large': {
    padding: '10px 24px',
    fontSize: '1.125rem',
  },
}));

const Button: React.FC<ButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  className,
  ...props
}) => {
  return (
    <StyledButton
      className={`${variant} ${size} ${className || ''}`}
      {...props}
    />
  );
};

export default Button; 