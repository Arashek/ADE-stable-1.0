import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaExclamationTriangle, FaClock } from 'react-icons/fa';
import PropTypes from 'prop-types';

const TimelineContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
`;

const TimelineHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const TimelineTitle = styled.h2`
  font-size: 18px;
  color: #1e293b;
  margin: 0;
`;

const TimelineControls = styled.div`
  display: flex;
  gap: 16px;
`;

const ControlButton = styled.button`
  padding: 6px 12px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: white;
  color: #64748b;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #f8fafc;
    border-color: #cbd5e1;
  }
`;

const TimelineGrid = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 24px;
`;

const TimelineItem = styled.div`
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    border-color: #3b82f6;
    box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
  }
`;

const TaskHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 12px;
`;

const TaskTitle = styled.h3`
  font-size: 16px;
  color: #1e293b;
  margin: 0;
  flex: 1;
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

const TaskInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const InfoRow = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 14px;
`;

const ProgressBar = styled.div`
  height: 4px;
  background: #e2e8f0;
  border-radius: 2px;
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

const TimelineView = ({ tasks, onTaskSelect, onStatusUpdate }) => {
  const [timeRange, setTimeRange] = useState('week');
  const [currentDate, setCurrentDate] = useState(new Date());

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

  const filteredTasks = tasks.filter(task => {
    const taskDate = new Date(task.startDate);
    const today = new Date();
    const diffTime = taskDate - today;
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));

    switch (timeRange) {
      case 'week':
        return diffDays >= 0 && diffDays <= 7;
      case 'month':
        return diffDays >= 0 && diffDays <= 30;
      case 'quarter':
        return diffDays >= 0 && diffDays <= 90;
      default:
        return true;
    }
  });

  return (
    <TimelineContainer>
      <TimelineHeader>
        <TimelineTitle>Timeline View</TimelineTitle>
        <TimelineControls>
          <ControlButton onClick={() => setTimeRange('week')}>
            Week
          </ControlButton>
          <ControlButton onClick={() => setTimeRange('month')}>
            Month
          </ControlButton>
          <ControlButton onClick={() => setTimeRange('quarter')}>
            Quarter
          </ControlButton>
        </TimelineControls>
      </TimelineHeader>

      <TimelineGrid>
        {filteredTasks.map(task => {
          const daysUntilDeadline = calculateDaysUntilDeadline(task.deadline);
          const isOverdue = daysUntilDeadline < 0;
          const isUrgent = daysUntilDeadline >= 0 && daysUntilDeadline <= 7;

          return (
            <TimelineItem key={task.id} onClick={() => onTaskSelect(task)}>
              <TaskHeader>
                <TaskTitle>{task.title}</TaskTitle>
                <StatusBadge status={task.status}>{task.status}</StatusBadge>
              </TaskHeader>

              <TaskInfo>
                <InfoRow>
                  <FaClock />
                  <span>Start: {new Date(task.startDate).toLocaleDateString()}</span>
                </InfoRow>
                <InfoRow>
                  <FaClock />
                  <span>End: {new Date(task.endDate).toLocaleDateString()}</span>
                </InfoRow>
                <DeadlineInfo daysUntilDeadline={daysUntilDeadline}>
                  {isOverdue && <FaExclamationTriangle />}
                  {getDeadlineText(daysUntilDeadline, task.deadline)}
                </DeadlineInfo>
              </TaskInfo>

              <ProgressBar>
                <Progress progress={task.progress} color={task.color} />
              </ProgressBar>
            </TimelineItem>
          );
        })}
      </TimelineGrid>
    </TimelineContainer>
  );
};

TimelineView.propTypes = {
  tasks: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      title: PropTypes.string.isRequired,
      status: PropTypes.string.isRequired,
      progress: PropTypes.number.isRequired,
      color: PropTypes.string.isRequired,
      startDate: PropTypes.string.isRequired,
      endDate: PropTypes.string.isRequired,
      deadline: PropTypes.string.isRequired,
    })
  ).isRequired,
  onTaskSelect: PropTypes.func.isRequired,
  onStatusUpdate: PropTypes.func.isRequired,
};

export default TimelineView; 