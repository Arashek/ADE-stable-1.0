import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { FaEllipsisV, FaClock, FaExclamationTriangle } from 'react-icons/fa';

const Card = styled.div`
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  }
`;

const CardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
`;

const CardTitle = styled.h3`
  font-size: 18px;
  color: #1e293b;
  margin: 0;
`;

const CardMenu = styled.button`
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

const CardInfo = styled.div`
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

const StatusBadge = styled.span`
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
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

const DeadlineInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  color: ${props => {
    const daysUntilDeadline = props.daysUntilDeadline;
    if (daysUntilDeadline < 0) return '#ef4444';
    if (daysUntilDeadline <= 7) return '#f59e0b';
    return '#64748b';
  }};
  font-size: 14px;
`;

const TimelineInfo = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  color: #64748b;
  font-size: 14px;
`;

const ProjectCard = ({ project, onMenuClick }) => {
  const calculateDaysUntilDeadline = () => {
    const deadline = new Date(project.deadline);
    const today = new Date();
    const diffTime = deadline - today;
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const daysUntilDeadline = calculateDaysUntilDeadline();
  const isOverdue = daysUntilDeadline < 0;
  const isUrgent = daysUntilDeadline >= 0 && daysUntilDeadline <= 7;

  const getDeadlineText = () => {
    if (isOverdue) return `${Math.abs(daysUntilDeadline)} days overdue`;
    if (isUrgent) return `${daysUntilDeadline} days left`;
    return `Due ${new Date(project.deadline).toLocaleDateString()}`;
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{project.title}</CardTitle>
        <CardMenu onClick={() => onMenuClick?.(project.id)}>
          <FaEllipsisV />
        </CardMenu>
      </CardHeader>

      <CardInfo>
        <InfoRow>
          <InfoLabel>Status</InfoLabel>
          <StatusBadge status={project.status}>{project.status}</StatusBadge>
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
          <InfoLabel>Timeline</InfoLabel>
          <TimelineInfo>
            <FaClock />
            {project.timeline}
          </TimelineInfo>
        </InfoRow>

        <InfoRow>
          <InfoLabel>Deadline</InfoLabel>
          <DeadlineInfo daysUntilDeadline={daysUntilDeadline}>
            {isOverdue && <FaExclamationTriangle />}
            {getDeadlineText()}
          </DeadlineInfo>
        </InfoRow>
      </CardInfo>
    </Card>
  );
};

ProjectCard.propTypes = {
  project: PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    status: PropTypes.string.isRequired,
    progress: PropTypes.number.isRequired,
    color: PropTypes.string.isRequired,
    tasks: PropTypes.number.isRequired,
    team: PropTypes.number.isRequired,
    deadline: PropTypes.string.isRequired,
    timeline: PropTypes.string.isRequired,
  }).isRequired,
  onMenuClick: PropTypes.func,
};

export default ProjectCard; 