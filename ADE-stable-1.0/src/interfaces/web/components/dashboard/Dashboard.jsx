import React from 'react';
import styled from 'styled-components';
import { FaProjectDiagram, FaTasks, FaRobot, FaChartLine } from 'react-icons/fa';

const DashboardContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const StatsGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
`;

const StatCard = styled.div`
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  gap: 16px;
`;

const StatIcon = styled.div`
  width: 48px;
  height: 48px;
  border-radius: 8px;
  background: ${props => props.color};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 24px;
`;

const StatInfo = styled.div`
  flex: 1;
`;

const StatLabel = styled.div`
  font-size: 14px;
  color: #64748b;
  margin-bottom: 4px;
`;

const StatValue = styled.div`
  font-size: 24px;
  font-weight: bold;
  color: #1e293b;
`;

const ActivitySection = styled.div`
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const SectionTitle = styled.h2`
  font-size: 18px;
  color: #1e293b;
  margin-bottom: 16px;
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
  background: #f8fafc;
`;

const ActivityIcon = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background: ${props => props.color};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
`;

const ActivityContent = styled.div`
  flex: 1;
`;

const ActivityTitle = styled.div`
  font-weight: 500;
  color: #1e293b;
`;

const ActivityTime = styled.div`
  font-size: 12px;
  color: #64748b;
`;

const stats = [
  { label: 'Active Projects', value: '12', icon: FaProjectDiagram, color: '#3b82f6' },
  { label: 'Pending Tasks', value: '28', icon: FaTasks, color: '#10b981' },
  { label: 'Active Agents', value: '5', icon: FaRobot, color: '#8b5cf6' },
  { label: 'System Health', value: '98%', icon: FaChartLine, color: '#f59e0b' },
];

const activities = [
  {
    title: 'New project created: "Website Redesign"',
    time: '2 minutes ago',
    icon: FaProjectDiagram,
    color: '#3b82f6',
  },
  {
    title: 'Task completed: "Update dependencies"',
    time: '15 minutes ago',
    icon: FaTasks,
    color: '#10b981',
  },
  {
    title: 'Agent "CodeReviewer" started working',
    time: '1 hour ago',
    icon: FaRobot,
    color: '#8b5cf6',
  },
];

const Dashboard = () => {
  return (
    <DashboardContainer>
      <StatsGrid>
        {stats.map((stat, index) => (
          <StatCard key={index}>
            <StatIcon color={stat.color}>
              <stat.icon />
            </StatIcon>
            <StatInfo>
              <StatLabel>{stat.label}</StatLabel>
              <StatValue>{stat.value}</StatValue>
            </StatInfo>
          </StatCard>
        ))}
      </StatsGrid>

      <ActivitySection>
        <SectionTitle>Recent Activity</SectionTitle>
        <ActivityList>
          {activities.map((activity, index) => (
            <ActivityItem key={index}>
              <ActivityIcon color={activity.color}>
                <activity.icon />
              </ActivityIcon>
              <ActivityContent>
                <ActivityTitle>{activity.title}</ActivityTitle>
                <ActivityTime>{activity.time}</ActivityTime>
              </ActivityContent>
            </ActivityItem>
          ))}
        </ActivityList>
      </ActivitySection>
    </DashboardContainer>
  );
};

export default Dashboard; 