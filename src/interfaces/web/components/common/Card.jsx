import React from 'react';
import styled, { css } from 'styled-components';

const paddingStyles = {
  none: css`
    padding: 0;
  `,
  small: css`
    padding: 16px;
  `,
  medium: css`
    padding: 24px;
  `,
  large: css`
    padding: 32px;
  `,
};

const CardContainer = styled.div`
  background-color: white;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  box-shadow: ${props => props.elevated 
    ? '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
    : '0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06)'
  };
  transition: all 0.2s ease;
  overflow: hidden;
  width: 100%;

  &:hover {
    box-shadow: ${props => props.elevated 
      ? '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)'
      : '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)'
    };
  }
`;

const CardHeader = styled.div`
  padding: ${props => {
    switch (props.padding) {
      case 'none': return '0';
      case 'small': return '16px';
      case 'large': return '32px';
      default: return '24px';
    }
  }};
  padding-bottom: ${props => props.padding === 'none' ? '0' : '16px'};
  border-bottom: ${props => props.divider ? '1px solid #e5e7eb' : 'none'};
`;

const CardTitle = styled.h3`
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.4;
`;

const CardSubtitle = styled.p`
  margin: 4px 0 0;
  font-size: 0.875rem;
  color: #6b7280;
  line-height: 1.5;
`;

const CardContent = styled.div`
  padding: ${props => {
    switch (props.padding) {
      case 'none': return '0';
      case 'small': return '16px';
      case 'large': return '32px';
      default: return '24px';
    }
  }};
  padding-top: ${props => props.padding === 'none' ? '0' : '16px'};
  padding-bottom: ${props => props.padding === 'none' ? '0' : '16px'};
`;

const CardFooter = styled.div`
  padding: ${props => {
    switch (props.padding) {
      case 'none': return '0';
      case 'small': return '16px';
      case 'large': return '32px';
      default: return '24px';
    }
  }};
  padding-top: ${props => props.padding === 'none' ? '0' : '16px'};
  border-top: ${props => props.divider ? '1px solid #e5e7eb' : 'none'};
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;

  @media (max-width: 640px) {
    flex-direction: column;
    align-items: stretch;
  }
`;

const Card = ({
  children,
  title,
  subtitle,
  footer,
  padding = 'medium',
  elevated = false,
  headerDivider = true,
  footerDivider = true,
  className,
  ...props
}) => {
  return (
    <CardContainer
      className={className}
      elevated={elevated}
      {...props}
    >
      {(title || subtitle) && (
        <CardHeader padding={padding} divider={headerDivider}>
          {title && <CardTitle>{title}</CardTitle>}
          {subtitle && <CardSubtitle>{subtitle}</CardSubtitle>}
        </CardHeader>
      )}

      <CardContent padding={padding}>
        {children}
      </CardContent>

      {footer && (
        <CardFooter padding={padding} divider={footerDivider}>
          {footer}
        </CardFooter>
      )}
    </CardContainer>
  );
};

export default Card; 