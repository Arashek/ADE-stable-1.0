import React from 'react';
import styled from 'styled-components';
import { FaExclamationTriangle, FaClock } from 'react-icons/fa';
import PropTypes from 'prop-types';

const ListContainer = styled.div`
  padding: 24px;
`;

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
`;

const TableHeader = styled.thead`
  background: #f8fafc;
  border-bottom: 1px solid #e2e8f0;
`;

const TableRow = styled.tr`
  border-bottom: 1px solid #e2e8f0;
  transition: background 0.2s;

  &:hover {
    background: #f8fafc;
  }
`;

const TableHeaderCell = styled.th`
  padding: 12px 16px;
  text-align: left;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
`;

const TableCell = styled.td`
  padding: 12px 16px;
  font-size: 14px;
  color: #1e293b;
`;

const TaskTitleCell = styled(TableCell)`
  font-weight: 500;
  cursor: pointer;
  color: #3b82f6;

  &:hover {
    text-decoration: underline;
  }
`;

const StatusBadge = styled.span`
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 12px;
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

const ProgressBar = styled.div`
  width: 100px;
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

const ListView = ({ tasks, onTaskSelect, onStatusUpdate }) => {
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

  return (
    <ListContainer>
      <Table>
        <TableHeader>
          <tr>
            <TableHeaderCell>Task</TableHeaderCell>
            <TableHeaderCell>Status</TableHeaderCell>
            <TableHeaderCell>Priority</TableHeaderCell>
            <TableHeaderCell>Progress</TableHeaderCell>
            <TableHeaderCell>Deadline</TableHeaderCell>
          </tr>
        </TableHeader>
        <tbody>
          {tasks.map(task => {
            const daysUntilDeadline = calculateDaysUntilDeadline(task.deadline);
            const isOverdue = daysUntilDeadline < 0;
            const isUrgent = daysUntilDeadline >= 0 && daysUntilDeadline <= 7;

            return (
              <TableRow key={task.id}>
                <TaskTitleCell onClick={() => onTaskSelect(task)}>
                  {task.title}
                </TaskTitleCell>
                <TableCell>
                  <StatusBadge status={task.status}>
                    {task.status}
                  </StatusBadge>
                </TableCell>
                <TableCell>
                  <PriorityBadge priority={task.priority}>
                    {task.priority}
                  </PriorityBadge>
                </TableCell>
                <TableCell>
                  <ProgressBar>
                    <Progress progress={task.progress} color={task.color} />
                  </ProgressBar>
                  <span style={{ fontSize: '12px', color: '#64748b', marginLeft: '8px' }}>
                    {task.progress}%
                  </span>
                </TableCell>
                <TableCell>
                  <DeadlineInfo daysUntilDeadline={daysUntilDeadline}>
                    {isOverdue && <FaExclamationTriangle />}
                    {getDeadlineText(daysUntilDeadline, task.deadline)}
                  </DeadlineInfo>
                </TableCell>
              </TableRow>
            );
          })}
        </tbody>
      </Table>
    </ListContainer>
  );
};

ListView.propTypes = {
  tasks: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      title: PropTypes.string.isRequired,
      status: PropTypes.string.isRequired,
      priority: PropTypes.string.isRequired,
      progress: PropTypes.number.isRequired,
      color: PropTypes.string.isRequired,
      deadline: PropTypes.string.isRequired,
    })
  ).isRequired,
  onTaskSelect: PropTypes.func.isRequired,
  onStatusUpdate: PropTypes.func.isRequired,
};

export default ListView; 