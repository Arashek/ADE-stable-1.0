import React, { useEffect, useRef, useState } from 'react';
import { styled } from '@mui/material/styles';
import { motion, useMotionValue, useTransform, useAnimation } from 'framer-motion';
import { monitoringService } from '../../services/monitoring.service';
import { accessibilityService } from '../../services/accessibility.service';

interface GestureNavigatorProps {
  children: React.ReactNode;
  onSwipe?: (direction: 'left' | 'right' | 'up' | 'down') => void;
  className?: string;
  'aria-label'?: string;
}

const Container = styled(motion.div)({
  position: 'relative',
  width: '100%',
  height: '100%',
  touchAction: 'none',
});

const GestureOverlay = styled(motion.div)({
  position: 'absolute',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  pointerEvents: 'none',
});

const GestureIndicator = styled(motion.div)(({ theme }) => ({
  width: 60,
  height: 60,
  borderRadius: '50%',
  backgroundColor: theme.palette.primary.main,
  opacity: 0.5,
  display: 'flex',
  alignItems: 'center',
  justifyContent: 'center',
  color: theme.palette.primary.contrastText,
  fontSize: '1.5rem',
}));

export const GestureNavigator: React.FC<GestureNavigatorProps> = ({
  children,
  onSwipe,
  className,
  'aria-label': ariaLabel,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [isGestureActive, setIsGestureActive] = useState(false);
  const [gestureDirection, setGestureDirection] = useState<'left' | 'right' | 'up' | 'down' | null>(null);

  const x = useMotionValue(0);
  const y = useMotionValue(0);
  const rotate = useTransform(x, [-200, 200], [-30, 30]);
  const scale = useTransform(x, [-200, 200], [0.8, 1.2]);

  const controls = useAnimation();

  useEffect(() => {
    if (containerRef.current) {
      accessibilityService.addAriaLabel(
        containerRef.current,
        ariaLabel || 'Gesture-based navigation area'
      );
    }
  }, [ariaLabel]);

  const handleDragStart = () => {
    setIsGestureActive(true);
    monitoringService.trackUserEvent({
      type: 'gesture_start',
      userId: 'anonymous',
      data: { timestamp: Date.now() },
    });
  };

  const handleDragEnd = (event: any, info: any) => {
    setIsGestureActive(false);
    setGestureDirection(null);

    const { offset } = info;
    const threshold = 100;

    if (Math.abs(offset.x) > threshold || Math.abs(offset.y) > threshold) {
      const direction = Math.abs(offset.x) > Math.abs(offset.y)
        ? offset.x > 0
          ? 'right'
          : 'left'
        : offset.y > 0
          ? 'down'
          : 'up';

      onSwipe?.(direction);
      monitoringService.trackUserEvent({
        type: 'gesture_complete',
        userId: 'anonymous',
        data: { direction, timestamp: Date.now() },
      });
    }

    controls.start({
      x: 0,
      y: 0,
      rotate: 0,
      scale: 1,
      transition: { type: 'spring', stiffness: 300, damping: 20 },
    });
  };

  const handleDrag = (event: any, info: any) => {
    const { offset } = info;
    const threshold = 50;

    if (Math.abs(offset.x) > threshold || Math.abs(offset.y) > threshold) {
      const direction = Math.abs(offset.x) > Math.abs(offset.y)
        ? offset.x > 0
          ? 'right'
          : 'left'
        : offset.y > 0
          ? 'down'
          : 'up';

      setGestureDirection(direction);
    } else {
      setGestureDirection(null);
    }
  };

  const getGestureIcon = () => {
    switch (gestureDirection) {
      case 'left':
        return '←';
      case 'right':
        return '→';
      case 'up':
        return '↑';
      case 'down':
        return '↓';
      default:
        return '↔';
    }
  };

  return (
    <Container
      ref={containerRef}
      className={className}
      drag
      dragConstraints={{ left: 0, right: 0, top: 0, bottom: 0 }}
      dragElastic={0.2}
      onDragStart={handleDragStart}
      onDrag={handleDrag}
      onDragEnd={handleDragEnd}
      animate={controls}
      style={{ x, y, rotate, scale }}
    >
      {children}
      {isGestureActive && (
        <GestureOverlay>
          <GestureIndicator
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            exit={{ scale: 0 }}
            transition={{ type: 'spring', stiffness: 300, damping: 20 }}
          >
            {getGestureIcon()}
          </GestureIndicator>
        </GestureOverlay>
      )}
    </Container>
  );
}; 