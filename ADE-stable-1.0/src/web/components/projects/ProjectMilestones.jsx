import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaFlag, FaPlus, FaTrash, FaEdit, FaSave, FaTimes, FaCalendar, FaCheckCircle, FaClock, FaUser, FaTag, FaPaperclip, FaCodeBranch } from 'react-icons/fa';
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

const MilestonesGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
`;

const MilestoneCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const MilestoneHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const MilestoneInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const MilestoneTitle = styled.h3`
  margin: 0;
  color: #333;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const MilestoneMeta = styled.div`
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

const MilestoneActions = styled.div`
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

const MilestoneDetails = styled.div`
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

const MilestoneDescription = styled.div`
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

const MilestoneProgress = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const ProgressTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
`;

const ProgressBar = styled.div`
  width: 100%;
  height: 8px;
  background: #e9ecef;
  border-radius: 4px;
  overflow: hidden;
`;

const ProgressFill = styled.div`
  width: ${props => props.progress}%;
  height: 100%;
  background: ${props => {
    if (props.progress >= 100) return '#28a745';
    if (props.progress >= 75) return '#17a2b8';
    if (props.progress >= 50) return '#ffc107';
    return '#dc3545';
  }};
  transition: width 0.3s ease;
`;

const ProgressText = styled.div`
  margin-top: 5px;
  font-size: 12px;
  color: #666;
  text-align: right;
`;

const MilestoneIssues = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const IssuesTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
`;

const IssuesList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const IssueItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
`;

const IssueInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const IssueMeta = styled.div`
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

const ProjectMilestones = ({ projectId }) => {
  const [milestones, setMilestones] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingMilestone, setEditingMilestone] = useState(null);
  const [newMilestone, setNewMilestone] = useState({
    title: '',
    description: '',
    dueDate: '',
    status: 'planned',
    progress: 0,
    issues: [],
    tags: []
  });
  
  const availableStatuses = [
    { id: 'planned', name: 'Planned', icon: FaClock },
    { id: 'in_progress', name: 'In Progress', icon: FaCheckCircle },
    { id: 'completed', name: 'Completed', icon: FaCheckCircle },
    { id: 'cancelled', name: 'Cancelled', icon: FaTimes }
  ];
  
  useEffect(() => {
    fetchMilestones();
  }, [projectId]);
  
  const fetchMilestones = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/milestones`);
      setMilestones(response.data);
    } catch (err) {
      setError('Failed to fetch milestones');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddMilestone = async (e) => {
    e.preventDefault();
    
    try {
      await axios.post(`/api/projects/${projectId}/milestones`, newMilestone);
      setSuccess(true);
      setShowAddModal(false);
      setNewMilestone({
        title: '',
        description: '',
        dueDate: '',
        status: 'planned',
        progress: 0,
        issues: [],
        tags: []
      });
      fetchMilestones();
    } catch (err) {
      setError('Failed to add milestone');
      console.error(err);
    }
  };
  
  const handleUpdateMilestone = async (e) => {
    e.preventDefault();
    
    try {
      await axios.put(`/api/projects/${projectId}/milestones/${editingMilestone.id}`, editingMilestone);
      setSuccess(true);
      setEditingMilestone(null);
      fetchMilestones();
    } catch (err) {
      setError('Failed to update milestone');
      console.error(err);
    }
  };
  
  const handleDeleteMilestone = async (milestoneId) => {
    if (!window.confirm('Are you sure you want to delete this milestone?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}/milestones/${milestoneId}`);
      setSuccess(true);
      fetchMilestones();
    } catch (err) {
      setError('Failed to delete milestone');
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
          <FaFlag />
          Project Milestones
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
        Add Milestone
      </Button>
      
      <MilestonesGrid>
        {milestones.map(milestone => {
          const StatusIcon = getStatusIcon(milestone.status);
          
          return (
            <MilestoneCard key={milestone.id}>
              <MilestoneHeader>
                <MilestoneInfo>
                  <MilestoneTitle>
                    <StatusIcon />
                    {milestone.title}
                  </MilestoneTitle>
                  <MilestoneMeta>
                    <MetaItem>
                      <FaCalendar />
                      {new Date(milestone.dueDate).toLocaleDateString()}
                    </MetaItem>
                    <MetaItem>
                      <FaTag />
                      {milestone.tags.length} tags
                    </MetaItem>
                    <MetaItem>
                      <FaCodeBranch />
                      {milestone.issues.length} issues
                    </MetaItem>
                  </MilestoneMeta>
                </MilestoneInfo>
                <MilestoneActions>
                  <Button onClick={() => setEditingMilestone(milestone)}>
                    <FaEdit />
                    Edit
                  </Button>
                  <Button
                    variant="danger"
                    onClick={() => handleDeleteMilestone(milestone.id)}
                  >
                    <FaTrash />
                    Delete
                  </Button>
                </MilestoneActions>
              </MilestoneHeader>
              
              <MilestoneDetails>
                <DetailRow>
                  <DetailLabel>Status</DetailLabel>
                  <DetailValue>
                    {milestone.status.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Due Date</DetailLabel>
                  <DetailValue>
                    {new Date(milestone.dueDate).toLocaleDateString()}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Created</DetailLabel>
                  <DetailValue>
                    {new Date(milestone.createdAt).toLocaleString()}
                  </DetailValue>
                </DetailRow>
                <DetailRow>
                  <DetailLabel>Last Updated</DetailLabel>
                  <DetailValue>
                    {new Date(milestone.updatedAt).toLocaleString()}
                  </DetailValue>
                </DetailRow>
              </MilestoneDetails>
              
              <MilestoneDescription>
                <DescriptionContent>
                  {milestone.description}
                </DescriptionContent>
              </MilestoneDescription>
              
              <MilestoneProgress>
                <ProgressTitle>Progress</ProgressTitle>
                <ProgressBar>
                  <ProgressFill progress={milestone.progress} />
                </ProgressBar>
                <ProgressText>
                  {milestone.progress}% Complete
                </ProgressText>
              </MilestoneProgress>
              
              <MilestoneIssues>
                <IssuesTitle>Issues</IssuesTitle>
                <IssuesList>
                  {milestone.issues?.map(issue => (
                    <IssueItem key={issue.id}>
                      <IssueInfo>
                        <div>{issue.title}</div>
                        <IssueMeta>
                          <span>{issue.status.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}</span>
                          <span>{issue.assignee?.name || 'Unassigned'}</span>
                        </IssueMeta>
                      </IssueInfo>
                    </IssueItem>
                  ))}
                </IssuesList>
              </MilestoneIssues>
            </MilestoneCard>
          );
        })}
      </MilestonesGrid>
      
      {showAddModal && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Add New Milestone</ModalTitle>
              <CloseButton onClick={() => setShowAddModal(false)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleAddMilestone}>
              <FormGroup>
                <Label>Milestone Title</Label>
                <Input
                  type="text"
                  value={newMilestone.title}
                  onChange={(e) => setNewMilestone(prev => ({
                    ...prev,
                    title: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Description</Label>
                <TextArea
                  value={newMilestone.description}
                  onChange={(e) => setNewMilestone(prev => ({
                    ...prev,
                    description: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Due Date</Label>
                <Input
                  type="date"
                  value={newMilestone.dueDate}
                  onChange={(e) => setNewMilestone(prev => ({
                    ...prev,
                    dueDate: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Status</Label>
                <Select
                  value={newMilestone.status}
                  onChange={(e) => setNewMilestone(prev => ({
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
              
              <FormGroup>
                <Label>Progress (%)</Label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  value={newMilestone.progress}
                  onChange={(e) => setNewMilestone(prev => ({
                    ...prev,
                    progress: parseInt(e.target.value)
                  }))}
                />
              </FormGroup>
              
              <Button type="submit">
                <FaPlus />
                Add Milestone
              </Button>
            </Form>
          </ModalContent>
        </Modal>
      )}
      
      {editingMilestone && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Edit Milestone</ModalTitle>
              <CloseButton onClick={() => setEditingMilestone(null)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleUpdateMilestone}>
              <FormGroup>
                <Label>Milestone Title</Label>
                <Input
                  type="text"
                  value={editingMilestone.title}
                  onChange={(e) => setEditingMilestone(prev => ({
                    ...prev,
                    title: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Description</Label>
                <TextArea
                  value={editingMilestone.description}
                  onChange={(e) => setEditingMilestone(prev => ({
                    ...prev,
                    description: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Due Date</Label>
                <Input
                  type="date"
                  value={editingMilestone.dueDate}
                  onChange={(e) => setEditingMilestone(prev => ({
                    ...prev,
                    dueDate: e.target.value
                  }))}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Status</Label>
                <Select
                  value={editingMilestone.status}
                  onChange={(e) => setEditingMilestone(prev => ({
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
              
              <FormGroup>
                <Label>Progress (%)</Label>
                <Input
                  type="number"
                  min="0"
                  max="100"
                  value={editingMilestone.progress}
                  onChange={(e) => setEditingMilestone(prev => ({
                    ...prev,
                    progress: parseInt(e.target.value)
                  }))}
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

export default ProjectMilestones; 