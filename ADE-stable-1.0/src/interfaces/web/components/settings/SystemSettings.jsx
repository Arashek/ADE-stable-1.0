import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaCog, FaDatabase, FaServer, FaNetworkWired, FaExclamationTriangle } from 'react-icons/fa';
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

const Select = styled.select`
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  transition: all 0.2s;
  background: white;

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

const SystemGroup = styled.div`
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
`;

const SystemHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
`;

const SystemTitle = styled.h3`
  font-size: 16px;
  color: #1e293b;
  margin: 0;
`;

const SystemDescription = styled.p`
  font-size: 14px;
  color: #64748b;
  margin: 0 0 12px 0;
`;

const SystemSettings = ({ onSettingChange }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    database: {
      type: 'postgresql',
      host: '',
      port: 5432,
      name: '',
      username: '',
      password: '',
      maxConnections: 100,
      backupEnabled: true,
      backupFrequency: 'daily',
      retentionDays: 30,
    },
    server: {
      port: 3000,
      host: '0.0.0.0',
      maxRequestsPerMinute: 100,
      timeout: 30,
      corsEnabled: true,
      allowedOrigins: ['*'],
      sslEnabled: false,
      sslCertPath: '',
      sslKeyPath: '',
    },
    logging: {
      level: 'info',
      fileEnabled: true,
      filePath: '/var/log/ade-platform/app.log',
      maxSize: 100,
      maxFiles: 10,
      consoleEnabled: true,
    },
    cache: {
      enabled: true,
      type: 'redis',
      host: 'localhost',
      port: 6379,
      password: '',
      ttl: 3600,
      maxSize: 1000,
    },
    monitoring: {
      enabled: true,
      metricsEnabled: true,
      healthCheckEnabled: true,
      alertingEnabled: true,
      prometheusEnabled: true,
      grafanaEnabled: true,
    },
  });

  useEffect(() => {
    fetchSystemSettings();
  }, []);

  const fetchSystemSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await settingsService.getSystemSettings();
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
      await settingsService.updateSystemSettings(formData);
      onSettingChange('System settings updated successfully');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Section>
      <SectionHeader>
        <FaCog />
        <div>
          <SectionTitle>System Settings</SectionTitle>
          <SectionDescription>Configure system-wide settings and preferences</SectionDescription>
        </div>
      </SectionHeader>

      {error && (
        <ErrorMessage>
          <FaExclamationTriangle />
          {error}
        </ErrorMessage>
      )}

      <Form onSubmit={handleSubmit}>
        <SystemGroup>
          <SystemHeader>
            <FaDatabase />
            <SystemTitle>Database Configuration</SystemTitle>
          </SystemHeader>
          <SystemDescription>
            Configure database connection and backup settings
          </SystemDescription>
          <FormGroup>
            <Label>Database Type</Label>
            <Select
              name="database.type"
              value={formData.database.type}
              onChange={handleInputChange}
              disabled={loading}
            >
              <option value="postgresql">PostgreSQL</option>
              <option value="mysql">MySQL</option>
              <option value="mongodb">MongoDB</option>
            </Select>
          </FormGroup>
          <FormGroup>
            <Label>Host</Label>
            <Input
              type="text"
              name="database.host"
              value={formData.database.host}
              onChange={handleInputChange}
              disabled={loading}
            />
          </FormGroup>
          <FormGroup>
            <Label>Port</Label>
            <Input
              type="number"
              name="database.port"
              value={formData.database.port}
              onChange={handleInputChange}
              disabled={loading}
            />
          </FormGroup>
          <FormGroup>
            <Label>Database Name</Label>
            <Input
              type="text"
              name="database.name"
              value={formData.database.name}
              onChange={handleInputChange}
              disabled={loading}
            />
          </FormGroup>
          <FormGroup>
            <Label>Username</Label>
            <Input
              type="text"
              name="database.username"
              value={formData.database.username}
              onChange={handleInputChange}
              disabled={loading}
            />
          </FormGroup>
          <FormGroup>
            <Label>Password</Label>
            <Input
              type="password"
              name="database.password"
              value={formData.database.password}
              onChange={handleInputChange}
              disabled={loading}
            />
          </FormGroup>
          <FormGroup>
            <Label>Max Connections</Label>
            <Input
              type="number"
              name="database.maxConnections"
              value={formData.database.maxConnections}
              onChange={handleInputChange}
              disabled={loading}
            />
          </FormGroup>
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="database.backupEnabled"
                checked={formData.database.backupEnabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable Automatic Backups
            </Label>
          </FormGroup>
          {formData.database.backupEnabled && (
            <>
              <FormGroup>
                <Label>Backup Frequency</Label>
                <Select
                  name="database.backupFrequency"
                  value={formData.database.backupFrequency}
                  onChange={handleInputChange}
                  disabled={loading}
                >
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </Select>
              </FormGroup>
              <FormGroup>
                <Label>Retention Period (days)</Label>
                <Input
                  type="number"
                  name="database.retentionDays"
                  value={formData.database.retentionDays}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
            </>
          )}
        </SystemGroup>

        <SystemGroup>
          <SystemHeader>
            <FaServer />
            <SystemTitle>Server Configuration</SystemTitle>
          </SystemHeader>
          <SystemDescription>
            Configure server settings and security
          </SystemDescription>
          <FormGroup>
            <Label>Port</Label>
            <Input
              type="number"
              name="server.port"
              value={formData.server.port}
              onChange={handleInputChange}
              disabled={loading}
            />
          </FormGroup>
          <FormGroup>
            <Label>Host</Label>
            <Input
              type="text"
              name="server.host"
              value={formData.server.host}
              onChange={handleInputChange}
              disabled={loading}
            />
          </FormGroup>
          <FormGroup>
            <Label>Max Requests per Minute</Label>
            <Input
              type="number"
              name="server.maxRequestsPerMinute"
              value={formData.server.maxRequestsPerMinute}
              onChange={handleInputChange}
              disabled={loading}
            />
          </FormGroup>
          <FormGroup>
            <Label>Timeout (seconds)</Label>
            <Input
              type="number"
              name="server.timeout"
              value={formData.server.timeout}
              onChange={handleInputChange}
              disabled={loading}
            />
          </FormGroup>
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="server.corsEnabled"
                checked={formData.server.corsEnabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable CORS
            </Label>
          </FormGroup>
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="server.sslEnabled"
                checked={formData.server.sslEnabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable SSL
            </Label>
          </FormGroup>
          {formData.server.sslEnabled && (
            <>
              <FormGroup>
                <Label>SSL Certificate Path</Label>
                <Input
                  type="text"
                  name="server.sslCertPath"
                  value={formData.server.sslCertPath}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>SSL Key Path</Label>
                <Input
                  type="text"
                  name="server.sslKeyPath"
                  value={formData.server.sslKeyPath}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
            </>
          )}
        </SystemGroup>

        <SystemGroup>
          <SystemHeader>
            <FaNetworkWired />
            <SystemTitle>Logging Configuration</SystemTitle>
          </SystemHeader>
          <SystemDescription>
            Configure logging settings and file management
          </SystemDescription>
          <FormGroup>
            <Label>Log Level</Label>
            <Select
              name="logging.level"
              value={formData.logging.level}
              onChange={handleInputChange}
              disabled={loading}
            >
              <option value="debug">Debug</option>
              <option value="info">Info</option>
              <option value="warn">Warn</option>
              <option value="error">Error</option>
            </Select>
          </FormGroup>
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="logging.fileEnabled"
                checked={formData.logging.fileEnabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable File Logging
            </Label>
          </FormGroup>
          {formData.logging.fileEnabled && (
            <>
              <FormGroup>
                <Label>Log File Path</Label>
                <Input
                  type="text"
                  name="logging.filePath"
                  value={formData.logging.filePath}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Max File Size (MB)</Label>
                <Input
                  type="number"
                  name="logging.maxSize"
                  value={formData.logging.maxSize}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Max Files</Label>
                <Input
                  type="number"
                  name="logging.maxFiles"
                  value={formData.logging.maxFiles}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
            </>
          )}
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="logging.consoleEnabled"
                checked={formData.logging.consoleEnabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable Console Logging
            </Label>
          </FormGroup>
        </SystemGroup>

        <SystemGroup>
          <SystemHeader>
            <FaCog />
            <SystemTitle>Cache Configuration</SystemTitle>
          </SystemHeader>
          <SystemDescription>
            Configure caching settings and performance
          </SystemDescription>
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="cache.enabled"
                checked={formData.cache.enabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable Caching
            </Label>
          </FormGroup>
          {formData.cache.enabled && (
            <>
              <FormGroup>
                <Label>Cache Type</Label>
                <Select
                  name="cache.type"
                  value={formData.cache.type}
                  onChange={handleInputChange}
                  disabled={loading}
                >
                  <option value="redis">Redis</option>
                  <option value="memcached">Memcached</option>
                  <option value="memory">In-Memory</option>
                </Select>
              </FormGroup>
              <FormGroup>
                <Label>Host</Label>
                <Input
                  type="text"
                  name="cache.host"
                  value={formData.cache.host}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Port</Label>
                <Input
                  type="number"
                  name="cache.port"
                  value={formData.cache.port}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Password</Label>
                <Input
                  type="password"
                  name="cache.password"
                  value={formData.cache.password}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>TTL (seconds)</Label>
                <Input
                  type="number"
                  name="cache.ttl"
                  value={formData.cache.ttl}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
              <FormGroup>
                <Label>Max Size (items)</Label>
                <Input
                  type="number"
                  name="cache.maxSize"
                  value={formData.cache.maxSize}
                  onChange={handleInputChange}
                  disabled={loading}
                />
              </FormGroup>
            </>
          )}
        </SystemGroup>

        <SystemGroup>
          <SystemHeader>
            <FaCog />
            <SystemTitle>Monitoring Configuration</SystemTitle>
          </SystemHeader>
          <SystemDescription>
            Configure monitoring and alerting settings
          </SystemDescription>
          <FormGroup>
            <Label>
              <input
                type="checkbox"
                name="monitoring.enabled"
                checked={formData.monitoring.enabled}
                onChange={handleInputChange}
                disabled={loading}
              />
              Enable Monitoring
            </Label>
          </FormGroup>
          {formData.monitoring.enabled && (
            <>
              <FormGroup>
                <Label>
                  <input
                    type="checkbox"
                    name="monitoring.metricsEnabled"
                    checked={formData.monitoring.metricsEnabled}
                    onChange={handleInputChange}
                    disabled={loading}
                  />
                  Enable Metrics Collection
                </Label>
              </FormGroup>
              <FormGroup>
                <Label>
                  <input
                    type="checkbox"
                    name="monitoring.healthCheckEnabled"
                    checked={formData.monitoring.healthCheckEnabled}
                    onChange={handleInputChange}
                    disabled={loading}
                  />
                  Enable Health Checks
                </Label>
              </FormGroup>
              <FormGroup>
                <Label>
                  <input
                    type="checkbox"
                    name="monitoring.alertingEnabled"
                    checked={formData.monitoring.alertingEnabled}
                    onChange={handleInputChange}
                    disabled={loading}
                  />
                  Enable Alerting
                </Label>
              </FormGroup>
              <FormGroup>
                <Label>
                  <input
                    type="checkbox"
                    name="monitoring.prometheusEnabled"
                    checked={formData.monitoring.prometheusEnabled}
                    onChange={handleInputChange}
                    disabled={loading}
                  />
                  Enable Prometheus Integration
                </Label>
              </FormGroup>
              <FormGroup>
                <Label>
                  <input
                    type="checkbox"
                    name="monitoring.grafanaEnabled"
                    checked={formData.monitoring.grafanaEnabled}
                    onChange={handleInputChange}
                    disabled={loading}
                  />
                  Enable Grafana Integration
                </Label>
              </FormGroup>
            </>
          )}
        </SystemGroup>

        <Button type="submit" disabled={loading}>
          Save Changes
        </Button>
      </Form>
    </Section>
  );
};

SystemSettings.propTypes = {
  onSettingChange: PropTypes.func.isRequired,
};

export default SystemSettings; 