import React, { useEffect, useState } from 'react';
import { styled } from '@mui/material/styles';
import { motion, AnimatePresence } from 'framer-motion';
import { monitoringService } from '../../services/monitoring.service';
import { accessibilityService } from '../../services/accessibility.service';

interface FeedbackOverlayProps {
  type: 'success' | 'error' | 'info' | 'warning';
  message: string;
  duration?: number;
  onClose?: () => void;
  position?: 'top' | 'bottom' | 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left';
  className?: string;
}

const Container = styled(motion.div)<{ position: FeedbackOverlayProps['position'] }>(
  ({ theme, position }) => ({
    position: 'fixed',
    padding: theme.spacing(2),
    borderRadius: theme.shape.borderRadius,
    backgroundColor: theme.palette.background.paper,
    boxShadow: theme.shadows[4],
    zIndex: theme.zIndex.snackbar,
    ...(position === 'top' && {
      top: theme.spacing(2),
      left: '50%',
      transform: 'translateX(-50%)',
    }),
    ...(position === 'bottom' && {
      bottom: theme.spacing(2),
      left: '50%',
      transform: 'translateX(-50%)',
    }),
    ...(position === 'top-right' && {
      top: theme.spacing(2),
      right: theme.spacing(2),
    }),
    ...(position === 'top-left' && {
      top: theme.spacing(2),
      left: theme.spacing(2),
    }),
    ...(position === 'bottom-right' && {
      bottom: theme.spacing(2),
      right: theme.spacing(2),
    }),
    ...(position === 'bottom-left' && {
      bottom: theme.spacing(2),
      left: theme.spacing(2),
    }),
  })
);

const IconWrapper = styled('span')(({ theme }) => ({
  marginRight: theme.spacing(1),
  display: 'inline-flex',
  alignItems: 'center',
}));

const Message = styled('span')(({ theme }) => ({
  color: theme.palette.text.primary,
  fontSize: theme.typography.body1.fontSize,
}));

const getIcon = (type: FeedbackOverlayProps['type']) => {
  switch (type) {
    case 'success':
      return '✓';
    case 'error':
      return '✕';
    case 'warning':
      return '⚠';
    case 'info':
      return 'ℹ';
    default:
      return '';
  }
};

const getBackgroundColor = (type: FeedbackOverlayProps['type'], theme: any) => {
  switch (type) {
    case 'success':
      return theme.palette.success.main;
    case 'error':
      return theme.palette.error.main;
    case 'warning':
      return theme.palette.warning.main;
    case 'info':
      return theme.palette.info.main;
    default:
      return theme.palette.primary.main;
  }
};

export const FeedbackOverlay: React.FC<FeedbackOverlayProps> = ({
  type,
  message,
  duration = 3000,
  onClose,
  position = 'top',
  className,
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const containerRef = React.useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      accessibilityService.addAriaLabel(
        containerRef.current,
        `${type} notification: ${message}`
      );
    }

    const timer = setTimeout(() => {
      setIsVisible(false);
      onClose?.();
    }, duration);

    monitoringService.trackUserEvent({
      type: 'feedback_shown',
      userId: 'anonymous',
      data: { type, message, duration },
    });

    return () => clearTimeout(timer);
  }, [duration, message, onClose, type]);

  const handleClose = () => {
    setIsVisible(false);
    onClose?.();
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <Container
          ref={containerRef}
          className={className}
          position={position}
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -20 }}
          transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          onClick={handleClose}
          style={{
            backgroundColor: getBackgroundColor(type, (window as any).theme),
          }}
        >
          <IconWrapper>{getIcon(type)}</IconWrapper>
          <Message>{message}</Message>
        </Container>
      )}
    </AnimatePresence>
  );
}; 