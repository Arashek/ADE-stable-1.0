import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaTag, FaPlus, FaTrash, FaEdit, FaSave, FaTimes, FaCalendar, FaCheckCircle, FaClock, FaUser, FaCodeBranch, FaDownload, FaCode } from 'react-icons/fa';
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

const ReleasesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
`;

const ReleaseCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const ReleaseHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const ReleaseInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const ReleaseTitle = styled.h3`
  margin: 0;
  color: #333;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ReleaseMeta = styled.div`
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

const ReleaseActions = styled.div`
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

const ReleaseDetails = styled.div`
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

const ReleaseDescription = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const DescriptionContent = styled.div`
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  font-size: 14px;
  color: #666;
  white-space: pre-wrap;
`;

const ReleaseAssets = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const AssetsTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
`;

const AssetsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const AssetItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
`;

const AssetInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const AssetMeta = styled.div`
  display: flex;
  gap: 10px;
  color: #999;
`;

const ReleaseChanges = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const ChangesTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
`;

const ChangesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const ChangeItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
`;

const ChangeInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const ChangeMeta = styled.div`
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

const TextArea = styled.textarea`
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
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const ProjectReleases = ({ projectId }) => {
  const [releases, setReleases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingRelease, setEditingRelease] = useState(null);
  const [newRelease, setNewRelease] = useState({
    title: '',
    description: '',
    version: '',
    releaseDate: '',
    status: 'draft',
    branch: '',
    assets: [],
    changes: []
  });
  
  const availableStatuses = [
    { id: 'draft', name: 'Draft', icon: FaClock },
    { id: 'published', name: 'Published', icon: FaCheckCircle },
    { id: 'archived', name: 'Archived', icon: FaTimes }
  ];
  
  useEffect(() => {
    fetchReleases();
  }, [projectId]);
  
  const fetchReleases = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/releases`);
      setReleases(response.data);
    } catch (err) {
      setError('Failed to fetch releases');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddRelease = async (e) => {
    e.preventDefault();
    
    try {
      await axios.post(`/api/projects/${projectId}/releases`, newRelease);
      setSuccess(true);
      setShowAddModal(false);
      setNewRelease({
        title: '',
        description: '',
        version: '',
        releaseDate: '',
        status: 'draft',
        branch: '',
        assets: [],
        changes: []
      });
      fetchReleases();
    } catch (err) {
      setError('Failed to add release');
      console.error(err);
    }
  };
  
  const handleUpdateRelease = async (e) => {
    e.preventDefault();
    
    try {
      await axios.put(`/api/projects/${projectId}/releases/${editingRelease.id}`, editingRelease);
      setSuccess(true);
      setEditingRelease(null);
      fetchReleases();
    } catch (err) {
      setError('Failed to update release');
      console.error(err);
    }
  };
  
  const handleDeleteRelease = async (releaseId) => {
    if (!window.confirm('Are you sure you want to delete this release?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}/releases/${releaseId}`);
      setSuccess(true);
      fetchReleases();
    } catch (err) {
      setError('Failed to delete release');
      console.error(err);
    }
  };
  
  const getStatusIcon = (status) => {
    const statusType = availableStatuses.find(s => s.id === status);
    return statusType ? statusType.icon : FaClock;
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>
          <FaTag />
          Project Releases
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
        Add Release
      </Button>
      
      <ReleasesGrid>
        {releases.map(release => {
          const StatusIcon = getStatusIcon(release.status);
          
          return (
            <ReleaseCard key={release.id}>
              <ReleaseHeader>
                <ReleaseInfo>
                  <ReleaseTitle>
                    <StatusIcon />
                    {release.title}
                  </ReleaseTitle>
                  <ReleaseMeta>
                    <MetaItem>
                      <FaTag />
                      v{release.version}
                    </MetaItem>
                    <MetaItem>
                      <FaCalendar />
                      {new Date(release.releaseDate).toLocaleDateString()}
                    </MetaItem>
                    <MetaItem>
                      <FaCodeBranch />
                      {release.branch}
                    </MetaItem>
                  </ReleaseMeta>
                </ReleaseInfo>
                <ReleaseActions>
                  <Button onClick={() => setEditingRelease(release)}>
                    <FaEdit />
                    Edit
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => handleDeleteRelease(release.id)}
                  >
                    <FaTrash />
                    Delete
                  </Button>
                </ReleaseActions>
              </ReleaseHeader>
              
              <ReleaseDetails>
                <DetailRow>
                  <DetailLabel>Status</DetailLabel>
                  <DetailValue>
                    {release.status.charAt(0).toUpperCase() + release.status.slice(1)}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Version</DetailLabel>
                  <DetailValue>
                    v{release.version}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Release Date</DetailLabel>
                  <DetailValue>
                    {new Date(release.releaseDate).toLocaleDateString()}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Branch</DetailLabel>
                  <DetailValue>
                    {release.branch}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Created</DetailLabel>
                  <DetailValue>
                    {new Date(release.createdAt).toLocaleString()}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Last Updated</DetailLabel>
                  <DetailValue>
                    {new Date(release.updatedAt).toLocaleString()}
                  </DetailValue>
                </DetailRow>
              </ReleaseDetails>
              
              <ReleaseDescription>
                <DescriptionContent>
                  {release.description}
                </DescriptionContent>
              </ReleaseDescription>
              
              <ReleaseAssets>
                <AssetsTitle>Assets</AssetsTitle>
                <AssetsList>
                  {release.assets?.map(asset => (
                    <AssetItem key={asset.id}>
                      <AssetInfo>
                        <div>{asset.name}</div>
                        <AssetMeta>
                          <span>{asset.size}</span>
                          <span>{asset.type}</span>
                          <span>{asset.downloads} downloads</span>
                        </AssetMeta>
                      </AssetInfo>
                      <Button>
                        <FaDownload />
                        Download
                      </Button>
                    </AssetItem>
                  ))}
                </AssetsList>
              </ReleaseAssets>
              
              <ReleaseChanges>
                <ChangesTitle>Changes</ChangesTitle>
                <ChangesList>
                  {release.changes?.map(change => (
                    <ChangeItem key={change.id}>
                      <ChangeInfo>
                        <div>{change.description}</div>
                        <ChangeMeta>
                          <span>{change.type}</span>
                          <span>{change.author}</span>
                          <span>{new Date(change.timestamp).toLocaleString()}</span>
                        </ChangeMeta>
                      </ChangeInfo>
                    </ChangeItem>
                  ))}
                </ChangesList>
              </ReleaseChanges>
            </ReleaseCard>
          );
        })}
      </ReleasesGrid>
      
      {showAddModal && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Add New Release</ModalTitle>
              <CloseButton onClick={() => setShowAddModal(false)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleAddRelease}>
              <FormGroup>
                <Label>Release Title</Label>
                <Input
                  type="text"
                  value={newRelease.title}
                  onChange={(e) => setNewRelease(prev => ({
                    ...prev,
                    title: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Description</Label>
                <TextArea
                  value={newRelease.description}
                  onChange={(e) => setNewRelease(prev => ({
                    ...prev,
                    description: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Version</Label>
                <Input
                  type="text"
                  value={newRelease.version}
                  onChange={(e) => setNewRelease(prev => ({
                    ...prev,
                    version: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Release Date</Label>
                <Input
                  type="date"
                  value={newRelease.releaseDate}
                  onChange={(e) => setNewRelease(prev => ({
                    ...prev,
                    releaseDate: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Status</Label>
                <Select
                  value={newRelease.status}
                  onChange={(e) => setNewRelease(prev => ({
                    ...prev,
                    status: e.target.value
                  }))}
                >
                  {availableStatuses.map(status => (
                    <option key={status.id} value={status.id}>
                      {status.name.charAt(0).toUpperCase() + status.name.slice(1)}
                    </option>
                  ))}
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label>Branch</Label>
                <Input
                  type="text"
                  value={newRelease.branch}
                  onChange={(e) => setNewRelease(prev => ({
                    ...prev,
                    branch: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <Button type="submit">
                <FaPlus />
                Add Release
              </Button>
            </Form>
          </ModalContent>
        </Modal>
      )}
      
      {editingRelease && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Edit Release</ModalTitle>
              <CloseButton onClick={() => setEditingRelease(null)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleUpdateRelease}>
              <FormGroup>
                <Label>Release Title</Label>
                <Input
                  type="text"
                  value={editingRelease.title}
                  onChange={(e) => setEditingRelease(prev => ({
                    ...prev,
                    title: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Description</Label>
                <TextArea
                  value={editingRelease.description}
                  onChange={(e) => setEditingRelease(prev => ({
                    ...prev,
                    description: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Version</Label>
                <Input
                  type="text"
                  value={editingRelease.version}
                  onChange={(e) => setEditingRelease(prev => ({
                    ...prev,
                    version: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Release Date</Label>
                <Input
                  type="date"
                  value={editingRelease.releaseDate}
                  onChange={(e) => setEditingRelease(prev => ({
                    ...prev,
                    releaseDate: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Status</Label>
                <Select
                  value={editingRelease.status}
                  onChange={(e) => setEditingRelease(prev => ({
                    ...prev,
                    status: e.target.value
                  }))}
                >
                  {availableStatuses.map(status => (
                    <option key={status.id} value={status.id}>
                      {status.name.charAt(0).toUpperCase() + status.name.slice(1)}
                    </option>
                  ))}
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label>Branch</Label>
                <Input
                  type="text"
                  value={editingRelease.branch}
                  onChange={(e) => setEditingRelease(prev => ({
                    ...prev,
                    branch: e.target.value
                  }))}
                  required
                />
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

export default ProjectReleases; 