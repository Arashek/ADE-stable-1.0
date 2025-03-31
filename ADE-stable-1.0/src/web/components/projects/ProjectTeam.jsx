import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaUsers, FaPlus, FaTrash, FaEdit, FaSave, FaTimes, FaUser, FaUserShield, FaUserPlus, FaUserMinus } from 'react-icons/fa';
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

const TeamGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
`;

const TeamCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const TeamHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const TeamInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const TeamName = styled.h3`
  margin: 0;
  color: #333;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TeamMeta = styled.div`
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

const TeamActions = styled.div`
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

const TeamDetails = styled.div`
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

const TeamMembers = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const MembersTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
`;

const MembersList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const MemberItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: #f8f9fa;
  border-radius: 4px;
  font-size: 12px;
`;

const MemberInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const MemberAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: #e9ecef;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #495057;
`;

const MemberDetails = styled.div`
  display: flex;
  flex-direction: column;
  gap: 2px;
`;

const MemberName = styled.div`
  font-weight: 500;
  color: #333;
`;

const MemberRole = styled.div`
  color: #666;
  font-size: 11px;
`;

const MemberActions = styled.div`
  display: flex;
  gap: 8px;
`;

const TeamPermissions = styled.div`
  margin-top: 15px;
  padding-top: 15px;
  border-top: 1px solid #eee;
`;

const PermissionsTitle = styled.h4`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 14px;
`;

const PermissionsList = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
`;

const PermissionTag = styled.span`
  padding: 4px 8px;
  background: #e9ecef;
  border-radius: 4px;
  font-size: 12px;
  color: #495057;
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

const ProjectTeam = ({ projectId }) => {
  const [teams, setTeams] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingTeam, setEditingTeam] = useState(null);
  const [newTeam, setNewTeam] = useState({
    name: '',
    description: '',
    members: [],
    permissions: []
  });
  
  const availableRoles = [
    'admin',
    'manager',
    'developer',
    'viewer'
  ];
  
  const availablePermissions = [
    'read',
    'write',
    'delete',
    'manage_members',
    'manage_settings',
    'manage_integrations',
    'manage_deployments',
    'view_analytics'
  ];
  
  useEffect(() => {
    fetchTeams();
  }, [projectId]);
  
  const fetchTeams = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/teams`);
      setTeams(response.data);
    } catch (err) {
      setError('Failed to fetch teams');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddTeam = async (e) => {
    e.preventDefault();
    
    try {
      await axios.post(`/api/projects/${projectId}/teams`, newTeam);
      setSuccess(true);
      setShowAddModal(false);
      setNewTeam({
        name: '',
        description: '',
        members: [],
        permissions: []
      });
      fetchTeams();
    } catch (err) {
      setError('Failed to add team');
      console.error(err);
    }
  };
  
  const handleUpdateTeam = async (e) => {
    e.preventDefault();
    
    try {
      await axios.put(`/api/projects/${projectId}/teams/${editingTeam.id}`, editingTeam);
      setSuccess(true);
      setEditingTeam(null);
      fetchTeams();
    } catch (err) {
      setError('Failed to update team');
      console.error(err);
    }
  };
  
  const handleDeleteTeam = async (teamId) => {
    if (!window.confirm('Are you sure you want to delete this team?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}/teams/${teamId}`);
      setSuccess(true);
      fetchTeams();
    } catch (err) {
      setError('Failed to delete team');
      console.error(err);
    }
  };
  
  const handleAddMember = async (teamId, userId) => {
    try {
      await axios.post(`/api/projects/${projectId}/teams/${teamId}/members`, { userId });
      setSuccess(true);
      fetchTeams();
    } catch (err) {
      setError('Failed to add team member');
      console.error(err);
    }
  };
  
  const handleRemoveMember = async (teamId, userId) => {
    try {
      await axios.delete(`/api/projects/${projectId}/teams/${teamId}/members/${userId}`);
      setSuccess(true);
      fetchTeams();
    } catch (err) {
      setError('Failed to remove team member');
      console.error(err);
    }
  };
  
  const togglePermission = (permission, team) => {
    const permissions = team.permissions.includes(permission)
      ? team.permissions.filter(p => p !== permission)
      : [...team.permissions, permission];
    
    if (team === newTeam) {
      setNewTeam(prev => ({ ...prev, permissions }));
    } else {
      setEditingTeam(prev => ({ ...prev, permissions }));
    }
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>
          <FaUsers />
          Project Teams
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
        Add Team
      </Button>
      
      <TeamGrid>
        {teams.map(team => (
          <TeamCard key={team.id}>
            <TeamHeader>
              <TeamInfo>
                <TeamName>
                  <FaUserShield />
                  {team.name}
                </TeamName>
                <TeamMeta>
                  <MetaItem>
                    <FaUsers />
                    {team.members.length} members
                  </MetaItem>
                  <MetaItem>
                    <FaUserShield />
                    {team.permissions.length} permissions
                  </MetaItem>
                </TeamMeta>
              </TeamInfo>
              <TeamActions>
                <Button onClick={() => setEditingTeam(team)}>
                  <FaEdit />
                  Edit
                </Button>
                <Button
                  variant="danger"
                  onClick={() => handleDeleteTeam(team.id)}
                >
                  <FaTrash />
                  Delete
                </Button>
              </TeamActions>
            </TeamHeader>
            
            <TeamDetails>
              <DetailRow>
                <DetailLabel>Description</DetailLabel>
                <DetailValue>
                  {team.description || 'No description'}
                </DetailValue>
              </DetailRow>
              <DetailRow>
                <DetailLabel>Created</DetailLabel>
                <DetailValue>
                  {new Date(team.createdAt).toLocaleString()}
                </DetailValue>
              </DetailRow>
            </TeamDetails>
            
            <TeamMembers>
              <MembersTitle>Team Members</MembersTitle>
              <MembersList>
                {team.members.map(member => (
                  <MemberItem key={member.id}>
                    <MemberInfo>
                      <MemberAvatar>
                        <FaUser />
                      </MemberAvatar>
                      <MemberDetails>
                        <MemberName>{member.name}</MemberName>
                        <MemberRole>{member.role}</MemberRole>
                      </MemberDetails>
                    </MemberInfo>
                    <MemberActions>
                      <Button
                        variant="danger"
                        onClick={() => handleRemoveMember(team.id, member.id)}
                      >
                        <FaUserMinus />
                        Remove
                      </Button>
                    </MemberActions>
                  </MemberItem>
                ))}
              </MembersList>
            </TeamMembers>
            
            <TeamPermissions>
              <PermissionsTitle>Permissions</PermissionsTitle>
              <PermissionsList>
                {availablePermissions.map(permission => (
                  <PermissionTag
                    key={permission}
                    style={{
                      background: team.permissions.includes(permission) ? '#cce5ff' : '#e9ecef',
                      color: team.permissions.includes(permission) ? '#004085' : '#495057'
                    }}
                  >
                    {permission.replace('_', ' ')}
                  </PermissionTag>
                ))}
              </PermissionsList>
            </TeamPermissions>
          </TeamCard>
        ))}
      </TeamGrid>
      
      {showAddModal && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Add New Team</ModalTitle>
              <CloseButton onClick={() => setShowAddModal(false)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleAddTeam}>
              <FormGroup>
                <Label>Team Name</Label>
                <Input
                  type="text"
                  value={newTeam.name}
                  onChange={(e) => setNewTeam(prev => ({
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
                  value={newTeam.description}
                  onChange={(e) => setNewTeam(prev => ({
                    ...prev,
                    description: e.target.value
                  }))}
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Permissions</Label>
                <CheckboxGroup>
                  {availablePermissions.map(permission => (
                    <CheckboxLabel key={permission}>
                      <input
                        type="checkbox"
                        checked={newTeam.permissions.includes(permission)}
                        onChange={() => togglePermission(permission, newTeam)}
                      />
                      {permission.replace('_', ' ')}
                    </CheckboxLabel>
                  ))}
                </CheckboxGroup>
              </FormGroup>
              
              <Button type="submit">
                <FaPlus />
                Add Team
              </Button>
            </Form>
          </ModalContent>
        </Modal>
      )}
      
      {editingTeam && (
        <Modal>
          <ModalContent>
            <ModalHeader>
              <ModalTitle>Edit Team</ModalTitle>
              <CloseButton onClick={() => setEditingTeam(null)}>
                ×
              </CloseButton>
            </ModalHeader>
            
            <Form onSubmit={handleUpdateTeam}>
              <FormGroup>
                <Label>Team Name</Label>
                <Input
                  type="text"
                  value={editingTeam.name}
                  onChange={(e) => setEditingTeam(prev => ({
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
                  value={editingTeam.description}
                  onChange={(e) => setEditingTeam(prev => ({
                    ...prev,
                    description: e.target.value
                  }))}
                />
              </FormGroup>
              
              <FormGroup>
                <Label>Permissions</Label>
                <CheckboxGroup>
                  {availablePermissions.map(permission => (
                    <CheckboxLabel key={permission}>
                      <input
                        type="checkbox"
                        checked={editingTeam.permissions.includes(permission)}
                        onChange={() => togglePermission(permission, editingTeam)}
                      />
                      {permission.replace('_', ' ')}
                    </CheckboxLabel>
                  ))}
                </CheckboxGroup>
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

export default ProjectTeam; 