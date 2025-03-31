import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaPlus, FaSearch, FaExclamationTriangle, FaList, FaCalendarAlt, FaColumns } from 'react-icons/fa';
import { taskService } from '../../services/taskService';
import TimelineView from './TimelineView';
import KanbanView from './KanbanView';
import TaskDetailsModal from './TaskDetailsModal';
import CreateTaskModal from './CreateTaskModal';

const PageContainer = styled.div`
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
`;

const Header = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const Title = styled.h1`
  font-size: 24px;
  color: #1e293b;
  margin: 0;
`;

const SearchBar = styled.div`
  display: flex;
  align-items: center;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  padding: 8px 12px;
  width: 300px;
`;

const SearchInput = styled.input`
  border: none;
  outline: none;
  width: 100%;
  margin-left: 8px;
  font-size: 14px;
`;

const CreateButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: background 0.2s;

  &:hover {
    background: #2563eb;
  }
`;

const ViewToggle = styled.div`
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
`;

const ToggleButton = styled.button`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  background: ${props => props.active ? '#f1f5f9' : 'white'};
  color: ${props => props.active ? '#1e293b' : '#64748b'};
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;

  &:hover {
    background: #f8fafc;
  }
`;

const MainContent = styled.div`
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  min-height: 600px;
`;

const LoadingSpinner = styled.div`
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 200px;
  color: #3b82f6;
  font-size: 16px;
`;

const ErrorMessage = styled.div`
  background: #fee2e2;
  color: #991b1b;
  padding: 16px;
  border-radius: 6px;
  margin: 16px 0;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TasksPage = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [viewMode, setViewMode] = useState('list');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTask, setSelectedTask] = useState(null);
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [filters, setFilters] = useState({
    status: 'all',
    priority: 'all',
    assignee: 'all',
    project: 'all'
  });

  const fetchTasks = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await taskService.getTasks(filters);
      setTasks(data);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [filters]);

  const handleCreateTask = async (taskData) => {
    try {
      const newTask = await taskService.createTask(taskData);
      setTasks(prev => [...prev, newTask]);
      setIsCreateModalOpen(false);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleTaskUpdate = async (taskId, updates) => {
    try {
      const updatedTask = await taskService.updateTask(taskId, updates);
      setTasks(prev => prev.map(task => 
        task.id === taskId ? updatedTask : task
      ));
    } catch (err) {
      setError(err.message);
    }
  };

  const handleTaskDelete = async (taskId) => {
    try {
      await taskService.deleteTask(taskId);
      setTasks(prev => prev.filter(task => task.id !== taskId));
      setSelectedTask(null);
    } catch (err) {
      setError(err.message);
    }
  };

  const handleStatusUpdate = async (taskId, newStatus) => {
    try {
      const updatedTask = await taskService.updateTaskStatus(taskId, newStatus);
      setTasks(prev => prev.map(task => 
        task.id === taskId ? updatedTask : task
      ));
    } catch (err) {
      setError(err.message);
    }
  };

  const filteredTasks = tasks.filter(task =>
    task.title.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const renderView = () => {
    switch (viewMode) {
      case 'timeline':
        return (
          <TimelineView
            tasks={filteredTasks}
            onTaskSelect={setSelectedTask}
            onStatusUpdate={handleStatusUpdate}
          />
        );
      case 'kanban':
        return (
          <KanbanView
            tasks={filteredTasks}
            onTaskSelect={setSelectedTask}
            onStatusUpdate={handleStatusUpdate}
          />
        );
      default:
        return (
          <ListView
            tasks={filteredTasks}
            onTaskSelect={setSelectedTask}
            onStatusUpdate={handleStatusUpdate}
          />
        );
    }
  };

  return (
    <PageContainer>
      <Header>
        <Title>Tasks</Title>
        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
          <SearchBar>
            <FaSearch color="#64748b" />
            <SearchInput
              type="text"
              placeholder="Search tasks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </SearchBar>
          <CreateButton onClick={() => setIsCreateModalOpen(true)}>
            <FaPlus />
            Create Task
          </CreateButton>
        </div>
      </Header>

      <ViewToggle>
        <ToggleButton
          active={viewMode === 'list'}
          onClick={() => setViewMode('list')}
        >
          <FaList />
          List View
        </ToggleButton>
        <ToggleButton
          active={viewMode === 'timeline'}
          onClick={() => setViewMode('timeline')}
        >
          <FaCalendarAlt />
          Timeline View
        </ToggleButton>
        <ToggleButton
          active={viewMode === 'kanban'}
          onClick={() => setViewMode('kanban')}
        >
          <FaColumns />
          Kanban View
        </ToggleButton>
      </ViewToggle>

      {error && (
        <ErrorMessage>
          <FaExclamationTriangle />
          {error}
        </ErrorMessage>
      )}

      <MainContent>
        {loading ? (
          <LoadingSpinner>Loading tasks...</LoadingSpinner>
        ) : (
          renderView()
        )}
      </MainContent>

      {selectedTask && (
        <TaskDetailsModal
          task={selectedTask}
          onClose={() => setSelectedTask(null)}
        />
      )}

      <CreateTaskModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateTask}
      />
    </PageContainer>
  );
};

export default TasksPage; 