import axios from 'axios';

const API_BASE_URL = '/api/projects';

export const projectService = {
  // Get all projects with optional filters
  getProjects: async (filters = {}) => {
    try {
      const response = await axios.get(API_BASE_URL, { params: filters });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch projects');
    }
  },

  // Get a single project by ID
  getProjectById: async (id) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/${id}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to fetch project details');
    }
  },

  // Create a new project
  createProject: async (projectData) => {
    try {
      const response = await axios.post(API_BASE_URL, projectData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to create project');
    }
  },

  // Update an existing project
  updateProject: async (id, projectData) => {
    try {
      const response = await axios.put(`${API_BASE_URL}/${id}`, projectData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update project');
    }
  },

  // Delete a project
  deleteProject: async (id) => {
    try {
      await axios.delete(`${API_BASE_URL}/${id}`);
      return true;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to delete project');
    }
  },

  // Update project status
  updateProjectStatus: async (id, status) => {
    try {
      const response = await axios.patch(`${API_BASE_URL}/${id}/status`, { status });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update project status');
    }
  },

  // Update project progress
  updateProjectProgress: async (id, progress) => {
    try {
      const response = await axios.patch(`${API_BASE_URL}/${id}/progress`, { progress });
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.message || 'Failed to update project progress');
    }
  }
}; 