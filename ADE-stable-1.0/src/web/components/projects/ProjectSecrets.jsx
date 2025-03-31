import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaKey, FaPlus, FaTrash, FaEdit, FaSave, FaTimes, FaEye, FaEyeSlash } from 'react-icons/fa';
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

const SecretsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
`;

const SecretCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const SecretHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const SecretInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const SecretName = styled.h3`
  margin: 0;
  color: #333;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const SecretMeta = styled.div`
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

const SecretActions = styled.div`
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

const SecretDetails = styled.div`
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

const SecretValue = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-family: monospace;
  font-size: 14px;
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

const ProjectSecrets = ({ projectId }) => {
  const [secrets, setSecrets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingSecret, setEditingSecret] = useState(null);
  const [newSecret, setNewSecret] = useState({
    name: '',
    value: '',
    type: 'environment',
    environment: 'development'
  });
  const [showValues, setShowValues] = useState({});
  
  useEffect(() => {
    fetchSecrets();
  }, [projectId]);
  
  const fetchSecrets = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/secrets`);
      setSecrets(response.data);
    } catch (err) {
      setError('Failed to fetch secrets');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddSecret = async (e) => {
    e.preventDefault();
    
    try {
      await axios.post(`/api/projects/${projectId}/secrets`, newSecret);
      setSuccess(true);
      setShowAddModal(false);
      setNewSecret({
        name: '',
        value: '',
        type: 'environment',
        environment: 'development'
      });
      fetchSecrets();
    } catch (err) {
      setError('Failed to add secret');
      console.error(err);
    }
  };
  
  const handleUpdateSecret = async (e) => {
    e.preventDefault();
    
    try {
      await axios.put(`/api/projects/${projectId}/secrets/${editingSecret.id}`, editingSecret);
      setSuccess(true);
      setEditingSecret(null);
      fetchSecrets();
    } catch (err) {
      setError('Failed to update secret');
      console.error(err);
    }
  };
  
  const handleDeleteSecret = async (secretId) => {
    if (!window.confirm('Are you sure you want to delete this secret?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}/secrets/${secretId}`);
      setSuccess(true);
      fetchSecrets();
    } catch (err) {
      setError('Failed to delete secret');
      console.error(err);
    }
  };
  
  const toggleValueVisibility = (secretId) => {
    setShowValues(prev => ({
      ...prev,
      [secretId]: !prev[secretId]
    }));
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>
          <FaKey />
          Project Secrets
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
        Add Secret
      </Button>
      
      <SecretsGrid>
        {secrets.map(secret => (
          <SecretCard key={secret.id}>
            <SecretHeader>
              <SecretInfo>
                <SecretName>
                  {secret.name}
                </SecretName>
                <SecretMeta>
                  <MetaItem>
                    Type: {secret.type}
                  </MetaItem>
                  <MetaItem>
                    Environment: {secret.environment}
                  </MetaItem>
                </SecretMeta>
              </SecretInfo>
              <SecretActions>
                <Button onClick={() => setEditingSecret(secret)}>
                  <FaEdit />
                  Edit
                </Button>
                <Button
                  variant="danger"
                  onClick={() => handleDeleteSecret(secret.id)}
                >
                  <FaTrash />
                  Delete
                </Button>
              </SecretActions>
            </SecretHeader>
            
            <SecretDetails>
              <DetailRow>
                <DetailLabel>Last Updated</DetailLabel>
                <DetailValue>
                  {new Date(secret.updatedAt).toLocaleString()}
                </DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>Value</DetailLabel>
                <DetailValue>
                  {showValues[secret.id] ? secret.value : '••••••••'}
                  <Button
                    onClick={() => toggleValueVisibility(secret.id)}
                    style={{ background: 'none', color: '#666', padding: '0 8px' }}
                  >
                    {showValues[secret.id] ? <FaEyeSlash /> : <FaEye />}
                  </Button>
                </DetailValue>
              </DetailRow>
            </SecretDetails>
          </SecretCard>
        ))}
      </SecretsGrid>
      
      {showAddModal && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Add New Secret</ModalTitle>
              <CloseButton onClick={() => setShowAddModal(false)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleAddSecret}>
              <FormGroup>
                <Label>Secret Name</Label>
                <Input
                  type="text"
                  value={newSecret.name}
                  onChange={(e) => setNewSecret(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Secret Value</Label>
                <Input
                  type="password"
                  value={newSecret.value}
                  onChange={(e) => setNewSecret(prev => ({
                    ...prev,
                    value: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Type</Label>
                <Select
                  value={newSecret.type}
                  onChange={(e) => setNewSecret(prev => ({
                    ...prev,
                    type: e.target.value
                  }))}
                >
                  <option value="environment">Environment Variable</option>
                  <option value="secret">Secret</option>
                  <option value="api_key">API Key</option>
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label>Environment</Label>
                <Select
                  value={newSecret.environment}
                  onChange={(e) => setNewSecret(prev => ({
                    ...prev,
                    environment: e.target.value
                  }))}
                >
                  <option value="development">Development</option>
                  <option value="staging">Staging</option>
                  <option value="production">Production</option>
                </Select>
              </FormGroup>
              
              <Button type="submit">
                <FaPlus />
                Add Secret
              </Button>
            </Form>
          </ModalContent>
        </Modal>
      )}
      
      {editingSecret && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Edit Secret</ModalTitle>
              <CloseButton onClick={() => setEditingSecret(null)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleUpdateSecret}>
              <FormGroup>
                <Label>Secret Name</Label>
                <Input
                  type="text"
                  value={editingSecret.name}
                  onChange={(e) => setEditingSecret(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Secret Value</Label>
                <Input
                  type="password"
                  value={editingSecret.value}
                  onChange={(e) => setEditingSecret(prev => ({
                    ...prev,
                    value: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Type</Label>
                <Select
                  value={editingSecret.type}
                  onChange={(e) => setEditingSecret(prev => ({
                    ...prev,
                    type: e.target.value
                  }))}
                >
                  <option value="environment">Environment Variable</option>
                  <option value="secret">Secret</option>
                  <option value="api_key">API Key</option>
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label>Environment</Label>
                <Select
                  value={editingSecret.environment}
                  onChange={(e) => setEditingSecret(prev => ({
                    ...prev,
                    environment: e.target.value
                  }))}
                >
                  <option value="development">Development</option>
                  <option value="staging">Staging</option>
                  <option value="production">Production</option>
                </Select>
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

export default ProjectSecrets; 