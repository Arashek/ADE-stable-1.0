import React, { useState } from 'react';
import styled from 'styled-components';
import { Routes, Route, useNavigate } from 'react-router-dom';
import { DragDropContext, Droppable, Draggable } from 'react-beautiful-dnd';
import Card from '../components/common/Card';
import Button from '../components/common/Button';
import { FaPlus, FaSearch, FaFilter, FaExclamationCircle, FaClock, FaUser, FaEdit, FaTrash } from 'react-icons/fa';

const TasksContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const TasksHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
`;

const SearchBar = styled.div`
  display: flex;
  align-items: center;
  gap: 12px;
  background-color: white;
  padding: 8px 16px;
  border-radius: 6px;
  border: 1px solid #e5e7eb;
  width: 300px;

  @media (max-width: 768px) {
    width: 100%;
  }
`;

const SearchInput = styled.input`
  border: none;
  outline: none;
  width: 100%;
  font-size: 0.875rem;
  color: #1f2937;

  &::placeholder {
    color: #9ca3af;
  }
`;

const FilterButton = styled(Button)`
  display: flex;
  align-items: center;
  gap: 8px;
`;

const KanbanBoard = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 24px;
  margin-top: 24px;
`;

const KanbanColumn = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const ColumnHeader = styled.div`
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 6px;
`;

const ColumnTitle = styled.div`
  font-weight: 500;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TaskCount = styled.div`
  background-color: #e5e7eb;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.875rem;
  color: #6b7280;
`;

const TaskCard = styled(Card)`
  cursor: pointer;
  transition: transform 0.2s ease;

  &:hover {
    transform: translateY(-2px);
  }
`;

const TaskHeader = styled.div`
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
`;

const TaskTitle = styled.div`
  font-weight: 500;
  color: #1f2937;
  flex: 1;
`;

const TaskMenu = styled.button`
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;

  &:hover {
    background-color: #f3f4f6;
    color: #1f2937;
  }
`;

const TaskInfo = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
`;

const TaskMeta = styled.div`
  display: flex;
  gap: 16px;
  color: #6b7280;
  font-size: 0.875rem;
`;

const TaskPriority = styled.div`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 2px 8px;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  background-color: ${props => {
    switch (props.priority) {
      case 'high': return '#fee2e2';
      case 'medium': return '#fef3c7';
      case 'low': return '#dcfce7';
      default: return '#f3f4f6';
    }
  }};
  color: ${props => {
    switch (props.priority) {
      case 'high': return '#dc2626';
      case 'medium': return '#d97706';
      case 'low': return '#16a34a';
      default: return '#6b7280';
    }
  }};
`;

const TaskActions = styled.div`
  display: flex;
  gap: 8px;
  margin-top: 12px;
`;

const ActionButton = styled.button`
  background: none;
  border: none;
  color: #6b7280;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.875rem;

  &:hover {
    background-color: #f3f4f6;
    color: #1f2937;
  }
`;

const FilterModal = styled.div`
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: white;
  padding: 24px;
  border-radius: 8px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  z-index: 1000;
  width: 90%;
  max-width: 500px;
`;

const FilterOverlay = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 999;
`;

const FilterForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 8px;
`;

const FormLabel = styled.label`
  font-weight: 500;
  color: #1f2937;
`;

const FormInput = styled.input`
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #1f2937;

  &:focus {
    outline: none;
    border-color: #4a7bff;
    box-shadow: 0 0 0 2px rgba(74, 123, 255, 0.1);
  }
`;

const FormSelect = styled.select`
  padding: 8px 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 0.875rem;
  color: #1f2937;
  background-color: white;

  &:focus {
    outline: none;
    border-color: #4a7bff;
    box-shadow: 0 0 0 2px rgba(74, 123, 255, 0.1);
  }
`;

const TaskForm = styled.form`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const TaskDetailsContainer = styled.div`
  display: flex;
  flex-direction: column;
  gap: 24px;
`;

const TaskDetailsHeader = styled.div`
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
`;

const TaskDetailsContent = styled.div`
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: 24px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
`;

const TaskDetailsMain = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const TaskDetailsSidebar = styled.div`
  display: flex;
  flex-direction: column;
  gap: 16px;
`;

const TaskDescription = styled.div`
  color: #4b5563;
  line-height: 1.6;
`;

const TaskComments = styled.div`
  display: flex;
  flex-direction: column;
  gap: 12px;
`;

const Comment = styled.div`
  padding: 12px;
  background-color: #f9fafb;
  border-radius: 6px;
`;

const CommentHeader = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
`;

const CommentAuthor = styled.div`
  font-weight: 500;
  color: #1f2937;
`;

const CommentTime = styled.div`
  font-size: 0.875rem;
  color: #6b7280;
`;

const CommentContent = styled.div`
  color: #4b5563;
  line-height: 1.5;
`;

// Mock data
const tasks = {
  todo: [
    {
      id: 1,
      title: 'Implement user authentication',
      priority: 'high',
      dueDate: '2024-03-20',
      assignee: 'John Doe',
      project: 'E-commerce Platform',
    },
    {
      id: 2,
      title: 'Design database schema',
      priority: 'medium',
      dueDate: '2024-03-22',
      assignee: 'Jane Smith',
      project: 'API Gateway',
    },
  ],
  inProgress: [
    {
      id: 3,
      title: 'Create API endpoints',
      priority: 'high',
      dueDate: '2024-03-19',
      assignee: 'Mike Johnson',
      project: 'API Gateway',
    },
    {
      id: 4,
      title: 'Implement frontend components',
      priority: 'medium',
      dueDate: '2024-03-21',
      assignee: 'Sarah Wilson',
      project: 'Mobile App',
    },
  ],
  done: [
    {
      id: 5,
      title: 'Setup development environment',
      priority: 'low',
      dueDate: '2024-03-18',
      assignee: 'John Doe',
      project: 'E-commerce Platform',
    },
    {
      id: 6,
      title: 'Create project documentation',
      priority: 'medium',
      dueDate: '2024-03-17',
      assignee: 'Jane Smith',
      project: 'Analytics Dashboard',
    },
  ],
};

const TasksList = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState({
    priority: '',
    assignee: '',
    project: '',
    dueDate: '',
  });
  const navigate = useNavigate();

  const handleDragEnd = (result) => {
    if (!result.destination) return;

    const { source, destination } = result;
    const sourceColumn = source.droppableId;
    const destColumn = destination.droppableId;
    const sourceIndex = source.index;
    const destIndex = destination.index;

    // Update task status based on destination column
    const updatedTasks = { ...tasks };
    const [movedTask] = updatedTasks[sourceColumn].splice(sourceIndex, 1);
    movedTask.status = destColumn;
    updatedTasks[destColumn].splice(destIndex, 0, movedTask);

    // In a real app, you would update the backend here
    console.log('Task moved:', movedTask);
  };

  const applyFilters = (task) => {
    if (filters.priority && task.priority !== filters.priority) return false;
    if (filters.assignee && task.assignee !== filters.assignee) return false;
    if (filters.project && task.project !== filters.project) return false;
    if (filters.dueDate && task.dueDate !== filters.dueDate) return false;
    return true;
  };

  const filteredTasks = {
    todo: tasks.todo.filter(task =>
      (task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.project.toLowerCase().includes(searchQuery.toLowerCase())) &&
      applyFilters(task)
    ),
    inProgress: tasks.inProgress.filter(task =>
      (task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.project.toLowerCase().includes(searchQuery.toLowerCase())) &&
      applyFilters(task)
    ),
    done: tasks.done.filter(task =>
      (task.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      task.project.toLowerCase().includes(searchQuery.toLowerCase())) &&
      applyFilters(task)
    ),
  };

  const renderTaskCard = (task, index) => (
    <Draggable key={task.id} draggableId={task.id.toString()} index={index}>
      {(provided) => (
        <TaskCard
          ref={provided.innerRef}
          {...provided.draggableProps}
          {...provided.dragHandleProps}
          onClick={() => navigate(`/tasks/${task.id}`)}
        >
          <TaskHeader>
            <TaskTitle>{task.title}</TaskTitle>
            <TaskMenu>
              <FaExclamationCircle />
            </TaskMenu>
          </TaskHeader>
          <TaskInfo>
            <TaskPriority priority={task.priority}>
              {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
            </TaskPriority>
            <TaskMeta>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <FaClock />
                {task.dueDate}
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                <FaUser />
                {task.assignee}
              </div>
            </TaskMeta>
            <div style={{ color: '#6b7280', fontSize: '0.875rem' }}>
              {task.project}
            </div>
          </TaskInfo>
          <TaskActions>
            <ActionButton onClick={(e) => {
              e.stopPropagation();
              navigate(`/tasks/${task.id}/edit`);
            }}>
              <FaEdit />
              Edit
            </ActionButton>
            <ActionButton onClick={(e) => {
              e.stopPropagation();
              // Handle delete
              console.log('Delete task:', task.id);
            }}>
              <FaTrash />
              Delete
            </ActionButton>
          </TaskActions>
        </TaskCard>
      )}
    </Draggable>
  );

  return (
    <TasksContainer>
      <TasksHeader>
        <SearchBar>
          <FaSearch color="#9ca3af" />
          <SearchInput
            type="text"
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
          />
        </SearchBar>
        <FilterButton variant="secondary" icon={<FaFilter />} onClick={() => setShowFilters(true)}>
          Filter
        </FilterButton>
      </TasksHeader>

      <DragDropContext onDragEnd={handleDragEnd}>
        <KanbanBoard>
          <KanbanColumn>
            <Droppable droppableId="todo">
              {(provided) => (
                <div ref={provided.innerRef} {...provided.droppableProps}>
                  <ColumnHeader>
                    <ColumnTitle>To Do</ColumnTitle>
                    <TaskCount>{filteredTasks.todo.length}</TaskCount>
                  </ColumnHeader>
                  {filteredTasks.todo.map((task, index) => renderTaskCard(task, index))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </KanbanColumn>

          <KanbanColumn>
            <Droppable droppableId="inProgress">
              {(provided) => (
                <div ref={provided.innerRef} {...provided.droppableProps}>
                  <ColumnHeader>
                    <ColumnTitle>In Progress</ColumnTitle>
                    <TaskCount>{filteredTasks.inProgress.length}</TaskCount>
                  </ColumnHeader>
                  {filteredTasks.inProgress.map((task, index) => renderTaskCard(task, index))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </KanbanColumn>

          <KanbanColumn>
            <Droppable droppableId="done">
              {(provided) => (
                <div ref={provided.innerRef} {...provided.droppableProps}>
                  <ColumnHeader>
                    <ColumnTitle>Done</ColumnTitle>
                    <TaskCount>{filteredTasks.done.length}</TaskCount>
                  </ColumnHeader>
                  {filteredTasks.done.map((task, index) => renderTaskCard(task, index))}
                  {provided.placeholder}
                </div>
              )}
            </Droppable>
          </KanbanColumn>
        </KanbanBoard>
      </DragDropContext>

      {showFilters && (
        <>
          <FilterOverlay onClick={() => setShowFilters(false)} />
          <FilterModal>
            <h3 style={{ margin: '0 0 16px 0', fontSize: '1.25rem', fontWeight: 600 }}>
              Filter Tasks
            </h3>
            <FilterForm>
              <FormGroup>
                <FormLabel>Priority</FormLabel>
                <FormSelect
                  value={filters.priority}
                  onChange={(e) => setFilters({ ...filters, priority: e.target.value })}
                >
                  <option value="">All Priorities</option>
                  <option value="high">High</option>
                  <option value="medium">Medium</option>
                  <option value="low">Low</option>
                </FormSelect>
              </FormGroup>

              <FormGroup>
                <FormLabel>Assignee</FormLabel>
                <FormSelect
                  value={filters.assignee}
                  onChange={(e) => setFilters({ ...filters, assignee: e.target.value })}
                >
                  <option value="">All Assignees</option>
                  <option value="John Doe">John Doe</option>
                  <option value="Jane Smith">Jane Smith</option>
                  <option value="Mike Johnson">Mike Johnson</option>
                  <option value="Sarah Wilson">Sarah Wilson</option>
                </FormSelect>
              </FormGroup>

              <FormGroup>
                <FormLabel>Project</FormLabel>
                <FormSelect
                  value={filters.project}
                  onChange={(e) => setFilters({ ...filters, project: e.target.value })}
                >
                  <option value="">All Projects</option>
                  <option value="E-commerce Platform">E-commerce Platform</option>
                  <option value="API Gateway">API Gateway</option>
                  <option value="Mobile App">Mobile App</option>
                  <option value="Analytics Dashboard">Analytics Dashboard</option>
                </FormSelect>
              </FormGroup>

              <FormGroup>
                <FormLabel>Due Date</FormLabel>
                <FormInput
                  type="date"
                  value={filters.dueDate}
                  onChange={(e) => setFilters({ ...filters, dueDate: e.target.value })}
                />
              </FormGroup>

              <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
                <Button variant="secondary" onClick={() => setShowFilters(false)}>
                  Cancel
                </Button>
                <Button onClick={() => {
                  setFilters({ priority: '', assignee: '', project: '', dueDate: '' });
                  setShowFilters(false);
                }}>
                  Clear Filters
                </Button>
              </div>
            </FilterForm>
          </FilterModal>
        </>
      )}
    </TasksContainer>
  );
};

const TaskCreate = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    priority: 'medium',
    dueDate: '',
    assignee: '',
    project: '',
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // In a real app, you would save the task to the backend here
    console.log('Create task:', formData);
    navigate('/tasks');
  };

  return (
    <Card title="Create New Task">
      <TaskForm onSubmit={handleSubmit}>
        <FormGroup>
          <FormLabel>Title</FormLabel>
          <FormInput
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            required
          />
        </FormGroup>

        <FormGroup>
          <FormLabel>Description</FormLabel>
          <FormInput
            as="textarea"
            rows="4"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
        </FormGroup>

        <FormGroup>
          <FormLabel>Priority</FormLabel>
          <FormSelect
            value={formData.priority}
            onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
          >
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </FormSelect>
        </FormGroup>

        <FormGroup>
          <FormLabel>Due Date</FormLabel>
          <FormInput
            type="date"
            value={formData.dueDate}
            onChange={(e) => setFormData({ ...formData, dueDate: e.target.value })}
            required
          />
        </FormGroup>

        <FormGroup>
          <FormLabel>Assignee</FormLabel>
          <FormSelect
            value={formData.assignee}
            onChange={(e) => setFormData({ ...formData, assignee: e.target.value })}
            required
          >
            <option value="">Select Assignee</option>
            <option value="John Doe">John Doe</option>
            <option value="Jane Smith">Jane Smith</option>
            <option value="Mike Johnson">Mike Johnson</option>
            <option value="Sarah Wilson">Sarah Wilson</option>
          </FormSelect>
        </FormGroup>

        <FormGroup>
          <FormLabel>Project</FormLabel>
          <FormSelect
            value={formData.project}
            onChange={(e) => setFormData({ ...formData, project: e.target.value })}
            required
          >
            <option value="">Select Project</option>
            <option value="E-commerce Platform">E-commerce Platform</option>
            <option value="API Gateway">API Gateway</option>
            <option value="Mobile App">Mobile App</option>
            <option value="Analytics Dashboard">Analytics Dashboard</option>
          </FormSelect>
        </FormGroup>

        <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
          <Button variant="secondary" onClick={() => navigate('/tasks')}>
            Cancel
          </Button>
          <Button type="submit">
            Create Task
          </Button>
        </div>
      </TaskForm>
    </Card>
  );
};

const TaskDetails = () => {
  const navigate = useNavigate();
  const taskId = window.location.pathname.split('/').pop();
  const task = [...tasks.todo, ...tasks.inProgress, ...tasks.done].find(t => t.id === parseInt(taskId));

  if (!task) {
    return <div>Task not found</div>;
  }

  return (
    <Card>
      <TaskDetailsContainer>
        <TaskDetailsHeader>
          <div>
            <h2 style={{ margin: '0 0 8px 0', fontSize: '1.5rem', fontWeight: 600 }}>
              {task.title}
            </h2>
            <TaskPriority priority={task.priority}>
              {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
            </TaskPriority>
          </div>
          <div style={{ display: 'flex', gap: '8px' }}>
            <Button variant="secondary" icon={<FaEdit />} onClick={() => navigate(`/tasks/${taskId}/edit`)}>
              Edit
            </Button>
            <Button variant="secondary" icon={<FaTrash />}>
              Delete
            </Button>
          </div>
        </TaskDetailsHeader>

        <TaskDetailsContent>
          <TaskDetailsMain>
            <div>
              <h3 style={{ margin: '0 0 8px 0', fontSize: '1.125rem', fontWeight: 500 }}>
                Description
              </h3>
              <TaskDescription>
                {task.description || 'No description provided.'}
              </TaskDescription>
            </div>

            <div>
              <h3 style={{ margin: '0 0 8px 0', fontSize: '1.125rem', fontWeight: 500 }}>
                Comments
              </h3>
              <TaskComments>
                <Comment>
                  <CommentHeader>
                    <CommentAuthor>John Doe</CommentAuthor>
                    <CommentTime>2 hours ago</CommentTime>
                  </CommentHeader>
                  <CommentContent>
                    Started working on this task. Initial setup is complete.
                  </CommentContent>
                </Comment>
                <Comment>
                  <CommentHeader>
                    <CommentAuthor>Jane Smith</CommentAuthor>
                    <CommentTime>1 day ago</CommentTime>
                  </CommentHeader>
                  <CommentContent>
                    Please make sure to follow the project guidelines.
                  </CommentContent>
                </Comment>
              </TaskComments>
            </div>
          </TaskDetailsMain>

          <TaskDetailsSidebar>
            <Card title="Task Information">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                <div>
                  <div style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '4px' }}>
                    Status
                  </div>
                  <div style={{ fontWeight: 500 }}>
                    {task.status.charAt(0).toUpperCase() + task.status.slice(1)}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '4px' }}>
                    Due Date
                  </div>
                  <div style={{ fontWeight: 500 }}>
                    {task.dueDate}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '4px' }}>
                    Assignee
                  </div>
                  <div style={{ fontWeight: 500 }}>
                    {task.assignee}
                  </div>
                </div>
                <div>
                  <div style={{ color: '#6b7280', fontSize: '0.875rem', marginBottom: '4px' }}>
                    Project
                  </div>
                  <div style={{ fontWeight: 500 }}>
                    {task.project}
                  </div>
                </div>
              </div>
            </Card>
          </TaskDetailsSidebar>
        </TaskDetailsContent>
      </TaskDetailsContainer>
    </Card>
  );
};

const TaskEdit = () => {
  const navigate = useNavigate();
  const taskId = window.location.pathname.split('/').pop();
  const task = [...tasks.todo, ...tasks.inProgress, ...tasks.done].find(t => t.id === parseInt(taskId));

  if (!task) {
    return <div>Task not found</div>;
  }

  const [formData, setFormData] = useState({
    title: task.title,
    description: task.description || '',
    priority: task.priority,
    dueDate: task.dueDate,
    assignee: task.assignee,
    project: task.project,
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    // In a real app, you would update the task in the backend here
    console.log('Update task:', formData);
    navigate(`/tasks/${taskId}`);
  };

  return (
    <Card title="Edit Task">
      <TaskForm onSubmit={handleSubmit}>
        <FormGroup>
          <FormLabel>Title</FormLabel>
          <FormInput
            type="text"
            value={formData.title}
            onChange={(e) => setFormData({ ...formData, title: e.target.value })}
            required
          />
        </FormGroup>

        <FormGroup>
          <FormLabel>Description</FormLabel>
          <FormInput
            as="textarea"
            rows="4"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          />
        </FormGroup>

        <FormGroup>
          <FormLabel>Priority</FormLabel>
          <FormSelect
            value={formData.priority}
            onChange={(e) => setFormData({ ...formData, priority: e.target.value })}
          >
            <option value="high">High</option>
            <option value="medium">Medium</option>
            <option value="low">Low</option>
          </FormSelect>
        </FormGroup>

        <FormGroup>
          <FormLabel>Due Date</FormLabel>
          <FormInput
            type="date"
            value={formData.dueDate}
            onChange={(e) => setFormData({ ...formData, dueDate: e.target.value })}
            required
          />
        </FormGroup>

        <FormGroup>
          <FormLabel>Assignee</FormLabel>
          <FormSelect
            value={formData.assignee}
            onChange={(e) => setFormData({ ...formData, assignee: e.target.value })}
            required
          >
            <option value="">Select Assignee</option>
            <option value="John Doe">John Doe</option>
            <option value="Jane Smith">Jane Smith</option>
            <option value="Mike Johnson">Mike Johnson</option>
            <option value="Sarah Wilson">Sarah Wilson</option>
          </FormSelect>
        </FormGroup>

        <FormGroup>
          <FormLabel>Project</FormLabel>
          <FormSelect
            value={formData.project}
            onChange={(e) => setFormData({ ...formData, project: e.target.value })}
            required
          >
            <option value="">Select Project</option>
            <option value="E-commerce Platform">E-commerce Platform</option>
            <option value="API Gateway">API Gateway</option>
            <option value="Mobile App">Mobile App</option>
            <option value="Analytics Dashboard">Analytics Dashboard</option>
          </FormSelect>
        </FormGroup>

        <div style={{ display: 'flex', gap: '8px', justifyContent: 'flex-end' }}>
          <Button variant="secondary" onClick={() => navigate(`/tasks/${taskId}`)}>
            Cancel
          </Button>
          <Button type="submit">
            Save Changes
          </Button>
        </div>
      </TaskForm>
    </Card>
  );
};

const TasksPage = () => {
  return (
    <div>
      <TasksHeader>
        <h1 style={{ margin: 0, fontSize: '1.5rem', fontWeight: 600 }}>
          Tasks
        </h1>
        <Button icon={<FaPlus />} onClick={() => navigate('/tasks/create')}>
          New Task
        </Button>
      </TasksHeader>

      <Routes>
        <Route path="/" element={<TasksList />} />
        <Route path="/create" element={<TaskCreate />} />
        <Route path="/:id" element={<TaskDetails />} />
        <Route path="/:id/edit" element={<TaskEdit />} />
      </Routes>
    </div>
  );
};

export default TasksPage; 