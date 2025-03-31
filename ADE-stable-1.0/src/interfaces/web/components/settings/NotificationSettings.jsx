import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaBell, FaEnvelope, FaDesktop, FaMobile, FaExclamationTriangle } from 'react-icons/fa';
import PropTypes from 'prop-types';
import { settingsService } from '../../services/settingsService';

const Section = styled.div`
  margin-bottom: 32px;
`;

const SectionHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 24px;
`;

const SectionTitle = styled.h2`
  font-size: 18px;
  color: #1e293b;
  margin: 0;
`;

const SectionDescription = styled.p`
  color: #64748b;
  margin: 4px 0 0 0;
  font-size: 14px;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const Label = styled.label`
  font-size: 14px;
  color: #64748b;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Button = styled.button`
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  align-self: flex-start;

  &:hover {
    background: #2563eb;
  }

  &:disabled {
    background: #94a3b8;
    cursor: not-allowed;
  }
`;

const ErrorMessage = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #fee2e2;
  color: #991b1b;
  padding: 12px 16px;
  border-radius: 6px;
`;

const NotificationGroup = styled.div`
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
`;

const NotificationHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
`;

const NotificationTitle = styled.h3`
  font-size: 16px;
  color: #1e293b;
  margin: 0;
`;

const NotificationDescription = styled.p`
  font-size: 14px;
  color: #64748b;
  margin: 0 0 12px 0;
`;

const NotificationOptions = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
`;

const NotificationOption = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px;
  background: white;
  border-radius: 6px;
  border: 1px solid #e2e8f0;
`;

const NotificationSettings = ({ onSettingChange }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    emailNotifications: {
      enabled: true,
      marketing: false,
      updates: true,
      security: true,
    },
    pushNotifications: {
      enabled: true,
      marketing: false,
      updates: true,
      security: true,
    },
    desktopNotifications: {
      enabled: true,
      marketing: false,
      updates: true,
      security: true,
    },
    mobileNotifications: {
      enabled: true,
      marketing: false,
      updates: true,
      security: true,
    },
    quietHours: {
      enabled: false,
      start: '22:00',
      end: '07:00',
    },
  });

  useEffect(() => {
    fetchNotificationSettings();
  }, []);

  const fetchNotificationSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await settingsService.getNotificationSettings();
      setFormData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    const [category, setting] = name.split('.');
    
    if (type === 'checkbox') {
      setFormData(prev => ({
        ...prev,
        [category]: {
          ...prev[category],
          [setting]: checked,
        },
      }));
    } else {
      setFormData(prev => ({
        ...prev,
        [category]: {
          ...prev[category],
          [setting]: value,
        },
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      await settingsService.updateNotificationSettings(formData);
      onSettingChange('Notification settings updated successfully');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Section>
      <SectionHeader>
        <FaBell />
        <div>
          <SectionTitle>Notifications</SectionTitle>
          <SectionDescription>Manage your notification preferences across different channels</SectionDescription>
        </div>
      </SectionHeader>

      {error && (
        <ErrorMessage>
          <FaExclamationTriangle />
          {error}
        </ErrorMessage>
      )}

      <Form onSubmit={handleSubmit}>
        <NotificationGroup>
          <NotificationHeader>
            <FaEnvelope />
            <NotificationTitle>Email Notifications</NotificationTitle>
          </NotificationHeader>
          <NotificationDescription>
            Receive notifications via email
          </NotificationDescription>
          <NotificationOptions>
            <NotificationOption>
              <input
                type="checkbox"
                name="emailNotifications.enabled"
                checked={formData.emailNotifications.enabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>Enable Email Notifications</Label>
            </NotificationOption>
            <NotificationOption>
              <input
                type="checkbox"
                name="emailNotifications.marketing"
                checked={formData.emailNotifications.marketing}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>Marketing Emails</Label>
            </NotificationOption>
            <NotificationOption>
              <input
                type="checkbox"
                name="emailNotifications.updates"
                checked={formData.emailNotifications.updates}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>Product Updates</Label>
            </NotificationOption>
            <NotificationOption>
              <input
                type="checkbox"
                name="emailNotifications.security"
                checked={formData.emailNotifications.security}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>Security Alerts</Label>
            </NotificationOption>
          </NotificationOptions>
        </NotificationGroup>

        <NotificationGroup>
          <NotificationHeader>
            <FaDesktop />
            <NotificationTitle>Desktop Notifications</NotificationTitle>
          </NotificationHeader>
          <NotificationDescription>
            Receive notifications on your desktop
          </NotificationDescription>
          <NotificationOptions>
            <NotificationOption>
              <input
                type="checkbox"
                name="desktopNotifications.enabled"
                checked={formData.desktopNotifications.enabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>Enable Desktop Notifications</Label>
            </NotificationOption>
            <NotificationOption>
              <input
                type="checkbox"
                name="desktopNotifications.marketing"
                checked={formData.desktopNotifications.marketing}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>Marketing Notifications</Label>
            </NotificationOption>
            <NotificationOption>
              <input
                type="checkbox"
                name="desktopNotifications.updates"
                checked={formData.desktopNotifications.updates}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>Product Updates</Label>
            </NotificationOption>
            <NotificationOption>
              <input
                type="checkbox"
                name="desktopNotifications.security"
                checked={formData.desktopNotifications.security}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>Security Alerts</Label>
            </NotificationOption>
          </NotificationOptions>
        </NotificationGroup>

        <NotificationGroup>
          <NotificationHeader>
            <FaMobile />
            <NotificationTitle>Mobile Notifications</NotificationTitle>
          </NotificationHeader>
          <NotificationDescription>
            Receive notifications on your mobile device
          </NotificationDescription>
          <NotificationOptions>
            <NotificationOption>
              <input
                type="checkbox"
                name="mobileNotifications.enabled"
                checked={formData.mobileNotifications.enabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>Enable Mobile Notifications</Label>
            </NotificationOption>
            <NotificationOption>
              <input
                type="checkbox"
                name="mobileNotifications.marketing"
                checked={formData.mobileNotifications.marketing}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>Marketing Notifications</Label>
            </NotificationOption>
            <NotificationOption>
              <input
                type="checkbox"
                name="mobileNotifications.updates"
                checked={formData.mobileNotifications.updates}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>Product Updates</Label>
            </NotificationOption>
            <NotificationOption>
              <input
                type="checkbox"
                name="mobileNotifications.security"
                checked={formData.mobileNotifications.security}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>Security Alerts</Label>
            </NotificationOption>
          </NotificationOptions>
        </NotificationGroup>

        <NotificationGroup>
          <NotificationHeader>
            <FaBell />
            <NotificationTitle>Quiet Hours</NotificationTitle>
          </NotificationHeader>
          <NotificationDescription>
            Configure when you don't want to receive notifications
          </NotificationDescription>
          <NotificationOptions>
            <NotificationOption>
              <input
                type="checkbox"
                name="quietHours.enabled"
                checked={formData.quietHours.enabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>Enable Quiet Hours</Label>
            </NotificationOption>
            <NotificationOption>
              <input
                type="time"
                name="quietHours.start"
                value={formData.quietHours.start}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>Start Time</Label>
            </NotificationOption>
            <NotificationOption>
              <input
                type="time"
                name="quietHours.end"
                value={formData.quietHours.end}
                onChange={handleInputChange}
                disabled={loading}
              />
              <Label>End Time</Label>
            </NotificationOption>
          </NotificationOptions>
        </NotificationGroup>

        <Button type="submit" disabled={loading}>
          Save Changes
        </Button>
      </Form>
    </Section>
  );
};

NotificationSettings.propTypes = {
  onSettingChange: PropTypes.func.isRequired,
};

export default NotificationSettings; 