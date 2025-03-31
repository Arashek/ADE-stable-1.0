import React, { useState } from 'react';
import styled from 'styled-components';
import { FaUsers, FaChartBar, FaTrophy, FaUserTie, FaClock, FaCheckCircle, FaExclamationCircle } from 'react-icons/fa';

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

const TeamMetrics = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
`;

const MetricCard = styled.div`
  background: ${props => props.theme.background};
  padding: 16px;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  gap: 8px;
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
  font-size: 24px;
  font-weight: 600;
`;

const TeamList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
  overflow-y: auto;
  flex: 1;
`;

const TeamItem = styled.div`
  background: ${props => props.theme.background};
  border-radius: 6px;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const TeamHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const TeamTitle = styled.div`
  font-weight: 500;
  color: ${props => props.theme.text};
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TeamStats = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 12px;
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const StatItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
`;

const MemberList = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 8px;
`;

const MemberItem = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px;
  background: ${props => props.theme.cardBackground};
  border-radius: 4px;
`;

const MemberInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const MemberAvatar = styled.div`
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: ${props => props.theme.primary};
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-weight: 500;
`;

const MemberDetails = styled.div`
  display: flex;
  flex-direction: column;
`;

const MemberName = styled.div`
  font-weight: 500;
  color: ${props => props.theme.text};
`;

const MemberRole = styled.div`
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const MemberMetrics = styled.div`
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const MetricItem = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
`;

const TeamPerformancePanel = () => {
  const [teams] = useState([
    {
      id: 1,
      name: 'Frontend Team',
      members: 5,
      tasksCompleted: 24,
      velocity: 8,
      members: [
        {
          id: 1,
          name: 'John Doe',
          role: 'Senior Developer',
          tasksCompleted: 8,
          hoursLogged: 120,
          performance: 'high'
        },
        {
          id: 2,
          name: 'Jane Smith',
          role: 'UI Developer',
          tasksCompleted: 6,
          hoursLogged: 90,
          performance: 'medium'
        },
        {
          id: 3,
          name: 'Mike Johnson',
          role: 'Frontend Developer',
          tasksCompleted: 10,
          hoursLogged: 150,
          performance: 'high'
        }
      ]
    },
    {
      id: 2,
      name: 'Backend Team',
      members: 4,
      tasksCompleted: 18,
      velocity: 6,
      members: [
        {
          id: 4,
          name: 'Sarah Wilson',
          role: 'Backend Lead',
          tasksCompleted: 7,
          hoursLogged: 100,
          performance: 'high'
        },
        {
          id: 5,
          name: 'Tom Brown',
          role: 'API Developer',
          tasksCompleted: 5,
          hoursLogged: 80,
          performance: 'medium'
        },
        {
          id: 6,
          name: 'Lisa Chen',
          role: 'Database Engineer',
          tasksCompleted: 6,
          hoursLogged: 90,
          performance: 'high'
        }
      ]
    }
  ]);

  const getPerformanceIcon = (performance) => {
    switch (performance) {
      case 'high':
        return <FaTrophy style={{ color: '#4CAF50' }} />;
      case 'medium':
        return <FaChartBar style={{ color: '#FFC107' }} />;
      case 'low':
        return <FaExclamationCircle style={{ color: '#F44336' }} />;
      default:
        return <FaChartBar />;
    }
  };

  return (
    <Container>
      <Header>
        <Title>
          <FaUsers />
          Team Performance
        </Title>
        <Controls>
          <ControlButton>
            <FaChartBar /> Analytics
          </ControlButton>
          <ControlButton>
            <FaUserTie /> Team Details
          </ControlButton>
        </Controls>
      </Header>

      <TeamMetrics>
        <MetricCard>
          <MetricTitle>
            <FaUsers />
            Total Teams
          </MetricTitle>
          <MetricValue>{teams.length}</MetricValue>
        </MetricCard>
        <MetricCard>
          <MetricTitle>
            <FaCheckCircle />
            Tasks Completed
          </MetricTitle>
          <MetricValue>
            {teams.reduce((sum, team) => sum + team.tasksCompleted, 0)}
          </MetricValue>
        </MetricCard>
        <MetricCard>
          <MetricTitle>
            <FaChartBar />
            Average Velocity
          </MetricTitle>
          <MetricValue>
            {Math.round(teams.reduce((sum, team) => sum + team.velocity, 0) / teams.length)}
          </MetricValue>
        </MetricCard>
        <MetricCard>
          <MetricTitle>
            <FaClock />
            Total Hours
          </MetricTitle>
          <MetricValue>
            {teams.reduce((sum, team) => 
              sum + team.members.reduce((memberSum, member) => memberSum + member.hoursLogged, 0), 0
            )}
          </MetricValue>
        </MetricCard>
      </TeamMetrics>

      <TeamList>
        {teams.map(team => (
          <TeamItem key={team.id}>
            <TeamHeader>
              <TeamTitle>
                <FaUsers />
                {team.name}
              </TeamTitle>
              <TeamStats>
                <StatItem>
                  <FaUsers />
                  {team.members.length} members
                </StatItem>
                <StatItem>
                  <FaCheckCircle />
                  {team.tasksCompleted} tasks
                </StatItem>
                <StatItem>
                  <FaChartBar />
                  Velocity: {team.velocity}
                </StatItem>
              </TeamStats>
            </TeamHeader>

            <MemberList>
              {team.members.map(member => (
                <MemberItem key={member.id}>
                  <MemberInfo>
                    <MemberAvatar>
                      {member.name.split(' ').map(n => n[0]).join('')}
                    </MemberAvatar>
                    <MemberDetails>
                      <MemberName>{member.name}</MemberName>
                      <MemberRole>{member.role}</MemberRole>
                    </MemberDetails>
                  </MemberInfo>
                  <MemberMetrics>
                    <MetricItem>
                      <FaCheckCircle />
                      {member.tasksCompleted} tasks
                    </MetricItem>
                    <MetricItem>
                      <FaClock />
                      {member.hoursLogged} hours
                    </MetricItem>
                    <MetricItem>
                      {getPerformanceIcon(member.performance)}
                      {member.performance.charAt(0).toUpperCase() + member.performance.slice(1)}
                    </MetricItem>
                  </MemberMetrics>
                </MemberItem>
              ))}
            </MemberList>
          </TeamItem>
        ))}
      </TeamList>
    </Container>
  );
};

export default TeamPerformancePanel; 