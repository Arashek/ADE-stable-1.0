import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaPlug, FaGithub, FaGoogle, FaSlack, FaExclamationTriangle } from 'react-icons/fa';
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

const Input = styled.input`
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
  }

  &:disabled {
    background: #f1f5f9;
    cursor: not-allowed;
  }
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

const IntegrationGroup = styled.div`
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
`;

const IntegrationHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
`;

const IntegrationTitle = styled.h3`
  font-size: 16px;
  color: #1e293b;
  margin: 0;
`;

const IntegrationDescription = styled.p`
  font-size: 14px;
  color: #64748b;
  margin: 0 0 12px 0;
`;

const StatusBadge = styled.span`
  display: inline-flex;
  align-items: center;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => props.connected ? '#dcfce7' : '#fee2e2'};
  color: ${props => props.connected ? '#166534' : '#991b1b'};
`;

const IntegrationSettings = ({ onSettingChange }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    github: {
      enabled: false,
      clientId: '',
      clientSecret: '',
      organization: '',
      repositories: [],
      webhookSecret: '',
    },
    google: {
      enabled: false,
      clientId: '',
      clientSecret: '',
      redirectUri: '',
      scopes: ['email', 'profile'],
    },
    slack: {
      enabled: false,
      botToken: '',
      signingSecret: '',
      defaultChannel: '',
      notifications: {
        enabled: true,
        mentions: true,
        directMessages: true,
      },
    },
    email: {
      enabled: false,
      provider: 'smtp',
      host: '',
      port: 587,
      username: '',
      password: '',
      fromAddress: '',
      useTls: true,
    },
    storage: {
      enabled: false,
      provider: 's3',
      accessKey: '',
      secretKey: '',
      bucket: '',
      region: '',
      endpoint: '',
    },
  });

  useEffect(() => {
    fetchIntegrationSettings();
  }, []);

  const fetchIntegrationSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await settingsService.getIntegrationSettings();
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

  const handleNotificationChange = (e) => {
    const { name, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      slack: {
        ...prev.slack,
        notifications: {
          ...prev.slack.notifications,
          [name]: checked,
        },
      },
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      await settingsService.updateIntegrationSettings(formData);
      onSettingChange('Integration settings updated successfully');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Section>
      <SectionHeader>
        <FaPlug />
        <div>
          <SectionTitle>Integration Settings</SectionTitle>
          <SectionDescription>Configure third-party service connections and integrations</SectionDescription>
        </div>
      </SectionHeader>

      {error && (
        <ErrorMessage>
          <FaExclamationTriangle />
          {error}
        </ErrorMessage>
      )}

      <Form onSubmit={handleSubmit}>
        <IntegrationGroup>
          <IntegrationHeader>
            <FaGithub />
            <IntegrationTitle>GitHub Integration</IntegrationTitle>
            <StatusBadge connected={formData.github.enabled}>
              {formData.github.enabled ? 'Connected' : 'Disconnected'}
            </StatusBadge>
          </IntegrationHeader>
          <IntegrationDescription>
            Connect your GitHub account for repository access and webhook notifications
          </IntegrationDescription>
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="github.enabled"
                checked={formData.github.enabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable GitHub Integration
            </Label>
          </FormGroup>
          {formData.github.enabled && (
            <>
              <FormGroup>
                <Label>Client ID</Label>
                <Input
                  type="text"
                  name="github.clientId"
                  value={formData.github.clientId}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Client Secret</Label>
                <Input
                  type="password"
                  name="github.clientSecret"
                  value={formData.github.clientSecret}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Organization</Label>
                <Input
                  type="text"
                  name="github.organization"
                  value={formData.github.organization}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Webhook Secret</Label>
                <Input
                  type="password"
                  name="github.webhookSecret"
                  value={formData.github.webhookSecret}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
            </>
          )}
        </IntegrationGroup>

        <IntegrationGroup>
          <IntegrationHeader>
            <FaGoogle />
            <IntegrationTitle>Google Integration</IntegrationTitle>
            <StatusBadge connected={formData.google.enabled}>
              {formData.google.enabled ? 'Connected' : 'Disconnected'}
            </StatusBadge>
          </IntegrationHeader>
          <IntegrationDescription>
            Connect your Google account for authentication and calendar integration
          </IntegrationDescription>
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="google.enabled"
                checked={formData.google.enabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable Google Integration
            </Label>
          </FormGroup>
          {formData.google.enabled && (
            <>
              <FormGroup>
                <Label>Client ID</Label>
                <Input
                  type="text"
                  name="google.clientId"
                  value={formData.google.clientId}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Client Secret</Label>
                <Input
                  type="password"
                  name="google.clientSecret"
                  value={formData.google.clientSecret}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Redirect URI</Label>
                <Input
                  type="text"
                  name="google.redirectUri"
                  value={formData.google.redirectUri}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
            </>
          )}
        </IntegrationGroup>

        <IntegrationGroup>
          <IntegrationHeader>
            <FaSlack />
            <IntegrationTitle>Slack Integration</IntegrationTitle>
            <StatusBadge connected={formData.slack.enabled}>
              {formData.slack.enabled ? 'Connected' : 'Disconnected'}
            </StatusBadge>
          </IntegrationHeader>
          <IntegrationDescription>
            Connect your Slack workspace for notifications and team collaboration
          </IntegrationDescription>
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="slack.enabled"
                checked={formData.slack.enabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable Slack Integration
            </Label>
          </FormGroup>
          {formData.slack.enabled && (
            <>
              <FormGroup>
                <Label>Bot Token</Label>
                <Input
                  type="password"
                  name="slack.botToken"
                  value={formData.slack.botToken}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Signing Secret</Label>
                <Input
                  type="password"
                  name="slack.signingSecret"
                  value={formData.slack.signingSecret}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Default Channel</Label>
                <Input
                  type="text"
                  name="slack.defaultChannel"
                  value={formData.slack.defaultChannel}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Notification Settings</Label>
                <div>
                  <Label>
                    <input
                      type="checkbox"
                      name="mentions"
                      checked={formData.slack.notifications.mentions}
                      onChange={handleNotificationChange}
                      disabled={loading}
                    />
                    Enable @mentions
                  </Label>
                  <Label>
                    <input
                      type="checkbox"
                      name="directMessages"
                      checked={formData.slack.notifications.directMessages}
                      onChange={handleNotificationChange}
                      disabled={loading}
                    />
                    Enable Direct Messages
                  </Label>
                </div>
              </FormGroup>
            </>
          )}
        </IntegrationGroup>

        <IntegrationGroup>
          <IntegrationHeader>
            <FaPlug />
            <IntegrationTitle>Email Integration</IntegrationTitle>
            <StatusBadge connected={formData.email.enabled}>
              {formData.email.enabled ? 'Connected' : 'Disconnected'}
            </StatusBadge>
          </IntegrationHeader>
          <IntegrationDescription>
            Configure email service for notifications and communications
          </IntegrationDescription>
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="email.enabled"
                checked={formData.email.enabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable Email Integration
            </Label>
          </FormGroup>
          {formData.email.enabled && (
            <>
              <FormGroup>
                <Label>Provider</Label>
                <select
                  name="email.provider"
                  value={formData.email.provider}
                  onChange={handleInputChange}
                  disabled={loading}
                >
                  <option value="smtp">SMTP</option>
                  <option value="sendgrid">SendGrid</option>
                  <option value="mailgun">Mailgun</option>
                </select>
              </FormGroup>
              <FormGroup>
                <Label>Host</Label>
                <Input
                  type="text"
                  name="email.host"
                  value={formData.email.host}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Port</Label>
                <Input
                  type="number"
                  name="email.port"
                  value={formData.email.port}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Username</Label>
                <Input
                  type="text"
                  name="email.username"
                  value={formData.email.username}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Password</Label>
                <Input
                  type="password"
                  name="email.password"
                  value={formData.email.password}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>From Address</Label>
                <Input
                  type="email"
                  name="email.fromAddress"
                  value={formData.email.fromAddress}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>
                  <input
                    type="checkbox"
                    name="email.useTls"
                    checked={formData.email.useTls}
                    onChange={handleInputChange}
                    disabled={loading}
                  />
                  Use TLS
                </Label>
              </FormGroup>
            </>
          )}
        </IntegrationGroup>

        <IntegrationGroup>
          <IntegrationHeader>
            <FaPlug />
            <IntegrationTitle>Storage Integration</IntegrationTitle>
            <StatusBadge connected={formData.storage.enabled}>
              {formData.storage.enabled ? 'Connected' : 'Disconnected'}
            </StatusBadge>
          </IntegrationHeader>
          <IntegrationDescription>
            Configure cloud storage for file uploads and data storage
          </IntegrationDescription>
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="storage.enabled"
                checked={formData.storage.enabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable Storage Integration
            </Label>
          </FormGroup>
          {formData.storage.enabled && (
            <>
              <FormGroup>
                <Label>Provider</Label>
                <select
                  name="storage.provider"
                  value={formData.storage.provider}
                  onChange={handleInputChange}
                  disabled={loading}
                >
                  <option value="s3">Amazon S3</option>
                  <option value="gcs">Google Cloud Storage</option>
                  <option value="azure">Azure Blob Storage</option>
                </select>
              </FormGroup>
              <FormGroup>
                <Label>Access Key</Label>
                <Input
                  type="text"
                  name="storage.accessKey"
                  value={formData.storage.accessKey}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Secret Key</Label>
                <Input
                  type="password"
                  name="storage.secretKey"
                  value={formData.storage.secretKey}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Bucket</Label>
                <Input
                  type="text"
                  name="storage.bucket"
                  value={formData.storage.bucket}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Region</Label>
                <Input
                  type="text"
                  name="storage.region"
                  value={formData.storage.region}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Endpoint</Label>
                <Input
                  type="text"
                  name="storage.endpoint"
                  value={formData.storage.endpoint}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
            </>
          )}
        </IntegrationGroup>

        <Button type="submit" disabled={loading}>
          Save Changes
        </Button>
      </Form>
    </Section>
  );
};

IntegrationSettings.propTypes = {
  onSettingChange: PropTypes.func.isRequired,
};

export default IntegrationSettings; 