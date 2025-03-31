import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaFileAlt, FaPlus, FaEdit, FaTrash, FaSave, FaTimes } from 'react-icons/fa';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

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
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h1`
  margin: 0;
  color: #333;
`;

const Button = styled.button`
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #007bff;
  color: white;
  border: none;
  
  &:hover {
    background: #0056b3;
  }
`;

const DocumentationList = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
`;

const DocumentCard = styled.div`
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
`;

const DocumentHeader = styled.div`
  padding: 15px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const DocumentTitle = styled.h3`
  margin: 0;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const DocumentActions = styled.div`
  display: flex;
  gap: 8px;
`;

const DocumentContent = styled.div`
  padding: 15px;
`;

const DocumentMeta = styled.div`
  padding: 15px;
  background: #f8f9fa;
  border-top: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 14px;
  color: #666;
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
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
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
  font-size: 14px;
  color: #666;
`;

const Input = styled.input`
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const TextArea = styled.textarea`
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  min-height: 200px;
  resize: vertical;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const ActionButton = styled.button`
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: 1px solid #ddd;
  color: #666;
  
  &:hover {
    background: #f5f5f5;
  }
  
  &.danger {
    color: #dc3545;
    border-color: #dc3545;
    
    &:hover {
      background: #dc3545;
      color: white;
    }
  }
`;

const ProjectDocumentation = ({ projectId }) => {
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingDoc, setEditingDoc] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    content: '',
    category: 'general'
  });
  
  useEffect(() => {
    fetchDocuments();
  }, [projectId]);
  
  const fetchDocuments = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/documents`);
      setDocuments(response.data);
    } catch (err) {
      setError('Failed to fetch documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCreateDocument = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`/api/projects/${projectId}/documents`, formData);
      setShowModal(false);
      setFormData({ title: '', content: '', category: 'general' });
      fetchDocuments();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create document');
    }
  };
  
  const handleUpdateDocument = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`/api/projects/${projectId}/documents/${editingDoc.id}`, formData);
      setShowModal(false);
      setEditingDoc(null);
      setFormData({ title: '', content: '', category: 'general' });
      fetchDocuments();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update document');
    }
  };
  
  const handleDeleteDocument = async (docId) => {
    if (!window.confirm('Are you sure you want to delete this document?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}/documents/${docId}`);
      fetchDocuments();
    } catch (err) {
      setError('Failed to delete document');
    }
  };
  
  const handleEditDocument = (doc) => {
    setEditingDoc(doc);
    setFormData({
      title: doc.title,
      content: doc.content,
      category: doc.category
    });
    setShowModal(true);
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const closeModal = () => {
    setShowModal(false);
    setEditingDoc(null);
    setFormData({ title: '', content: '', category: 'general' });
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>Project Documentation</Title>
        <Button onClick={() => setShowModal(true)}>
          <FaPlus />
          New Document
        </Button>
      </Header>
      
      {error && (
        <div style={{ color: 'red', marginBottom: '20px' }}>
          {error}
        </div>
      )}
      
      <DocumentationList>
        {documents.map(doc => (
          <DocumentCard key={doc.id}>
            <DocumentHeader>
              <DocumentTitle>
                <FaFileAlt />
                {doc.title}
              </DocumentTitle>
              <DocumentActions>
                <ActionButton onClick={() => handleEditDocument(doc)}>
                  <FaEdit />
                  Edit
                </ActionButton>
                <ActionButton
                  className="danger"
                  onClick={() => handleDeleteDocument(doc.id)}
                >
                  <FaTrash />
                  Delete
                </ActionButton>
              </DocumentActions>
            </DocumentHeader>
            <DocumentContent>
              <ReactMarkdown>{doc.content}</ReactMarkdown>
            </DocumentContent>
            <DocumentMeta>
              <span>Category: {doc.category}</span>
              <span>Last updated: {new Date(doc.updated_at).toLocaleDateString()}</span>
            </DocumentMeta>
          </DocumentCard>
        ))}
      </DocumentationList>
      
      {showModal && (
        <Modal>
          <ModalContent>
            <h2>{editingDoc ? 'Edit Document' : 'New Document'}</h2>
            <Form onSubmit={editingDoc ? handleUpdateDocument : handleCreateDocument}>
              <FormGroup>
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="category">Category</Label>
                <Input
                  id="category"
                  name="category"
                  value={formData.category}
                  onChange={handleChange}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="content">Content (Markdown)</Label>
                <TextArea
                  id="content"
                  name="content"
                  value={formData.content}
                  onChange={handleChange}
                  required
                />
              </FormGroup>
              
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <ActionButton type="button" onClick={closeModal}>
                  <FaTimes />
                  Cancel
                </ActionButton>
                <Button type="submit">
                  <FaSave />
                  {editingDoc ? 'Update' : 'Create'}
                </Button>
              </div>
            </Form>
          </ModalContent>
        </Modal>
      )}
    </Container>
  );
};

export default ProjectDocumentation; 