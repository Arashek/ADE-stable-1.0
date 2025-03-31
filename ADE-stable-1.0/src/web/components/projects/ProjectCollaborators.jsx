import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaUserPlus, FaUserMinus, FaUserShield } from 'react-icons/fa';
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
  margin: 0 0 10px 0;
  color: #333;
`;

const CollaboratorList = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const CollaboratorItem = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 15px;
  border-bottom: 1px solid #eee;
  
  &:last-child {
    border-bottom: none;
  }
`;

const CollaboratorInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 15px;
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: #007bff;
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
`;

const UserInfo = styled.div`
  display: flex;
  flex-direction: column;
`;

const UserName = styled.span`
  font-weight: 500;
  color: #333;
`;

const UserEmail = styled.span`
  font-size: 14px;
  color: #666;
`;

const RoleBadge = styled.span`
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  background: ${props => props.admin ? '#dc3545' : '#28a745'};
  color: white;
`;

const Button = styled.button`
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

const AddCollaboratorForm = styled.form`
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
`;

const Input = styled.input`
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const Select = styled.select`
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const ProjectCollaborators = ({ projectId }) => {
  const [collaborators, setCollaborators] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [newCollaborator, setNewCollaborator] = useState({
    email: '',
    role: 'member'
  });
  
  useEffect(() => {
    fetchCollaborators();
  }, [projectId]);
  
  const fetchCollaborators = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/collaborators`);
      setCollaborators(response.data);
    } catch (err) {
      setError('Failed to fetch collaborators');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleAddCollaborator = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`/api/projects/${projectId}/collaborators`, newCollaborator);
      setNewCollaborator({ email: '', role: 'member' });
      fetchCollaborators();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to add collaborator');
    }
  };
  
  const handleRemoveCollaborator = async (userId) => {
    if (!window.confirm('Are you sure you want to remove this collaborator?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}/collaborators/${userId}`);
      fetchCollaborators();
    } catch (err) {
      setError('Failed to remove collaborator');
    }
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setNewCollaborator(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>Project Collaborators</Title>
      </Header>
      
      <AddCollaboratorForm onSubmit={handleAddCollaborator}>
        <Input
          type="email"
          name="email"
          placeholder="Enter email address"
          value={newCollaborator.email}
          onChange={handleChange}
          required
        />
        <Select
          name="role"
          value={newCollaborator.role}
          onChange={handleChange}
        >
          <option value="member">Member</option>
          <option value="admin">Admin</option>
        </Select>
        <Button type="submit">
          <FaUserPlus />
          Add Collaborator
        </Button>
      </AddCollaboratorForm>
      
      {error && (
        <div style={{ color: 'red', marginBottom: '20px' }}>
          {error}
        </div>
      )}
      
      <CollaboratorList>
        {collaborators.map(collaborator => (
          <CollaboratorItem key={collaborator.id}>
            <CollaboratorInfo>
              <Avatar>
                {collaborator.name.charAt(0).toUpperCase()}
              </Avatar>
              <UserInfo>
                <UserName>{collaborator.name}</UserName>
                <UserEmail>{collaborator.email}</UserEmail>
              </UserInfo>
            </CollaboratorInfo>
            
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <RoleBadge admin={collaborator.role === 'admin'}>
                {collaborator.role === 'admin' ? 'Admin' : 'Member'}
              </RoleBadge>
              <Button
                className="danger"
                onClick={() => handleRemoveCollaborator(collaborator.id)}
              >
                <FaUserMinus />
                Remove
              </Button>
            </div>
          </CollaboratorItem>
        ))}
      </CollaboratorList>
    </Container>
  );
};

export default ProjectCollaborators; 