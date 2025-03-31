import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaPalette, FaMoon, FaFont, FaExclamationTriangle } from 'react-icons/fa';
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

const Select = styled.select`
  padding: 8px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  font-size: 14px;
  background: white;
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

const ColorPicker = styled.input`
  width: 100%;
  height: 40px;
  padding: 4px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  cursor: pointer;

  &:disabled {
    opacity: 0.5;
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

const PreviewSection = styled.div`
  background: ${props => props.theme === 'dark' ? '#1e293b' : '#f8fafc'};
  border-radius: 8px;
  padding: 24px;
  margin-top: 16px;
  transition: all 0.3s;
`;

const PreviewText = styled.p`
  color: ${props => props.theme === 'dark' ? '#e2e8f0' : '#1e293b'};
  font-family: ${props => props.fontFamily};
  font-size: 16px;
  margin: 0;
`;

const AppearanceSettings = ({ onSettingChange }) => {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState({
    theme: 'light',
    primaryColor: '#3b82f6',
    fontFamily: 'Inter',
    fontSize: 'medium',
    compactMode: false,
    animations: true,
  });

  useEffect(() => {
    fetchAppearanceSettings();
  }, []);

  const fetchAppearanceSettings = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await settingsService.getAppearanceSettings();
      setFormData(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      setLoading(true);
      setError(null);
      await settingsService.updateAppearanceSettings(formData);
      onSettingChange('Appearance settings updated successfully');
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Section>
      <SectionHeader>
        <FaPalette />
        <div>
          <SectionTitle>Appearance</SectionTitle>
          <SectionDescription>Customize the look and feel of your interface</SectionDescription>
        </div>
      </SectionHeader>

      {error && (
        <ErrorMessage>
          <FaExclamationTriangle />
          {error}
        </ErrorMessage>
      )}

      <Form onSubmit={handleSubmit}>
        <FormGroup>
          <Label>Theme</Label>
          <Select
            name="theme"
            value={formData.theme}
            onChange={handleInputChange}
            disabled={loading}
          >
            <option value="light">Light</option>
            <option value="dark">Dark</option>
            <option value="system">System</option>
          </Select>
        </FormGroup>

        <FormGroup>
          <Label>Primary Color</Label>
          <ColorPicker
            type="color"
            name="primaryColor"
            value={formData.primaryColor}
            onChange={handleInputChange}
            disabled={loading}
          />
        </FormGroup>

        <FormGroup>
          <Label>Font Family</Label>
          <Select
            name="fontFamily"
            value={formData.fontFamily}
            onChange={handleInputChange}
            disabled={loading}
          >
            <option value="Inter">Inter</option>
            <option value="Roboto">Roboto</option>
            <option value="Open Sans">Open Sans</option>
            <option value="Lato">Lato</option>
          </Select>
        </FormGroup>

        <FormGroup>
          <Label>Font Size</Label>
          <Select
            name="fontSize"
            value={formData.fontSize}
            onChange={handleInputChange}
            disabled={loading}
          >
            <option value="small">Small</option>
            <option value="medium">Medium</option>
            <option value="large">Large</option>
          </Select>
        </FormGroup>

        <FormGroup>
          <Label>
            <input
              type="checkbox"
              name="compactMode"
              checked={formData.compactMode}
              onChange={handleInputChange}
              disabled={loading}
            />
            Compact Mode
          </Label>
        </FormGroup>

        <FormGroup>
          <Label>
            <input
              type="checkbox"
              name="animations"
              checked={formData.animations}
              onChange={handleInputChange}
              disabled={loading}
            />
            Enable Animations
          </Label>
        </FormGroup>

        <PreviewSection theme={formData.theme}>
          <PreviewText fontFamily={formData.fontFamily}>
            Preview Text - This is how your interface will look with the current settings.
          </PreviewText>
        </PreviewSection>

        <Button type="submit" disabled={loading}>
          Save Changes
        </Button>
      </Form>
    </Section>
  );
};

AppearanceSettings.propTypes = {
  onSettingChange: PropTypes.func.isRequired,
};

export default AppearanceSettings; 