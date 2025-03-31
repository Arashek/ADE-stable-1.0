import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaBug, FaPlus, FaTrash, FaEdit, FaSave, FaTimes, FaExclamationTriangle, FaExclamationCircle, FaCheckCircle, FaClock, FaUser, FaTag, FaPaperclip, FaComment } from 'react-icons/fa';
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

const IssuesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
`;

const IssueCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const IssueHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const IssueInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const IssueTitle = styled.h3`
  margin: 0;
  color: #333;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const IssueMeta = styled.div`
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

const IssueActions = styled.div`
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

const IssueDetails = styled.div`
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

const IssueDescription = styled.div`
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

const IssueStatus = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const StatusTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
`;

const StatusList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const StatusItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
`;

const StatusInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const StatusMeta = styled.div`
  display: flex;
  gap: 10px;
  color: #999;
`;

const IssueComments = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const CommentsTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
`;

const CommentsList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const CommentItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
`;

const CommentInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const CommentMeta = styled.div`
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

const ProjectIssues = ({ projectId }) => {
  const [issues, setIssues] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingIssue, setEditingIssue] = useState(null);
  const [newIssue, setNewIssue] = useState({
    title: '',
    description: '',
    type: 'bug',
    priority: 'medium',
    status: 'open',
    assignee: null,
    tags: [],
    attachments: []
  });
  
  const availableTypes = [
    { id: 'bug', name: 'Bug', icon: FaBug },
    { id: 'feature', name: 'Feature', icon: FaPlus },
    { id: 'task', name: 'Task', icon: FaCheckCircle }
  ];
  
  const availablePriorities = [
    { id: 'low', name: 'Low', icon: FaExclamationCircle },
    { id: 'medium', name: 'Medium', icon: FaExclamationTriangle },
    { id: 'high', name: 'High', icon: FaBug }
  ];
  
  const availableStatuses = [
    { id: 'open', name: 'Open', icon: FaClock },
    { id: 'in_progress', name: 'In Progress', icon: FaCheckCircle },
    { id: 'resolved', name: 'Resolved', icon: FaCheckCircle },
    { id: 'closed', name: 'Closed', icon: FaTimes }
  ];
  
  useEffect(() => {
    fetchIssues();
  }, [projectId]);
  
  const fetchIssues = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/issues`);
      setIssues(response.data);
    } catch (err) {
      setError('Failed to fetch issues');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddIssue = async (e) => {
    e.preventDefault();
    
    try {
      await axios.post(`/api/projects/${projectId}/issues`, newIssue);
      setSuccess(true);
      setShowAddModal(false);
      setNewIssue({
        title: '',
        description: '',
        type: 'bug',
        priority: 'medium',
        status: 'open',
        assignee: null,
        tags: [],
        attachments: []
      });
      fetchIssues();
    } catch (err) {
      setError('Failed to add issue');
      console.error(err);
    }
  };
  
  const handleUpdateIssue = async (e) => {
    e.preventDefault();
    
    try {
      await axios.put(`/api/projects/${projectId}/issues/${editingIssue.id}`, editingIssue);
      setSuccess(true);
      setEditingIssue(null);
      fetchIssues();
    } catch (err) {
      setError('Failed to update issue');
      console.error(err);
    }
  };
  
  const handleDeleteIssue = async (issueId) => {
    if (!window.confirm('Are you sure you want to delete this issue?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}/issues/${issueId}`);
      setSuccess(true);
      fetchIssues();
    } catch (err) {
      setError('Failed to delete issue');
      console.error(err);
    }
  };
  
  const getIssueIcon = (type) => {
    const issueType = availableTypes.find(t => t.id === type);
    return issueType ? issueType.icon : FaBug;
  };
  
  const getPriorityIcon = (priority) => {
    const priorityType = availablePriorities.find(p => p.id === priority);
    return priorityType ? priorityType.icon : FaExclamationCircle;
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
          <FaBug />
          Project Issues
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
        Add Issue
      </Button>
      
      <IssuesGrid>
        {issues.map(issue => {
          const TypeIcon = getIssueIcon(issue.type);
          const PriorityIcon = getPriorityIcon(issue.priority);
          const StatusIcon = getStatusIcon(issue.status);
          
          return (
            <IssueCard key={issue.id}>
              <IssueHeader>
                <IssueInfo>
                  <IssueTitle>
                    <TypeIcon />
                    {issue.title}
                    <PriorityIcon />
                    <StatusIcon />
                  </IssueTitle>
                  <IssueMeta>
                    <MetaItem>
                      <FaUser />
                      {issue.assignee?.name || 'Unassigned'}
                    </MetaItem>
                    <MetaItem>
                      <FaTag />
                      {issue.tags.length} tags
                    </MetaItem>
                    <MetaItem>
                      <FaPaperclip />
                      {issue.attachments.length} attachments
                    </MetaItem>
                  </IssueMeta>
                </IssueInfo>
                <IssueActions>
                  <Button onClick={() => setEditingIssue(issue)}>
                    <FaEdit />
                    Edit
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => handleDeleteIssue(issue.id)}
                  >
                    <FaTrash />
                    Delete
                  </Button>
                </IssueActions>
              </IssueHeader>
              
              <IssueDetails>
                <DetailRow>
                  <DetailLabel>Type</DetailLabel>
                  <DetailValue>
                    {issue.type.charAt(0).toUpperCase() + issue.type.slice(1)}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Priority</DetailLabel>
                  <DetailValue>
                    {issue.priority.charAt(0).toUpperCase() + issue.priority.slice(1)}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Status</DetailLabel>
                  <DetailValue>
                    {issue.status.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Created</DetailLabel>
                  <DetailValue>
                    {new Date(issue.createdAt).toLocaleString()}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Last Updated</DetailLabel>
                  <DetailValue>
                    {new Date(issue.updatedAt).toLocaleString()}
                  </DetailValue>
                </DetailRow>
              </IssueDetails>
              
              <IssueDescription>
                <DescriptionContent>
                  {issue.description}
                </DescriptionContent>
              </IssueDescription>
              
              <IssueStatus>
                <StatusTitle>Status History</StatusTitle>
                <StatusList>
                  {issue.statusHistory?.map(status => (
                    <StatusItem key={status.id}>
                      <StatusInfo>
                        <div>{status.status.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}</div>
                        <StatusMeta>
                          <span>{new Date(status.timestamp).toLocaleString()}</span>
                          <span>{status.user}</span>
                        </StatusMeta>
                      </StatusInfo>
                    </StatusItem>
                  ))}
                </StatusList>
              </IssueStatus>
              
              <IssueComments>
                <CommentsTitle>Comments</CommentsTitle>
                <CommentsList>
                  {issue.comments?.map(comment => (
                    <CommentItem key={comment.id}>
                      <CommentInfo>
                        <div>{comment.content}</div>
                        <CommentMeta>
                          <span>{new Date(comment.timestamp).toLocaleString()}</span>
                          <span>{comment.user}</span>
                        </CommentMeta>
                      </CommentInfo>
                    </CommentItem>
                  ))}
                </CommentsList>
              </IssueComments>
            </IssueCard>
          );
        })}
      </IssuesGrid>
      
      {showAddModal && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Add New Issue</ModalTitle>
              <CloseButton onClick={() => setShowAddModal(false)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleAddIssue}>
              <FormGroup>
                <Label>Issue Title</Label>
                <Input
                  type="text"
                  value={newIssue.title}
                  onChange={(e) => setNewIssue(prev => ({
                    ...prev,
                    title: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Description</Label>
                <TextArea
                  value={newIssue.description}
                  onChange={(e) => setNewIssue(prev => ({
                    ...prev,
                    description: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Type</Label>
                <Select
                  value={newIssue.type}
                  onChange={(e) => setNewIssue(prev => ({
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
                <Label>Priority</Label>
                <Select
                  value={newIssue.priority}
                  onChange={(e) => setNewIssue(prev => ({
                    ...prev,
                    priority: e.target.value
                  }))}
                >
                  {availablePriorities.map(priority => (
                    <option key={priority.id} value={priority.id}>
                      {priority.name}
                    </option>
                  ))}
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label>Status</Label>
                <Select
                  value={newIssue.status}
                  onChange={(e) => setNewIssue(prev => ({
                    ...prev,
                    status: e.target.value
                  }))}
                >
                  {availableStatuses.map(status => (
                    <option key={status.id} value={status.id}>
                      {status.name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                    </option>
                  ))}
                </Select>
              </FormGroup>
              
              <Button type="submit">
                <FaPlus />
                Add Issue
              </Button>
            </Form>
          </ModalContent>
        </Modal>
      )}
      
      {editingIssue && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Edit Issue</ModalTitle>
              <CloseButton onClick={() => setEditingIssue(null)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleUpdateIssue}>
              <FormGroup>
                <Label>Issue Title</Label>
                <Input
                  type="text"
                  value={editingIssue.title}
                  onChange={(e) => setEditingIssue(prev => ({
                    ...prev,
                    title: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Description</Label>
                <TextArea
                  value={editingIssue.description}
                  onChange={(e) => setEditingIssue(prev => ({
                    ...prev,
                    description: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Type</Label>
                <Select
                  value={editingIssue.type}
                  onChange={(e) => setEditingIssue(prev => ({
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
                <Label>Priority</Label>
                <Select
                  value={editingIssue.priority}
                  onChange={(e) => setEditingIssue(prev => ({
                    ...prev,
                    priority: e.target.value
                  }))}
                >
                  {availablePriorities.map(priority => (
                    <option key={priority.id} value={priority.id}>
                      {priority.name}
                    </option>
                  ))}
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label>Status</Label>
                <Select
                  value={editingIssue.status}
                  onChange={(e) => setEditingIssue(prev => ({
                    ...prev,
                    status: e.target.value
                  }))}
                >
                  {availableStatuses.map(status => (
                    <option key={status.id} value={status.id}>
                      {status.name.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                    </option>
                  ))}
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

export default ProjectIssues; 