import React, { useState } from 'react';
import styled from 'styled-components';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import { FaPlus, FaFilter, FaChartBar, FaEdit } from 'react-icons/fa';

const BoardContainer = styled.div`
  display: flex;
  flex-direction: column;
  height: 100%;
  background: ${props => props.theme.background};
`;

const BoardHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  border-bottom: 1px solid ${props => props.theme.border};
`;

const BoardControls = styled.div`
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

const BoardContent = styled.div`
  display: flex;
  flex: 1;
  gap: 16px;
  padding: 16px;
  overflow-x: auto;
`;

const Column = styled.div`
  flex: 1;
  min-width: 300px;
  background: ${props => props.theme.cardBackground};
  border-radius: 8px;
  display: flex;
  flex-direction: column;
`;

const ColumnHeader = styled.div`
  padding: 12px;
  border-bottom: 1px solid ${props => props.theme.border};
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const ColumnTitle = styled.div`
  font-weight: 600;
  color: ${props => props.theme.text};
`;

const ColumnCount = styled.div`
  background: ${props => props.theme.metaBackground};
  color: ${props => props.theme.metaText};
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 12px;
`;

const TaskList = styled.div`
  flex: 1;
  padding: 12px;
  overflow-y: auto;
`;

const TaskCard = styled.div`
  background: ${props => props.theme.background};
  border-radius: 4px;
  padding: 12px;
  margin-bottom: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: all 0.2s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
  }
`;

const TaskTitle = styled.div`
  font-weight: 500;
  color: ${props => props.theme.text};
  margin-bottom: 4px;
`;

const TaskMeta = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: ${props => props.theme.metaText};
`;

const TaskProgress = styled.div`
  height: 4px;
  background: ${props => props.theme.metaBackground};
  border-radius: 2px;
  margin-top: 8px;
  overflow: hidden;
`;

const ProgressBar = styled.div`
  height: 100%;
  background: ${props => props.theme.primary};
  width: ${props => props.progress}%;
  transition: width 0.3s ease;
`;

const TaskTags = styled.div`
  display: flex;
  gap: 4px;
  margin-top: 8px;
`;

const Tag = styled.div`
  background: ${props => props.theme.metaBackground};
  color: ${props => props.theme.metaText};
  padding: 2px 6px;
  border-radius: 12px;
  font-size: 10px;
`;

const KanbanBoard = () => {
  const [columns, setColumns] = useState({
    'todo': {
      id: 'todo',
      title: 'To Do',
      tasks: [
        {
          id: 'task-1',
          title: 'Implement user authentication',
          assignee: 'John Doe',
          dueDate: '2024-03-15',
          progress: 0,
          tags: ['frontend', 'security']
        },
        {
          id: 'task-2',
          title: 'Design database schema',
          assignee: 'Jane Smith',
          dueDate: '2024-03-10',
          progress: 0,
          tags: ['backend', 'database']
        }
      ]
    },
    'in-progress': {
      id: 'in-progress',
      title: 'In Progress',
      tasks: [
        {
          id: 'task-3',
          title: 'Create API endpoints',
          assignee: 'Mike Johnson',
          dueDate: '2024-03-20',
          progress: 45,
          tags: ['backend', 'api']
        }
      ]
    },
    'review': {
      id: 'review',
      title: 'Review',
      tasks: [
        {
          id: 'task-4',
          title: 'Code review: Frontend components',
          assignee: 'Sarah Wilson',
          dueDate: '2024-03-12',
          progress: 80,
          tags: ['frontend', 'review']
        }
      ]
    },
    'done': {
      id: 'done',
      title: 'Done',
      tasks: [
        {
          id: 'task-5',
          title: 'Project setup and configuration',
          assignee: 'Alex Brown',
          dueDate: '2024-03-05',
          progress: 100,
          tags: ['setup']
        }
      ]
    }
  });

  const onDragEnd = (result) => {
    const { destination, source, draggableId } = result;

    if (!destination) return;

    if (
      destination.droppableId === source.droppableId &&
      destination.index === source.index
    ) {
      return;
    }

    const sourceColumn = columns[source.droppableId];
    const destColumn = columns[destination.droppableId];
    const sourceTasks = [...sourceColumn.tasks];
    const destTasks = source.droppableId === destination.droppableId
      ? sourceTasks
      : [...destColumn.tasks];
    const [removed] = sourceTasks.splice(source.index, 1);
    destTasks.splice(destination.index, 0, removed);

    setColumns({
      ...columns,
      [source.droppableId]: {
        ...sourceColumn,
        tasks: sourceTasks
      },
      [destination.droppableId]: {
        ...destColumn,
        tasks: destTasks
      }
    });
  };

  return (
    <BoardContainer>
      <BoardHeader>
        <BoardControls>
          <ControlButton>
            <FaPlus /> Add Task
          </ControlButton>
          <ControlButton>
            <FaFilter /> Filter
          </ControlButton>
          <ControlButton>
            <FaChartBar /> Analytics
          </ControlButton>
        </BoardControls>
      </BoardHeader>

      <DragDropContext onDragEnd={onDragEnd}>
        <BoardContent>
          {Object.values(columns).map(column => (
            <Column key={column.id}>
              <ColumnHeader>
                <ColumnTitle>{column.title}</ColumnTitle>
                <ColumnCount>{column.tasks.length}</ColumnCount>
              </ColumnHeader>
              <Droppable droppableId={column.id}>
                {(provided) => (
                  <TaskList
                    ref={provided.innerRef}
                    {...provided.droppableProps}
                  >
                    {column.tasks.map((task, index) => (
                      <Draggable
                        key={task.id}
                        draggableId={task.id}
                        index={index}
                      >
                        {(provided) => (
                          <TaskCard
                            ref={provided.innerRef}
                            {...provided.draggableProps}
                            {...provided.dragHandleProps}
                          >
                            <TaskTitle>{task.title}</TaskTitle>
                            <TaskMeta>
                              <span>{task.assignee}</span>
                              <span>{task.dueDate}</span>
                            </TaskMeta>
                            <TaskProgress>
                              <ProgressBar progress={task.progress} />
                            </TaskProgress>
                            <TaskTags>
                              {task.tags.map(tag => (
                                <Tag key={tag}>{tag}</Tag>
                              ))}
                            </TaskTags>
                          </TaskCard>
                        )}
                      </Draggable>
                    ))}
                    {provided.placeholder}
                  </TaskList>
                )}
              </Droppable>
            </Column>
          ))}
        </BoardContent>
      </DragDropContext>
    </BoardContainer>
  );
};

export default KanbanBoard; 