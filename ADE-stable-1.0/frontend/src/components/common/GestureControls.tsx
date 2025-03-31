import React, { useEffect, useRef, useState } from 'react';
import { Box, styled } from '@mui/material';

const GestureContainer = styled(Box)(({ theme }) => ({
  position: 'fixed',
  top: 0,
  left: 0,
  right: 0,
  bottom: 0,
  touchAction: 'none',
  zIndex: theme.zIndex.modal,
  display: 'none',
  [theme.breakpoints.down('sm')]: {
    display: 'block',
  },
}));

const GestureIndicator = styled(Box)(({ theme }) => ({
  position: 'absolute',
  width: 40,
  height: 40,
  borderRadius: '50%',
  backgroundColor: theme.palette.primary.main,
  opacity: 0.5,
  pointerEvents: 'none',
  transition: 'transform 0.2s ease-out',
}));

interface GestureControlsProps {
  onSwipeLeft?: () => void;
  onSwipeRight?: () => void;
  onSwipeUp?: () => void;
  onSwipeDown?: () => void;
  onPinchIn?: () => void;
  onPinchOut?: () => void;
  enabled?: boolean;
}

export const GestureControls: React.FC<GestureControlsProps> = ({
  onSwipeLeft,
  onSwipeRight,
  onSwipeUp,
  onSwipeDown,
  onPinchIn,
  onPinchOut,
  enabled = true,
}) => {
  const containerRef = useRef<HTMLDivElement>(null);
  const [touchStart, setTouchStart] = useState<{ x: number; y: number } | null>(null);
  const [touchEnd, setTouchEnd] = useState<{ x: number; y: number } | null>(null);
  const [initialDistance, setInitialDistance] = useState<number | null>(null);

  const handleTouchStart = (e: TouchEvent) => {
    if (!enabled) return;
    
    const touch = e.touches[0];
    setTouchStart({ x: touch.clientX, y: touch.clientY });
    
    if (e.touches.length === 2) {
      const touch1 = e.touches[0];
      const touch2 = e.touches[1];
      const distance = Math.hypot(
        touch2.clientX - touch1.clientX,
        touch2.clientY - touch1.clientY
      );
      setInitialDistance(distance);
    }
  };

  const handleTouchMove = (e: TouchEvent) => {
    if (!enabled || !touchStart) return;
    
    const touch = e.touches[0];
    setTouchEnd({ x: touch.clientX, y: touch.clientY });
    
    if (e.touches.length === 2 && initialDistance) {
      const touch1 = e.touches[0];
      const touch2 = e.touches[1];
      const currentDistance = Math.hypot(
        touch2.clientX - touch1.clientX,
        touch2.clientY - touch1.clientY
      );
      
      const diff = currentDistance - initialDistance;
      if (Math.abs(diff) > 50) {
        if (diff > 0) {
          onPinchOut?.();
        } else {
          onPinchIn?.();
        }
      }
    }
  };

  const handleTouchEnd = () => {
    if (!enabled || !touchStart || !touchEnd) return;
    
    const dx = touchEnd.x - touchStart.x;
    const dy = touchEnd.y - touchStart.y;
    const threshold = 50;
    
    if (Math.abs(dx) > threshold || Math.abs(dy) > threshold) {
      if (Math.abs(dx) > Math.abs(dy)) {
        if (dx > 0) {
          onSwipeRight?.();
        } else {
          onSwipeLeft?.();
        }
      } else {
        if (dy > 0) {
          onSwipeDown?.();
        } else {
          onSwipeUp?.();
        }
      }
    }
    
    setTouchStart(null);
    setTouchEnd(null);
    setInitialDistance(null);
  };

  useEffect(() => {
    const container = containerRef.current;
    if (!container) return;

    container.addEventListener('touchstart', handleTouchStart);
    container.addEventListener('touchmove', handleTouchMove);
    container.addEventListener('touchend', handleTouchEnd);
    container.addEventListener('touchcancel', handleTouchEnd);

    return () => {
      container.removeEventListener('touchstart', handleTouchStart);
      container.removeEventListener('touchmove', handleTouchMove);
      container.removeEventListener('touchend', handleTouchEnd);
      container.removeEventListener('touchcancel', handleTouchEnd);
    };
  }, [enabled, touchStart, touchEnd, initialDistance]);

  return (
    <GestureContainer ref={containerRef}>
      {touchStart && touchEnd && (
        <GestureIndicator
          sx={{
            left: touchEnd.x - 20,
            top: touchEnd.y - 20,
            transform: `scale(${Math.abs(touchEnd.x - touchStart.x) / 100 + 1})`,
          }}
        />
      )}
    </GestureContainer>
  );
}; 