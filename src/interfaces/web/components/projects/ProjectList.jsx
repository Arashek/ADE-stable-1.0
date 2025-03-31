import React from 'react';
import PropTypes from 'prop-types';
import styled from 'styled-components';
import { FaEllipsisV, FaClock, FaExclamationTriangle } from 'react-icons/fa';
import CommandCenter from './components/command-center/CommandCenter';
import CommandCenterNav from './components/command-center/CommandCenterNav';
import useCommandCenterStore from './store/commandCenterStore';

const Table = styled.table`
  width: 100%;
  border-collapse: collapse;
  background: white;
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
`;

const TableHeader = styled.thead`
  background: #f8fafc;
`;

const TableBody = styled.tbody`
  tr:nth-child(even) {
    background: #f8fafc;
  }
`;

const TableRow = styled.tr`
  &:hover {
    background: #f1f5f9;
  }
`;

const TableCell = styled.td`
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  color: #1e293b;
  font-size: 14px;
`;

const TableHeaderCell = styled.th`
  padding: 16px;
  text-align: left;
  background: #f8fafc;
  color: #64748b;
  font-weight: 600;
  font-size: 14px;
  border-bottom: 2px solid #e2e8f0;
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

const MenuButton = styled.button`
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

const DeadlineCell = styled.td`
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  color: ${props => {
    const daysUntilDeadline = props.daysUntilDeadline;
    if (daysUntilDeadline < 0) return '#ef4444';
    if (daysUntilDeadline <= 7) return '#f59e0b';
    return '#64748b';
  }};
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const TimelineCell = styled.td`
  padding: 16px;
  text-align: left;
  border-bottom: 1px solid #e2e8f0;
  color: #64748b;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 4px;
`;

const ProjectList = ({ projects, onMenuClick }) => {
  const { activeProject, tasks, updateTask } = useCommandCenterStore();

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
    <Table>
      <TableHeader>
        <TableRow>
          <TableHeaderCell>Project</TableHeaderCell>
          <TableHeaderCell>Status</TableHeaderCell>
          <TableHeaderCell>Progress</TableHeaderCell>
          <TableHeaderCell>Timeline</TableHeaderCell>
          <TableHeaderCell>Tasks</TableHeaderCell>
          <TableHeaderCell>Team</TableHeaderCell>
          <TableHeaderCell>Deadline</TableHeaderCell>
          <TableHeaderCell></TableHeaderCell>
        </TableRow>
      </TableHeader>
      <TableBody>
        {projects.map((project) => {
          const daysUntilDeadline = calculateDaysUntilDeadline(project.deadline);
          const isOverdue = daysUntilDeadline < 0;
          const isUrgent = daysUntilDeadline >= 0 && daysUntilDeadline <= 7;

          return (
            <TableRow key={project.id}>
              <TableCell>{project.title}</TableCell>
              <TableCell>
                <StatusBadge status={project.status}>{project.status}</StatusBadge>
              </TableCell>
              <TableCell>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <ProgressBar>
                    <Progress progress={project.progress} color={project.color} />
                  </ProgressBar>
                  <span>{project.progress}%</span>
                </div>
              </TableCell>
              <TimelineCell>
                <FaClock />
                {project.timeline}
              </TimelineCell>
              <TableCell>{project.tasks} tasks</TableCell>
              <TableCell>{project.team} members</TableCell>
              <DeadlineCell daysUntilDeadline={daysUntilDeadline}>
                {isOverdue && <FaExclamationTriangle />}
                {getDeadlineText(daysUntilDeadline, project.deadline)}
              </DeadlineCell>
              <TableCell>
                <MenuButton onClick={() => onMenuClick?.(project.id)}>
                  <FaEllipsisV />
                </MenuButton>
              </TableCell>
            </TableRow>
          );
        })}
      </TableBody>
    </Table>
  );
};

ProjectList.propTypes = {
  projects: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      title: PropTypes.string.isRequired,
      status: PropTypes.string.isRequired,
      progress: PropTypes.number.isRequired,
      color: PropTypes.string.isRequired,
      tasks: PropTypes.number.isRequired,
      team: PropTypes.number.isRequired,
      deadline: PropTypes.string.isRequired,
      timeline: PropTypes.string.isRequired,
    })
  ).isRequired,
  onMenuClick: PropTypes.func,
};

export default ProjectList; 