import React from 'react';
import styled from 'styled-components';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { FaExclamationTriangle, FaClock } from 'react-icons/fa';
import PropTypes from 'prop-types';

const KanbanContainer = styled.div`
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  overflow-x: auto;
`;

const KanbanHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const KanbanTitle = styled.h2`
  font-size: 18px;
  color: #1e293b;
  margin: 0;
`;

const KanbanBoard = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
`;

const Column = styled.div`
  background: #f8fafc;
  border-radius: 8px;
  padding: 16px;
`;

const ColumnHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
`;

const ColumnTitle = styled.h3`
  font-size: 16px;
  color: #1e293b;
  margin: 0;
`;

const TaskCount = styled.span`
  background: #e2e8f0;
  color: #64748b;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
`;

const TaskList = styled.div`
  min-height: 100px;
`;

const TaskCard = styled.div`
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 8px;
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
  margin-bottom: 8px;
`;

const TaskTitle = styled.h4`
  font-size: 14px;
  color: #1e293b;
  margin: 0;
  flex: 1;
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

const TaskInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 4px;
`;

const InfoRow = styled.div`
  display: flex;
  align-items: center;
  gap: 4px;
  color: #64748b;
  font-size: 12px;
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
  font-size: 12px;
`;

const KanbanView = ({ tasks, onTaskSelect, onStatusUpdate }) => {
  const columns = {
    'To Do': {
      title: 'To Do',
      tasks: tasks.filter(task => task.status === 'To Do')
    },
    'In Progress': {
      title: 'In Progress',
      tasks: tasks.filter(task => task.status === 'In Progress')
    },
    'Review': {
      title: 'Review',
      tasks: tasks.filter(task => task.status === 'Review')
    },
    'Done': {
      title: 'Done',
      tasks: tasks.filter(task => task.status === 'Done')
    }
  };

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

  const onDragEnd = (result) => {
    const { destination, source, draggableId } = result;

    if (!destination) return;

    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const newStatus = destination.droppableId;
    onStatusUpdate(draggableId, newStatus);
  };

  return (
    <KanbanContainer>
      <KanbanHeader>
        <KanbanTitle>Kanban Board</KanbanTitle>
      </KanbanHeader>

      <DragDropContext onDragEnd={onDragEnd}>
        <KanbanBoard>
          {Object.entries(columns).map(([columnId, column]) => (
            <Column key={columnId}>
              <ColumnHeader>
                <ColumnTitle>{column.title}</ColumnTitle>
                <TaskCount>{column.tasks.length}</TaskCount>
              </ColumnHeader>

              <Droppable droppableId={columnId}>
                {(provided) => (
                  <TaskList
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                  >
                    {column.tasks.map((task, index) => {
                      const daysUntilDeadline = calculateDaysUntilDeadline(task.deadline);
                      const isOverdue = daysUntilDeadline < 0;
                      const isUrgent = daysUntilDeadline >= 0 && daysUntilDeadline <= 7;

                      return (
                        <Draggable
                          key={task.id}
                          draggableId={task.id.toString()}
                          index={index}
                        >
                          {(provided) => (
                            <TaskCard
                              ref={provided.innerRef}
                              {...provided.draggableProps}
                              {...provided.dragHandleProps}
                              onClick={() => onTaskSelect(task)}
                            >
                              <TaskHeader>
                                <TaskTitle>{task.title}</TaskTitle>
                                <PriorityBadge priority={task.priority}>
                                  {task.priority}
                                </PriorityBadge>
                              </TaskHeader>

                              <TaskInfo>
                                <InfoRow>
                                  <FaClock />
                                  <span>Due: {new Date(task.deadline).toLocaleDateString()}</span>
                                </InfoRow>
                                <DeadlineInfo daysUntilDeadline={daysUntilDeadline}>
                                  {isOverdue && <FaExclamationTriangle />}
                                  {getDeadlineText(daysUntilDeadline, task.deadline)}
                                </DeadlineInfo>
                              </TaskInfo>

                              <ProgressBar>
                                <Progress progress={task.progress} color={task.color} />
                              </ProgressBar>
                            </TaskCard>
                          )}
                        </Draggable>
                      );
                    })}
                    {provided.placeholder}
                  </TaskList>
                )}
              </Droppable>
            </Column>
          ))}
        </KanbanBoard>
      </DragDropContext>
    </KanbanContainer>
  );
};

KanbanView.propTypes = {
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

export default KanbanView; 