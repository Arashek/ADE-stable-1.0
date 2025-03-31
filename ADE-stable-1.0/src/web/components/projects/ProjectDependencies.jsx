import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaBox, FaSearch, FaPlus, FaTrash, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';
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

const SearchContainer = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
`;

const SearchInput = styled.input`
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const SearchButton = styled.button`
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  background: #007bff;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    background: #0056b3;
  }
`;

const DependenciesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
`;

const DependencyCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const DependencyHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const DependencyName = styled.h3`
  margin: 0;
  color: #333;
  font-size: 16px;
`;

const DependencyVersion = styled.span`
  color: #666;
  font-size: 14px;
`;

const DependencyDescription = styled.p`
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
`;

const DependencyMeta = styled.div`
  display: flex;
  gap: 15px;
  margin-bottom: 15px;
  font-size: 12px;
  color: #999;
`;

const MetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: 5px;
`;

const DependencyActions = styled.div`
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

const ProjectDependencies = ({ projectId }) => {
  const [dependencies, setDependencies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [newDependency, setNewDependency] = useState({
    name: '',
    version: '',
    type: 'dependencies'
  });
  
  useEffect(() => {
    fetchDependencies();
  }, [projectId]);
  
  const fetchDependencies = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/dependencies`);
      setDependencies(response.data);
    } catch (err) {
      setError('Failed to fetch dependencies');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    
    try {
      const response = await axios.get(`/api/projects/${projectId}/dependencies/search`, {
        params: { query: searchQuery }
      });
      setDependencies(response.data);
    } catch (err) {
      setError('Failed to search dependencies');
      console.error(err);
    }
  };
  
  const handleAddDependency = async (e) => {
    e.preventDefault();
    
    try {
      await axios.post(`/api/projects/${projectId}/dependencies`, newDependency);
      setSuccess(true);
      setShowAddModal(false);
      setNewDependency({ name: '', version: '', type: 'dependencies' });
      fetchDependencies();
    } catch (err) {
      setError('Failed to add dependency');
      console.error(err);
    }
  };
  
  const handleRemoveDependency = async (dependencyId) => {
    if (!window.confirm('Are you sure you want to remove this dependency?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}/dependencies/${dependencyId}`);
      setSuccess(true);
      fetchDependencies();
    } catch (err) {
      setError('Failed to remove dependency');
      console.error(err);
    }
  };
  
  const handleUpdateDependency = async (dependencyId, version) => {
    try {
      await axios.put(`/api/projects/${projectId}/dependencies/${dependencyId}`, {
        version
      });
      setSuccess(true);
      fetchDependencies();
    } catch (err) {
      setError('Failed to update dependency');
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
          <FaBox />
          Project Dependencies
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
      
      <SearchContainer>
        <SearchInput
          type="text"
          placeholder="Search dependencies..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
        />
        <SearchButton onClick={handleSearch}>
          <FaSearch />
          Search
        </SearchButton>
        <SearchButton onClick={() => setShowAddModal(true)}>
          <FaPlus />
          Add Dependency
        </SearchButton>
      </SearchContainer>
      
      <DependenciesGrid>
        {dependencies.map(dependency => (
          <DependencyCard key={dependency.id}>
            <DependencyHeader>
              <div>
                <DependencyName>{dependency.name}</DependencyName>
                <DependencyVersion>v{dependency.version}</DependencyVersion>
              </div>
              <DependencyActions>
                <Button
                  onClick={() => handleUpdateDependency(dependency.id, dependency.latestVersion)}
                  disabled={dependency.version === dependency.latestVersion}
                >
                  <FaCheckCircle />
                  Update
                </Button>
                <Button
                  variant="danger"
                  onClick={() => handleRemoveDependency(dependency.id)}
                >
                  <FaTrash />
                  Remove
                </Button>
              </DependencyActions>
            </DependencyHeader>
            
            <DependencyDescription>
              {dependency.description}
            </DependencyDescription>
            
            <DependencyMeta>
              <MetaItem>
                <FaBox />
                {dependency.type}
              </MetaItem>
              <MetaItem>
                <FaExclamationTriangle />
                {dependency.vulnerabilities} vulnerabilities
              </MetaItem>
            </DependencyMeta>
          </DependencyCard>
        ))}
      </DependenciesGrid>
      
      {showAddModal && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Add New Dependency</ModalTitle>
              <CloseButton onClick={() => setShowAddModal(false)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleAddDependency}>
              <FormGroup>
                <Label>Package Name</Label>
                <Input
                  type="text"
                  value={newDependency.name}
                  onChange={(e) => setNewDependency(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Version</Label>
                <Input
                  type="text"
                  value={newDependency.version}
                  onChange={(e) => setNewDependency(prev => ({
                    ...prev,
                    version: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Type</Label>
                <Select
                  value={newDependency.type}
                  onChange={(e) => setNewDependency(prev => ({
                    ...prev,
                    type: e.target.value
                  }))}
                >
                  <option value="dependencies">Dependencies</option>
                  <option value="devDependencies">Dev Dependencies</option>
                  <option value="peerDependencies">Peer Dependencies</option>
                </Select>
              </FormGroup>
              
              <Button type="submit">
                <FaPlus />
                Add Dependency
              </Button>
            </Form>
          </ModalContent>
        </Modal>
      )}
    </Container>
  );
};

export default ProjectDependencies; 