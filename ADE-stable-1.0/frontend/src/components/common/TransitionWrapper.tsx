import React from 'react';
import {
  Fade,
  Slide,
  Grow,
  Zoom,
  Collapse,
  styled,
} from '@mui/material';

const TransitionContainer = styled('div')({
  position: 'relative',
  width: '100%',
  height: '100%',
});

type TransitionType = 'fade' | 'slide' | 'grow' | 'zoom' | 'collapse';

interface TransitionWrapperProps {
  children: React.ReactElement;
  type?: TransitionType;
  in?: boolean;
  direction?: 'up' | 'down' | 'left' | 'right';
  timeout?: number | { enter?: number; exit?: number };
  mountOnEnter?: boolean;
  unmountOnExit?: boolean;
}

export const TransitionWrapper: React.FC<TransitionWrapperProps> = ({
  children,
  type = 'fade',
  in: show = true,
  direction = 'up',
  timeout,
  mountOnEnter = true,
  unmountOnExit = true,
}) => {
  const renderTransition = () => {
    switch (type) {
      case 'fade':
        return (
          <Fade
            in={show}
            timeout={timeout}
            mountOnEnter={mountOnEnter}
            unmountOnExit={unmountOnExit}
          >
            {children}
          </Fade>
        );
      case 'slide':
        return (
          <Slide
            direction={direction}
            in={show}
            timeout={timeout}
            mountOnEnter={mountOnEnter}
            unmountOnExit={unmountOnExit}
          >
            {children}
          </Slide>
        );
      case 'grow':
        return (
          <Grow
            in={show}
            timeout={timeout}
            mountOnEnter={mountOnEnter}
            unmountOnExit={unmountOnExit}
          >
            {children}
          </Grow>
        );
      case 'zoom':
        return (
          <Zoom
            in={show}
            timeout={timeout}
            mountOnEnter={mountOnEnter}
            unmountOnExit={unmountOnExit}
          >
            {children}
          </Zoom>
        );
      case 'collapse':
        return (
          <Collapse
            in={show}
            timeout={timeout}
            mountOnEnter={mountOnEnter}
            unmountOnExit={unmountOnExit}
          >
            {children}
          </Collapse>
        );
      default:
        return children;
    }
  };

  return <TransitionContainer>{renderTransition()}</TransitionContainer>;
}; 