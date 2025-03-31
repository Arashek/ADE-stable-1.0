import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { FaPlus, FaSearch } from 'react-icons/fa';
import { FaExclamationTriangle } from 'react-icons/fa';

import ProjectCard from './ProjectCard';
import ProjectList from './ProjectList';
import ProjectFilters from './ProjectFilters';
import CreateProjectModal from './CreateProjectModal';
import { projectService } from '../../services/projectService';

const PageContainer = styled.div`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const Title = styled.h1`
  font-size: 24px;
  color: #1e293b;
  margin: 0;
`;

const SearchBar = styled.div`
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 8px 12px;
  width: 300px;
`;

const SearchInput = styled.input`
  border: none;
  outline: none;
  width: 100%;
  margin-left: 8px;
  font-size: 14px;
`;

const CreateButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: #2563eb;
  }
`;

const ViewToggle = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
`;

const ToggleButton = styled.button`
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: ${props => props.active ? '#f1f5f9' : 'white'};
  color: ${props => props.active ? '#1e293b' : '#64748b'};
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #f8fafc;
  }
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  color: #3b82f6;
  font-size: 16px;
`;

const ErrorMessage = styled.div`
  background: #fee2e2;
  color: #991b1b;
  padding: 16px;
  border-radius: 6px;
  margin: 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ProjectsPage = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('list');
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    status: 'all',
    timeline: 'all',
    teamSize: 'all'
  });

  const fetchProjects = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await projectService.getProjects(filters);
      setProjects(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProjects();
  }, [filters]);

  const handleCreateProject = async (projectData) => {
    try {
      const newProject = await projectService.createProject(projectData);
      setProjects(prev => [...prev, newProject]);
      setIsCreateModalOpen(false);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleMenuClick = async (projectId, action) => {
    try {
      switch (action) {
        case 'delete':
          await projectService.deleteProject(projectId);
          setProjects(prev => prev.filter(p => p.id !== projectId));
          break;
        case 'status':
          // Handle status update
          break;
        case 'progress':
          // Handle progress update
          break;
        default:
          break;
      }
    } catch (err) {
      setError(err.message);
    }
  };

  const filteredProjects = projects.filter(project =>
    project.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <PageContainer>
      <Header>
        <Title>Projects</Title>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <SearchBar>
            <FaSearch color="#64748b" />
            <SearchInput
              type="text"
              placeholder="Search projects..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </SearchBar>
          <CreateButton onClick={() => setIsCreateModalOpen(true)}>
            <FaPlus />
            Create Project
          </CreateButton>
        </div>
      </Header>

      <ViewToggle>
        <ToggleButton
          active={viewMode === 'list'}
          onClick={() => setViewMode('list')}
        >
          List View
        </ToggleButton>
        <ToggleButton
          active={viewMode === 'grid'}
          onClick={() => setViewMode('grid')}
        >
          Grid View
        </ToggleButton>
      </ViewToggle>

      <ProjectFilters filters={filters} onFilterChange={setFilters} />

      {error && (
        <ErrorMessage>
          <FaExclamationTriangle />
          {error}
        </ErrorMessage>
      )}

      {loading ? (
        <LoadingSpinner>Loading projects...</LoadingSpinner>
      ) : (
        viewMode === 'list' ? (
          <ProjectList
            projects={filteredProjects}
            onMenuClick={handleMenuClick}
          />
        ) : (
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '24px'
          }}>
            {filteredProjects.map(project => (
              <ProjectCard
                key={project.id}
                project={project}
                onMenuClick={handleMenuClick}
              />
            ))}
          </div>
        )
      )}

      <CreateProjectModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateProject}
      />
    </PageContainer>
  );
};

export default ProjectsPage; 