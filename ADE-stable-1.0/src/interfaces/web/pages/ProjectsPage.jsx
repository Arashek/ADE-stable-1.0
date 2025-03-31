import React, { useState } from 'react';
import styled from 'styled-components';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { FaPlus, FaSearch, FaFilter, FaFolder, FaClock, FaUsers } from 'react-icons/fa';

const ProjectsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const ProjectsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const SearchBar = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: white;
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  width: 300px;

  @media (max-width: 768px) {
    width: 100%;
  }
`;

const SearchInput = styled.input`
  border: none;
  outline: none;
  width: 100%;
  font-size: 0.875rem;
  color: #1f2937;

  &::placeholder {
    color: #9ca3af;
  }
`;

const FilterButton = styled(Button)`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ProjectsGrid = styled.div`
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
`;

const ProjectCard = styled(Card)`
  display: flex;
  flex-direction: column;
  gap: 16px;
  cursor: pointer;
  transition: transform 0.2s ease;

  &:hover {
    transform: translateY(-2px);
  }
`;

const ProjectHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const ProjectIcon = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background-color: #4a7bff20;
  color: #4a7bff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
`;

const ProjectInfo = styled.div`
  flex: 1;
`;

const ProjectName = styled.div`
  font-weight: 500;
  color: #1f2937;
`;

const ProjectStatus = styled.div`
  font-size: 12px;
  color: ${props => {
    switch (props.status) {
      case 'active': return '#10b981';
      case 'archived': return '#6b7280';
      case 'on-hold': return '#f59e0b';
      default: return '#6b7280';
    }
  }};
`;

const ProjectMeta = styled.div`
  display: flex;
  gap: 16px;
  color: #6b7280;
  font-size: 0.875rem;
`;

const MetaItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
`;

const ProjectProgress = styled.div`
  width: 100%;
  height: 4px;
  background-color: #e5e7eb;
  border-radius: 2px;
  overflow: hidden;
`;

const ProgressBar = styled.div`
  height: 100%;
  background-color: #4a7bff;
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
`;

const ProjectActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: auto;
`;

// Mock data
const projects = [
  {
    id: 1,
    name: 'E-commerce Platform',
    status: 'active',
    progress: 75,
    teamSize: 5,
    lastUpdated: '2 hours ago',
    description: 'Modern e-commerce platform with AI-powered recommendations',
  },
  {
    id: 2,
    name: 'Mobile App',
    status: 'on-hold',
    progress: 45,
    teamSize: 3,
    lastUpdated: '1 day ago',
    description: 'Cross-platform mobile application for task management',
  },
  {
    id: 3,
    name: 'API Gateway',
    status: 'active',
    progress: 90,
    teamSize: 4,
    lastUpdated: '30 minutes ago',
    description: 'Microservices API gateway with authentication',
  },
  {
    id: 4,
    name: 'Analytics Dashboard',
    status: 'archived',
    progress: 100,
    teamSize: 2,
    lastUpdated: '1 week ago',
    description: 'Data visualization dashboard for business metrics',
  },
];

const ProjectsList = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();

  const filteredProjects = projects.filter(project =>
    project.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
    project.description.toLowerCase().includes(searchQuery.toLowerCase())
  );

  return (
    <ProjectsContainer>
      <ProjectsHeader>
        <SearchBar>
          <FaSearch color="#9ca3af" />
          <SearchInput
            type="text"
            placeholder="Search projects..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </SearchBar>
        <FilterButton variant="secondary" icon={<FaFilter />}>
          Filter
        </FilterButton>
      </ProjectsHeader>

      <ProjectsGrid>
        {filteredProjects.map(project => (
          <ProjectCard
            key={project.id}
            onClick={() => navigate(`/projects/${project.id}`)}
          >
            <ProjectHeader>
              <ProjectIcon>
                <FaFolder />
              </ProjectIcon>
              <ProjectInfo>
                <ProjectName>{project.name}</ProjectName>
                <ProjectStatus status={project.status}>
                  {project.status.charAt(0).toUpperCase() + project.status.slice(1)}
                </ProjectStatus>
              </ProjectInfo>
            </ProjectHeader>

            <div style={{ color: '#6b7280', fontSize: '14px' }}>
              {project.description}
            </div>

            <ProjectMeta>
              <MetaItem>
                <FaUsers />
                {project.teamSize} members
              </MetaItem>
              <MetaItem>
                <FaClock />
                {project.lastUpdated}
              </MetaItem>
            </ProjectMeta>

            <ProjectProgress>
              <ProgressBar progress={project.progress} />
            </ProjectProgress>

            <ProjectActions>
              <Button size="small" variant="secondary">
                View Details
              </Button>
              <Button size="small">
                Manage
              </Button>
            </ProjectActions>
          </ProjectCard>
        ))}
      </ProjectsGrid>
    </ProjectsContainer>
  );
};

const ProjectCreate = () => {
  return (
    <Card title="Create New Project">
      {/* Project creation form will go here */}
      <div>Project creation form coming soon...</div>
    </Card>
  );
};

const ProjectDetails = () => {
  return (
    <Card title="Project Details">
      {/* Project details view will go here */}
      <div>Project details view coming soon...</div>
    </Card>
  );
};

const ProjectsPage = () => {
  return (
    <div>
      <ProjectsHeader>
        <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 600 }}>
          Projects
        </h1>
        <Button icon={<FaPlus />}>
          New Project
        </Button>
      </ProjectsHeader>

      <Routes>
        <Route path="/" element={<ProjectsList />} />
        <Route path="/create" element={<ProjectCreate />} />
        <Route path="/:id" element={<ProjectDetails />} />
      </Routes>
    </div>
  );
};

export default ProjectsPage; 