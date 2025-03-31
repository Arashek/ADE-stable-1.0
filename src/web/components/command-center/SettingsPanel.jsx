import React from 'react';
import styled from 'styled-components';
import { FaTimes, FaMoon, FaBell, FaPalette } from 'react-icons/fa';
import { colors, spacing, shadows } from '../styles';
import useCommandCenterStore from '../../store/commandCenterStore';

const SettingsContainer = styled.div`
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  width: 400px;
  background: white;
  box-shadow: ${shadows.lg};
  z-index: 1100;
  display: flex;
  flex-direction: column;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${spacing.md};
  border-bottom: 1px solid ${colors.border};
`;

const Title = styled.h2`
  margin: 0;
  font-size: 1.2rem;
  color: ${colors.text};
`;

const CloseButton = styled.button`
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

const Content = styled.div`
  flex: 1;
  overflow-y: auto;
  padding: ${spacing.md};
`;

const Section = styled.div`
  margin-bottom: ${spacing.xl};
`;

const SectionTitle = styled.h3`
  margin: 0 0 ${spacing.md};
  font-size: 1rem;
  color: ${colors.text};
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
`;

const SettingItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: ${spacing.md};
  background: ${colors.background};
  border-radius: 4px;
  margin-bottom: ${spacing.sm};
`;

const SettingLabel = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.sm};
  color: ${colors.text};
`;

const Toggle = styled.label`
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;

  input {
    opacity: 0;
    width: 0;
    height: 0;
  }

  .slider {
    position: absolute;
    cursor: pointer;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-color: ${colors.border};
    transition: .4s;
    border-radius: 24px;

    &:before {
      position: absolute;
      content: "";
      height: 18px;
      width: 18px;
      left: 3px;
      bottom: 3px;
      background-color: white;
      transition: .4s;
      border-radius: 50%;
    }
  }

  input:checked + .slider {
    background-color: ${colors.primary};
  }

  input:checked + .slider:before {
    transform: translateX(24px);
  }
`;

const ColorPicker = styled.div`
  display: flex;
  gap: ${spacing.sm};
`;

const ColorOption = styled.button`
  width: 24px;
  height: 24px;
  border-radius: 50%;
  border: 2px solid ${props => props.isSelected ? colors.primary : 'transparent'};
  background: ${props => props.color};
  cursor: pointer;
  padding: 0;
  transition: transform 0.2s ease;

  &:hover {
    transform: scale(1.1);
  }
`;

const SettingsPanel = ({ onClose }) => {
  const { preferences, updatePreferences } = useCommandCenterStore();

  const handleThemeToggle = () => {
    updatePreferences({
      theme: preferences.theme === 'light' ? 'dark' : 'light'
    });
  };

  const handleNotificationsToggle = () => {
    updatePreferences({
      notifications: !preferences.notifications
    });
  };

  const handleColorSelect = (color) => {
    updatePreferences({
      accentColor: color
    });
  };

  return (
    <SettingsContainer>
      <Header>
        <Title>Settings</Title>
        <CloseButton onClick={onClose}>
          <FaTimes />
        </CloseButton>
      </Header>

      <Content>
        <Section>
          <SectionTitle>
            <FaMoon />
            Theme
          </SectionTitle>
          <SettingItem>
            <SettingLabel>Dark Mode</SettingLabel>
            <Toggle>
              <input
                type="checkbox"
                checked={preferences.theme === 'dark'}
                onChange={handleThemeToggle}
              />
              <span className="slider"></span>
            </Toggle>
          </SettingItem>
        </Section>

        <Section>
          <SectionTitle>
            <FaBell />
            Notifications
          </SectionTitle>
          <SettingItem>
            <SettingLabel>Enable Notifications</SettingLabel>
            <Toggle>
              <input
                type="checkbox"
                checked={preferences.notifications}
                onChange={handleNotificationsToggle}
              />
              <span className="slider"></span>
            </Toggle>
          </SettingItem>
        </Section>

        <Section>
          <SectionTitle>
            <FaPalette />
            Accent Color
          </SectionTitle>
          <ColorPicker>
            <ColorOption
              color="#3B82F6"
              isSelected={preferences.accentColor === '#3B82F6'}
              onClick={() => handleColorSelect('#3B82F6')}
            />
            <ColorOption
              color="#10B981"
              isSelected={preferences.accentColor === '#10B981'}
              onClick={() => handleColorSelect('#10B981')}
            />
            <ColorOption
              color="#F59E0B"
              isSelected={preferences.accentColor === '#F59E0B'}
              onClick={() => handleColorSelect('#F59E0B')}
            />
            <ColorOption
              color="#EF4444"
              isSelected={preferences.accentColor === '#EF4444'}
              onClick={() => handleColorSelect('#EF4444')}
            />
          </ColorPicker>
        </Section>
      </Content>
    </SettingsContainer>
  );
};

export default SettingsPanel; 