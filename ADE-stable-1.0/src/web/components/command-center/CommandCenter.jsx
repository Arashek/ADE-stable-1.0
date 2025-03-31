import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { useWebSocket, subscribeToEvents } from '../../services/websocket';
import { colors, spacing, shadows, breakpoints } from '../styles';
import CommandPanel from './CommandPanel';
import ProgressVisualization from './ProgressVisualization';
import { FaChevronLeft, FaChevronRight, FaBell } from 'react-icons/fa';

// Styled Components
const CommandCenterContainer = styled.div`
  position: fixed;
  right: ${props => props.isCollapsed ? '-400px' : '0'};
  top: 0;
  bottom: 0;
  width: 400px;
  background: white;
  box-shadow: ${shadows.lg};
  transition: right 0.3s ease;
  z-index: 1000;
  display: flex;
  flex-direction: column;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${spacing.md};
  border-bottom: 1px solid ${colors.border};
  background: ${colors.background};
`;

const Title = styled.h2`
  margin: 0;
  font-size: 1.2rem;
  color: ${colors.text};
`;

const Controls = styled.div`
  display: flex;
  gap: ${spacing.sm};
  align-items: center;
`;

const ToggleButton = styled.button`
  background: none;
  border: none;
  color: ${colors.text};
  cursor: pointer;
  padding: ${spacing.sm};
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;

  &:hover {
    background: ${colors.background};
  }
`;

const NotificationBadge = styled.div`
  position: absolute;
  top: 0;
  right: 0;
  width: 8px;
  height: 8px;
  background: ${colors.error};
  border-radius: 50%;
  border: 2px solid white;
`;

const PanelContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
`;

const ResizeHandle = styled.div`
  height: 4px;
  background: ${colors.border};
  cursor: row-resize;
  transition: background 0.2s ease;

  &:hover {
    background: ${colors.primary};
  }
`;

const Panel = styled.div`
  flex: ${props => props.flex};
  min-height: ${props => props.minHeight};
  max-height: ${props => props.maxHeight};
  overflow: hidden;
  transition: flex 0.3s ease;
`;

const QuickAccessButton = styled.button`
  position: fixed;
  right: ${props => props.isCollapsed ? '20px' : '420px'};
  top: 50%;
  transform: translateY(-50%);
  background: ${colors.primary};
  color: white;
  border: none;
  border-radius: 4px;
  padding: ${spacing.sm};
  cursor: pointer;
  transition: right 0.3s ease;
  z-index: 999;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: ${shadows.md};

  &:hover {
    background: ${colors.primaryDark};
  }

  @media (max-width: ${breakpoints.md}) {
    display: none;
  }
`;

// Main Component
const CommandCenter = ({ onClose }) => {
  const [isCollapsed, setIsCollapsed] = useState(false);
  const [hasNotifications, setHasNotifications] = useState(false);
  const [panelSizes, setPanelSizes] = useState({ top: 0.6, bottom: 0.4 });
  const [isDragging, setIsDragging] = useState(false);
  const [startY, setStartY] = useState(0);
  const [startSizes, setStartSizes] = useState(null);
  const { connect, disconnect } = useWebSocket();

  useEffect(() => {
    connect();

    const unsubscribe = subscribeToEvents((event) => {
      if (event.type === 'agent_update' || event.type === 'task_update') {
        setHasNotifications(true);
      }
    });

    return () => {
      unsubscribe();
      disconnect();
    };
  }, []);

  const handleResizeStart = (e) => {
    setIsDragging(true);
    setStartY(e.clientY);
    setStartSizes({ ...panelSizes });
  };

  const handleResizeMove = (e) => {
    if (!isDragging) return;

    const deltaY = e.clientY - startY;
    const containerHeight = e.currentTarget.parentElement.offsetHeight;
    const deltaRatio = deltaY / containerHeight;

    setPanelSizes({
      top: Math.max(0.3, Math.min(0.7, startSizes.top + deltaRatio)),
      bottom: Math.max(0.3, Math.min(0.7, startSizes.bottom - deltaRatio))
    });
  };

  const handleResizeEnd = () => {
    setIsDragging(false);
    setStartSizes(null);
  };

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleResizeMove);
      window.addEventListener('mouseup', handleResizeEnd);
    }

    return () => {
      window.removeEventListener('mousemove', handleResizeMove);
      window.removeEventListener('mouseup', handleResizeEnd);
    };
  }, [isDragging]);

  return (
    <>
      <QuickAccessButton
        isCollapsed={isCollapsed}
        onClick={() => setIsCollapsed(false)}
      >
        <FaBell />
      </QuickAccessButton>

      <CommandCenterContainer isCollapsed={isCollapsed}>
        <Header>
          <Title>Command Center</Title>
          <Controls>
            {hasNotifications && <NotificationBadge />}
            <ToggleButton onClick={() => setIsCollapsed(!isCollapsed)}>
              {isCollapsed ? <FaChevronLeft /> : <FaChevronRight />}
            </ToggleButton>
          </Controls>
        </Header>

        <PanelContainer>
          <Panel flex={panelSizes.top} minHeight="30%" maxHeight="70%">
            <CommandPanel />
          </Panel>

          <ResizeHandle
            onMouseDown={handleResizeStart}
            style={{ cursor: isDragging ? 'row-resize' : 'default' }}
          />

          <Panel flex={panelSizes.bottom} minHeight="30%" maxHeight="70%">
            <ProgressVisualization />
          </Panel>
        </PanelContainer>
      </CommandCenterContainer>
    </>
  );
};

export default CommandCenter; 