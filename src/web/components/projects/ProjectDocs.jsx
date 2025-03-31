import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaBook, FaPlus, FaTrash, FaEdit, FaSave, FaTimes, FaFolder, FaFile, FaFileAlt, FaFileCode, FaFileImage, FaFilePdf, FaFileWord, FaFileExcel, FaFileArchive, FaFileVideo, FaFileAudio } from 'react-icons/fa';
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

const DocsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
`;

const DocCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const DocHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const DocInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const DocName = styled.h3`
  margin: 0;
  color: #333;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const DocMeta = styled.div`
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

const DocActions = styled.div`
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

const DocDetails = styled.div`
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

const DocContent = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const ContentPreview = styled.div`
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  font-size: 14px;
  color: #666;
  max-height: 200px;
  overflow-y: auto;
`;

const DocVersions = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const VersionsTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
`;

const VersionsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const VersionItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
`;

const VersionInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const VersionMeta = styled.div`
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

const ProjectDocs = ({ projectId }) => {
  const [docs, setDocs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingDoc, setEditingDoc] = useState(null);
  const [newDoc, setNewDoc] = useState({
    name: '',
    description: '',
    type: 'markdown',
    content: '',
    category: 'general',
    tags: []
  });
  
  const availableTypes = [
    { id: 'markdown', name: 'Markdown', icon: FaFileAlt },
    { id: 'code', name: 'Code', icon: FaFileCode },
    { id: 'image', name: 'Image', icon: FaFileImage },
    { id: 'pdf', name: 'PDF', icon: FaFilePdf },
    { id: 'word', name: 'Word', icon: FaFileWord },
    { id: 'excel', name: 'Excel', icon: FaFileExcel },
    { id: 'archive', name: 'Archive', icon: FaFileArchive },
    { id: 'video', name: 'Video', icon: FaFileVideo },
    { id: 'audio', name: 'Audio', icon: FaFileAudio }
  ];
  
  const availableCategories = [
    'general',
    'api',
    'setup',
    'deployment',
    'development',
    'testing',
    'maintenance',
    'security'
  ];
  
  useEffect(() => {
    fetchDocs();
  }, [projectId]);
  
  const fetchDocs = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/docs`);
      setDocs(response.data);
    } catch (err) {
      setError('Failed to fetch documentation');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddDoc = async (e) => {
    e.preventDefault();
    
    try {
      await axios.post(`/api/projects/${projectId}/docs`, newDoc);
      setSuccess(true);
      setShowAddModal(false);
      setNewDoc({
        name: '',
        description: '',
        type: 'markdown',
        content: '',
        category: 'general',
        tags: []
      });
      fetchDocs();
    } catch (err) {
      setError('Failed to add documentation');
      console.error(err);
    }
  };
  
  const handleUpdateDoc = async (e) => {
    e.preventDefault();
    
    try {
      await axios.put(`/api/projects/${projectId}/docs/${editingDoc.id}`, editingDoc);
      setSuccess(true);
      setEditingDoc(null);
      fetchDocs();
    } catch (err) {
      setError('Failed to update documentation');
      console.error(err);
    }
  };
  
  const handleDeleteDoc = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this documentation?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}/docs/${docId}`);
      setSuccess(true);
      fetchDocs();
    } catch (err) {
      setError('Failed to delete documentation');
      console.error(err);
    }
  };
  
  const getDocIcon = (type) => {
    const docType = availableTypes.find(t => t.id === type);
    return docType ? docType.icon : FaFile;
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>
          <FaBook />
          Project Documentation
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
        Add Documentation
      </Button>
      
      <DocsGrid>
        {docs.map(doc => {
          const Icon = getDocIcon(doc.type);
          return (
            <DocCard key={doc.id}>
              <DocHeader>
                <DocInfo>
                  <DocName>
                    <Icon />
                    {doc.name}
                  </DocName>
                  <DocMeta>
                    <MetaItem>
                      <FaFolder />
                      {doc.category}
                    </MetaItem>
                    <MetaItem>
                      <FaFile />
                      {doc.type}
                    </MetaItem>
                  </DocMeta>
                </DocInfo>
                <DocActions>
                  <Button onClick={() => setEditingDoc(doc)}>
                    <FaEdit />
                    Edit
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => handleDeleteDoc(doc.id)}
                  >
                    <FaTrash />
                    Delete
                  </Button>
                </DocActions>
              </DocHeader>
              
              <DocDetails>
                <DetailRow>
                  <DetailLabel>Description</DetailLabel>
                  <DetailValue>
                    {doc.description || 'No description'}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Created</DetailLabel>
                  <DetailValue>
                    {new Date(doc.createdAt).toLocaleString()}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Last Updated</DetailLabel>
                  <DetailValue>
                    {new Date(doc.updatedAt).toLocaleString()}
                  </DetailValue>
                </DetailRow>
              </DocDetails>
              
              <DocContent>
                <ContentPreview>
                  {doc.type === 'markdown' ? (
                    <div dangerouslySetInnerHTML={{ __html: doc.content }} />
                  ) : (
                    <div>Preview not available for this file type</div>
                  )}
                </ContentPreview>
              </DocContent>
              
              <DocVersions>
                <VersionsTitle>Version History</VersionsTitle>
                <VersionsList>
                  {doc.versions?.map(version => (
                    <VersionItem key={version.id}>
                      <VersionInfo>
                        <div>Version {version.number}</div>
                        <VersionMeta>
                          <span>{new Date(version.createdAt).toLocaleString()}</span>
                          <span>{version.author}</span>
                        </VersionMeta>
                      </VersionInfo>
                    </VersionItem>
                  ))}
                </VersionsList>
              </DocVersions>
            </DocCard>
          );
        })}
      </DocsGrid>
      
      {showAddModal && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Add New Documentation</ModalTitle>
              <CloseButton onClick={() => setShowAddModal(false)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleAddDoc}>
              <FormGroup>
                <Label>Document Name</Label>
                <Input
                  type="text"
                  value={newDoc.name}
                  onChange={(e) => setNewDoc(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Description</Label>
                <Input
                  type="text"
                  value={newDoc.description}
                  onChange={(e) => setNewDoc(prev => ({
                    ...prev,
                    description: e.target.value
                  }))}
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Type</Label>
                <Select
                  value={newDoc.type}
                  onChange={(e) => setNewDoc(prev => ({
                    ...prev,
                    type: e.target.value
                  }))}
                >
                  {availableTypes.map(type => (
                    <option key={type.id} value={type.id}>
                      {type.name}
                    </option>
                  ))}
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label>Category</Label>
                <Select
                  value={newDoc.category}
                  onChange={(e) => setNewDoc(prev => ({
                    ...prev,
                    category: e.target.value
                  }))}
                >
                  {availableCategories.map(category => (
                    <option key={category} value={category}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </option>
                  ))}
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label>Content</Label>
                <TextArea
                  value={newDoc.content}
                  onChange={(e) => setNewDoc(prev => ({
                    ...prev,
                    content: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <Button type="submit">
                <FaPlus />
                Add Documentation
              </Button>
            </Form>
          </ModalContent>
        </Modal>
      )}
      
      {editingDoc && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Edit Documentation</ModalTitle>
              <CloseButton onClick={() => setEditingDoc(null)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleUpdateDoc}>
              <FormGroup>
                <Label>Document Name</Label>
                <Input
                  type="text"
                  value={editingDoc.name}
                  onChange={(e) => setEditingDoc(prev => ({
                    ...prev,
                    name: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Description</Label>
                <Input
                  type="text"
                  value={editingDoc.description}
                  onChange={(e) => setEditingDoc(prev => ({
                    ...prev,
                    description: e.target.value
                  }))}
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Type</Label>
                <Select
                  value={editingDoc.type}
                  onChange={(e) => setEditingDoc(prev => ({
                    ...prev,
                    type: e.target.value
                  }))}
                >
                  {availableTypes.map(type => (
                    <option key={type.id} value={type.id}>
                      {type.name}
                    </option>
                  ))}
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label>Category</Label>
                <Select
                  value={editingDoc.category}
                  onChange={(e) => setEditingDoc(prev => ({
                    ...prev,
                    category: e.target.value
                  }))}
                >
                  {availableCategories.map(category => (
                    <option key={category} value={category}>
                      {category.charAt(0).toUpperCase() + category.slice(1)}
                    </option>
                  ))}
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label>Content</Label>
                <TextArea
                  value={editingDoc.content}
                  onChange={(e) => setEditingDoc(prev => ({
                    ...prev,
                    content: e.target.value
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

export default ProjectDocs; 