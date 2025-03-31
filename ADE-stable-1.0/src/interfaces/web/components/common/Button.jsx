import React from 'react';
import styled, { css } from 'styled-components';
import { FaSpinner } from 'react-icons/fa';

const sizeStyles = {
  small: css`
    padding: 6px 12px;
    font-size: 0.875rem;
  `,
  medium: css`
    padding: 8px 16px;
    font-size: 0.875rem;
  `,
  large: css`
    padding: 12px 24px;
    font-size: 1rem;
  `,
};

const variantStyles = {
  primary: css`
    background-color: ${props => props.customColor || '#3b82f6'};
    color: white;
    border: none;

    &:hover:not(:disabled) {
      background-color: ${props => props.customColor || '#2563eb'};
    }

    &:focus {
      box-shadow: 0 0 0 2px ${props => props.customColor || '#3b82f6'}40;
    }
  `,
  secondary: css`
    background-color: white;
    color: ${props => props.customColor || '#3b82f6'};
    border: 1px solid ${props => props.customColor || '#3b82f6'};

    &:hover:not(:disabled) {
      background-color: ${props => props.customColor || '#3b82f6'}10;
    }

    &:focus {
      box-shadow: 0 0 0 2px ${props => props.customColor || '#3b82f6'}40;
    }
  `,
  tertiary: css`
    background-color: transparent;
    color: ${props => props.customColor || '#6b7280'};
    border: none;

    &:hover:not(:disabled) {
      background-color: #f3f4f6;
      color: ${props => props.customColor || '#4b5563'};
    }

    &:focus {
      box-shadow: 0 0 0 2px #e5e7eb;
    }
  `,
};

const StyledButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  border-radius: 6px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  min-width: ${props => props.fullWidth ? '100%' : 'auto'};
  ${props => sizeStyles[props.size]}
  ${props => variantStyles[props.variant]}

  &:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }

  &:focus {
    outline: none;
  }

  /* Loading state styles */
  ${props => props.isLoading && css`
    color: transparent;
    position: relative;
  `}
`;

const IconWrapper = styled.span`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  font-size: ${props => {
    switch (props.size) {
      case 'small': return '0.875rem';
      case 'large': return '1.25rem';
      default: return '1rem';
    }
  }};
  ${props => props.position === 'right' && 'order: 2;'}
`;

const Spinner = styled(FaSpinner)`
  position: absolute;
  left: 50%;
  top: 50%;
  transform: translate(-50%, -50%);
  animation: spin 1s linear infinite;
  font-size: ${props => {
    switch (props.size) {
      case 'small': return '0.875rem';
      case 'large': return '1.25rem';
      default: return '1rem';
    }
  }};

  @keyframes spin {
    from {
      transform: translate(-50%, -50%) rotate(0deg);
    }
    to {
      transform: translate(-50%, -50%) rotate(360deg);
    }
  }
`;

const Button = ({
  children,
  variant = 'primary',
  size = 'medium',
  icon,
  iconPosition = 'left',
  isLoading = false,
  disabled = false,
  customColor,
  fullWidth = false,
  type = 'button',
  onClick,
  ...props
}) => {
  const buttonProps = {
    variant,
    size,
    disabled: disabled || isLoading,
    customColor,
    fullWidth,
    type,
    isLoading,
    onClick: disabled || isLoading ? undefined : onClick,
    ...props,
  };

  return (
    <StyledButton
      {...buttonProps}
      aria-disabled={disabled || isLoading}
      aria-busy={isLoading}
    >
      {isLoading && <Spinner size={size} />}
      {icon && iconPosition === 'left' && (
        <IconWrapper position="left" size={size}>
          {icon}
        </IconWrapper>
      )}
      {children}
      {icon && iconPosition === 'right' && (
        <IconWrapper position="right" size={size}>
          {icon}
        </IconWrapper>
      )}
    </StyledButton>
  );
};

export default Button; 