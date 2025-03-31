import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaServer, FaPlus, FaTrash, FaCheckCircle, FaTimesCircle, FaSpinner, FaGlobe } from 'react-icons/fa';
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

const EnvironmentsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
`;

const EnvironmentCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const EnvironmentHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const EnvironmentInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const EnvironmentName = styled.h3`
  margin: 0;
  color: #333;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const EnvironmentMeta = styled.div`
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

const EnvironmentStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  background: ${props => {
    switch (props.status) {
      case 'active': return '#d4edda';
      case 'deploying': return '#cce5ff';
      case 'failed': return '#f8d7da';
      default: return '#e2e3e5';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case 'active': return '#155724';
      case 'deploying': return '#004085';
      case 'failed': return '#721c24';
      default: return '#383d41';
    }
  }};
`;

const EnvironmentActions = styled.div`
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

const EnvironmentDetails = styled.div`
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

const DeploymentHistory = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const HistoryTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
`;

const HistoryList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const HistoryItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
`;

const HistoryInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const HistoryMeta = styled.div`
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

const ProjectEnvironments = ({ projectId }) => {
  const [environments, setEnvironments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newEnvironment, setNewEnvironment] = useState({
    name: '',
    type: 'development',
    url: '',
    branch: 'main',
    autoDeploy: true
  });
  
  useEffect(() => {
    fetchEnvironments();
    // Set up polling for deploying environments
    const interval = setInterval(() => {
      const hasDeployingEnvs = environments.some(env => env.status === 'deploying');
      if (hasDeployingEnvs) {
        fetchEnvironments();
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, [projectId]);
  
  const fetchEnvironments = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/environments`);
      setEnvironments(response.data);
    } catch (err) {
      setError('Failed to fetch environments');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddEnvironment = async (e) => {
    e.preventDefault();
    
    try {
      await axios.post(`/api/projects/${projectId}/environments`, newEnvironment);
      setSuccess(true);
      setShowAddModal(false);
      setNewEnvironment({
        name: '',
        type: 'development',
        url: '',
        branch: 'main',
        autoDeploy: true
      });
      fetchEnvironments();
    } catch (err) {
      setError('Failed to add environment');
      console.error(err);
    }
  };
  
  const handleDeleteEnvironment = async (environmentId) => {
    if (!window.confirm('Are you sure you want to delete this environment?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}/environments/${environmentId}`);
      setSuccess(true);
      fetchEnvironments();
    } catch (err) {
      setError('Failed to delete environment');
      console.error(err);
    }
  };
  
  const handleDeploy = async (environmentId) => {
    try {
      await axios.post(`/api/projects/${projectId}/environments/${environmentId}/deploy`);
      setSuccess(true);
      fetchEnvironments();
    } catch (err) {
      setError('Failed to deploy to environment');
      console.error(err);
    }
  };
  
  const getStatusIcon = (status) => {
    switch (status) {
      case 'active':
        return <FaCheckCircle />;
      case 'failed':
        return <FaTimesCircle />;
      case 'deploying':
        return <FaSpinner className="fa-spin" />;
      default:
        return null;
    }
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>
          <FaServer />
          Project Environments
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
        Add Environment
      </Button>
      
      <EnvironmentsGrid>
        {environments.map(environment => (
          <EnvironmentCard key={environment.id}>
            <EnvironmentHeader>
              <EnvironmentInfo>
                <EnvironmentName>
                  {environment.name}
                  <EnvironmentStatus status={environment.status}>
                    {getStatusIcon(environment.status)}
                    {environment.status}
                  </EnvironmentStatus>
                </EnvironmentName>
                <EnvironmentMeta>
                  <MetaItem>
                    <FaGlobe />
                    {environment.type}
                  </MetaItem>
                  <MetaItem>
                    Branch: {environment.branch}
                  </MetaItem>
                </EnvironmentMeta>
              </EnvironmentInfo>
              <EnvironmentActions>
                <Button onClick={() => handleDeploy(environment.id)}>
                  Deploy
                </Button>
                <Button
                  variant="danger"
                  onClick={() => handleDeleteEnvironment(environment.id)}
                >
                  <FaTrash />
                  Delete
                </Button>
              </EnvironmentActions>
            </EnvironmentHeader>
            
            <EnvironmentDetails>
              <DetailRow>
                <DetailLabel>URL</DetailLabel>
                <DetailValue>
                  <a href={environment.url} target="_blank" rel="noopener noreferrer">
                    {environment.url}
                  </a>
                </DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>Last Deployed</DetailLabel>
                <DetailValue>
                  {new Date(environment.lastDeployedAt).toLocaleString()}
                </DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>Auto Deploy</DetailLabel>
                <DetailValue>
                  {environment.autoDeploy ? 'Enabled' : 'Disabled'}
                </DetailValue>
              </DetailRow>
            </EnvironmentDetails>
            
            <DeploymentHistory>
              <HistoryTitle>Recent Deployments</HistoryTitle>
              <HistoryList>
                {environment.deployments?.map(deployment => (
                  <HistoryItem key={deployment.id}>
                    <HistoryInfo>
                      <div>Deployment #{deployment.number}</div>
                      <HistoryMeta>
                        <span>{new Date(deployment.startedAt).toLocaleString()}</span>
                        <span>{deployment.status}</span>
                      </HistoryMeta>
                    </HistoryInfo>
                  </HistoryItem>
                ))}
              </HistoryList>
            </DeploymentHistory>
          </EnvironmentCard>
        ))}
      </EnvironmentsGrid>
      
      {showAddModal && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Add New Environment</ModalTitle>
              <CloseButton onClick={() => setShowAddModal(false)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleAddEnvironment}>
              <FormGroup>
                <Label>Environment Name</Label>
                <Input
                  type="text"
                  value={newEnvironment.name}
                  onChange={(e) => setNewEnvironment(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Type</Label>
                <Select
                  value={newEnvironment.type}
                  onChange={(e) => setNewEnvironment(prev => ({
                    ...prev,
                    type: e.target.value
                  }))}
                >
                  <option value="development">Development</option>
                  <option value="staging">Staging</option>
                  <option value="production">Production</option>
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label>URL</Label>
                <Input
                  type="url"
                  value={newEnvironment.url}
                  onChange={(e) => setNewEnvironment(prev => ({
                    ...prev,
                    url: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Branch</Label>
                <Input
                  type="text"
                  value={newEnvironment.branch}
                  onChange={(e) => setNewEnvironment(prev => ({
                    ...prev,
                    branch: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>
                  <input
                    type="checkbox"
                    checked={newEnvironment.autoDeploy}
                    onChange={(e) => setNewEnvironment(prev => ({
                      ...prev,
                      autoDeploy: e.target.checked
                    }))}
                  />
                  Enable Auto Deploy
                </Label>
              </FormGroup>
              
              <Button type="submit">
                <FaPlus />
                Add Environment
              </Button>
            </Form>
          </ModalContent>
        </Modal>
      )}
    </Container>
  );
};

export default ProjectEnvironments; 