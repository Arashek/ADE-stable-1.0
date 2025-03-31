import React, { useState } from 'react';
import styled from 'styled-components';
import { FaSave, FaUser, FaLock, FaBell, FaPalette, FaCode } from 'react-icons/fa';

const SettingsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
  max-width: 800px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h1`
  font-size: 24px;
  color: #1e293b;
`;

const SaveButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background: #2563eb;
  }
`;

const SettingsSection = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
`;

const SectionTitle = styled.h2`
  font-size: 18px;
  color: #1e293b;
  margin: 0;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  color: #64748b;
  font-size: 14px;
`;

const Input = styled.input`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  color: #1e293b;

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  color: #1e293b;
  background: white;

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
  }
`;

const Switch = styled.label`
  display: inline-flex;
  align-items: center;
  cursor: pointer;
`;

const SwitchInput = styled.input`
  display: none;
`;

const SwitchSlider = styled.span`
  position: relative;
  display: inline-block;
  width: 48px;
  height: 24px;
  background: #e2e8f0;
  border-radius: 12px;
  transition: background-color 0.2s;

  &:before {
    content: '';
    position: absolute;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    background: white;
    top: 2px;
    left: 2px;
    transition: transform 0.2s;
  }

  ${SwitchInput}:checked + & {
    background: #3b82f6;
  }

  ${SwitchInput}:checked + &:before {
    transform: translateX(24px);
  }
`;

const Settings = () => {
  const [settings, setSettings] = useState({
    profile: {
      name: 'John Doe',
      email: 'john@example.com',
      language: 'en',
    },
    security: {
      twoFactor: false,
      emailNotifications: true,
    },
    appearance: {
      theme: 'light',
      fontSize: 'medium',
    },
    notifications: {
      email: true,
      push: true,
      desktop: false,
    },
  });

  const handleChange = (section, field, value) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [field]: value,
      },
    }));
  };

  const handleSave = () => {
    // TODO: Implement save functionality
    console.log('Saving settings:', settings);
  };

  return (
    <SettingsContainer>
      <Header>
        <Title>Settings</Title>
        <SaveButton onClick={handleSave}>
          <FaSave />
          Save Changes
        </SaveButton>
      </Header>

      <SettingsSection>
        <SectionHeader>
          <FaUser color="#64748b" />
          <SectionTitle>Profile Settings</SectionTitle>
        </SectionHeader>
        <FormGroup>
          <Label>Name</Label>
          <Input
            type="text"
            value={settings.profile.name}
            onChange={(e) => handleChange('profile', 'name', e.target.value)}
          />
        </FormGroup>
        <FormGroup>
          <Label>Email</Label>
          <Input
            type="email"
            value={settings.profile.email}
            onChange={(e) => handleChange('profile', 'email', e.target.value)}
          />
        </FormGroup>
        <FormGroup>
          <Label>Language</Label>
          <Select
            value={settings.profile.language}
            onChange={(e) => handleChange('profile', 'language', e.target.value)}
          >
            <option value="en">English</option>
            <option value="es">Spanish</option>
            <option value="fr">French</option>
            <option value="de">German</option>
          </Select>
        </FormGroup>
      </SettingsSection>

      <SettingsSection>
        <SectionHeader>
          <FaLock color="#64748b" />
          <SectionTitle>Security</SectionTitle>
        </SectionHeader>
        <FormGroup>
          <Switch>
            <SwitchInput
              type="checkbox"
              checked={settings.security.twoFactor}
              onChange={(e) => handleChange('security', 'twoFactor', e.target.checked)}
            />
            <SwitchSlider />
            <span style={{ marginLeft: '12px' }}>Two-Factor Authentication</span>
          </Switch>
        </FormGroup>
        <FormGroup>
          <Switch>
            <SwitchInput
              type="checkbox"
              checked={settings.security.emailNotifications}
              onChange={(e) => handleChange('security', 'emailNotifications', e.target.checked)}
            />
            <SwitchSlider />
            <span style={{ marginLeft: '12px' }}>Email Notifications</span>
          </Switch>
        </FormGroup>
      </SettingsSection>

      <SettingsSection>
        <SectionHeader>
          <FaPalette color="#64748b" />
          <SectionTitle>Appearance</SectionTitle>
        </SectionHeader>
        <FormGroup>
          <Label>Theme</Label>
          <Select
            value={settings.appearance.theme}
            onChange={(e) => handleChange('appearance', 'theme', e.target.value)}
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System</option>
          </Select>
        </FormGroup>
        <FormGroup>
          <Label>Font Size</Label>
          <Select
            value={settings.appearance.fontSize}
            onChange={(e) => handleChange('appearance', 'fontSize', e.target.value)}
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </Select>
        </FormGroup>
      </SettingsSection>

      <SettingsSection>
        <SectionHeader>
          <FaBell color="#64748b" />
          <SectionTitle>Notifications</SectionTitle>
        </SectionHeader>
        <FormGroup>
          <Switch>
            <SwitchInput
              type="checkbox"
              checked={settings.notifications.email}
              onChange={(e) => handleChange('notifications', 'email', e.target.checked)}
            />
            <SwitchSlider />
            <span style={{ marginLeft: '12px' }}>Email Notifications</span>
          </Switch>
        </FormGroup>
        <FormGroup>
          <Switch>
            <SwitchInput
              type="checkbox"
              checked={settings.notifications.push}
              onChange={(e) => handleChange('notifications', 'push', e.target.checked)}
            />
            <SwitchSlider />
            <span style={{ marginLeft: '12px' }}>Push Notifications</span>
          </Switch>
        </FormGroup>
        <FormGroup>
          <Switch>
            <SwitchInput
              type="checkbox"
              checked={settings.notifications.desktop}
              onChange={(e) => handleChange('notifications', 'desktop', e.target.checked)}
            />
            <SwitchSlider />
            <span style={{ marginLeft: '12px' }}>Desktop Notifications</span>
          </Switch>
        </FormGroup>
      </SettingsSection>

      <SettingsSection>
        <SectionHeader>
          <FaCode color="#64748b" />
          <SectionTitle>API Settings</SectionTitle>
        </SectionHeader>
        <FormGroup>
          <Label>API Key</Label>
          <Input
            type="password"
            value="••••••••••••••••"
            readOnly
          />
        </FormGroup>
        <FormGroup>
          <Label>API Secret</Label>
          <Input
            type="password"
            value="••••••••••••••••"
            readOnly
          />
        </FormGroup>
      </SettingsSection>
    </SettingsContainer>
  );
};

export default Settings; 