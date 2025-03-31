import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { FaArrowLeft, FaEdit, FaTrash, FaUsers, FaTasks, FaCalendar, FaExclamationTriangle } from 'react-icons/fa';
import { projectService } from '../../services/projectService';

const PageContainer = styled.div`
  padding: 24px;
  max-width: 1200px;
  margin: 0 auto;
`;

const BackButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: none;
  color: #64748b;
  font-size: 14px;
  cursor: pointer;
  padding: 8px 0;
  margin-bottom: 24px;

  &:hover {
    color: #1e293b;
  }
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
`;

const Title = styled.h1`
  font-size: 24px;
  color: #1e293b;
  margin: 0;
`;

const ActionButtons = styled.div`
  display: flex;
  gap: 12px;
`;

const Button = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;

  ${props => props.variant === 'primary' ? `
    background: #3b82f6;
    color: white;
    border: none;

    &:hover {
      background: #2563eb;
    }
  ` : props.variant === 'danger' ? `
    background: #fee2e2;
    color: #dc2626;
    border: none;

    &:hover {
      background: #fecaca;
    }
  ` : `
    background: white;
    color: #64748b;
    border: 1px solid #e2e8f0;

    &:hover {
      background: #f8fafc;
      border-color: #cbd5e1;
    }
  `}
`;

const Content = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;
`;

const MainContent = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const Sidebar = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const Card = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const Section = styled.div`
  margin-bottom: 24px;

  &:last-child {
    margin-bottom: 0;
  }
`;

const SectionTitle = styled.h2`
  font-size: 18px;
  color: #1e293b;
  margin: 0 0 16px 0;
`;

const Text = styled.p`
  color: #64748b;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
`;

const ProgressBar = styled.div`
  height: 8px;
  background: #e2e8f0;
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 8px;
`;

const Progress = styled.div`
  height: 100%;
  background: ${props => props.color};
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
`;

const ProgressText = styled.div`
  display: flex;
  justify-content: space-between;
  color: #64748b;
  font-size: 14px;
`;

const StatusBadge = styled.span`
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 500;
  background: ${props => {
    switch (props.status) {
      case 'In Progress':
        return '#dbeafe';
      case 'Completed':
        return '#dcfce7';
      case 'Planning':
        return '#fef3c7';
      default:
        return '#f3f4f6';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case 'In Progress':
        return '#1e40af';
      case 'Completed':
        return '#166534';
      case 'Planning':
        return '#92400e';
      default:
        return '#374151';
    }
  }};
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
`;

const InfoItem = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const InfoLabel = styled.span`
  color: #64748b;
  font-size: 14px;
`;

const InfoValue = styled.span`
  color: #1e293b;
  font-size: 16px;
  font-weight: 500;
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
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

const ProjectDetailsPage = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProject = async () => {
      try {
        setLoading(true);
        setError(null);
        const data = await projectService.getProjectById(id);
        setProject(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchProject();
  }, [id]);

  const handleStatusUpdate = async (newStatus) => {
    try {
      const updatedProject = await projectService.updateProjectStatus(id, newStatus);
      setProject(updatedProject);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleProgressUpdate = async (newProgress) => {
    try {
      const updatedProject = await projectService.updateProjectProgress(id, newProgress);
      setProject(updatedProject);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <PageContainer>
        <LoadingSpinner>Loading project details...</LoadingSpinner>
      </PageContainer>
    );
  }

  if (error) {
    return (
      <PageContainer>
        <ErrorMessage>
          <FaExclamationTriangle />
          {error}
        </ErrorMessage>
      </PageContainer>
    );
  }

  if (!project) {
    return (
      <PageContainer>
        <ErrorMessage>
          <FaExclamationTriangle />
          Project not found
        </ErrorMessage>
      </PageContainer>
    );
  }

  return (
    <PageContainer>
      <BackButton onClick={() => navigate('/projects')}>
        <FaArrowLeft />
        Back to Projects
      </BackButton>

      <Header>
        <Title>{project.title}</Title>
        <StatusBadge status={project.status}>{project.status}</StatusBadge>
      </Header>

      <Content>
        <MainContent>
          <Section>
            <SectionTitle>Description</SectionTitle>
            <Text>{project.description}</Text>
          </Section>

          <Section>
            <SectionTitle>Project Goals</SectionTitle>
            <Text style={{ whiteSpace: 'pre-line' }}>{project.goals}</Text>
          </Section>

          <Section>
            <SectionTitle>Timeline</SectionTitle>
            <InfoGrid>
              <InfoItem>
                <InfoLabel>Start Date</InfoLabel>
                <InfoValue>{new Date(project.startDate).toLocaleDateString()}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>End Date</InfoLabel>
                <InfoValue>{new Date(project.endDate).toLocaleDateString()}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>Duration</InfoLabel>
                <InfoValue>{project.timeline}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>Status</InfoLabel>
                <InfoValue>{project.status}</InfoValue>
              </InfoItem>
            </InfoGrid>
          </Section>
        </MainContent>

        <Sidebar>
          <Card>
            <SectionTitle>Progress</SectionTitle>
            <ProgressBar>
              <Progress progress={project.progress} color={project.color} />
            </ProgressBar>
            <ProgressText>
              <span>Project Progress</span>
              <span>{project.progress}%</span>
            </ProgressText>
          </Card>

          <Card>
            <SectionTitle>Project Details</SectionTitle>
            <InfoGrid>
              <InfoItem>
                <InfoLabel>Team Size</InfoLabel>
                <InfoValue>{project.team} members</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>Tasks</InfoLabel>
                <InfoValue>{project.tasks} tasks</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>Created</InfoLabel>
                <InfoValue>{new Date(project.createdAt).toLocaleDateString()}</InfoValue>
              </InfoItem>
              <InfoItem>
                <InfoLabel>Last Updated</InfoLabel>
                <InfoValue>{new Date(project.updatedAt).toLocaleDateString()}</InfoValue>
              </InfoItem>
            </InfoGrid>
          </Card>
        </Sidebar>
      </Content>
    </PageContainer>
  );
};

export default ProjectDetailsPage; 