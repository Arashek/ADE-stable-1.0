import React, { useState } from 'react';
import styled from 'styled-components';
import { FaPlus, FaSearch, FaFilter, FaEllipsisV } from 'react-icons/fa';

const ProjectsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h1`
  font-size: 24px;
  color: #1e293b;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background: #2563eb;
  }
`;

const SearchBar = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  padding: 8px 16px;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const SearchInput = styled.input`
  border: none;
  outline: none;
  font-size: 14px;
  width: 100%;
`;

const ProjectsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
`;

const ProjectCard = styled.div`
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const ProjectHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const ProjectTitle = styled.h3`
  font-size: 18px;
  color: #1e293b;
  margin: 0;
`;

const ProjectMenu = styled.button`
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;

  &:hover {
    background: #f1f5f9;
  }
`;

const ProjectInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const InfoRow = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const InfoLabel = styled.span`
  color: #64748b;
  font-size: 14px;
`;

const InfoValue = styled.span`
  color: #1e293b;
  font-size: 14px;
`;

const ProgressBar = styled.div`
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
  overflow: hidden;
`;

const Progress = styled.div`
  height: 100%;
  background: ${props => props.color};
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
`;

const projects = [
  {
    id: 1,
    title: 'Website Redesign',
    status: 'In Progress',
    progress: 65,
    color: '#3b82f6',
    tasks: 12,
    team: 5,
    deadline: '2024-04-15',
  },
  {
    id: 2,
    title: 'Mobile App Development',
    status: 'Planning',
    progress: 20,
    color: '#10b981',
    tasks: 8,
    team: 3,
    deadline: '2024-05-01',
  },
  {
    id: 3,
    title: 'API Integration',
    status: 'Completed',
    progress: 100,
    color: '#8b5cf6',
    tasks: 15,
    team: 4,
    deadline: '2024-03-10',
  },
];

const Projects = () => {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <ProjectsContainer>
      <Header>
        <Title>Projects</Title>
        <ActionButton>
          <FaPlus />
          New Project
        </ActionButton>
      </Header>

      <SearchBar>
        <FaSearch color="#64748b" />
        <SearchInput
          placeholder="Search projects..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <FaFilter color="#64748b" />
      </SearchBar>

      <ProjectsGrid>
        {projects.map((project) => (
          <ProjectCard key={project.id}>
            <ProjectHeader>
              <ProjectTitle>{project.title}</ProjectTitle>
              <ProjectMenu>
                <FaEllipsisV />
              </ProjectMenu>
            </ProjectHeader>

            <ProjectInfo>
              <InfoRow>
                <InfoLabel>Status</InfoLabel>
                <InfoValue>{project.status}</InfoValue>
              </InfoRow>

              <InfoRow>
                <InfoLabel>Progress</InfoLabel>
                <InfoValue>{project.progress}%</InfoValue>
              </InfoRow>

              <ProgressBar>
                <Progress progress={project.progress} color={project.color} />
              </ProgressBar>

              <InfoRow>
                <InfoLabel>Tasks</InfoLabel>
                <InfoValue>{project.tasks} tasks</InfoValue>
              </InfoRow>

              <InfoRow>
                <InfoLabel>Team</InfoLabel>
                <InfoValue>{project.team} members</InfoValue>
              </InfoRow>

              <InfoRow>
                <InfoLabel>Deadline</InfoLabel>
                <InfoValue>{project.deadline}</InfoValue>
              </InfoRow>
            </ProjectInfo>
          </ProjectCard>
        ))}
      </ProjectsGrid>
    </ProjectsContainer>
  );
};

export default Projects; 