import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaCode, FaCog, FaHistory, FaUsers, FaBook } from 'react-icons/fa';
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

const ProjectTitle = styled.h1`
  margin: 0 0 10px 0;
  color: #333;
`;

const ProjectDescription = styled.p`
  margin: 0;
  color: #666;
`;

const ProjectMeta = styled.div`
  display: flex;
  gap: 20px;
  margin-top: 15px;
  color: #888;
  font-size: 14px;
`;

const Tabs = styled.div`
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
`;

const Tab = styled.button`
  padding: 10px 20px;
  background: ${props => props.active ? '#007bff' : 'white'};
  color: ${props => props.active ? 'white' : '#666'};
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
  
  &:hover {
    background: ${props => props.active ? '#0056b3' : '#f5f5f5'};
  }
  
  svg {
    font-size: 16px;
  }
`;

const TabContent = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const Section = styled.div`
  margin-bottom: 30px;
  
  &:last-child {
    margin-bottom: 0;
  }
`;

const SectionTitle = styled.h2`
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
`;

const Grid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
  gap: 20px;
`;

const Card = styled.div`
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #ddd;
`;

const CardTitle = styled.h3`
  margin: 0 0 10px 0;
  color: #333;
  font-size: 16px;
`;

const CardContent = styled.div`
  color: #666;
  font-size: 14px;
`;

const ProjectDetails = ({ projectId }) => {
  const [project, setProject] = useState(null);
  const [activeTab, setActiveTab] = useState('code');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  
  useEffect(() => {
    fetchProjectDetails();
  }, [projectId]);
  
  const fetchProjectDetails = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}`);
      setProject(response.data);
    } catch (err) {
      setError('Failed to fetch project details');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  if (error) {
    return <div>Error: {error}</div>;
  }
  
  if (!project) {
    return <div>Project not found</div>;
  }
  
  return (
    <Container>
      <Header>
        <ProjectTitle>{project.name}</ProjectTitle>
        <ProjectDescription>
          {project.config.description || 'No description'}
        </ProjectDescription>
        <ProjectMeta>
          <span>Created: {new Date(project.metadata.created_at).toLocaleDateString()}</span>
          <span>Status: {project.metadata.status}</span>
          {project.template && <span>Template: {project.template}</span>}
        </ProjectMeta>
      </Header>
      
      <Tabs>
        <Tab
          active={activeTab === 'code'}
          onClick={() => setActiveTab('code')}
        >
          <FaCode />
          Code
        </Tab>
        <Tab
          active={activeTab === 'settings'}
          onClick={() => setActiveTab('settings')}
        >
          <FaCog />
          Settings
        </Tab>
        <Tab
          active={activeTab === 'history'}
          onClick={() => setActiveTab('history')}
        >
          <FaHistory />
          History
        </Tab>
        <Tab
          active={activeTab === 'collaborators'}
          onClick={() => setActiveTab('collaborators')}
        >
          <FaUsers />
          Collaborators
        </Tab>
        <Tab
          active={activeTab === 'docs'}
          onClick={() => setActiveTab('docs')}
        >
          <FaBook />
          Documentation
        </Tab>
      </Tabs>
      
      <TabContent>
        {activeTab === 'code' && (
          <Section>
            <SectionTitle>Repository</SectionTitle>
            {project.repository ? (
              <Card>
                <CardTitle>Repository Details</CardTitle>
                <CardContent>
                  <p>URL: {project.repository.url}</p>
                  <p>Type: {project.repository.type}</p>
                  <p>Branch: {project.repository.branch}</p>
                </CardContent>
              </Card>
            ) : (
              <p>No repository connected</p>
            )}
          </Section>
        )}
        
        {activeTab === 'settings' && (
          <Section>
            <SectionTitle>Project Settings</SectionTitle>
            <Grid>
              <Card>
                <CardTitle>General</CardTitle>
                <CardContent>
                  <p>Name: {project.name}</p>
                  <p>Description: {project.config.description || 'No description'}</p>
                  <p>Status: {project.metadata.status}</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardTitle>Template</CardTitle>
                <CardContent>
                  <p>Template: {project.template || 'None'}</p>
                  <p>Created from template: {project.metadata.template ? 'Yes' : 'No'}</p>
                </CardContent>
              </Card>
            </Grid>
          </Section>
        )}
        
        {activeTab === 'history' && (
          <Section>
            <SectionTitle>Project History</SectionTitle>
            <Card>
              <CardContent>
                <p>Created: {new Date(project.metadata.created_at).toLocaleString()}</p>
                <p>Last updated: {new Date(project.metadata.updated_at).toLocaleString()}</p>
              </CardContent>
            </Card>
          </Section>
        )}
        
        {activeTab === 'collaborators' && (
          <Section>
            <SectionTitle>Project Collaborators</SectionTitle>
            <Card>
              <CardContent>
                <p>Collaborator management coming soon...</p>
              </CardContent>
            </Card>
          </Section>
        )}
        
        {activeTab === 'docs' && (
          <Section>
            <SectionTitle>Project Documentation</SectionTitle>
            <Card>
              <CardContent>
                <p>Documentation coming soon...</p>
              </CardContent>
            </Card>
          </Section>
        )}
      </TabContent>
    </Container>
  );
};

export default ProjectDetails; 