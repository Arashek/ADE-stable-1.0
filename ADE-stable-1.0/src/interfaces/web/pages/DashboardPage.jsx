import React from 'react';
import styled from 'styled-components';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { FaProjectDiagram, FaTasks, FaRobot, FaClock } from 'react-icons/fa';

const DashboardContainer = styled.div`
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
`;

const StatsGrid = styled.div`
  display: grid;
  gap: 24px;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  margin-bottom: 24px;
`;

const StatCard = styled(Card)`
  display: flex;
  align-items: center;
  gap: 16px;
`;

const StatIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 12px;
  background-color: ${props => props.color}20;
  color: ${props => props.color};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
`;

const StatInfo = styled.div`
  flex: 1;
`;

const StatValue = styled.div`
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: #6b7280;
`;

const ActivityList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const ActivityItem = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  background-color: #f9fafb;
  transition: background-color 0.2s ease;

  &:hover {
    background-color: #f3f4f6;
  }
`;

const ActivityIcon = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background-color: ${props => props.color}20;
  color: ${props => props.color};
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
`;

const ActivityContent = styled.div`
  flex: 1;
`;

const ActivityTitle = styled.div`
  font-weight: 500;
  color: #1f2937;
`;

const ActivityTime = styled.div`
  font-size: 12px;
  color: #6b7280;
`;

const AgentStatusGrid = styled.div`
  display: grid;
  gap: 16px;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
`;

const AgentCard = styled(Card)`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const AgentHeader = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
`;

const AgentIcon = styled.div`
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

const AgentInfo = styled.div`
  flex: 1;
`;

const AgentName = styled.div`
  font-weight: 500;
  color: #1f2937;
`;

const AgentStatus = styled.div`
  font-size: 12px;
  color: ${props => props.status === 'active' ? '#10b981' : '#6b7280'};
`;

const AgentActions = styled.div`
  display: flex;
  gap: 8px;
`;

// Mock data
const stats = [
  { label: 'Active Projects', value: '12', icon: <FaProjectDiagram />, color: '#4a7bff' },
  { label: 'Tasks in Progress', value: '28', icon: <FaTasks />, color: '#10b981' },
  { label: 'Available Agents', value: '5', icon: <FaRobot />, color: '#f59e0b' },
  { label: 'Recent Activities', value: '18', icon: <FaClock />, color: '#6366f1' },
];

const activities = [
  {
    id: 1,
    title: 'New project created: E-commerce Platform',
    time: '2 hours ago',
    icon: <FaProjectDiagram />,
    color: '#4a7bff',
  },
  {
    id: 2,
    title: 'Task completed: Database Schema Design',
    time: '3 hours ago',
    icon: <FaTasks />,
    color: '#10b981',
  },
  {
    id: 3,
    title: 'Agent deployed: Code Review Bot',
    time: '4 hours ago',
    icon: <FaRobot />,
    color: '#f59e0b',
  },
  {
    id: 4,
    title: 'System update completed',
    time: '5 hours ago',
    icon: <FaClock />,
    color: '#6366f1',
  },
];

const agents = [
  {
    id: 1,
    name: 'Code Review Bot',
    status: 'active',
    description: 'Specialized in code quality and best practices',
  },
  {
    id: 2,
    name: 'Test Generator',
    status: 'active',
    description: 'Automated test case generation and validation',
  },
  {
    id: 3,
    name: 'Documentation Assistant',
    status: 'inactive',
    description: 'Helps maintain project documentation',
  },
];

const DashboardPage = () => {
  return (
    <div>
      <StatsGrid>
        {stats.map((stat, index) => (
          <StatCard key={index}>
            <StatIcon color={stat.color}>{stat.icon}</StatIcon>
            <StatInfo>
              <StatValue>{stat.value}</StatValue>
              <StatLabel>{stat.label}</StatLabel>
            </StatInfo>
          </StatCard>
        ))}
      </StatsGrid>

      <DashboardContainer>
        <Card title="Recent Activities">
          <ActivityList>
            {activities.map(activity => (
              <ActivityItem key={activity.id}>
                <ActivityIcon color={activity.color}>
                  {activity.icon}
                </ActivityIcon>
                <ActivityContent>
                  <ActivityTitle>{activity.title}</ActivityTitle>
                  <ActivityTime>{activity.time}</ActivityTime>
                </ActivityContent>
              </ActivityItem>
            ))}
          </ActivityList>
        </Card>

        <Card title="Available Agents">
          <AgentStatusGrid>
            {agents.map(agent => (
              <AgentCard key={agent.id}>
                <AgentHeader>
                  <AgentIcon>
                    <FaRobot />
                  </AgentIcon>
                  <AgentInfo>
                    <AgentName>{agent.name}</AgentName>
                    <AgentStatus status={agent.status}>
                      {agent.status === 'active' ? 'Active' : 'Inactive'}
                    </AgentStatus>
                  </AgentInfo>
                </AgentHeader>
                <div style={{ color: '#6b7280', fontSize: '14px' }}>
                  {agent.description}
                </div>
                <AgentActions>
                  <Button size="small" variant="secondary">
                    Configure
                  </Button>
                  <Button size="small">
                    {agent.status === 'active' ? 'Deactivate' : 'Activate'}
                  </Button>
                </AgentActions>
              </AgentCard>
            ))}
          </AgentStatusGrid>
        </Card>
      </DashboardContainer>
    </div>
  );
};

export default DashboardPage; 