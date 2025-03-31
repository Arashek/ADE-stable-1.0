import React, { useState } from 'react';
import styled from 'styled-components';
import { FaBell, FaCog } from 'react-icons/fa';
import { colors, spacing, shadows } from '../styles';
import useCommandCenterStore from '../../store/commandCenterStore';

const NavContainer = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
  padding: ${spacing.sm} ${spacing.md};
  background: ${colors.background};
  border-bottom: 1px solid ${colors.border};
`;

const NavButton = styled.button`
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
  padding: ${spacing.sm} ${spacing.md};
  background: ${props => props.isActive ? colors.primary + '20' : 'transparent'};
  color: ${props => props.isActive ? colors.primary : colors.text};
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;

  &:hover {
    background: ${colors.primary + '10'};
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

const SettingsButton = styled.button`
  background: none;
  border: none;
  color: ${colors.text};
  cursor: pointer;
  padding: ${spacing.sm};
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-left: auto;

  &:hover {
    background: ${colors.background};
  }
`;

const CommandCenterNav = ({ onToggleCommandCenter, onOpenSettings }) => {
  const [isActive, setIsActive] = useState(false);
  const { preferences, tasks } = useCommandCenterStore();
  const hasNotifications = tasks.some(task => task.status === 'blocked' || task.status === 'urgent');

  const handleToggle = () => {
    setIsActive(!isActive);
    onToggleCommandCenter();
  };

  return (
    <NavContainer>
      <NavButton
        isActive={isActive}
        onClick={handleToggle}
      >
        <FaBell />
        Command Center
        {hasNotifications && <NotificationBadge />}
      </NavButton>

      <SettingsButton onClick={onOpenSettings}>
        <FaCog />
      </SettingsButton>
    </NavContainer>
  );
};

export default CommandCenterNav; 