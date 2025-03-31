import React, { useState } from 'react';
import styled from 'styled-components';
import { FaPlus, FaSearch, FaFilter, FaEllipsisV, FaClock } from 'react-icons/fa';

const TasksContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h1`
  font-size: 24px;
  color: #1e293b;
`;

const ActionButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background: #2563eb;
  }
`;

const SearchBar = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  background: white;
  padding: 8px 16px;
  border-radius: 6px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
`;

const SearchInput = styled.input`
  border: none;
  outline: none;
  font-size: 14px;
  width: 100%;
`;

const KanbanBoard = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 20px;
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

const TaskCard = styled.div`
  background: white;
  border-radius: 6px;
  padding: 12px;
  margin-bottom: 12px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  cursor: pointer;
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-2px);
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
`;

const TaskMenu = styled.button`
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

const TaskInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const TaskMeta = styled.div`
  display: flex;
  align-items: center;
  gap: 8px;
  color: #64748b;
  font-size: 12px;
`;

const TaskPriority = styled.span`
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  background: ${props => props.color};
  color: white;
`;

const tasks = {
  todo: [
    {
      id: 1,
      title: 'Design new landing page',
      priority: 'High',
      priorityColor: '#ef4444',
      project: 'Website Redesign',
      dueDate: '2024-03-25',
    },
    {
      id: 2,
      title: 'Update API documentation',
      priority: 'Medium',
      priorityColor: '#f59e0b',
      project: 'API Integration',
      dueDate: '2024-03-28',
    },
  ],
  inProgress: [
    {
      id: 3,
      title: 'Implement user authentication',
      priority: 'High',
      priorityColor: '#ef4444',
      project: 'Mobile App',
      dueDate: '2024-03-30',
    },
    {
      id: 4,
      title: 'Optimize database queries',
      priority: 'Low',
      priorityColor: '#10b981',
      project: 'Performance',
      dueDate: '2024-04-01',
    },
  ],
  done: [
    {
      id: 5,
      title: 'Setup CI/CD pipeline',
      priority: 'High',
      priorityColor: '#ef4444',
      project: 'DevOps',
      dueDate: '2024-03-20',
    },
  ],
};

const Tasks = () => {
  const [searchQuery, setSearchQuery] = useState('');

  return (
    <TasksContainer>
      <Header>
        <Title>Tasks</Title>
        <ActionButton>
          <FaPlus />
          New Task
        </ActionButton>
      </Header>

      <SearchBar>
        <FaSearch color="#64748b" />
        <SearchInput
          placeholder="Search tasks..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
        />
        <FaFilter color="#64748b" />
      </SearchBar>

      <KanbanBoard>
        {Object.entries(tasks).map(([status, statusTasks]) => (
          <Column key={status}>
            <ColumnHeader>
              <ColumnTitle>
                {status.charAt(0).toUpperCase() + status.slice(1)}
              </ColumnTitle>
              <TaskCount>{statusTasks.length}</TaskCount>
            </ColumnHeader>

            {statusTasks.map((task) => (
              <TaskCard key={task.id}>
                <TaskHeader>
                  <TaskTitle>{task.title}</TaskTitle>
                  <TaskMenu>
                    <FaEllipsisV />
                  </TaskMenu>
                </TaskHeader>

                <TaskInfo>
                  <TaskPriority color={task.priorityColor}>
                    {task.priority}
                  </TaskPriority>
                  <TaskMeta>
                    <span>{task.project}</span>
                    <FaClock />
                    <span>{task.dueDate}</span>
                  </TaskMeta>
                </TaskInfo>
              </TaskCard>
            ))}
          </Column>
        ))}
      </KanbanBoard>
    </TasksContainer>
  );
};

export default Tasks; 