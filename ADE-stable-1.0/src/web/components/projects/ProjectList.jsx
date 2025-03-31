import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaPlus, FaFolder, FaArchive, FaTrash } from 'react-icons/fa';
import axios from 'axios';

const ProjectListContainer = styled.div`
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
`;

const Title = styled.h1`
  margin: 0;
  color: #333;
`;

const CreateButton = styled.button`
  display: flex;
  align-items: center;
  padding: 10px 20px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-size: 16px;
  
  &:hover {
    background: #0056b3;
  }
  
  svg {
    margin-right: 8px;
  }
`;

const ProjectGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
`;

const ProjectCard = styled.div`
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  transition: transform 0.2s;
  
  &:hover {
    transform: translateY(-2px);
  }
`;

const ProjectHeader = styled.div`
  display: flex;
  align-items: center;
  margin-bottom: 15px;
  
  svg {
    margin-right: 10px;
    color: #666;
  }
`;

const ProjectName = styled.h2`
  margin: 0;
  font-size: 18px;
  color: #333;
`;

const ProjectDescription = styled.p`
  margin: 0 0 15px 0;
  color: #666;
  font-size: 14px;
`;

const ProjectMeta = styled.div`
  display: flex;
  justify-content: space-between;
  color: #888;
  font-size: 12px;
`;

const ProjectActions = styled.div`
  display: flex;
  gap: 10px;
  margin-top: 15px;
`;

const ActionButton = styled.button`
  padding: 5px 10px;
  background: none;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  color: #666;
  
  &:hover {
    background: #f5f5f5;
  }
  
  svg {
    margin-right: 4px;
  }
`;

const ProjectList = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    fetchProjects();
  }, []);
  
  const fetchProjects = async () => {
    try {
      const response = await axios.get('/api/projects');
      setProjects(response.data);
    } catch (err) {
      setError('Failed to fetch projects');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleArchive = async (projectId) => {
    try {
      await axios.post(`/api/projects/${projectId}/archive`);
      fetchProjects();
    } catch (err) {
      console.error(err);
    }
  };
  
  const handleDelete = async (projectId) => {
    if (!window.confirm('Are you sure you want to delete this project?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}`);
      fetchProjects();
    } catch (err) {
      console.error(err);
    }
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (error) {
    return <div>Error: {error}</div>;
  }
  
  return (
    <ProjectListContainer>
      <Header>
        <Title>Projects</Title>
        <CreateButton>
          <FaPlus />
          New Project
        </CreateButton>
      </Header>
      
      <ProjectGrid>
        {projects.map(project => (
          <ProjectCard key={project.id}>
            <ProjectHeader>
              <FaFolder />
              <ProjectName>{project.name}</ProjectName>
            </ProjectHeader>
            
            <ProjectDescription>
              {project.config.description || 'No description'}
            </ProjectDescription>
            
            <ProjectMeta>
              <span>Created: {new Date(project.metadata.created_at).toLocaleDateString()}</span>
              <span>Status: {project.metadata.status}</span>
            </ProjectMeta>
            
            <ProjectActions>
              <ActionButton>
                Open
              </ActionButton>
              <ActionButton onClick={() => handleArchive(project.id)}>
                <FaArchive />
                Archive
              </ActionButton>
              <ActionButton onClick={() => handleDelete(project.id)}>
                <FaTrash />
                Delete
              </ActionButton>
            </ProjectActions>
          </ProjectCard>
        ))}
      </ProjectGrid>
    </ProjectListContainer>
  );
};

export default ProjectList; 