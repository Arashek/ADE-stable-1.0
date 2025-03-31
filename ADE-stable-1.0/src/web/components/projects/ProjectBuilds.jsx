import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaCogs, FaPlay, FaStop, FaTrash, FaCheckCircle, FaTimesCircle, FaSpinner } from 'react-icons/fa';
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

const BuildList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const BuildCard = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
`;

const BuildHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
`;

const BuildInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const BuildNumber = styled.h3`
  margin: 0;
  color: #333;
  font-size: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const BuildMeta = styled.div`
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

const BuildStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  background: ${props => {
    switch (props.status) {
      case 'success': return '#d4edda';
      case 'failed': return '#f8d7da';
      case 'running': return '#cce5ff';
      default: return '#e2e3e5';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case 'success': return '#155724';
      case 'failed': return '#721c24';
      case 'running': return '#004085';
      default: return '#383d41';
    }
  }};
`;

const BuildActions = styled.div`
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

const BuildLogs = styled.pre`
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin: 15px 0;
  font-family: monospace;
  font-size: 12px;
  white-space: pre-wrap;
  max-height: 200px;
  overflow-y: auto;
`;

const BuildMetrics = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 15px;
  margin-top: 15px;
`;

const MetricCard = styled.div`
  background: #f8f9fa;
  padding: 10px;
  border-radius: 4px;
  text-align: center;
`;

const MetricValue = styled.div`
  font-size: 18px;
  font-weight: bold;
  color: #333;
`;

const MetricLabel = styled.div`
  font-size: 12px;
  color: #666;
`;

const Alert = styled.div`
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 20px;
  background: ${props => props.type === 'success' ? '#d4edda' : '#f8d7da'};
  color: ${props => props.type === 'success' ? '#155724' : '#721c24'};
  border: 1px solid ${props => props.type === 'success' ? '#c3e6cb' : '#f5c6cb'};
`;

const ProjectBuilds = ({ projectId }) => {
  const [builds, setBuilds] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(false);
  
  useEffect(() => {
    fetchBuilds();
    // Set up polling for running builds
    const interval = setInterval(() => {
      const hasRunningBuilds = builds.some(build => build.status === 'running');
      if (hasRunningBuilds) {
        fetchBuilds();
      }
    }, 5000);
    
    return () => clearInterval(interval);
  }, [projectId]);
  
  const fetchBuilds = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/builds`);
      setBuilds(response.data);
    } catch (err) {
      setError('Failed to fetch builds');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleStartBuild = async () => {
    try {
      await axios.post(`/api/projects/${projectId}/builds/start`);
      setSuccess(true);
      fetchBuilds();
    } catch (err) {
      setError('Failed to start build');
      console.error(err);
    }
  };
  
  const handleStopBuild = async (buildId) => {
    try {
      await axios.post(`/api/projects/${projectId}/builds/${buildId}/stop`);
      setSuccess(true);
      fetchBuilds();
    } catch (err) {
      setError('Failed to stop build');
      console.error(err);
    }
  };
  
  const handleDeleteBuild = async (buildId) => {
    if (!window.confirm('Are you sure you want to delete this build?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}/builds/${buildId}`);
      setSuccess(true);
      fetchBuilds();
    } catch (err) {
      setError('Failed to delete build');
      console.error(err);
    }
  };
  
  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <FaCheckCircle />;
      case 'failed':
        return <FaTimesCircle />;
      case 'running':
        return <FaSpinner className="fa-spin" />;
      default:
        return null;
    }
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>
          <FaCogs />
          Project Builds
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
      
      <Button onClick={handleStartBuild} style={{ marginBottom: '20px' }}>
        <FaPlay />
        Start New Build
      </Button>
      
      <BuildList>
        {builds.map(build => (
          <BuildCard key={build.id}>
            <BuildHeader>
              <BuildInfo>
                <BuildNumber>
                  Build #{build.number}
                  <BuildStatus status={build.status}>
                    {getStatusIcon(build.status)}
                    {build.status}
                  </BuildStatus>
                </BuildNumber>
                <BuildMeta>
                  <MetaItem>
                    Branch: {build.branch}
                  </MetaItem>
                  <MetaItem>
                    Commit: {build.commit.slice(0, 7)}
                  </MetaItem>
                  <MetaItem>
                    Started: {new Date(build.startedAt).toLocaleString()}
                  </MetaItem>
                </BuildMeta>
              </BuildInfo>
              <BuildActions>
                {build.status === 'running' && (
                  <Button onClick={() => handleStopBuild(build.id)}>
                    <FaStop />
                    Stop
                  </Button>
                )}
                <Button
                  variant="danger"
                  onClick={() => handleDeleteBuild(build.id)}
                >
                  <FaTrash />
                  Delete
                </Button>
              </BuildActions>
            </BuildHeader>
            
            {build.logs && (
              <BuildLogs>
                {build.logs}
              </BuildLogs>
            )}
            
            <BuildMetrics>
              <MetricCard>
                <MetricValue>{build.duration}s</MetricValue>
                <MetricLabel>Duration</MetricLabel>
              </MetricCard>
              <MetricCard>
                <MetricValue>{build.steps}</MetricValue>
                <MetricLabel>Steps</MetricLabel>
              </MetricCard>
              <MetricCard>
                <MetricValue>{build.artifacts}</MetricValue>
                <MetricLabel>Artifacts</MetricLabel>
              </MetricCard>
              <MetricCard>
                <MetricValue>{build.size}</MetricValue>
                <MetricLabel>Size</MetricLabel>
              </MetricCard>
            </BuildMetrics>
          </BuildCard>
        ))}
      </BuildList>
    </Container>
  );
};

export default ProjectBuilds; 