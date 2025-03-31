import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:3000/api';

const taskService = {
  // Get all tasks with optional filters
  getTasks: async (filters = {}) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks`, { params: filters });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch tasks');
    }
  },

  // Get a single task by ID
  getTask: async (taskId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks/${taskId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch task');
    }
  },

  // Create a new task
  createTask: async (taskData) => {
    try {
      const response = await axios.post(`${API_BASE_URL}/tasks`, taskData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to create task');
    }
  },

  // Update a task
  updateTask: async (taskId, updates) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/tasks/${taskId}`, updates);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update task');
    }
  },

  // Delete a task
  deleteTask: async (taskId) => {
    try {
      await axios.delete(`${API_BASE_URL}/tasks/${taskId}`);
      return taskId; // Return the deleted task ID for UI updates
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to delete task');
    }
  },

  // Update task status
  updateTaskStatus: async (taskId, newStatus) => {
    try {
      const response = await axios.patch(`${API_BASE_URL}/tasks/${taskId}/status`, {
        status: newStatus
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update task status');
    }
  },

  // Update task progress
  updateTaskProgress: async (taskId, progress) => {
    try {
      const response = await axios.patch(`${API_BASE_URL}/tasks/${taskId}/progress`, {
        progress
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update task progress');
    }
  },

  // Assign task to user
  assignTask: async (taskId, userId) => {
    try {
      const response = await axios.patch(`${API_BASE_URL}/tasks/${taskId}/assign`, {
        userId
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to assign task');
    }
  },

  // Get tasks by project
  getProjectTasks: async (projectId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/projects/${projectId}/tasks`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch project tasks');
    }
  },

  // Get tasks by user
  getUserTasks: async (userId) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/users/${userId}/tasks`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch user tasks');
    }
  },

  // Get tasks by status
  getTasksByStatus: async (status) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks/status/${status}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch tasks by status');
    }
  },

  // Get tasks by priority
  getTasksByPriority: async (priority) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks/priority/${priority}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch tasks by priority');
    }
  },

  // Get tasks by deadline range
  getTasksByDeadlineRange: async (startDate, endDate) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks/deadline-range`, {
        params: { startDate, endDate }
      });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch tasks by deadline range');
    }
  },

  // Get overdue tasks
  getOverdueTasks: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks/overdue`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch overdue tasks');
    }
  },

  // Get upcoming tasks (within next 7 days)
  getUpcomingTasks: async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/tasks/upcoming`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch upcoming tasks');
    }
  }
};

export { taskService }; 