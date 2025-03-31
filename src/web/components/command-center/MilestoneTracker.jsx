import React, { useState } from 'react';
import styled from 'styled-components';
import { FaFlag, FaCheckCircle, FaExclamationCircle, FaClock, FaChartBar, FaTasks } from 'react-icons/fa';

const Container = styled.div`
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
`;

const Title = styled.h3`
  color: ${props => props.theme.text};
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const Controls = styled.div`
  display: flex;
  gap: 8px;
`;

const ControlButton = styled.button`
  padding: 6px 12px;
  border: none;
  border-radius: 4px;
  background: ${props => props.theme.buttonBackground};
  color: ${props => props.theme.text};
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
  transition: all 0.2s ease;

  &:hover {
    background: ${props => props.theme.buttonHoverBackground};
  }
`;

const MilestoneList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  flex: 1;
`;

const MilestoneItem = styled.div`
  background: ${props => props.theme.background};
  border-radius: 6px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
  position: relative;
  border-left: 4px solid ${props => {
    switch (props.status) {
      case 'completed': return props.theme.success;
      case 'in_progress': return props.theme.warning;
      case 'blocked': return props.theme.error;
      default: return props.theme.metaText;
    }
  }};
`;

const MilestoneHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const MilestoneTitle = styled.div`
  font-weight: 500;
  color: ${props => props.theme.text};
  display: flex;
  align-items: center;
  gap: 8px;
`;

const MilestoneStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: ${props => {
    switch (props.status) {
      case 'completed': return props.theme.success;
      case 'in_progress': return props.theme.warning;
      case 'blocked': return props.theme.error;
      default: return props.theme.metaText;
    }
  }};
`;

const MilestoneProgress = styled.div`
  height: 4px;
  background: ${props => props.theme.metaBackground};
  border-radius: 2px;
  overflow: hidden;
`;

const ProgressBar = styled.div`
  height: 100%;
  background: ${props => props.theme.primary};
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
`;

const MilestoneDetails = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const DetailItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
`;

const TaskList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
`;

const TaskItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: ${props => props.theme.cardBackground};
  border-radius: 4px;
  font-size: 12px;
`;

const TaskStatus = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  color: ${props => {
    switch (props.status) {
      case 'completed': return props.theme.success;
      case 'in_progress': return props.theme.warning;
      case 'blocked': return props.theme.error;
      default: return props.theme.metaText;
    }
  }};
`;

const MilestoneTracker = () => {
  const [milestones] = useState([
    {
      id: 1,
      title: 'Project Setup',
      status: 'completed',
      progress: 100,
      dueDate: '2024-03-01',
      tasks: [
        { id: 1, title: 'Initialize repository', status: 'completed' },
        { id: 2, title: 'Set up development environment', status: 'completed' },
        { id: 3, title: 'Configure CI/CD pipeline', status: 'completed' }
      ]
    },
    {
      id: 2,
      title: 'Core Features Development',
      status: 'in_progress',
      progress: 65,
      dueDate: '2024-03-15',
      tasks: [
        { id: 4, title: 'Implement user authentication', status: 'completed' },
        { id: 5, title: 'Create database schema', status: 'in_progress' },
        { id: 6, title: 'Develop API endpoints', status: 'in_progress' }
      ]
    },
    {
      id: 3,
      title: 'Integration Testing',
      status: 'blocked',
      progress: 0,
      dueDate: '2024-03-20',
      tasks: [
        { id: 7, title: 'Write unit tests', status: 'blocked' },
        { id: 8, title: 'Perform integration tests', status: 'blocked' },
        { id: 9, title: 'Fix identified issues', status: 'blocked' }
      ]
    },
    {
      id: 4,
      title: 'Deployment',
      status: 'pending',
      progress: 0,
      dueDate: '2024-03-25',
      tasks: [
        { id: 10, title: 'Prepare deployment configuration', status: 'pending' },
        { id: 11, title: 'Deploy to staging environment', status: 'pending' },
        { id: 12, title: 'Deploy to production', status: 'pending' }
      ]
    }
  ]);

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <FaCheckCircle />;
      case 'in_progress':
        return <FaClock />;
      case 'blocked':
        return <FaExclamationCircle />;
      default:
        return <FaFlag />;
    }
  };

  return (
    <Container>
      <Header>
        <Title>
          <FaFlag />
          Milestone Tracker
        </Title>
        <Controls>
          <ControlButton>
            <FaFlag /> Add Milestone
          </ControlButton>
          <ControlButton>
            <FaChartBar /> Analytics
          </ControlButton>
        </Controls>
      </Header>

      <MilestoneList>
        {milestones.map(milestone => (
          <MilestoneItem key={milestone.id} status={milestone.status}>
            <MilestoneHeader>
              <MilestoneTitle>
                {getStatusIcon(milestone.status)}
                {milestone.title}
              </MilestoneTitle>
              <MilestoneStatus status={milestone.status}>
                {milestone.status.replace('_', ' ')}
              </MilestoneStatus>
            </MilestoneHeader>

            <MilestoneProgress>
              <ProgressBar progress={milestone.progress} />
            </MilestoneProgress>

            <MilestoneDetails>
              <DetailItem>
                <FaClock />
                Due: {milestone.dueDate}
              </DetailItem>
              <DetailItem>
                <FaChartBar />
                Progress: {milestone.progress}%
              </DetailItem>
              <DetailItem>
                <FaTasks />
                Tasks: {milestone.tasks.length}
              </DetailItem>
            </MilestoneDetails>

            <TaskList>
              {milestone.tasks.map(task => (
                <TaskItem key={task.id}>
                  <div>{task.title}</div>
                  <TaskStatus status={task.status}>
                    {getStatusIcon(task.status)}
                    {task.status.replace('_', ' ')}
                  </TaskStatus>
                </TaskItem>
              ))}
            </TaskList>
          </MilestoneItem>
        ))}
      </MilestoneList>
    </Container>
  );
};

export default MilestoneTracker; 