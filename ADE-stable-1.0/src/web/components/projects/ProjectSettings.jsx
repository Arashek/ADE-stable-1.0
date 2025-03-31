import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaCog, FaSave, FaTrash, FaExclamationTriangle } from 'react-icons/fa';
import axios from 'axios';

const Container = styled.div`
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
`;

const Header = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const Title = styled.h1`
  margin: 0;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const SettingsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
`;

const SettingsSection = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const SectionTitle = styled.h2`
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const FormGroup = styled.div`
  margin-bottom: 20px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  color: #666;
  font-size: 14px;
`;

const Input = styled.input`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  min-height: 100px;
  resize: vertical;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const Select = styled.select`
  width: 100%;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const Checkbox = styled.input`
  margin-right: 8px;
`;

const Button = styled.button`
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  background: ${props => props.variant === 'danger' ? '#dc3545' : '#007bff'};
  color: white;
  border: none;
  
  &:hover {
    background: ${props => props.variant === 'danger' ? '#c82333' : '#0056b3'};
  }
  
  &:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 20px;
`;

const Alert = styled.div`
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  background: ${props => props.type === 'success' ? '#d4edda' : '#f8d7da'};
  color: ${props => props.type === 'success' ? '#155724' : '#721c24'};
  border: 1px solid ${props => props.type === 'success' ? '#c3e6cb' : '#f5c6cb'};
`;

const DangerZone = styled.div`
  background: #fff5f5;
  padding: 20px;
  border-radius: 8px;
  margin-top: 20px;
  border: 1px solid #feb2b2;
`;

const DangerZoneTitle = styled.h2`
  margin: 0 0 15px 0;
  color: #c53030;
  font-size: 18px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const DangerZoneDescription = styled.p`
  margin: 0 0 15px 0;
  color: #4a5568;
  font-size: 14px;
`;

const ProjectSettings = ({ projectId }) => {
  const [settings, setSettings] = useState({
    name: '',
    description: '',
    visibility: 'private',
    defaultBranch: 'main',
    autoMerge: false,
    requireReviews: true,
    minReviewers: 1,
    enableCI: true,
    enableCD: true,
    buildCommand: '',
    deployCommand: '',
    environment: 'development'
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  useEffect(() => {
    fetchSettings();
  }, [projectId]);
  
  const fetchSettings = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/settings`);
      setSettings(response.data);
    } catch (err) {
      setError('Failed to fetch project settings');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setSettings(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);
    setSuccess(false);
    
    try {
      await axios.put(`/api/projects/${projectId}/settings`, settings);
      setSuccess(true);
    } catch (err) {
      setError('Failed to save project settings');
      console.error(err);
    } finally {
      setSaving(false);
    }
  };
  
  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}`);
      // Redirect to projects list or handle deletion success
    } catch (err) {
      setError('Failed to delete project');
      console.error(err);
    }
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>
          <FaCog />
          Project Settings
        </Title>
      </Header>
      
      {error && (
        <Alert type="error">
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert type="success">
          Settings saved successfully
        </Alert>
      )}
      
      <form onSubmit={handleSubmit}>
        <SettingsGrid>
          <SettingsSection>
            <SectionTitle>General Settings</SectionTitle>
            
            <FormGroup>
              <Label>Project Name</Label>
              <Input
                type="text"
                name="name"
                value={settings.name}
                onChange={handleChange}
                required
              />
            </FormGroup>
            
            <FormGroup>
              <Label>Description</Label>
              <TextArea
                name="description"
                value={settings.description}
                onChange={handleChange}
              />
            </FormGroup>
            
            <FormGroup>
              <Label>Visibility</Label>
              <Select
                name="visibility"
                value={settings.visibility}
                onChange={handleChange}
              >
                <option value="private">Private</option>
                <option value="public">Public</option>
                <option value="internal">Internal</option>
              </Select>
            </FormGroup>
          </SettingsSection>
          
          <SettingsSection>
            <SectionTitle>Repository Settings</SectionTitle>
            
            <FormGroup>
              <Label>Default Branch</Label>
              <Input
                type="text"
                name="defaultBranch"
                value={settings.defaultBranch}
                onChange={handleChange}
              />
            </FormGroup>
            
            <FormGroup>
              <Label>
                <Checkbox
                  type="checkbox"
                  name="autoMerge"
                  checked={settings.autoMerge}
                  onChange={handleChange}
                />
                Enable Auto-Merge
              </Label>
            </FormGroup>
            
            <FormGroup>
              <Label>
                <Checkbox
                  type="checkbox"
                  name="requireReviews"
                  checked={settings.requireReviews}
                  onChange={handleChange}
                />
                Require Reviews
              </Label>
            </FormGroup>
            
            {settings.requireReviews && (
              <FormGroup>
                <Label>Minimum Reviewers</Label>
                <Input
                  type="number"
                  name="minReviewers"
                  value={settings.minReviewers}
                  onChange={handleChange}
                  min="1"
                />
              </FormGroup>
            )}
          </SettingsSection>
          
          <SettingsSection>
            <SectionTitle>CI/CD Settings</SectionTitle>
            
            <FormGroup>
              <Label>
                <Checkbox
                  type="checkbox"
                  name="enableCI"
                  checked={settings.enableCI}
                  onChange={handleChange}
                />
                Enable Continuous Integration
              </Label>
            </FormGroup>
            
            <FormGroup>
              <Label>
                <Checkbox
                  type="checkbox"
                  name="enableCD"
                  checked={settings.enableCD}
                  onChange={handleChange}
                />
                Enable Continuous Deployment
              </Label>
            </FormGroup>
            
            <FormGroup>
              <Label>Build Command</Label>
              <Input
                type="text"
                name="buildCommand"
                value={settings.buildCommand}
                onChange={handleChange}
                placeholder="npm run build"
              />
            </FormGroup>
            
            <FormGroup>
              <Label>Deploy Command</Label>
              <Input
                type="text"
                name="deployCommand"
                value={settings.deployCommand}
                onChange={handleChange}
                placeholder="npm run deploy"
              />
            </FormGroup>
            
            <FormGroup>
              <Label>Environment</Label>
              <Select
                name="environment"
                value={settings.environment}
                onChange={handleChange}
              >
                <option value="development">Development</option>
                <option value="staging">Staging</option>
                <option value="production">Production</option>
              </Select>
            </FormGroup>
          </SettingsSection>
        </SettingsGrid>
        
        <ButtonGroup>
          <Button type="submit" disabled={saving}>
            <FaSave />
            {saving ? 'Saving...' : 'Save Settings'}
          </Button>
        </ButtonGroup>
      </form>
      
      <DangerZone>
        <DangerZoneTitle>
          <FaExclamationTriangle />
          Danger Zone
        </DangerZoneTitle>
        <DangerZoneDescription>
          Once you delete a project, there is no going back. Please be certain.
        </DangerZoneDescription>
        <Button variant="danger" onClick={handleDelete}>
          <FaTrash />
          Delete Project
        </Button>
      </DangerZone>
    </Container>
  );
};

export default ProjectSettings; 