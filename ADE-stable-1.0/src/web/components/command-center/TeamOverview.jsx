import React from 'react';
import styled from 'styled-components';
import { FaUser, FaEnvelope, FaClock, FaTasks } from 'react-icons/fa';
import { colors, spacing, shadows } from '../styles';
import useCommandCenterStore from '../../store/commandCenterStore';

const Container = styled.div`
  background: white;
  border-radius: 8px;
  box-shadow: ${shadows.md};
  padding: ${spacing.md};
  height: 100%;
  display: flex;
  flex-direction: column;
`;

const Header = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: ${spacing.md};
`;

const Title = styled.h3`
  margin: 0;
  font-size: 1.1rem;
  color: ${colors.text};
`;

const TeamList = styled.div`
  flex: 1;
  overflow-y: auto;
`;

const TeamMember = styled.div`
  display: flex;
  align-items: center;
  padding: ${spacing.md};
  background: ${colors.background};
  border-radius: 4px;
  margin-bottom: ${spacing.sm};
  transition: all 0.2s ease;

  &:hover {
    background: ${colors.primary + '10'};
  }
`;

const Avatar = styled.div`
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: ${colors.primary + '20'};
  color: ${colors.primary};
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 500;
  margin-right: ${spacing.md};
`;

const MemberInfo = styled.div`
  flex: 1;
`;

const MemberName = styled.div`
  font-weight: 500;
  color: ${colors.text};
  margin-bottom: 2px;
`;

const MemberRole = styled.div`
  font-size: 0.9rem;
  color: ${colors.textLight};
`;

const MemberStats = styled.div`
  display: flex;
  gap: ${spacing.md};
  margin-top: ${spacing.sm};
`;

const StatItem = styled.div`
  display: flex;
  align-items: center;
  gap: ${spacing.xs};
  font-size: 0.9rem;
  color: ${colors.textLight};
`;

const StatusIndicator = styled.div`
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: ${props => {
    switch (props.status) {
      case 'online':
        return colors.success;
      case 'away':
        return colors.warning;
      case 'offline':
        return colors.textLight;
      default:
        return colors.textLight;
    }
  }};
  margin-left: ${spacing.sm};
`;

const TeamOverview = () => {
  const { team, tasks } = useCommandCenterStore();

  const getMemberTasks = (memberId) => {
    return tasks.filter(task => task.assignedTo === memberId);
  };

  const getMemberActiveTasks = (memberId) => {
    return getMemberTasks(memberId).filter(task => task.status === 'in_progress');
  };

  return (
    <Container>
      <Header>
        <Title>Team Overview</Title>
      </Header>

      <TeamList>
        {team.map(member => {
          const memberTasks = getMemberTasks(member.id);
          const activeTasks = getMemberActiveTasks(member.id);

          return (
            <TeamMember key={member.id}>
              <Avatar>
                {member.name.charAt(0)}
              </Avatar>
              <MemberInfo>
                <MemberName>
                  {member.name}
                  <StatusIndicator status={member.status} />
                </MemberName>
                <MemberRole>{member.role}</MemberRole>
                <MemberStats>
                  <StatItem>
                    <FaTasks />
                    {memberTasks.length} tasks
                  </StatItem>
                  <StatItem>
                    <FaClock />
                    {activeTasks.length} active
                  </StatItem>
                </MemberStats>
              </MemberInfo>
            </TeamMember>
          );
        })}
      </TeamList>
    </Container>
  );
};

export default TeamOverview; 