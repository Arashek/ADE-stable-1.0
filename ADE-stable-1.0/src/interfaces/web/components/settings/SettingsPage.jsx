import React, { useState } from 'react';
import styled from 'styled-components';
import { FaUser, FaPalette, FaBell, FaShieldAlt, FaCog, FaPlug, FaCheck } from 'react-icons/fa';
import PropTypes from 'prop-types';
import UserProfileSettings from './UserProfileSettings';
import AppearanceSettings from './AppearanceSettings';
import NotificationSettings from './NotificationSettings';
import SecuritySettings from './SecuritySettings';
import SystemSettings from './SystemSettings';
import IntegrationSettings from './IntegrationSettings';

const PageContainer = styled.div`
  padding: 24px;
  background: #f8fafc;
  min-height: calc(100vh - 64px);
`;

const Header = styled.div`
  margin-bottom: 32px;
`;

const Title = styled.h1`
  font-size: 24px;
  color: #1e293b;
  margin: 0 0 8px 0;
`;

const Description = styled.p`
  color: #64748b;
  margin: 0;
`;

const Content = styled.div`
  display: flex;
  gap: 24px;
`;

const Sidebar = styled.div`
  width: 240px;
  flex-shrink: 0;
`;

const MainContent = styled.div`
  flex: 1;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 24px;
`;

const NavList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const NavItem = styled.button`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border: none;
  background: ${props => props.active ? '#eff6ff' : 'transparent'};
  color: ${props => props.active ? '#2563eb' : '#64748b'};
  border-radius: 6px;
  cursor: pointer;
  width: 100%;
  text-align: left;
  font-size: 14px;
  transition: all 0.2s;

  &:hover {
    background: #f1f5f9;
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`;

const NavIcon = styled.div`
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
`;

const SuccessMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #dcfce7;
  color: #166534;
  padding: 12px 16px;
  border-radius: 6px;
  margin-bottom: 16px;
`;

const SettingsPage = () => {
  const [activeSection, setActiveSection] = useState('profile');
  const [successMessage, setSuccessMessage] = useState(null);

  const sections = [
    { id: 'profile', label: 'Profile', icon: <FaUser />, component: UserProfileSettings },
    { id: 'appearance', label: 'Appearance', icon: <FaPalette />, component: AppearanceSettings },
    { id: 'notifications', label: 'Notifications', icon: <FaBell />, component: NotificationSettings },
    { id: 'security', label: 'Security', icon: <FaShieldAlt />, component: SecuritySettings },
    { id: 'system', label: 'System', icon: <FaCog />, component: SystemSettings },
    { id: 'integrations', label: 'Integrations', icon: <FaPlug />, component: IntegrationSettings },
  ];

  const handleSettingChange = (message) => {
    setSuccessMessage(message);
    setTimeout(() => setSuccessMessage(null), 3000);
  };

  const ActiveComponent = sections.find(s => s.id === activeSection)?.component;

  return (
    <PageContainer>
      <Header>
        <Title>Settings</Title>
        <Description>Manage your account settings and preferences</Description>
      </Header>

      <Content>
        <Sidebar>
          <NavList>
            {sections.map(section => (
              <NavItem
                key={section.id}
                active={activeSection === section.id}
                onClick={() => setActiveSection(section.id)}
              >
                <NavIcon>{section.icon}</NavIcon>
                {section.label}
              </NavItem>
            ))}
          </NavList>
        </Sidebar>

        <MainContent>
          {successMessage && (
            <SuccessMessage>
              <FaCheck />
              {successMessage}
            </SuccessMessage>
          )}

          {ActiveComponent && (
            <ActiveComponent onSettingChange={handleSettingChange} />
          )}
        </MainContent>
      </Content>
    </PageContainer>
  );
};

export default SettingsPage; 