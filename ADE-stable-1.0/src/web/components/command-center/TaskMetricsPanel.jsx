import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaClock, FaUser, FaChartBar, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';

const PanelContainer = styled.div`
  background: ${props => props.theme.cardBackground};
  border-radius: 8px;
  padding: 20px;
  height: 100%;
  display: flex;
  flex-direction: column;
  gap: 20px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
`;

const Title = styled.h3`
  color: ${props => props.theme.text};
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TaskSelector = styled.select`
  padding: 8px 12px;
  border-radius: 4px;
  background: ${props => props.theme.inputBackground};
  color: ${props => props.theme.text};
  border: 1px solid ${props => props.theme.border};
  cursor: pointer;
`;

const MetricsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
  margin-bottom: 20px;
`;

const MetricCard = styled.div`
  background: ${props => props.theme.background};
  padding: 12px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const MetricTitle = styled.div`
  color: ${props => props.theme.metaText};
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const MetricValue = styled.div`
  color: ${props => props.theme.text};
  font-size: 18px;
  font-weight: 600;
`;

const ProgressSection = styled.div`
  background: ${props => props.theme.background};
  padding: 16px;
  border-radius: 6px;
`;

const ProgressBar = styled.div`
  height: 8px;
  background: ${props => props.theme.metaBackground};
  border-radius: 4px;
  overflow: hidden;
  margin-top: 8px;
`;

const ProgressFill = styled.div`
  height: 100%;
  background: ${props => props.theme.primary};
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
`;

const TimelineSection = styled.div`
  background: ${props => props.theme.background};
  padding: 16px;
  border-radius: 6px;
`;

const TimelineItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 0;
  border-bottom: 1px solid ${props => props.theme.border};

  &:last-child {
    border-bottom: none;
  }
`;

const TimelineLabel = styled.div`
  color: ${props => props.theme.metaText};
  font-size: 12px;
`;

const TimelineValue = styled.div`
  color: ${props => props.theme.text};
  font-size: 14px;
`;

const DependenciesSection = styled.div`
  background: ${props => props.theme.background};
  padding: 16px;
  border-radius: 6px;
`;

const DependencyList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
`;

const DependencyItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: ${props => props.theme.cardBackground};
  border-radius: 4px;
`;

const StatusIndicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => {
    switch (props.status) {
      case 'completed': return props.theme.success;
      case 'in_progress': return props.theme.warning;
      case 'blocked': return props.theme.error;
      default: return props.theme.metaText;
    }
  }};
`;

const ResourceSection = styled.div`
  background: ${props => props.theme.background};
  padding: 16px;
  border-radius: 6px;
`;

const ResourceList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
`;

const ResourceItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: ${props => props.theme.cardBackground};
  border-radius: 4px;
`;

const TaskMetricsPanel = () => {
  const [selectedTask, setSelectedTask] = useState('task-1');
  const [taskMetrics, setTaskMetrics] = useState({
    progress: 65,
    estimatedHours: 40,
    actualHours: 26,
    startDate: '2024-03-01',
    endDate: '2024-03-15',
    status: 'in_progress',
    assignee: 'John Doe',
    dependencies: [
      { id: 'task-2', title: 'Database Setup', status: 'completed' },
      { id: 'task-3', title: 'API Integration', status: 'in_progress' }
    ],
    resources: [
      { name: 'John Doe', role: 'Developer', hours: 26 },
      { name: 'Jane Smith', role: 'Designer', hours: 10 }
    ]
  });

  const calculateTimeMetrics = () => {
    const start = new Date(taskMetrics.startDate);
    const end = new Date(taskMetrics.endDate);
    const now = new Date();

    const totalDuration = end - start;
    const elapsedTime = now - start;
    const remainingTime = end - now;

    return {
      total: Math.ceil(totalDuration / (1000 * 60 * 60 * 24)),
      elapsed: Math.ceil(elapsedTime / (1000 * 60 * 60 * 24)),
      remaining: Math.ceil(remainingTime / (1000 * 60 * 60 * 24))
    };
  };

  const timeMetrics = calculateTimeMetrics();

  return (
    <PanelContainer>
      <Header>
        <Title>
          <FaChartBar />
          Task Metrics
        </Title>
        <TaskSelector
          value={selectedTask}
          onChange={(e) => setSelectedTask(e.target.value)}
        >
          <option value="task-1">Frontend Development</option>
          <option value="task-2">Database Setup</option>
          <option value="task-3">API Integration</option>
        </TaskSelector>
      </Header>

      <MetricsGrid>
        <MetricCard>
          <MetricTitle>
            <FaClock />
            Progress
          </MetricTitle>
          <MetricValue>{taskMetrics.progress}%</MetricValue>
        </MetricCard>
        <MetricCard>
          <MetricTitle>
            <FaUser />
            Assignee
          </MetricTitle>
          <MetricValue>{taskMetrics.assignee}</MetricValue>
        </MetricCard>
        <MetricCard>
          <MetricTitle>
            <FaClock />
            Hours
          </MetricTitle>
          <MetricValue>{taskMetrics.actualHours}/{taskMetrics.estimatedHours}</MetricValue>
        </MetricCard>
        <MetricCard>
          <MetricTitle>
            <FaExclamationTriangle />
            Status
          </MetricTitle>
          <MetricValue style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <StatusIndicator status={taskMetrics.status} />
            {taskMetrics.status.replace('_', ' ')}
          </MetricValue>
        </MetricCard>
      </MetricsGrid>

      <ProgressSection>
        <MetricTitle>Progress Overview</MetricTitle>
        <ProgressBar>
          <ProgressFill progress={taskMetrics.progress} />
        </ProgressBar>
      </ProgressSection>

      <TimelineSection>
        <MetricTitle>Timeline</MetricTitle>
        <TimelineItem>
          <TimelineLabel>Start Date</TimelineLabel>
          <TimelineValue>{taskMetrics.startDate}</TimelineValue>
        </TimelineItem>
        <TimelineItem>
          <TimelineLabel>End Date</TimelineLabel>
          <TimelineValue>{taskMetrics.endDate}</TimelineValue>
        </TimelineItem>
        <TimelineItem>
          <TimelineLabel>Total Duration</TimelineLabel>
          <TimelineValue>{timeMetrics.total} days</TimelineValue>
        </TimelineItem>
        <TimelineItem>
          <TimelineLabel>Elapsed Time</TimelineLabel>
          <TimelineValue>{timeMetrics.elapsed} days</TimelineValue>
        </TimelineItem>
        <TimelineItem>
          <TimelineLabel>Remaining Time</TimelineLabel>
          <TimelineValue>{timeMetrics.remaining} days</TimelineValue>
        </TimelineItem>
      </TimelineSection>

      <DependenciesSection>
        <MetricTitle>Dependencies</MetricTitle>
        <DependencyList>
          {taskMetrics.dependencies.map(dep => (
            <DependencyItem key={dep.id}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <StatusIndicator status={dep.status} />
                {dep.title}
              </div>
              <div style={{ color: dep.status === 'completed' ? '#4CAF50' : 
                          dep.status === 'in_progress' ? '#FFC107' : '#F44336' }}>
                {dep.status.replace('_', ' ')}
              </div>
            </DependencyItem>
          ))}
        </DependencyList>
      </DependenciesSection>

      <ResourceSection>
        <MetricTitle>Resource Allocation</MetricTitle>
        <ResourceList>
          {taskMetrics.resources.map(resource => (
            <ResourceItem key={resource.name}>
              <div>
                <div style={{ fontWeight: 500 }}>{resource.name}</div>
                <div style={{ fontSize: '12px', color: '#666' }}>{resource.role}</div>
              </div>
              <div>{resource.hours} hours</div>
            </ResourceItem>
          ))}
        </ResourceList>
      </ResourceSection>
    </PanelContainer>
  );
};

export default TaskMetricsPanel; 