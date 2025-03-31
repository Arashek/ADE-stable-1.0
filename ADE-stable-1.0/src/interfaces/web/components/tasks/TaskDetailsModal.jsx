import React from 'react';
import styled from 'styled-components';
import { FaTimes, FaClock, FaUser, FaExclamationTriangle, FaCheckCircle } from 'react-icons/fa';
import PropTypes from 'prop-types';

const ModalOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  border-radius: 8px;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
  position: relative;
  padding: 24px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
`;

const CloseButton = styled.button`
  position: absolute;
  top: 16px;
  right: 16px;
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: all 0.2s;

  &:hover {
    background: #f1f5f9;
    color: #1e293b;
  }
`;

const ModalHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
`;

const TaskTitle = styled.h2`
  font-size: 24px;
  color: #1e293b;
  margin: 0;
  flex: 1;
  padding-right: 32px;
`;

const StatusBadge = styled.span`
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 14px;
  font-weight: 500;
  background: ${props => {
    switch (props.status) {
      case 'Done':
        return '#dcfce7';
      case 'In Progress':
        return '#dbeafe';
      case 'Review':
        return '#fef3c7';
      default:
        return '#f3f4f6';
    }
  }};
  color: ${props => {
    switch (props.status) {
      case 'Done':
        return '#166534';
      case 'In Progress':
        return '#1e40af';
      case 'Review':
        return '#92400e';
      default:
        return '#374151';
    }
  }};
`;

const Section = styled.div`
  margin-bottom: 24px;
`;

const SectionTitle = styled.h3`
  font-size: 16px;
  color: #64748b;
  margin: 0 0 12px 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
`;

const InfoGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
`;

const InfoItem = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: #1e293b;
  font-size: 14px;
`;

const PriorityBadge = styled.span`
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => {
    switch (props.priority) {
      case 'High':
        return '#fee2e2';
      case 'Medium':
        return '#fef3c7';
      case 'Low':
        return '#dcfce7';
      default:
        return '#f3f4f6';
    }
  }};
  color: ${props => {
    switch (props.priority) {
      case 'High':
        return '#991b1b';
      case 'Medium':
        return '#92400e';
      case 'Low':
        return '#166534';
      default:
        return '#374151';
    }
  }};
`;

const Description = styled.p`
  color: #475569;
  font-size: 14px;
  line-height: 1.6;
  margin: 0;
`;

const ProgressBar = styled.div`
  height: 6px;
  background: #e2e8f0;
  border-radius: 3px;
  overflow: hidden;
  margin-top: 8px;
`;

const Progress = styled.div`
  height: 100%;
  background: ${props => props.color};
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
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

const TaskDetailsModal = ({ task, onClose }) => {
  const calculateDaysUntilDeadline = (deadline) => {
    const deadlineDate = new Date(deadline);
    const today = new Date();
    const diffTime = deadlineDate - today;
    return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
  };

  const getDeadlineText = (daysUntilDeadline, deadline) => {
    if (daysUntilDeadline < 0) return `${Math.abs(daysUntilDeadline)} days overdue`;
    if (daysUntilDeadline <= 7) return `${daysUntilDeadline} days left`;
    return `Due ${new Date(deadline).toLocaleDateString()}`;
  };

  if (!task) return null;

  const daysUntilDeadline = calculateDaysUntilDeadline(task.deadline);
  const isOverdue = daysUntilDeadline < 0;
  const isUrgent = daysUntilDeadline >= 0 && daysUntilDeadline <= 7;

  return (
    <ModalOverlay onClick={onClose}>
      <ModalContent onClick={e => e.stopPropagation()}>
        <CloseButton onClick={onClose}>
          <FaTimes />
        </CloseButton>

        <ModalHeader>
          <TaskTitle>{task.title}</TaskTitle>
          <StatusBadge status={task.status}>{task.status}</StatusBadge>
        </ModalHeader>

        <Section>
          <SectionTitle>Details</SectionTitle>
          <InfoGrid>
            <InfoItem>
              <FaClock />
              <span>Deadline: {new Date(task.deadline).toLocaleDateString()}</span>
            </InfoItem>
            <InfoItem>
              <FaUser />
              <span>Assigned to: {task.assignee || 'Unassigned'}</span>
            </InfoItem>
            <InfoItem>
              <PriorityBadge priority={task.priority}>
                {task.priority} Priority
              </PriorityBadge>
            </InfoItem>
          </InfoGrid>
        </Section>

        <Section>
          <SectionTitle>Description</SectionTitle>
          <Description>{task.description || 'No description provided.'}</Description>
        </Section>

        <Section>
          <SectionTitle>Progress</SectionTitle>
          <ProgressBar>
            <Progress progress={task.progress} color={task.color} />
          </ProgressBar>
          <span style={{ fontSize: '14px', color: '#64748b' }}>
            {task.progress}% Complete
          </span>
        </Section>

        <Section>
          <SectionTitle>Timeline</SectionTitle>
          <DeadlineInfo daysUntilDeadline={daysUntilDeadline}>
            {isOverdue && <FaExclamationTriangle />}
            {isUrgent && !isOverdue && <FaCheckCircle />}
            {getDeadlineText(daysUntilDeadline, task.deadline)}
          </DeadlineInfo>
        </Section>
      </ModalContent>
    </ModalOverlay>
  );
};

TaskDetailsModal.propTypes = {
  task: PropTypes.shape({
    id: PropTypes.number.isRequired,
    title: PropTypes.string.isRequired,
    status: PropTypes.string.isRequired,
    priority: PropTypes.string.isRequired,
    progress: PropTypes.number.isRequired,
    color: PropTypes.string.isRequired,
    deadline: PropTypes.string.isRequired,
    description: PropTypes.string,
    assignee: PropTypes.string,
  }),
  onClose: PropTypes.func.isRequired,
};

export default TaskDetailsModal; 