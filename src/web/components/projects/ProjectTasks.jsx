import React, { useState, useEffect } from 'react';
import styled from 'styled-components';
import { FaTasks, FaPlus, FaEdit, FaTrash, FaSave, FaTimes, FaCheck, FaClock } from 'react-icons/fa';
import axios from 'axios';

const Container = styled.div`
  padding: 20px;
  background: #f5f5f5;
  min-height: 100vh;
`;

const Header = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const Title = styled.h1`
  margin: 0;
  color: #333;
  display: flex;
  align-items: center;
  gap: 10px;
`;

const Button = styled.button`
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  background: #007bff;
  color: white;
  border: none;
  
  &:hover {
    background: #0056b3;
  }
`;

const TaskList = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 20px;
`;

const TaskCard = styled.div`
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  overflow: hidden;
`;

const TaskHeader = styled.div`
  padding: 15px;
  border-bottom: 1px solid #eee;
  display: flex;
  justify-content: space-between;
  align-items: center;
`;

const TaskTitle = styled.h3`
  margin: 0;
  color: #333;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const TaskActions = styled.div`
  display: flex;
  gap: 8px;
`;

const TaskContent = styled.div`
  padding: 15px;
`;

const TaskDescription = styled.p`
  margin: 0 0 15px 0;
  color: #666;
`;

const TaskMeta = styled.div`
  padding: 15px;
  background: #f8f9fa;
  border-top: 1px solid #eee;
  display: flex;
  flex-direction: column;
  gap: 8px;
  font-size: 14px;
  color: #666;
`;

const TaskStatus = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  background: ${props => {
    switch (props.status) {
      case 'completed':
        return '#28a745';
      case 'in_progress':
        return '#ffc107';
      case 'pending':
        return '#6c757d';
      default:
        return '#6c757d';
    }
  }};
  color: white;
`;

const TaskDueDate = styled.span`
  display: inline-flex;
  align-items: center;
  gap: 4px;
  color: ${props => props.overdue ? '#dc3545' : '#666'};
`;

const Modal = styled.div`
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
`;

const ModalContent = styled.div`
  background: white;
  padding: 20px;
  border-radius: 8px;
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
`;

const Form = styled.form`
  display: flex;
  flex-direction: column;
  gap: 15px;
`;

const FormGroup = styled.div`
  display: flex;
  flex-direction: column;
  gap: 5px;
`;

const Label = styled.label`
  font-size: 14px;
  color: #666;
`;

const Input = styled.input`
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const TextArea = styled.textarea`
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  min-height: 100px;
  resize: vertical;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const Select = styled.select`
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
  
  &:focus {
    outline: none;
    border-color: #007bff;
  }
`;

const ActionButton = styled.button`
  padding: 8px 16px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 8px;
  background: none;
  border: 1px solid #ddd;
  color: #666;
  
  &:hover {
    background: #f5f5f5;
  }
  
  &.danger {
    color: #dc3545;
    border-color: #dc3545;
    
    &:hover {
      background: #dc3545;
      color: white;
    }
  }
`;

const ProjectTasks = ({ projectId }) => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    status: 'pending',
    due_date: '',
    priority: 'medium',
    assignee: ''
  });
  
  useEffect(() => {
    fetchTasks();
  }, [projectId]);
  
  const fetchTasks = async () => {
    try {
      const response = await axios.get(`/api/projects/${projectId}/tasks`);
      setTasks(response.data);
    } catch (err) {
      setError('Failed to fetch tasks');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCreateTask = async (e) => {
    e.preventDefault();
    try {
      await axios.post(`/api/projects/${projectId}/tasks`, formData);
      setShowModal(false);
      setFormData({
        title: '',
        description: '',
        status: 'pending',
        due_date: '',
        priority: 'medium',
        assignee: ''
      });
      fetchTasks();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create task');
    }
  };
  
  const handleUpdateTask = async (e) => {
    e.preventDefault();
    try {
      await axios.put(`/api/projects/${projectId}/tasks/${editingTask.id}`, formData);
      setShowModal(false);
      setEditingTask(null);
      setFormData({
        title: '',
        description: '',
        status: 'pending',
        due_date: '',
        priority: 'medium',
        assignee: ''
      });
      fetchTasks();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to update task');
    }
  };
  
  const handleDeleteTask = async (taskId) => {
    if (!window.confirm('Are you sure you want to delete this task?')) {
      return;
    }
    
    try {
      await axios.delete(`/api/projects/${projectId}/tasks/${taskId}`);
      fetchTasks();
    } catch (err) {
      setError('Failed to delete task');
    }
  };
  
  const handleEditTask = (task) => {
    setEditingTask(task);
    setFormData({
      title: task.title,
      description: task.description,
      status: task.status,
      due_date: task.due_date,
      priority: task.priority,
      assignee: task.assignee
    });
    setShowModal(true);
  };
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const closeModal = () => {
    setShowModal(false);
    setEditingTask(null);
    setFormData({
      title: '',
      description: '',
      status: 'pending',
      due_date: '',
      priority: 'medium',
      assignee: ''
    });
  };
  
  const isOverdue = (dueDate) => {
    return new Date(dueDate) < new Date() && dueDate;
  };
  
  if (loading) {
    return <div>Loading...</div>;
  }
  
  return (
    <Container>
      <Header>
        <Title>
          <FaTasks />
          Project Tasks
        </Title>
        <Button onClick={() => setShowModal(true)}>
          <FaPlus />
          New Task
        </Button>
      </Header>
      
      {error && (
        <div style={{ color: 'red', marginBottom: '20px' }}>
          {error}
        </div>
      )}
      
      <TaskList>
        {tasks.map(task => (
          <TaskCard key={task.id}>
            <TaskHeader>
              <TaskTitle>
                {task.title}
              </TaskTitle>
              <TaskActions>
                <ActionButton onClick={() => handleEditTask(task)}>
                  <FaEdit />
                  Edit
                </ActionButton>
                <ActionButton
                  className="danger"
                  onClick={() => handleDeleteTask(task.id)}
                >
                  <FaTrash />
                  Delete
                </ActionButton>
              </TaskActions>
            </TaskHeader>
            <TaskContent>
              <TaskDescription>{task.description}</TaskDescription>
              <TaskMeta>
                <TaskStatus status={task.status}>
                  {task.status === 'completed' && <FaCheck />}
                  {task.status === 'in_progress' && <FaClock />}
                  {task.status.charAt(0).toUpperCase() + task.status.slice(1).replace('_', ' ')}
                </TaskStatus>
                <TaskDueDate overdue={isOverdue(task.due_date)}>
                  <FaClock />
                  Due: {new Date(task.due_date).toLocaleDateString()}
                </TaskDueDate>
                <span>Priority: {task.priority}</span>
                <span>Assignee: {task.assignee || 'Unassigned'}</span>
              </TaskMeta>
            </TaskContent>
          </TaskCard>
        ))}
      </TaskList>
      
      {showModal && (
        <Modal>
          <ModalContent>
            <h2>{editingTask ? 'Edit Task' : 'New Task'}</h2>
            <Form onSubmit={editingTask ? handleUpdateTask : handleCreateTask}>
              <FormGroup>
                <Label htmlFor="title">Title</Label>
                <Input
                  id="title"
                  name="title"
                  value={formData.title}
                  onChange={handleChange}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="description">Description</Label>
                <TextArea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  required
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="status">Status</Label>
                <Select
                  id="status"
                  name="status"
                  value={formData.status}
                  onChange={handleChange}
                >
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="due_date">Due Date</Label>
                <Input
                  type="date"
                  id="due_date"
                  name="due_date"
                  value={formData.due_date}
                  onChange={handleChange}
                />
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="priority">Priority</Label>
                <Select
                  id="priority"
                  name="priority"
                  value={formData.priority}
                  onChange={handleChange}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </Select>
              </FormGroup>
              
              <FormGroup>
                <Label htmlFor="assignee">Assignee</Label>
                <Input
                  id="assignee"
                  name="assignee"
                  value={formData.assignee}
                  onChange={handleChange}
                  placeholder="Enter email address"
                />
              </FormGroup>
              
              <div style={{ display: 'flex', gap: '10px', justifyContent: 'flex-end' }}>
                <ActionButton type="button" onClick={closeModal}>
                  <FaTimes />
                  Cancel
                </ActionButton>
                <Button type="submit">
                  <FaSave />
                  {editingTask ? 'Update' : 'Create'}
                </Button>
              </div>
            </Form>
          </ModalContent>
        </Modal>
      )}
    </Container>
  );
};

export default ProjectTasks; 