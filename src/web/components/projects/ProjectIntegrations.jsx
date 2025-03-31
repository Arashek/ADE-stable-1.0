import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaPlug, FaPlus, FaTrash, FaEdit, FaSave, FaTimes, FaCheckCircle, FaTimesCircle, FaGithub, FaSlack, FaJira, FaTrello, FaBitbucket } from 'react-icons/fa';
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

const IntegrationsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
`;

const IntegrationCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const IntegrationHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const IntegrationInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const IntegrationName = styled.h3`
  margin: 0;
  color: #333;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const IntegrationMeta = styled.div`
  display: flex;
  gap: 15px;
  font-size: 12px;
  color: #999;
`;

const MetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: 5px;
`;

const IntegrationStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  background: ${props => props.active ? '#d4edda' : '#f8d7da'};
  color: ${props => props.active ? '#155724' : '#721c24'};
`;

const IntegrationActions = styled.div`
  display: flex;
  gap: 10px;
`;

const Button = styled.button`
  padding: 6px 12px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
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

const IntegrationDetails = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const DetailRow = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
  font-size: 14px;
`;

const DetailLabel = styled.span`
  color: #666;
`;

const DetailValue = styled.span`
  color: #333;
  font-weight: 500;
`;

const IntegrationFeatures = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const FeaturesTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
`;

const FeaturesList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const FeatureTag = styled.span`
  padding: 4px 8px;
  background: #e9ecef;
  border-radius: 4px;
  font-size: 12px;
  color: #495057;
`;

const IntegrationActivity = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const ActivityTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
`;

const ActivityList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const ActivityItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
`;

const ActivityInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const ActivityMeta = styled.div`
  display: flex;
  gap: 10px;
  color: #999;
`;

const Alert = styled.div`
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  background: ${props => props.type === 'success' ? '#d4edda' : '#f8d7da'};
  color: ${props => props.type === 'success' ? '#155724' : '#721c24'};
  border: 1px solid ${props => props.type === 'success' ? '#c3e6cb' : '#f5c6cb'};
`;

const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 100%;
  max-width: 500px;
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const ModalTitle = styled.h2`
  margin: 0;
  color: #333;
`;

const CloseButton = styled.button`
  background: none;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: #666;
  
  &:hover {
    color: #333;
  }
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const Label = styled.label`
  color: #666;
  font-size: 14px;
`;

const Input = styled.input`
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const Select = styled.select`
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const CheckboxGroup = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
`;

const CheckboxLabel = styled.label`
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 14px;
  color: #666;
`;

const ProjectIntegrations = ({ projectId }) => {
  const [integrations, setIntegrations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingIntegration, setEditingIntegration] = useState(null);
  const [newIntegration, setNewIntegration] = useState({
    name: '',
    type: 'github',
    config: {},
    features: [],
    active: true
  });
  
  const availableIntegrations = [
    { id: 'github', name: 'GitHub', icon: FaGithub },
    { id: 'slack', name: 'Slack', icon: FaSlack },
    { id: 'jira', name: 'Jira', icon: FaJira },
    { id: 'trello', name: 'Trello', icon: FaTrello },
    { id: 'bitbucket', name: 'Bitbucket', icon: FaBitbucket }
  ];
  
  const availableFeatures = [
    'issue_tracking',
    'pull_requests',
    'notifications',
    'deployments',
    'builds',
    'tests',
    'releases',
    'comments'
  ];
  
  useEffect(() => {
    fetchIntegrations();
  }, [projectId]);
  
  const fetchIntegrations = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/integrations`);
      setIntegrations(response.data);
    } catch (err) {
      setError('Failed to fetch integrations');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddIntegration = async (e) => {
    e.preventDefault();
    
    try {
      await axios.post(`/api/projects/${projectId}/integrations`, newIntegration);
      setSuccess(true);
      setShowAddModal(false);
      setNewIntegration({
        name: '',
        type: 'github',
        config: {},
        features: [],
        active: true
      });
      fetchIntegrations();
    } catch (err) {
      setError('Failed to add integration');
      console.error(err);
    }
  };
  
  const handleUpdateIntegration = async (e) => {
    e.preventDefault();
    
    try {
      await axios.put(`/api/projects/${projectId}/integrations/${editingIntegration.id}`, editingIntegration);
      setSuccess(true);
      setEditingIntegration(null);
      fetchIntegrations();
    } catch (err) {
      setError('Failed to update integration');
      console.error(err);
    }
  };
  
  const handleDeleteIntegration = async (integrationId) => {
    if (!window.confirm('Are you sure you want to delete this integration?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}/integrations/${integrationId}`);
      setSuccess(true);
      fetchIntegrations();
    } catch (err) {
      setError('Failed to delete integration');
      console.error(err);
    }
  };
  
  const toggleFeature = (feature, integration) => {
    const features = integration.features.includes(feature)
      ? integration.features.filter(f => f !== feature)
      : [...integration.features, feature];
    
    if (integration === newIntegration) {
      setNewIntegration(prev => ({ ...prev, features }));
    } else {
      setEditingIntegration(prev => ({ ...prev, features }));
    }
  };
  
  const getIntegrationIcon = (type) => {
    const integration = availableIntegrations.find(i => i.id === type);
    return integration ? integration.icon : FaPlug;
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>
          <FaPlug />
          Project Integrations
        </Title>
      </Header>
      
      {error && (
        <Alert type="error">
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert type="success">
          Operation completed successfully
        </Alert>
      )}
      
      <Button onClick={() => setShowAddModal(true)} style={{ marginBottom: '20px' }}>
        <FaPlus />
        Add Integration
      </Button>
      
      <IntegrationsGrid>
        {integrations.map(integration => {
          const Icon = getIntegrationIcon(integration.type);
          return (
            <IntegrationCard key={integration.id}>
              <IntegrationHeader>
                <IntegrationInfo>
                  <IntegrationName>
                    <Icon />
                    {integration.name}
                    <IntegrationStatus active={integration.active}>
                      {integration.active ? <FaCheckCircle /> : <FaTimesCircle />}
                      {integration.active ? 'Active' : 'Inactive'}
                    </IntegrationStatus>
                  </IntegrationName>
                  <IntegrationMeta>
                    <MetaItem>
                      Type: {integration.type}
                    </MetaItem>
                    <MetaItem>
                      Last Sync: {integration.lastSyncedAt ? new Date(integration.lastSyncedAt).toLocaleString() : 'Never'}
                    </MetaItem>
                  </IntegrationMeta>
                </IntegrationInfo>
                <IntegrationActions>
                  <Button onClick={() => setEditingIntegration(integration)}>
                    <FaEdit />
                    Edit
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => handleDeleteIntegration(integration.id)}
                  >
                    <FaTrash />
                    Delete
                  </Button>
                </IntegrationActions>
              </IntegrationHeader>
              
              <IntegrationDetails>
                <DetailRow>
                  <DetailLabel>Connected Account</DetailLabel>
                  <DetailValue>
                    {integration.config.account || 'Not connected'}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Created</DetailLabel>
                  <DetailValue>
                    {new Date(integration.createdAt).toLocaleString()}
                  </DetailValue>
                </DetailRow>
              </IntegrationDetails>
              
              <IntegrationFeatures>
                <FeaturesTitle>Features</FeaturesTitle>
                <FeaturesList>
                  {availableFeatures.map(feature => (
                    <FeatureTag
                      key={feature}
                      style={{
                        background: integration.features.includes(feature) ? '#cce5ff' : '#e9ecef',
                        color: integration.features.includes(feature) ? '#004085' : '#495057'
                      }}
                    >
                      {feature.replace('_', ' ')}
                    </FeatureTag>
                  ))}
                </FeaturesList>
              </IntegrationFeatures>
              
              <IntegrationActivity>
                <ActivityTitle>Recent Activity</ActivityTitle>
                <ActivityList>
                  {integration.activities?.map(activity => (
                    <ActivityItem key={activity.id}>
                      <ActivityInfo>
                        <div>{activity.description}</div>
                        <ActivityMeta>
                          <span>{new Date(activity.timestamp).toLocaleString()}</span>
                          <span>{activity.status}</span>
                        </ActivityMeta>
                      </ActivityInfo>
                    </ActivityItem>
                  ))}
                </ActivityList>
              </IntegrationActivity>
            </IntegrationCard>
          );
        })}
      </IntegrationsGrid>
      
      {showAddModal && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Add New Integration</ModalTitle>
              <CloseButton onClick={() => setShowAddModal(false)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleAddIntegration}>
              <FormGroup>
                <Label>Integration Name</Label>
                <Input
                  type="text"
                  value={newIntegration.name}
                  onChange={(e) => setNewIntegration(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Integration Type</Label>
                <Select
                  value={newIntegration.type}
                  onChange={(e) => setNewIntegration(prev => ({
                    ...prev,
                    type: e.target.value
                  }))}
                >
                  {availableIntegrations.map(integration => (
                    <option key={integration.id} value={integration.id}>
                      {integration.name}
                    </option>
                  ))}
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label>Features</Label>
                <CheckboxGroup>
                  {availableFeatures.map(feature => (
                    <CheckboxLabel key={feature}>
                      <input
                        type="checkbox"
                        checked={newIntegration.features.includes(feature)}
                        onChange={() => toggleFeature(feature, newIntegration)}
                      />
                      {feature.replace('_', ' ')}
                    </CheckboxLabel>
                  ))}
                </CheckboxGroup>
              </FormGroup>
              
              <FormGroup>
                <Label>
                  <input
                    type="checkbox"
                    checked={newIntegration.active}
                    onChange={(e) => setNewIntegration(prev => ({
                      ...prev,
                      active: e.target.checked
                    }))}
                  />
                  Active
                </Label>
              </FormGroup>
              
              <Button type="submit">
                <FaPlus />
                Add Integration
              </Button>
            </Form>
          </ModalContent>
        </Modal>
      )}
      
      {editingIntegration && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Edit Integration</ModalTitle>
              <CloseButton onClick={() => setEditingIntegration(null)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleUpdateIntegration}>
              <FormGroup>
                <Label>Integration Name</Label>
                <Input
                  type="text"
                  value={editingIntegration.name}
                  onChange={(e) => setEditingIntegration(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Integration Type</Label>
                <Select
                  value={editingIntegration.type}
                  onChange={(e) => setEditingIntegration(prev => ({
                    ...prev,
                    type: e.target.value
                  }))}
                >
                  {availableIntegrations.map(integration => (
                    <option key={integration.id} value={integration.id}>
                      {integration.name}
                    </option>
                  ))}
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label>Features</Label>
                <CheckboxGroup>
                  {availableFeatures.map(feature => (
                    <CheckboxLabel key={feature}>
                      <input
                        type="checkbox"
                        checked={editingIntegration.features.includes(feature)}
                        onChange={() => toggleFeature(feature, editingIntegration)}
                      />
                      {feature.replace('_', ' ')}
                    </CheckboxLabel>
                  ))}
                </CheckboxGroup>
              </FormGroup>
              
              <FormGroup>
                <Label>
                  <input
                    type="checkbox"
                    checked={editingIntegration.active}
                    onChange={(e) => setEditingIntegration(prev => ({
                      ...prev,
                      active: e.target.checked
                    }))}
                  />
                  Active
                </Label>
              </FormGroup>
              
              <Button type="submit">
                <FaSave />
                Save Changes
              </Button>
            </Form>
          </ModalContent>
        </Modal>
      )}
    </Container>
  );
};

export default ProjectIntegrations; 