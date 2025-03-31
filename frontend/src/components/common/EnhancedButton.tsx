import React from 'react';
import { Button, CircularProgress, Tooltip } from '@mui/material';
import { styled } from '@mui/material/styles';
import { motion } from 'framer-motion';
import { accessibilityService } from '../../services/accessibility.service';

interface EnhancedButtonProps {
  variant?: 'primary' | 'secondary' | 'outline' | 'text';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  icon?: React.ReactNode;
  tooltip?: string;
  onClick?: () => void;
  children: React.ReactNode;
  fullWidth?: boolean;
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  className?: string;
  'aria-label'?: string;
}

const StyledButton = styled(motion(Button))(({ theme }) => ({
  position: 'relative',
  overflow: 'hidden',
  transition: theme.transitions.create(['transform', 'box-shadow']),
  '&:hover': {
    transform: 'translateY(-2px)',
    boxShadow: theme.shadows[4],
  },
  '&:active': {
    transform: 'translateY(0)',
  },
  '&.Mui-disabled': {
    transform: 'none',
    boxShadow: 'none',
  },
}));

const LoadingOverlay = styled('div')({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  backgroundColor: 'rgba(255, 255, 255, 0.7)',
  borderRadius: 'inherit',
});

const IconWrapper = styled('span')(({ theme }) => ({
  marginRight: theme.spacing(1),
  display: 'inline-flex',
  alignItems: 'center',
}));

export const EnhancedButton: React.FC<EnhancedButtonProps> = ({
  variant = 'primary',
  size = 'medium',
  loading = false,
  disabled = false,
  icon,
  tooltip,
  onClick,
  children,
  fullWidth = false,
  color = 'primary',
  className,
  'aria-label': ariaLabel,
}) => {
  const buttonRef = React.useRef<HTMLButtonElement>(null);

  React.useEffect(() => {
    if (buttonRef.current) {
      accessibilityService.addAriaLabel(buttonRef.current, ariaLabel || '');
    }
  }, [ariaLabel]);

  const handleClick = (e: React.MouseEvent) => {
    if (loading || disabled) return;
    onClick?.();
  };

  const buttonContent = (
    <StyledButton
      ref={buttonRef}
      variant={variant}
      size={size}
      disabled={disabled || loading}
      onClick={handleClick}
      fullWidth={fullWidth}
      color={color}
      className={className}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
    >
      {loading && (
        <LoadingOverlay>
          <CircularProgress size={24} color={color} />
        </LoadingOverlay>
      )}
      {icon && <IconWrapper>{icon}</IconWrapper>}
      {children}
    </StyledButton>
  );

  if (tooltip) {
    return (
      <Tooltip title={tooltip} arrow placement="top">
        {buttonContent}
      </Tooltip>
    );
  }

  return buttonContent;
}; 